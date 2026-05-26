"""
HW4 Bonus MVP (C): A minimal tool-using LLM agent in the ReAct style.

Demonstrates the agent loop discussed in Part 3 (Agentic AI):
    Thought -> Action -> Observation -> Thought -> ... -> Final Answer

Two tools are exposed:
  1. calculator(expression)  — safe arithmetic eval
  2. wiki_search(query)      — local mini-corpus lookup (no network needed)

LLM backend:
  - If ANTHROPIC_API_KEY env var is set, calls Claude (claude-haiku-4-5-20251001).
  - Otherwise falls back to a deterministic offline planner so the demo
    always runs and produces a transcript, even without API access.

Run:
    python code/llm_agent_demo.py
    python code/llm_agent_demo.py "What is sqrt(144) plus AlphaGo's debut year?"

Output:
    artifacts/agent_transcript.txt   — full ReAct trace
"""

from __future__ import annotations

import ast
import json
import math
import operator
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


ARTIFACT_DIR = Path(__file__).resolve().parent.parent / "artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


# ---------- 1. Tools -------------------------------------------------------

_ALLOWED_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_ALLOWED_FUNCS = {
    "sqrt": math.sqrt, "log": math.log, "log2": math.log2, "log10": math.log10,
    "exp": math.exp, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "abs": abs, "round": round, "min": min, "max": max,
}


def _safe_eval(node: ast.AST) -> Any:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCS:
        args = [_safe_eval(a) for a in node.args]
        return _ALLOWED_FUNCS[node.func.id](*args)
    raise ValueError(f"unsupported node: {ast.dump(node)}")


def tool_calculator(expression: str) -> str:
    """Safe arithmetic evaluator. Returns the numeric result as a string."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree)
        return f"{result}"
    except Exception as e:
        return f"ERROR: {e}"


_WIKI_CORPUS = {
    "alphago": "AlphaGo is a computer Go program developed by DeepMind. Its match versus Lee Sedol took place in March 2016. AlphaGo Zero was published in October 2017.",
    "muzero": "MuZero, published in Nature in December 2020, is a model-based reinforcement learning algorithm by DeepMind that learns a latent dynamics model and uses Monte Carlo Tree Search.",
    "ppo": "Proximal Policy Optimization (PPO) was introduced by John Schulman and colleagues at OpenAI in 2017. It became the de facto standard on-policy DRL algorithm and the backbone of RLHF training pipelines.",
    "sac": "Soft Actor-Critic (SAC) was introduced by Haarnoja et al. at ICML 2018. It is an off-policy maximum-entropy actor-critic for continuous control.",
    "deepseek-r1": "DeepSeek-R1, published in Nature in 2025, is an open-weights reasoning model trained with pure reinforcement learning from verifiable rewards using a method called GRPO. It is the first peer-reviewed LLM paper published in Nature.",
    "dreamerv3": "DreamerV3 is a world-model-based reinforcement learning agent by Hafner et al., published in Nature 2025. It is the first algorithm to collect diamonds in Minecraft from scratch without human data and uses a single hyperparameter configuration across 150+ tasks.",
    "openvla": "OpenVLA is an open-source 7-billion-parameter vision-language-action model released by Stanford and collaborators in 2024, trained on the Open X-Embodiment dataset.",
    "alphafold": "AlphaFold 2 was published in Nature in 2021 and AlphaFold 3 in May 2024. AlphaFold 3 generalises to nucleic acids, ligands, and ions using a diffusion architecture.",
    "alphaproof": "AlphaProof, together with AlphaGeometry 2, reached silver-medal level (28/42) at the International Mathematical Olympiad 2024. The full method was published in Nature in November 2025.",
}


def tool_wiki_search(query: str) -> str:
    """Search a small in-memory corpus of DRL/AI facts. Returns up to 2 matches."""
    q = query.lower().strip()
    hits = []
    for key, text in _WIKI_CORPUS.items():
        if key in q or any(word in text.lower() for word in q.split() if len(word) > 3):
            hits.append(f"[{key}] {text}")
    if not hits:
        return f"NO_RESULTS for query: {query!r}"
    return "\n".join(hits[:2])


TOOLS: dict[str, Callable[[str], str]] = {
    "calculator": tool_calculator,
    "wiki_search": tool_wiki_search,
}

TOOL_DOCS = """Available tools:
  calculator(expression)  — evaluate an arithmetic expression, e.g. "sqrt(144) + 2"
  wiki_search(query)      — look up a fact from the local DRL/AI mini-wiki, e.g. "AlphaGo"
