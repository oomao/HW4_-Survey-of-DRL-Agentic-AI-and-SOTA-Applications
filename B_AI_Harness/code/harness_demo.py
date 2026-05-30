"""
HW4 Version B — AI Harness Demo (DRL Research Assistant)

A minimal but end-to-end runnable implementation of the four-phase
AI Harness described in report/report.md:

    PHASE 1  PLAN     — decompose user query into sub-topics
    PHASE 2  EXECUTE  — ReAct loop per sub-topic (search → summarize → note_save)
    PHASE 3  CRITIC   — coverage check, optionally trigger more searches
    PHASE 4  COMPILE  — assemble notes + citations into a Markdown report

Two LLM backends are supported (selected automatically):
  - If env var ANTHROPIC_API_KEY is set    → real Claude (claude-haiku-4-5-20251001)
  - Otherwise                              → deterministic offline planner

Run:
    python code/harness_demo.py
    python code/harness_demo.py "Survey foundation agents in 2024-2026"

Output:
    artifacts/demo_run.md       — full transcript + compiled mini-survey
    artifacts/notes.json        — persisted note store from PHASE 2
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools import (
    arxiv_search,
    search_scored,
    paper_summarize,
    citation_format,
    note_save,
    get_note_store,
    reset_note_store,
    TOOL_REGISTRY,
)

HERE = Path(__file__).resolve().parent
ARTIFACT_DIR = HERE.parent / "artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Trace data structures
# ---------------------------------------------------------------------------

@dataclass
class TraceEvent:
    phase: str
    role: str
    content: str
    ts: float = field(default_factory=time.time)


@dataclass
class HarnessRun:
    query: str
    backend: str
    events: list[TraceEvent] = field(default_factory=list)
    tool_calls: int = 0
    useful_tool_calls: int = 0
    critic_rounds_fired: int = 0
    elapsed: float = 0.0
    sub_topics: list[str] = field(default_factory=list)
    compiled_report: str = ""
    paper_ids: list[str] = field(default_factory=list)
    summary_cache: dict[str, dict] = field(default_factory=dict)

    def log(self, phase: str, role: str, content: str) -> None:
        self.events.append(TraceEvent(phase, role, content))

    def summarize_memoized(self, arxiv_id: str) -> dict:
        """paper_summarize with within-run memoization (short-term memory).

        A repeated id is served from cache and does *not* count as a new tool
        call — this is the controller reusing short-term memory rather than
        re-paying for an identical observation.
        """
        if arxiv_id in self.summary_cache:
            self.log("EXECUTE", "observation",
                     f"(memoized) reused cached summary for {arxiv_id}")
            return self.summary_cache[arxiv_id]
        s = paper_summarize(arxiv_id)
        self.tool_calls += 1
        if "error" not in s:
            self.useful_tool_calls += 1
            self.summary_cache[arxiv_id] = s
        return s


# ---------------------------------------------------------------------------
# PHASE 1 — Planner
# ---------------------------------------------------------------------------

PLAN_BY_KEYWORD: dict[tuple[str, ...], list[str]] = {
    ("robotics", "vla"): ["VLA foundation models", "Diffusion Policy", "Humanoid VLA"],
    ("robotics", "humanoid"): ["Humanoid VLA", "Sim2Real for humanoid", "VLA foundation models"],
    ("agentic", "ai"): ["LLM agents", "RLHF alignment", "Reasoning RL"],
    ("agentic", "agent"): ["LLM agents", "RLHF alignment", "Reasoning RL"],
    ("foundation", "agent"): ["LLM agents", "VLA foundation models", "Reasoning RL"],
    ("rlhf", ): ["RLHF alignment", "Reasoning RL"],
    ("reasoning", ): ["Reasoning RL", "RLHF alignment"],
    ("world", "model"): ["World models", "VLA foundation models"],
    ("sim2real", ): ["Sim2Real for humanoid", "VLA foundation models"],
    ("game", "ai"): ["Game AI agents", "World models"],
    ("minecraft", ): ["Game AI agents", "World models"],
    ("alphago", ): ["Game AI agents"],
    ("diffusion", "policy"): ["Diffusion Policy", "VLA foundation models"],
    ("vla", ): ["VLA foundation models", "Diffusion Policy", "Humanoid VLA"],
}

# Map abstract sub-topic name -> concrete search query for arxiv_search
SUBTOPIC_QUERIES: dict[str, str] = {
    "VLA foundation models": "vla foundation",
    "Diffusion Policy": "diffusion policy robot",
    "Humanoid VLA": "humanoid robot vla",
    "LLM agents": "llm agent agentic",
    "RLHF alignment": "rlhf preference alignment llm",
    "Reasoning RL": "reasoning rl verifiable reward llm",
    "World models": "world model dreamerv3",
    "Sim2Real for humanoid": "sim2real domain randomization llm reward",
    "Game AI agents": "game ai minecraft agent",
}


def plan_offline(query: str) -> list[str]:
    """Deterministic planner: keyword-match the query into sub-topics."""
    q = query.lower()
    for keys, plan in PLAN_BY_KEYWORD.items():
        if all(k in q for k in keys):
            return plan
    # default fallback: try single-keyword fallback
    for keys, plan in PLAN_BY_KEYWORD.items():
        if any(k in q for k in keys):
            return plan
    return ["VLA foundation models", "LLM agents", "Reasoning RL"]


def plan_with_claude(query: str) -> list[str]:
    """Calls Claude to decompose query into 2-4 sub-topics."""
    import anthropic
    client = anthropic.Anthropic()
    sys_prompt = (
        "You are the Planner role of an AI Harness for DRL literature survey. "
        "Decompose the user query into 2-4 narrow sub-topics. Respond with a "
        "JSON array of strings, no commentary. "
        "Sub-topics must be drawn from this fixed taxonomy (case-sensitive): "
        + json.dumps(list(SUBTOPIC_QUERIES.keys()))
    )
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        system=sys_prompt,
        messages=[{"role": "user", "content": query}],
    )
    text = resp.content[0].text.strip()
    m = re.search(r"\[.*?\]", text, re.DOTALL)
    if not m:
        return plan_offline(query)
    try:
        plan = json.loads(m.group(0))
        plan = [p for p in plan if p in SUBTOPIC_QUERIES]
        return plan or plan_offline(query)
    except json.JSONDecodeError:
        return plan_offline(query)


def choose_planner():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic", plan_with_claude
    return "offline", plan_offline


# ---------------------------------------------------------------------------
# PHASE 2 — Executor (search -> cross-topic dedup -> summarize -> note_save)
# ---------------------------------------------------------------------------

def search_subtopic(
    sub_topic: str,
    run: HarnessRun,
    max_results: int = 4,
    year_min: int = 2024,
) -> list[tuple[dict, int]]:
    """ReAct search step for one sub-topic. Returns [(paper, score), ...]."""
    search_query = SUBTOPIC_QUERIES.get(sub_topic, sub_topic.lower())
    run.log("EXECUTE", "agent",
            f"Thought: I need to gather recent papers on '{sub_topic}'.")
    run.log("EXECUTE", "action",
            f"arxiv_search(query={search_query!r}, year_min={year_min}, year_max=2026, max_results={max_results})")
    scored = search_scored(search_query, year_min=year_min, year_max=2026, max_results=max_results)
    run.tool_calls += 1
    run.useful_tool_calls += 1
    run.log("EXECUTE", "observation",
            "Returned " + (", ".join(f"{p['arxiv_id']}(score {s})" for p, s in scored) or "nothing"))
    return scored


def assign_papers(
    scored_by_topic: dict[str, list[tuple[dict, int]]],
    sub_topics: list[str],
    already_assigned: dict[str, str] | None = None,
) -> dict[str, list[dict]]:
    """Cross-topic de-duplication.

    Each unique paper is assigned to the single sub-topic where it scores
    highest (ties break toward the earlier sub-topic in the plan). A paper
    already claimed by a previous round is never reassigned. This is what
    stops the same paper appearing under three headings.
    """
    already_assigned = already_assigned or {}
    best: dict[str, tuple[str, int, dict]] = {}  # arxiv_id -> (topic, score, paper)
    for topic in sub_topics:
        for rank, (paper, score) in enumerate(scored_by_topic.get(topic, [])):
            aid = paper["arxiv_id"]
            if aid in already_assigned:
                continue
            if aid not in best or score > best[aid][1]:
                best[aid] = (topic, score, paper)

    per_topic: dict[str, list[dict]] = {t: [] for t in sub_topics}
    for aid, (topic, _score, paper) in best.items():
        per_topic[topic].append(paper)
    return per_topic


def summarize_and_store(
    sub_topic: str,
    papers: list[dict],
    run: HarnessRun,
) -> None:
    """Summarize each assigned paper and persist a structured note (meta)."""
    for p in papers:
        run.log("EXECUTE", "agent",
                f"Thought: Summarise paper {p['arxiv_id']} ({p['title'][:50]}…).")
        run.log("EXECUTE", "action", f"paper_summarize(arxiv_id={p['arxiv_id']!r})")
        s = run.summarize_memoized(p["arxiv_id"])
        if "error" in s:
            run.log("EXECUTE", "observation", f"ERROR: {s['error']}")
            continue
        run.log("EXECUTE", "observation", f"contribution: {s['key_contribution']}")

        body = (
            f"**{s['title']}** ({s['venue']} {s['year']}; arxiv:{s['arxiv_id']})\n"
            f"- Contribution: {s['key_contribution']}\n"
            f"- Methods: {s['methods']}\n"
            f"- Results: {s['results']}\n"
            f"- Limitations: {s['limitations']}"
        )
        meta = {k: s[k] for k in
                ("arxiv_id", "title", "authors", "year", "venue",
                 "key_contribution", "methods", "results", "limitations")}
        meta["sub_topic"] = sub_topic
        ack = note_save(sub_topic, body, tags=[sub_topic], meta=meta)
        run.tool_calls += 1
        run.useful_tool_calls += 1
        run.log("EXECUTE", "action",
                f"note_save(topic={sub_topic!r}, content=<{len(body)} chars>, meta=<paper record>)")
        run.log("EXECUTE", "observation",
                f"note_count={ack['note_count']} total_chars={ack['total_chars']} persisted={ack['persisted']}")


def view_from_store(sub_topics: list[str]) -> dict[str, list[dict]]:
    """Reconstruct the per-topic paper view *purely from the note store*.

    This is the Compiler's only source of truth — it reads persisted note
    `meta`, de-duplicates by arxiv_id (keeping the first persisted topic), and
    never trusts any in-context fact the LLM did not commit via note_save.
    """
    store = get_note_store()
    per_topic: dict[str, list[dict]] = {t: [] for t in sub_topics}
    seen: set[str] = set()
    for topic in sub_topics:
        bucket = store.get_topic(topic)
        for note in bucket.get("notes", []):
            meta = note.get("meta") or {}
            aid = meta.get("arxiv_id")
            if not aid or aid in seen:
                continue
            seen.add(aid)
            per_topic[topic].append(meta)
    return per_topic


# ---------------------------------------------------------------------------
# PHASE 3 — Critic
# ---------------------------------------------------------------------------

def critic_review(
    run: HarnessRun,
    sub_topics: list[str],
    view: dict[str, list[dict]],
    target_per_topic: int = 1,
) -> list[str]:
    """Binary coverage check over the *de-duplicated* store view.

    A sub-topic is weak if, after cross-topic de-duplication, it owns fewer
    than `target_per_topic` papers — i.e. all of its hits were more relevant
    to another sub-topic, leaving it with no distinctive coverage.
    """
    counts = {t: len(view.get(t, [])) for t in sub_topics}
    run.log("CRITIC", "agent",
            "Post-dedup coverage: " + ", ".join(f"{t}={c}" for t, c in counts.items()))
    weak = [t for t in sub_topics if counts[t] < target_per_topic]
    if weak:
        run.log("CRITIC", "agent",
                f"Coverage GAP on {weak} → broadening year range and re-searching (1 round).")
    else:
        run.log("CRITIC", "agent",
                f"Coverage check passed for all {len(sub_topics)} sub-topics.")
    return weak


# ---------------------------------------------------------------------------
# PHASE 4 — Compiler
# ---------------------------------------------------------------------------

REPORT_TEMPLATE = """# {title}

