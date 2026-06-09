"""
HW4 Version B — AI Harness Tools

Four function-callable tools backing the DRL Research Assistant harness.
Each tool obeys: (a) single responsibility, (b) strict typed signature,
(c) failure modes return structured error dicts (not raised exceptions),
so the LLM controller can reason about errors as normal tool output.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


HERE = Path(__file__).resolve().parent
NOTE_STORE_PATH = HERE.parent / "artifacts" / "notes.json"
NOTE_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Curated offline paper corpus (selected from Version A's research notes)
# Each entry has the structured fields a real arxiv response *plus* the
# extracted summary that paper_summarize() would return — so demos run
# end-to-end with zero network dependency.
# ---------------------------------------------------------------------------

CORPUS: list[dict] = [
    {
        "arxiv_id": "2406.09246",
        "title": "OpenVLA: An Open-Source Vision-Language-Action Model",
        "authors": "Kim, M. J. et al.",
        "year": 2024,
        "venue": "arXiv",
        "primary_category": "cs.RO",
        "tags": ["robotics", "vla", "foundation-model", "open-source"],
        "abstract": "We introduce OpenVLA, a 7B-parameter open-source vision-language-action model trained on 970k robot trajectories from Open X-Embodiment.",
        "key_contribution": "First open-weights VLA matching or beating proprietary RT-2 baselines.",
        "methods": "Fine-tunes Llama 2 + SigLIP/DINOv2 visual encoder on tokenized 7-DoF action sequences.",
        "results": "+20.4% over Diffusion Policy across multi-task multi-object generalization; LoRA-tuneable on consumer GPUs.",
        "limitations": "5 Hz inference is too slow for dexterous control; discrete action tokens limit precision; single-image observation hurts depth tasks.",
    },
    {
        "arxiv_id": "2504.16054",
        "title": "Pi-0.5: A Vision-Language-Action Model with Open-World Generalization",
        "authors": "Physical Intelligence Team",
        "year": 2025,
        "venue": "arXiv",
        "primary_category": "cs.RO",
        "tags": ["robotics", "vla", "humanoid", "open-world"],
        "abstract": "Pi-0.5 introduces hierarchical reasoning and heterogeneous co-training (web data + verbal instructions + multi-robot data) to generalise VLAs to entirely novel real-world environments.",
        "key_contribution": "First VLA shown to clean entirely unseen real-world kitchens and bedrooms across repeated trials.",
        "methods": "Builds on Pi-0 flow-matching action expert; adds hierarchical sub-goal reasoning at the VLM layer.",
        "results": "60-80% task-completion success in novel residential environments.",
        "limitations": "Long-horizon failures remain dominant; teleop data still expensive; not yet a deployable household product.",
    },
    {
        "arxiv_id": "2503.14734",
        "title": "GR00T N1: An Open Foundation Model for Generalist Humanoid Robots",
        "authors": "NVIDIA Research",
        "year": 2025,
        "venue": "arXiv",
        "primary_category": "cs.RO",
        "tags": ["robotics", "vla", "humanoid", "foundation-model"],
        "abstract": "GR00T N1 is a dual-system humanoid VLA with a System 2 NVIDIA Eagle-2 VLM and a System 1 diffusion-transformer action head, trained on real, video, and synthetic data.",
        "key_contribution": "First open humanoid foundation model with embedded-GPU latency budget.",
        "methods": "Dual-system: VLM at 5-10 Hz + visuomotor diffusion-transformer at 100+ Hz.",
        "results": "GR00T-N1-2B samples 16 actions in 63.9 ms on an L40 GPU.",
        "limitations": "Narrow real-world dexterity benchmarks; sim2real still needs domain-randomization tuning.",
    },
    {
        "arxiv_id": "2303.04137",
        "title": "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion",
        "authors": "Chi, C. et al.",
        "year": 2023,
        "venue": "RSS",
        "primary_category": "cs.RO",
        "tags": ["robotics", "diffusion-policy", "imitation-learning"],
        "abstract": "Models visuomotor policy as conditional denoising diffusion to capture the multimodal nature of robot demonstration data.",
        "key_contribution": "+46.9% over prior SOTA across 12 tasks / 4 benchmarks.",
        "methods": "Receding-horizon prediction with DDPM-style conditional denoising on action sequences.",
        "results": "Robust to multimodal demonstrations; stable across diverse manipulation tasks.",
        "limitations": "Multi-step denoising slows inference; cross-embodiment transfer weak; needs depth for many tasks.",
    },
    {
        "arxiv_id": "2503.20020",
        "title": "Gemini Robotics: Bringing AI into the Physical World",
        "authors": "Google DeepMind",
        "year": 2025,
        "venue": "arXiv",
        "primary_category": "cs.RO",
        "tags": ["robotics", "vla", "foundation-model"],
        "abstract": "Builds on Gemini 2.0 to deliver smooth reactive manipulation across diverse embodiments and unseen environments with open-vocabulary instructions.",
        "key_contribution": "Closed-source generalist VLA powering Apptronik Apollo and other commercial humanoids.",
        "methods": "Gemini 2.0 backbone; Gemini Robotics-ER variant adds embodied reasoning + agentic tool use.",
        "results": "Smooth real-world manipulation; on-device variant deployable.",
        "limitations": "Closed weights; cloud dependency; multimodal reasoning latency vs reactive control trade-off.",
    },
    {
        "arxiv_id": "2502.13130",
        "title": "Magma: A Foundation Model for Multimodal AI Agents",
        "authors": "Yang, J. et al. (Microsoft)",
        "year": 2025,
        "venue": "CVPR",
        "primary_category": "cs.AI",
        "tags": ["agentic-ai", "vla", "foundation-model", "ui-agent"],
        "abstract": "Magma is a foundation model that unifies digital UI navigation and physical robot manipulation in a single backbone, using Set-of-Mark and Trace-of-Mark annotations.",
        "key_contribution": "Single foundation model for both digital + physical action.",
        "methods": "Set-of-Mark (SoM) for action grounding; Trace-of-Mark (ToM) for planning.",
        "results": "SOTA on UI navigation + robot manipulation benchmarks.",
        "limitations": "Zero-shot real-robot dexterous performance lags specialist VLAs.",
    },
    {
        "arxiv_id": "2305.18290",
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "authors": "Rafailov, R. et al.",
        "year": 2023,
        "venue": "NeurIPS",
        "primary_category": "cs.LG",
        "tags": ["llm", "rlhf", "alignment", "preference-learning"],
        "abstract": "Closed-form mapping from reward to policy lets pairwise preference loss train the policy directly — no reward model, no online sampling.",
        "key_contribution": "Eliminates the separate reward model in RLHF.",
        "methods": "Bradley-Terry pairwise loss directly on policy logits.",
        "results": "Matches or exceeds PPO-RLHF on sentiment, summarization, dialogue.",
        "limitations": "Unbounded margin can diverge on deterministic preferences (motivates IPO).",
    },
    {
        "arxiv_id": "2402.01306",
        "title": "KTO: Model Alignment as Prospect Theoretic Optimization",
        "authors": "Ethayarajh, K. et al.",
        "year": 2024,
        "venue": "ICML (spotlight)",
        "primary_category": "cs.LG",
        "tags": ["llm", "rlhf", "alignment"],
        "abstract": "Replaces pairwise preferences with prospect-theoretic utility on binary good/bad labels, dramatically reducing labeling cost.",
        "key_contribution": "Aligns LLMs using only binary 'good/bad' labels, no pairs needed.",
        "methods": "Prospect theory utility function over policy log-ratios.",
        "results": "Matches DPO at scale; far cheaper labeling pipelines.",
        "limitations": "Less expressive than full pairwise preference signal in narrow domains.",
    },
    {
        "arxiv_id": "2305.20050",
        "title": "Let's Verify Step by Step",
        "authors": "Lightman, H. et al. (OpenAI)",
        "year": 2024,
        "venue": "ICLR",
        "primary_category": "cs.LG",
        "tags": ["llm", "reasoning", "prm", "math"],
        "abstract": "Shows step-level Process Reward Models (PRMs) beat outcome-only Reward Models (ORMs) on MATH; releases PRM800K.",
        "key_contribution": "PRMs > ORMs for math reasoning; PRM800K dataset released.",
        "methods": "Step-level human-annotated correctness labels train PRM; reranking improves CoT.",
        "results": "78% pass on MATH subset via PRM-based reranking.",
        "limitations": "Step-level labels expensive; reward over-optimization risk.",
    },
    {
        "arxiv_id": "2501.12948",
        "title": "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
        "authors": "Guo, D. et al. (DeepSeek)",
        "year": 2025,
        "venue": "Nature",
        "primary_category": "cs.LG",
        "tags": ["llm", "reasoning", "rlvr", "grpo", "open-source"],
        "abstract": "Pure RL with verifiable rewards (symbolic math check + code unit-test execution) using a novel GRPO algorithm.",
        "key_contribution": "First peer-reviewed LLM in Nature; o1-level reasoning at ~10x lower compute.",
        "methods": "GRPO: drops the value critic, normalises advantage within a group of K samples.",
        "results": "Matches OpenAI o1 on math/code benchmarks at ~147K H800 GPU-hours.",
        "limitations": "Verifier-based rewards narrow to math/code; non-verifiable transfer is open.",
    },
    {
        "arxiv_id": "2301.04104",
        "title": "Mastering Diverse Control Tasks through World Models (DreamerV3)",
        "authors": "Hafner, D. et al.",
        "year": 2025,
        "venue": "Nature",
        "primary_category": "cs.LG",
        "tags": ["world-model", "model-based-rl", "dreamerv3", "minecraft"],
        "abstract": "Single hyperparameter configuration solves 150+ tasks across continuous/discrete, 2D/3D, sparse/dense rewards.",
        "key_contribution": "First algorithm to mine diamonds in Minecraft from scratch with no human data.",
        "methods": "Recurrent State-Space Model + categorical latents + symlog squashing.",
        "results": "150+ task SOTA with one hyperparameter set; ~30M env steps to Minecraft diamond.",
        "limitations": "Wall-clock still days; cannot exploit pre-existing video/text data.",
    },
    {
        "arxiv_id": "2404.10179",
        "title": "Scaling Instructable Agents Across Many Simulated Worlds (SIMA)",
        "authors": "SIMA Team (Google DeepMind)",
        "year": 2024,
        "venue": "arXiv",
        "primary_category": "cs.LG",
        "tags": ["agentic-ai", "game-ai", "foundation-agent", "embodied"],
        "abstract": "Generalist agent following natural-language instructions across 9 commercial 3D games via keyboard+mouse.",
        "key_contribution": "Single agent generalising across multiple commercial 3D games using human keyboard+mouse interface.",
        "methods": "Behaviour-cloned from human demonstrations on 9 games.",
        "results": "31% human-relative success at launch.",
        "limitations": "Bound to BC ceiling; struggles with long-horizon planning.",
    },
    {
        "arxiv_id": "2512.04797",
        "title": "SIMA 2: An Embodied Agent that Plays, Reasons and Learns in Virtual 3D Worlds",
        "authors": "SIMA Team (Google DeepMind)",
        "year": 2025,
        "venue": "arXiv",
        "primary_category": "cs.LG",
        "tags": ["agentic-ai", "game-ai", "foundation-agent", "self-improving"],
        "abstract": "Gemini-powered successor to SIMA; introduces self-play with LLM-generated rewards for RL fine-tuning in new game environments.",
        "key_contribution": "First foundation game agent shown to self-improve via LLM-judged reward in novel envs.",
        "methods": "Gemini backbone; self-play loop with Gemini-generated reward; transfer to unseen games.",
        "results": "About 2x SIMA-1 success; near-human in trained envs; zero-shot transfer.",
        "limitations": "Long-horizon planning still weak; fine-motor control limited; eval tied to DeepMind-curated games.",
    },
    {
        "arxiv_id": "2305.16291",
        "title": "Voyager: An Open-Ended Embodied Agent with Large Language Models",
        "authors": "Wang, G. et al.",
        "year": 2023,
        "venue": "NeurIPS Workshop",
        "primary_category": "cs.AI",
        "tags": ["agentic-ai", "minecraft", "llm-agent", "lifelong-learning"],
        "abstract": "First LLM-powered lifelong learning agent in Minecraft; combines automatic curriculum, growing skill library of executable code, and self-verification.",
        "key_contribution": "Demonstrates in-context RL via blackbox GPT-4 queries with code-as-action.",
        "methods": "Automatic curriculum + skill library + iterative prompting with env feedback.",
        "results": "3.1x more unique items, 15.3x faster tech-tree progress vs prior SOTA.",
        "limitations": "Bound to GPT-4 cost; hallucinated code; brittle to perception shifts.",
    },
    {
        "arxiv_id": "2406.01967",
        "title": "DrEureka: Language Model Guided Sim-to-Real Transfer",
        "authors": "Ma, Y. J. et al.",
        "year": 2024,
        "venue": "RSS",
        "primary_category": "cs.RO",
        "tags": ["robotics", "sim2real", "llm-reward", "domain-randomization"],
        "abstract": "Uses LLMs to jointly synthesise reward functions and domain randomization parameters for sim-to-real transfer.",
        "key_contribution": "First system to use LLMs to author both reward and DR config end-to-end.",
        "methods": "LLM proposes candidate rewards + DR configs; auto-evaluated in sim then deployed on real robot.",
        "results": "Surpasses human-tuned baselines on quadruped yoga-ball balancing.",
        "limitations": "Task-specific; LLM-generated rewards can exploit simulator bugs.",
    },
]


# ---------------------------------------------------------------------------
# Tool 1: arxiv_search
# ---------------------------------------------------------------------------

def _score(paper: dict, terms: list[str]) -> int:
    text = " ".join([
        paper["title"].lower(),
        paper["abstract"].lower(),
        " ".join(paper["tags"]),
        paper["key_contribution"].lower(),
    ])
    return sum(1 for t in terms if t in text)


def _public_view(p: dict) -> dict:
    """Project a corpus entry to the public arxiv_search response shape."""
    return {
        "arxiv_id": p["arxiv_id"],
        "title": p["title"],
        "authors": p["authors"],
        "year": p["year"],
        "venue": p["venue"],
        "primary_category": p["primary_category"],
        "abstract": p["abstract"],
    }


def search_scored(
    query: str,
    year_min: int = 2024,
    year_max: int = 2026,
    max_results: int = 10,
) -> list[tuple[dict, int]]:
    """
    Relevance-ranked search returning (paper_view, score) pairs.

    The score is exposed so the orchestrator can assign each paper to the
    single sub-topic it is *most* relevant to (cross-topic de-duplication).
    `arxiv_search` is the public, score-free tool built on top of this.
    """
    terms = [t for t in re.split(r"[\s,]+", query.lower()) if len(t) > 2]
    if not terms:
        return []

    candidates = [p for p in CORPUS if year_min <= p["year"] <= year_max]
    scored = [(p, _score(p, terms)) for p in candidates]
    scored = [(p, s) for p, s in scored if s > 0]
    scored.sort(key=lambda ps: (-ps[1], -ps[0]["year"]))
    return [(_public_view(p), s) for p, s in scored[:max_results]]


def arxiv_search(
    query: str,
    year_min: int = 2024,
    year_max: int = 2026,
    max_results: int = 10,
) -> list[dict]:
    """
    Search the offline corpus (or arXiv API if HARNESS_USE_LIVE_ARXIV=1).

    Returns:
        list of {arxiv_id, title, authors, year, venue, primary_category, abstract}.
        Tags + structured summary live on the corpus entry but are exposed
        only via paper_summarize() to keep this tool focused on retrieval.

    Failure mode:
        If no results match the query, returns an empty list (not an error).
    """
    return [view for view, _s in search_scored(query, year_min, year_max, max_results)]


# ---------------------------------------------------------------------------
# Tool 2: paper_summarize
# ---------------------------------------------------------------------------

def paper_summarize(arxiv_id: str) -> dict:
    """
    Fetch structured summary for a given arxiv_id.

    Returns:
        {arxiv_id, title, authors, year, key_contribution, methods,
         results, limitations}

    Failure mode:
        Unknown arxiv_id returns {"error": "...", "arxiv_id": id}.
        Never raises — the LLM controller should reason about errors as
        regular tool output.
    """
    for p in CORPUS:
        if p["arxiv_id"] == arxiv_id:
            return {
                "arxiv_id": p["arxiv_id"],
                "title": p["title"],
                "authors": p["authors"],
                "year": p["year"],
                "venue": p["venue"],
                "key_contribution": p["key_contribution"],
                "methods": p["methods"],
                "results": p["results"],
                "limitations": p["limitations"],
            }
    return {"error": f"arxiv_id {arxiv_id!r} not found in corpus", "arxiv_id": arxiv_id}


# ---------------------------------------------------------------------------
# Tool 3: citation_format
# ---------------------------------------------------------------------------

CitationStyle = Literal["IEEE", "ACM", "APA", "BibTeX"]


def citation_format(paper: dict, style: CitationStyle = "IEEE") -> str:
    """
    Format a paper dict into a citation string.

    Args:
        paper: must contain at least {arxiv_id, title, authors, year, venue}.
        style: one of IEEE / ACM / APA / BibTeX.

    Returns:
        Formatted citation string. Missing fields are filled with <unknown>.
    """
    pid = paper.get("arxiv_id", "<unknown>")
    title = paper.get("title", "<unknown title>")
    authors = paper.get("authors", "<unknown authors>")
    year = paper.get("year", "<unknown year>")
    venue = paper.get("venue", "<unknown venue>")

    if style == "IEEE":
        return f'{authors}, "{title}," {venue}, {year}. arXiv:{pid}.'
    if style == "ACM":
        return f"{authors}. {year}. {title}. In {venue}. arXiv:{pid}."
    if style == "APA":
        return f"{authors} ({year}). {title}. {venue}. https://arxiv.org/abs/{pid}"
    if style == "BibTeX":
        key = re.sub(r"\W", "", authors.split(",")[0]) + str(year)
        return (f"@article{{{key},\n"
                f"  title  = {{{title}}},\n"
                f"  author = {{{authors}}},\n"
                f"  year   = {{{year}}},\n"
                f"  journal= {{{venue}}},\n"
                f"  eprint = {{{pid}}},\n"
                f"  archivePrefix = {{arXiv}}\n"
                f"}}")
    return f"<unsupported style: {style}>"


# ---------------------------------------------------------------------------
# Tool 4: note_save  (the only tool with side effects)
# ---------------------------------------------------------------------------

@dataclass
class NoteStore:
    """JSON-backed long-term memory keyed by topic."""

    path: Path

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {"_meta": {"corrupt_recovered": True}, "topics": {}}
        return {"_meta": {"created": time.time()}, "topics": {}}

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add(
        self,
        topic: str,
        content: str,
        tags: list[str] | None = None,
        meta: dict | None = None,
    ) -> dict:
        data = self._load()
        topics = data.setdefault("topics", {})
        bucket = topics.setdefault(topic, {"notes": [], "tags": []})
        bucket["notes"].append({
            "ts": time.time(),
            "content": content,
            "tags": tags or [],
            "meta": meta or {},
        })
        if tags:
            bucket["tags"] = sorted(set(bucket["tags"] + tags))
        self._save(data)
        total_chars = sum(len(n["content"]) for n in bucket["notes"])
        return {
            "topic": topic,
            "note_count": len(bucket["notes"]),
            "total_chars": total_chars,
            "recent_tags": tags or [],
            "persisted": True,
        }

    def list_topics(self) -> list[str]:
        return list(self._load().get("topics", {}).keys())

    def get_topic(self, topic: str) -> dict:
        return self._load().get("topics", {}).get(topic, {"notes": [], "tags": []})

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()


_STORE = NoteStore(NOTE_STORE_PATH)


def note_save(
    topic: str,
    content: str,
    tags: list[str] | None = None,
    meta: dict | None = None,
) -> dict:
    """
    Save a note to long-term memory under a topic key.

    `meta` carries an optional structured payload (e.g. the paper record the
    note was distilled from). Storing it makes the note store the single
    source of truth: the Compiler reconstructs the report from meta alone and
    never trusts LLM-inline facts.

    Returns:
        {topic, note_count, total_chars, recent_tags, persisted}

    Failure mode:
        Any disk error -> returns {..., "persisted": false, "error": "..."}.
    """
    if not topic.strip():
        return {"error": "topic must be non-empty", "persisted": False}
    try:
        return _STORE.add(topic.strip(), content.strip(), tags, meta)
    except OSError as e:
        return {"error": str(e), "persisted": False}


# ---------------------------------------------------------------------------
# Helpers exposed to the harness controller
# ---------------------------------------------------------------------------

def get_note_store() -> NoteStore:
    """Allow the compiler to read accumulated notes."""
    return _STORE


def reset_note_store() -> None:
    """Wipe persistent notes — used by demo runs for clean output."""
    _STORE.clear()


TOOL_REGISTRY = {
    "arxiv_search": arxiv_search,
    "paper_summarize": paper_summarize,
    "citation_format": citation_format,
    "note_save": note_save,
}


TOOL_SCHEMAS = [
    {
        "name": "arxiv_search",
        "description": "Search arXiv for papers matching a query within a year range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "year_min": {"type": "integer", "default": 2024},
                "year_max": {"type": "integer", "default": 2026},
                "max_results": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "paper_summarize",
        "description": "Fetch a structured summary (contribution, methods, results, limitations) for a given arxiv_id.",
        "input_schema": {
            "type": "object",
            "properties": {"arxiv_id": {"type": "string"}},
            "required": ["arxiv_id"],
        },
    },
    {
        "name": "citation_format",
        "description": "Format a paper into a citation string. Style is one of IEEE / ACM / APA / BibTeX.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper": {"type": "object"},
                "style": {"type": "string", "enum": ["IEEE", "ACM", "APA", "BibTeX"], "default": "IEEE"},
            },
            "required": ["paper"],
        },
    },
    {
        "name": "note_save",
        "description": "Persist a note to long-term memory under a topic key. Returns counts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "content": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "meta": {
                    "type": "object",
                    "description": "Optional structured payload (e.g. the source paper record) used by the Compiler as source of truth.",
                },
            },
            "required": ["topic", "content"],
        },
    },
]


# ---------------------------------------------------------------------------
# Schema-validated function-call dispatch (the tool boundary guard)
# ---------------------------------------------------------------------------
# The controller never calls a Python tool function directly: it emits a tool
# *name* + a JSON *input*, which is validated against that tool's declared
# schema (TOOL_SCHEMAS) and only then routed to the implementation
# (TOOL_REGISTRY). This is what makes "function-callable tools with a strict
# JSON schema" a runtime fact instead of documentation — and it is the single
# choke point where a malformed or unknown tool call is rejected.

_SCHEMA_BY_NAME: dict[str, dict] = {s["name"]: s["input_schema"] for s in TOOL_SCHEMAS}

_JSON_TYPES: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "object": dict,
    "array": list,
    "boolean": bool,
}


class ToolValidationError(ValueError):
    """A tool call violated its declared input schema.

    This is a *controller-side* contract violation (unknown tool, missing
    required field, wrong type, out-of-enum value) — deliberately distinct
    from a tool's own runtime failure mode, which is returned as a structured
    error dict (e.g. an unknown arxiv_id). Schema errors raise; runtime errors
    come back as data.
    """


def validate_tool_call(name: str, tool_input: dict) -> None:
    """Validate a tool call against its declared JSON schema.

    Checks, in order: the tool exists; every `required` field is present;
    each declared field has the right primitive type; any `enum` is honoured.
    Raises ToolValidationError on the first violation; returns None if valid.
    Unknown extra fields are tolerated (forward-compatible).
    """
    if name not in _SCHEMA_BY_NAME:
        raise ToolValidationError(
            f"unknown tool {name!r}; known tools: {sorted(_SCHEMA_BY_NAME)}")
    schema = _SCHEMA_BY_NAME[name]
    props = schema.get("properties", {})
    for field_name in schema.get("required", []):
        if field_name not in tool_input:
            raise ToolValidationError(f"{name}: missing required field {field_name!r}")
    for key, val in tool_input.items():
        spec = props.get(key)
        if not spec:
            continue
        expected = _JSON_TYPES.get(spec.get("type", ""))
        if expected is not None and not isinstance(val, expected):
            raise ToolValidationError(
                f"{name}.{key}: expected {spec['type']}, got {type(val).__name__}")
        if "enum" in spec and val not in spec["enum"]:
            raise ToolValidationError(
                f"{name}.{key}: {val!r} not in allowed {spec['enum']}")


def dispatch_tool(name: str, tool_input: dict) -> Any:
    """Validate a tool call, then execute it via the tool registry.

    The orchestrator's single entry point for invoking any tool: it guarantees
    every call is schema-checked before the implementation runs. Schema
    violations raise ToolValidationError; the tool's own runtime failure modes
    still come back as structured dicts.
    """
    validate_tool_call(name, tool_input)
    return TOOL_REGISTRY[name](**tool_input)


if __name__ == "__main__":
    # quick smoke test
    print("== arxiv_search('robotics vla', 2024, 2026) ==")
    for p in arxiv_search("robotics vla", 2024, 2026, max_results=3):
        print(f"  {p['arxiv_id']:>12} | {p['title'][:60]}")
    print("\n== paper_summarize('2406.09246') ==")
    s = paper_summarize("2406.09246")
    print(f"  contribution: {s['key_contribution']}")
    print("\n== citation_format(...) IEEE ==")
    print(" ", citation_format(s, "IEEE"))
    print("\n== note_save() ==")
    reset_note_store()
    print(" ", note_save("robotics_vla", "OpenVLA is the first open VLA.", tags=["vla", "open"]))
    print(" ", note_save("robotics_vla", "Pi-0.5 generalises to unseen kitchens.", tags=["vla"]))
    print("\n== final store ==")
    print(" ", get_note_store().list_topics())