"""


# ---------- 2. LLM backends -----------------------------------------------

SYSTEM_PROMPT = f"""You are a tool-using ReAct agent.

{TOOL_DOCS}

For each step, respond with EXACTLY ONE of the following on a single line:
  Thought: <free-form reasoning>
  Action: <tool_name>(<single string argument>)
  FinalAnswer: <the user-visible answer>

Rules:
  - After Action you will receive an Observation. Then you must continue.
  - When you have enough information, emit FinalAnswer and stop.
  - Never emit two actions in one response. Never invent tools.
"""


def llm_anthropic(messages: list[dict]) -> str:
    import anthropic
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return resp.content[0].text.strip()


def llm_offline(messages: list[dict]) -> str:
    """Deterministic offline planner — drives the loop without an API key.

    Walks through a hard-coded plan keyed on what's already been observed in
    the conversation so the demo always finishes successfully.
    """
    user_q = ""
    observations: list[str] = []
    actions_taken: list[str] = []
    for m in messages:
        if m["role"] == "user":
            text = m["content"]
            if user_q == "":
                user_q = text
            elif text.startswith("Observation:"):
                observations.append(text[len("Observation:"):].strip())
        elif m["role"] == "assistant":
            a = ACTION_RE.search(text := m["content"])
            if a:
                actions_taken.append(f"{a.group(1)}({a.group(2).strip()})")

    obs_blob = "\n".join(observations)
    obs_lower = obs_blob.lower()
    q_lower = user_q.lower()

    has_wiki_alphago = any(a.startswith("wiki_search") and "alphago" in a.lower() for a in actions_taken)
    has_calc_2016 = any(a.startswith("calculator") and "2016" in a for a in actions_taken)

    if "alphago" in q_lower and ("year" in q_lower or "debut" in q_lower or "sedol" in q_lower):
        if not has_wiki_alphago:
            return "Thought: I need AlphaGo's debut year. I'll check the wiki.\nAction: wiki_search(AlphaGo)"
        if "144" in q_lower and not has_calc_2016:
            return ("Thought: Good — AlphaGo's Lee-Sedol match was in 2016. "
                    "Now compute sqrt(144) + 2016.\nAction: calculator(sqrt(144) + 2016)")
        nums = re.findall(r"\b(\d{2,5}(?:\.\d+)?)\b", obs_blob)
        result = nums[-1] if nums else "2028"
        return (f"FinalAnswer: sqrt(144) = 12 and AlphaGo's Lee-Sedol match was in 2016, "
                f"so the answer is {result}.")

    has_wiki_deepseek = any(a.startswith("wiki_search") and "deepseek" in a.lower() for a in actions_taken)
    if "deepseek" in q_lower:
        if not has_wiki_deepseek:
            return "Thought: Let me look up DeepSeek-R1.\nAction: wiki_search(DeepSeek-R1)"
        return ("FinalAnswer: DeepSeek-R1 is an open-weights reasoning model trained with pure RL "
                "from verifiable rewards using GRPO. It is the first peer-reviewed LLM in Nature (2025).")

    has_wiki_muzero = any(a.startswith("wiki_search") and "muzero" in a.lower() for a in actions_taken)
    if "muzero" in q_lower:
        if not has_wiki_muzero:
            return "Thought: I'll look up MuZero.\nAction: wiki_search(MuZero)"
        return ("FinalAnswer: MuZero (DeepMind, Nature 2020) is a model-based RL algorithm that learns a "
                "latent dynamics model and plans with MCTS — handling Atari and board games with one architecture.")

    is_arithmetic = any(op in user_q for op in "+-*/") or "sqrt" in user_q.lower()
    if is_arithmetic:
        has_calc = any(a.startswith("calculator") for a in actions_taken)
        if has_calc and observations:
            return f"FinalAnswer: {observations[-1].strip()}"
        m = re.search(r"(?:compute|calculate|what is)\s*(.+?)(?:\?|$)", user_q.lower())
        expr = (m.group(1) if m else user_q).strip()
        return f"Thought: Pure arithmetic — use calculator.\nAction: calculator({expr})"

    return ("FinalAnswer: I do not have enough information offline. "
            "Try again with ANTHROPIC_API_KEY set to use the real Claude backend.")


def choose_backend():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic", llm_anthropic
    return "offline", llm_offline


# ---------- 3. The ReAct loop ----------------------------------------------

ACTION_RE = re.compile(r"^Action:\s*([A-Za-z_]+)\((.*)\)\s*$", re.MULTILINE)
FINAL_RE = re.compile(r"^FinalAnswer:\s*(.+)$", re.MULTILINE | re.DOTALL)


@dataclass
class TraceStep:
    role: str
    content: str


@dataclass
class AgentRun:
    question: str
    steps: list[TraceStep] = field(default_factory=list)
    final_answer: str = ""
    tool_calls: int = 0
    elapsed_sec: float = 0.0
    backend: str = ""


def run_agent(question: str, max_steps: int = 8) -> AgentRun:
    backend_name, llm = choose_backend()
    run = AgentRun(question=question, backend=backend_name)
    messages = [{"role": "user", "content": question}]
    run.steps.append(TraceStep("user", question))

    t0 = time.time()
    for step_i in range(max_steps):
        reply = llm(messages)
        run.steps.append(TraceStep("assistant", reply))
        messages.append({"role": "assistant", "content": reply})

        final = FINAL_RE.search(reply)
        if final:
            run.final_answer = final.group(1).strip()
            break

        action = ACTION_RE.search(reply)
        if action:
            name = action.group(1)
            arg = action.group(2).strip().strip('"').strip("'")
            tool = TOOLS.get(name)
            if tool is None:
                obs = f"ERROR: unknown tool {name!r}"
            else:
                obs = tool(arg)
                run.tool_calls += 1
            run.steps.append(TraceStep("tool", f"{name}({arg!r}) -> {obs}"))
            messages.append({"role": "user", "content": f"Observation: {obs}"})
            continue

        run.steps.append(TraceStep("system", "No actionable directive parsed — stopping."))
        run.final_answer = reply
        break

    run.elapsed_sec = time.time() - t0
    return run


# ---------- 4. CLI ---------------------------------------------------------

DEFAULT_QUESTIONS = [
    "What is sqrt(144) plus the year AlphaGo played Lee Sedol?",
    "Tell me about DeepSeek-R1.",
    "Compute 2 ** 10 - 24",
]


def render(run: AgentRun) -> str:
    out = [f"Q: {run.question}", f"backend: {run.backend}", f"tool_calls: {run.tool_calls}",
           f"elapsed: {run.elapsed_sec:.2f}s", ""]
    for st in run.steps:
        prefix = {"user": "USER", "assistant": "AGENT", "tool": "TOOL", "system": "SYS"}[st.role]
        out.append(f"[{prefix}] {st.content}")
    out.append("")
    out.append(f"FINAL: {run.final_answer}")
    return "\n".join(out)


def main():
    questions = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_QUESTIONS
    transcripts: list[str] = []
    for q in questions:
        print(f"\n--- Question: {q}")
        run = run_agent(q)
        block = render(run)
        print(block)
        transcripts.append(block)

    out_path = ARTIFACT_DIR / "agent_transcript.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n" + ("=" * 72) + "\n\n".join(transcripts))
    print(f"\n[llm_agent_demo] Transcript saved -> {out_path}")


if __name__ == "__main__":
    main()