> *AI Harness compiled survey — generated by DRL Research Assistant ({backend} backend).*
> Query: **"{query}"**

## 1. Overview

{intro}

## 2. Findings by Sub-topic

{sections}

## 3. Comparison Snapshot

{comparison_table}

## 4. References

{references}

---
\\textit{{Compiled in {elapsed:.2f}s · {tool_calls} tool calls · {n_papers} papers across {n_topics} sub-topics.}}
"""


def compile_report(
    run: HarnessRun,
    query: str,
    sub_topics: list[str],
    view: dict[str, list[dict]],
) -> str:
    # Strip a leading "Survey " so the title doesn't read "Mini-Survey on Survey…",
    # and keep the query verbatim so acronyms (VLA, RLHF) keep their casing.
    topic = re.sub(r"^\s*survey\s+", "", query.strip().rstrip(".?!"), flags=re.IGNORECASE)
    title = "A Mini-Survey on " + topic
    n_papers = sum(len(ps) for ps in view.values())
    intro = (
        f"This mini-survey was compiled by an AI Harness from {n_papers} papers across "
        f"{len(sub_topics)} sub-topic(s): {', '.join(sub_topics)}. "
        f"Every entry below is reconstructed from the persistent note store (each note's "
        f"structured `meta`); no LLM-inline paper IDs or facts are accepted by the Compiler stage."
    )

    section_blocks = []
    for st in sub_topics:
        papers = view.get(st, [])
        if not papers:
            continue
        bullet_lines = []
        for p in papers:
            bullet_lines.append(
                f"- **{p['title']}** ({p['venue']} {p['year']}; arxiv:{p['arxiv_id']}). "
                f"_{p['key_contribution']}_ "
                f"Limitation: {p['limitations']}"
            )
        section_blocks.append(f"### 2.{sub_topics.index(st)+1} {st}\n\n" + "\n".join(bullet_lines))
    sections = "\n\n".join(section_blocks)

    rows = ["| Paper | Sub-topic | Year | Venue | One-line contribution |",
            "|---|---|---|---|---|"]
    for st in sub_topics:
        for p in view.get(st, []):
            rows.append(
                f"| {p['title'][:48]} | {st} | {p['year']} | {p['venue']} | "
                f"{p['key_contribution'][:70]} |"
            )
    comparison_table = "\n".join(rows)

    refs: list[str] = []
    seen: set[str] = set()
    for st in sub_topics:
        for p in view.get(st, []):
            if p["arxiv_id"] in seen:
                continue
            seen.add(p["arxiv_id"])
            refs.append(f"[{len(refs)+1}] " + citation_format(p, style="IEEE"))
            run.tool_calls += 1
            run.useful_tool_calls += 1
    references = "\n\n".join(refs)
    run.paper_ids = list(seen)

    return REPORT_TEMPLATE.format(
        title=title,
        backend=run.backend,
        query=query,
        intro=intro,
        sections=sections,
        comparison_table=comparison_table,
        references=references,
        elapsed=run.elapsed,
        tool_calls=run.tool_calls,
        n_papers=n_papers,
        n_topics=len(sub_topics),
    )


# ---------------------------------------------------------------------------
# End-to-end runner
# ---------------------------------------------------------------------------

def _assigned_map(view: dict[str, list[dict]]) -> dict[str, str]:
    return {p["arxiv_id"]: topic for topic, papers in view.items() for p in papers}


def run_harness(
    query: str,
    max_critic_rounds: int = 1,
    enable_critic: bool = True,
    enable_planner: bool = True,
) -> HarnessRun:
    reset_note_store()
    backend_name, planner = choose_planner()
    run = HarnessRun(query=query, backend=backend_name)
    t0 = time.time()

    # PHASE 1 — PLAN
    run.log("PLAN", "agent", f"User query: {query!r}")
    if enable_planner:
        plan = planner(query)
    else:
        # ablation: skip decomposition, treat the whole query as one sub-topic
        plan = ["VLA foundation models"]
    run.sub_topics = plan
    run.log("PLAN", "agent", f"Plan: {len(plan)} sub-topics → {plan}")

    # PHASE 2 — EXECUTE: search every sub-topic, then cross-topic dedup,
    # then summarize + persist only the paper assigned to each sub-topic.
    scored_by_topic: dict[str, list[tuple[dict, int]]] = {}
    for st in plan:
        run.log("EXECUTE", "agent", f"--- Sub-topic: {st} ---")
        scored_by_topic[st] = search_subtopic(st, run, max_results=4, year_min=2024)

    assigned = assign_papers(scored_by_topic, plan)
    run.log("EXECUTE", "agent",
            "Cross-topic dedup → " +
            ", ".join(f"{t}: [{', '.join(p['arxiv_id'] for p in ps)}]" for t, ps in assigned.items()))
    for st in plan:
        summarize_and_store(st, assigned[st], run)

    view = view_from_store(plan)

    # PHASE 3 — CRITIC (binary coverage check + ≤1 broadened re-search round)
    if enable_critic:
        for _round in range(max_critic_rounds):
            weak = critic_review(run, plan, view, target_per_topic=1)
            if not weak:
                break
            run.critic_rounds_fired += 1
            scored_weak: dict[str, list[tuple[dict, int]]] = {}
            for st in weak:
                run.log("EXECUTE", "agent",
                        f"Critic-triggered re-search for {st!r} (year_min=2022).")
                scored_weak[st] = search_subtopic(st, run, max_results=4, year_min=2022)
            extra = assign_papers(scored_weak, weak, already_assigned=_assigned_map(view))
            run.log("EXECUTE", "agent",
                    "Re-search dedup → " +
                    ", ".join(f"{t}: [{', '.join(p['arxiv_id'] for p in ps)}]" for t, ps in extra.items()))
            for st in weak:
                summarize_and_store(st, extra[st], run)
            view = view_from_store(plan)
    else:
        run.log("CRITIC", "agent", "[ablation] critic disabled — skipping coverage check.")

    # PHASE 4 — COMPILE (purely from the persistent note store)
    run.elapsed = time.time() - t0
    run.compiled_report = compile_report(run, query, plan, view)
    run.log("COMPILE", "agent",
            f"Report compiled from note store ({len(run.compiled_report)} chars, "
            f"{run.tool_calls} total tool calls, {run.critic_rounds_fired} critic round(s) fired).")
    return run


# ---------------------------------------------------------------------------
# Rendering & CLI
# ---------------------------------------------------------------------------

def render_transcript(run: HarnessRun) -> str:
    lines = [
        "# AI Harness Demo Run",
        "",
        f"- **Query**: {run.query}",
        f"- **Backend**: {run.backend}",
        f"- **Sub-topics**: {run.sub_topics}",
        f"- **Total tool calls**: {run.tool_calls}",
        f"- **Tool-call efficiency**: {run.useful_tool_calls}/{run.tool_calls} "
        f"= {(run.useful_tool_calls / run.tool_calls * 100 if run.tool_calls else 0):.0f}%",
        f"- **Critic rounds fired**: {run.critic_rounds_fired}",
        f"- **Wallclock**: {run.elapsed:.2f}s",
        "",
        "## Phase Transcript",
        "",
    ]
    for ev in run.events:
        lines.append(f"`[{ev.phase}][{ev.role}]` {ev.content}")
    lines.append("\n---\n")
    lines.append("## Compiled Report\n")
    lines.append(run.compiled_report)
    return "\n".join(lines)


def main() -> None:
    query = " ".join(sys.argv[1:]) or "Survey robotics VLA models in 2024-2026"
    print(f"[harness] running query: {query}\n")
    run = run_harness(query)

    out = render_transcript(run)
    transcript_path = ARTIFACT_DIR / "demo_run.md"
    transcript_path.write_text(out, encoding="utf-8")

    report_only = run.compiled_report
    report_path = ARTIFACT_DIR / "compiled_report.md"
    report_path.write_text(report_only, encoding="utf-8")

    print(f"[harness] backend            : {run.backend}")
    print(f"[harness] sub-topics         : {run.sub_topics}")
    print(f"[harness] tool calls         : {run.tool_calls}")
    print(f"[harness] tool efficiency    : {run.useful_tool_calls}/{run.tool_calls}")
    print(f"[harness] critic rounds      : {run.critic_rounds_fired}")
    print(f"[harness] wallclock          : {run.elapsed:.2f}s")
    print(f"[harness] transcript         -> {transcript_path}")
    print(f"[harness] compiled report    -> {report_path}")
    print()
    print("=" * 72)
    print(report_only)


if __name__ == "__main__":
    main()
