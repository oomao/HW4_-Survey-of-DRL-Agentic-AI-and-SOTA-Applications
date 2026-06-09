"""
HW4 Version B — test suite for the AI Harness.

Covers the four tools (unit) and the end-to-end pipeline invariants that back
the report's design claims:

  - no duplicate papers across sub-topics      (cross-topic dedup)
  - every cited id exists in the corpus        (anti-hallucination guarantee)
  - the Critic loop actually fires on a gap    (orchestration is not dead code)
  - offline backend is deterministic           (CI-safe / reproducible)

Run:
    python -m pytest code/test_harness.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tools
from tools import (
    arxiv_search,
    search_scored,
    paper_summarize,
    citation_format,
    note_save,
    reset_note_store,
    get_note_store,
    dispatch_tool,
    validate_tool_call,
    ToolValidationError,
    CORPUS,
)
from harness_demo import run_harness

CORPUS_IDS = {p["arxiv_id"] for p in CORPUS}
FLAGSHIP = "Survey robotics VLA models in 2024-2026"
DIFFUSION_POLICY_ID = "2303.04137"  # seminal, pre-2024


# --------------------------------------------------------------------------
# Tool 1: arxiv_search
# --------------------------------------------------------------------------

def test_arxiv_search_returns_relevant_papers():
    results = arxiv_search("robotics vla", year_min=2024, year_max=2026, max_results=3)
    assert 1 <= len(results) <= 3
    assert all("arxiv_id" in p and "title" in p for p in results)
    assert all(2024 <= p["year"] <= 2026 for p in results)


def test_arxiv_search_year_filter_excludes_then_includes():
    # Diffusion Policy (2023) must be filtered out at year_min=2024 ...
    ids_2024 = {p["arxiv_id"] for p in arxiv_search("diffusion policy robot", year_min=2024)}
    assert DIFFUSION_POLICY_ID not in ids_2024
    # ... and recoverable once the year range is broadened (what the Critic does).
    ids_2022 = {p["arxiv_id"] for p in arxiv_search("diffusion policy robot", year_min=2022)}
    assert DIFFUSION_POLICY_ID in ids_2022


def test_arxiv_search_no_match_returns_empty_list():
    assert arxiv_search("quantum chromodynamics lattice qft") == []


def test_search_scored_is_descending():
    scored = search_scored("humanoid robot vla", year_min=2024, max_results=5)
    scores = [s for _p, s in scored]
    assert scores == sorted(scores, reverse=True)
    assert all(s > 0 for s in scores)


# --------------------------------------------------------------------------
# Tool 2: paper_summarize
# --------------------------------------------------------------------------

def test_paper_summarize_known_id_is_structured():
    s = paper_summarize("2406.09246")
    for field in ("key_contribution", "methods", "results", "limitations"):
        assert field in s and s[field]


def test_paper_summarize_unknown_id_returns_error_not_raise():
    s = paper_summarize("9999.99999")
    assert "error" in s
    assert s["arxiv_id"] == "9999.99999"


# --------------------------------------------------------------------------
# Tool 3: citation_format
# --------------------------------------------------------------------------

def test_citation_format_all_styles():
    paper = paper_summarize("2501.12948")
    assert "arXiv:2501.12948" in citation_format(paper, "IEEE")
    assert citation_format(paper, "APA").startswith(paper["authors"])
    assert citation_format(paper, "BibTeX").startswith("@article{")
    assert "In " in citation_format(paper, "ACM")


def test_citation_format_missing_field_uses_placeholder():
    out = citation_format({"title": "Orphan paper"}, "IEEE")
    assert "<unknown" in out


# --------------------------------------------------------------------------
# Tool 4: note_save (the only tool with side effects)
# --------------------------------------------------------------------------

def test_note_save_persists_with_meta():
    reset_note_store()
    ack = note_save("topicX", "a note", tags=["t"], meta={"arxiv_id": "1234.5678"})
    assert ack["persisted"] is True
    assert ack["note_count"] == 1
    bucket = get_note_store().get_topic("topicX")
    assert bucket["notes"][0]["meta"]["arxiv_id"] == "1234.5678"
    reset_note_store()


def test_note_save_empty_topic_rejected():
    ack = note_save("   ", "content")
    assert ack["persisted"] is False
    assert "error" in ack


# --------------------------------------------------------------------------
# Schema-validated dispatch (the function-calling boundary guard)
# --------------------------------------------------------------------------

def test_dispatch_tool_executes_valid_call():
    # A schema-valid call is routed through TOOL_REGISTRY and returns the result.
    s = dispatch_tool("paper_summarize", {"arxiv_id": "2406.09246"})
    assert s["title"].startswith("OpenVLA")


def test_validate_rejects_unknown_tool():
    with pytest.raises(ToolValidationError):
        validate_tool_call("delete_everything", {"path": "/"})


def test_validate_rejects_missing_required_field():
    # note_save requires both topic and content; omitting content must fail.
    with pytest.raises(ToolValidationError):
        validate_tool_call("note_save", {"topic": "t"})


def test_validate_rejects_out_of_enum_style():
    # citation_format.style is constrained to IEEE/ACM/APA/BibTeX.
    with pytest.raises(ToolValidationError):
        validate_tool_call("citation_format", {"paper": {}, "style": "MLA"})


def test_dispatch_preserves_tool_failsafe():
    # A schema-valid call to a runtime-failing tool still returns the tool's
    # structured error dict (it does NOT raise) — the two error layers are distinct.
    out = dispatch_tool("paper_summarize", {"arxiv_id": "9999.99999"})
    assert "error" in out and out["arxiv_id"] == "9999.99999"


# --------------------------------------------------------------------------
# Pipeline invariants
# --------------------------------------------------------------------------

def test_pipeline_has_no_duplicate_papers():
    run = run_harness(FLAGSHIP)
    assert len(run.paper_ids) == len(set(run.paper_ids)), "duplicate papers in output"


def test_pipeline_every_cited_id_exists_in_corpus():
    # The anti-hallucination guarantee: the Compiler never emits an id the
    # tools did not actually return from the corpus.
    run = run_harness(FLAGSHIP)
    assert run.paper_ids
    assert all(pid in CORPUS_IDS for pid in run.paper_ids)


def test_critic_loop_fires_and_recovers_seminal_paper():
    run = run_harness(FLAGSHIP)
    assert run.critic_rounds_fired >= 1, "critic never fired — loopback is dead code"
    assert DIFFUSION_POLICY_ID in run.paper_ids, "critic did not recover Diffusion Policy"


def test_disabling_critic_drops_the_recovered_paper():
    run = run_harness(FLAGSHIP, enable_critic=False)
    assert run.critic_rounds_fired == 0
    assert DIFFUSION_POLICY_ID not in run.paper_ids


def test_offline_backend_is_deterministic():
    a = run_harness(FLAGSHIP)
    b = run_harness(FLAGSHIP)
    assert sorted(a.paper_ids) == sorted(b.paper_ids)
    assert a.tool_calls == b.tool_calls
