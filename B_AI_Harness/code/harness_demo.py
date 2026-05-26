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
    elapsed: float = 0.0
    sub_topics: list[str] = field(default_factory=list)
    compiled_report: str = ""

    def log(self, phase: str, role: str, content: str) -> None:
        self.events.append(TraceEvent(phase, role, content))


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
# PHASE 2 — Executor (per sub-topic ReAct loop)
# ---------------------------------------------------------------------------

def execute_subtopic(
    sub_topic: str,
    run: HarnessRun,
    per_topic_papers: int = 3,
) -> list[dict]:
    """For one sub-topic: search -> top-K -> summarize each -> note_save."""
    search_query = SUBTOPIC_QUERIES.get(sub_topic, sub_topic.lower())
    run.log("EXECUTE", "agent",
            f"Thought: I need to gather recent papers on '{sub_topic}'.")
    run.log("EXECUTE", "action",
            f"arxiv_search(query={search_query!r}, year_min=2024, year_max=2026, max_results={per_topic_papers})")
    papers = arxiv_search(search_query, year_min=2024, year_max=2026, max_results=per_topic_papers)
    run.tool_calls += 1
    run.log("EXECUTE", "observation",
            f"Returned {len(papers)} papers: " + ", ".join(p["arxiv_id"] for p in papers))

    summarised: list[dict] = []
    for p in papers:
        run.log("EXECUTE", "agent",
                f"Thought: Summarise paper {p['arxiv_id']} ({p['title'][:50]}…).")
        run.log("EXECUTE", "action", f"paper_summarize(arxiv_id={p['arxiv_id']!r})")
        s = paper_summarize(p["arxiv_id"])
        run.tool_calls += 1
        if "error" in s:
            run.log("EXECUTE", "observation", f"ERROR: {s['error']}")
            continue
        run.log("EXECUTE", "observation",
                f"contribution: {s['key_contribution']}")

        body = (
            f"**{s['title']}** ({s['venue']} {s['year']}; arxiv:{s['arxiv_id']})\n"
            f"- Contribution: {s['key_contribution']}\n"
            f"- Methods: {s['methods']}\n"
            f"- Results: {s['results']}\n"
            f"- Limitations: {s['limitations']}"
        )
        ack = note_save(sub_topic, body, tags=[sub_topic])
        run.tool_calls += 1
        run.log("EXECUTE", "action",
                f"note_save(topic={sub_topic!r}, content=<{len(body)} chars>)")
        run.log("EXECUTE", "observation",
                f"note_count={ack['note_count']} total_chars={ack['total_chars']}")
        summarised.append({**p, **{k: s[k] for k in
                                   ("key_contribution", "methods", "results", "limitations")}})

    return summarised


# ---------------------------------------------------------------------------
# PHASE 3 — Critic
# ---------------------------------------------------------------------------

def critic_review(
    run: HarnessRun,
    sub_topics: list[str],
    all_papers: dict[str, list[dict]],
    target_per_topic: int = 2,
) -> list[str]:
    """Return list of sub-topics that need more search; empty if coverage OK."""
    weak = [t for t in sub_topics if len(all_papers.get(t, [])) < target_per_topic]
    if weak:
        run.log("CRITIC", "agent",
                f"Coverage gap: {weak}. Recommending one extra search per gap.")
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
    all_papers: dict[str, list[dict]],
) -> str:
    title = "A Mini-Survey on " + query.strip().rstrip(".?!").title()
    n_papers = sum(len(ps) for ps in all_papers.values())
    intro = (
        f"This mini-survey was compiled by an AI Harness from {n_papers} papers across "
        f"{len(sub_topics)} sub-topic(s): {', '.join(sub_topics)}. "
        f"All citations come from a tool-verified arXiv lookup; no LLM-generated paper IDs "
        f"are accepted by the Compiler stage."
    )

    section_blocks = []
    for st in sub_topics:
        papers = all_papers.get(st, [])
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
        for p in all_papers.get(st, []):
            rows.append(
                f"| {p['title'][:48]} | {st} | {p['year']} | {p['venue']} | "
                f"{p['key_contribution'][:70]} |"
            )
    comparison_table = "\n".join(rows)

    refs: list[str] = []
    seen: set[str] = set()
    for st in sub_topics:
        for p in all_papers.get(st, []):
            if p["arxiv_id"] in seen:
                continue
            seen.add(p["arxiv_id"])
            refs.append(f"[{len(refs)+1}] " + citation_format(p, style="IEEE"))
            run.tool_calls += 1
    references = "\n\n".join(refs)

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

def run_harness(query: str, max_critic_rounds: int = 1) -> HarnessRun:
    reset_note_store()
    backend_name, planner = choose_planner()
    run = HarnessRun(query=query, backend=backend_name)
    t0 = time.time()

    # PHASE 1
    run.log("PLAN", "agent", f"User query: {query!r}")
    plan = planner(query)
    run.sub_topics = plan
    run.log("PLAN", "agent", f"Plan: {len(plan)} sub-topics → {plan}")

    # PHASE 2
    all_papers: dict[str, list[dict]] = {}
    for st in plan:
        run.log("EXECUTE", "agent", f"--- Sub-topic: {st} ---")
        all_papers[st] = execute_subtopic(st, run, per_topic_papers=3)

    # PHASE 3
    for round_i in range(max_critic_rounds):
        weak = critic_review(run, plan, all_papers, target_per_topic=2)
        if not weak:
            break
        for st in weak:
            run.log("EXECUTE", "agent", f"Critic-triggered re-search for {st!r}.")
            extra = execute_subtopic(st, run, per_topic_papers=4)
            existing_ids = {p["arxiv_id"] for p in all_papers[st]}
            for p in extra:
                if p["arxiv_id"] not in existing_ids:
                    all_papers[st].append(p)

    # PHASE 4
    run.elapsed = time.time() - t0
    run.compiled_report = compile_report(run, query, plan, all_papers)
    run.log("COMPILE", "agent",
            f"Report compiled ({len(run.compiled_report)} chars, "
            f"{run.tool_calls} total tool calls).")
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
    print(f"[harness] wallclock          : {run.elapsed:.2f}s")
    print(f"[harness] transcript         -> {transcript_path}")
    print(f"[harness] compiled report    -> {report_path}")
    print()
    print("=" * 72)
    print(report_only)


if __name__ == "__main__":
    main()
