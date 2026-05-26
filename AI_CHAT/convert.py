"""Convert Claude Code session jsonl -> readable markdown.

Extracts user / assistant turns and drops harness queue/operation events.
Tool calls and tool results are summarized so the transcript stays readable.
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path


def text_from_content(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    out = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type")
        if btype == "text":
            out.append(block.get("text", ""))
        elif btype == "thinking":
            think = block.get("thinking", "")
            if think.strip():
                out.append(f"<details><summary>thinking</summary>\n\n{think}\n\n</details>")
        elif btype == "tool_use":
            name = block.get("name", "?")
            inp = block.get("input", {})
            # keep short summary, not the full payload
            preview = json.dumps(inp, ensure_ascii=False)
            if len(preview) > 400:
                preview = preview[:400] + "…"
            out.append(f"`[tool_use {name}]` {preview}")
        elif btype == "tool_result":
            content_val = block.get("content", "")
            txt = text_from_content(content_val) if isinstance(content_val, list) else str(content_val)
            txt = txt.strip()
            if len(txt) > 800:
                txt = txt[:800] + "\n…(truncated)"
            out.append(f"<details><summary>tool_result</summary>\n\n```\n{txt}\n```\n\n</details>")
    return "\n\n".join(s for s in out if s)


SYSTEM_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)
COMMAND_BLOCK_RE = re.compile(r"<(command-name|command-message|command-args|local-command-stdout)>.*?</\1>", re.DOTALL)


def clean_user(text: str) -> str:
    text = SYSTEM_REMINDER_RE.sub("", text)
    text = COMMAND_BLOCK_RE.sub("", text)
    return text.strip()


def convert(jsonl_path: Path, out_path: Path) -> None:
    lines_out: list[str] = [f"# Session transcript — {jsonl_path.name}\n"]
    with jsonl_path.open("r", encoding="utf-8") as f:
        for raw in f:
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                continue
            etype = ev.get("type")
            if etype == "user":
                msg = ev.get("message", {})
                content = msg.get("content")
                txt = clean_user(text_from_content(content))
                if txt:
                    lines_out.append(f"\n## 🧑 User — {ev.get('timestamp','')}\n\n{txt}\n")
            elif etype == "assistant":
                msg = ev.get("message", {})
                content = msg.get("content")
                txt = text_from_content(content).strip()
                if txt:
                    lines_out.append(f"\n## 🤖 Assistant — {ev.get('timestamp','')}\n\n{txt}\n")
            # ignore queue-operation, summary, etc.
    out_path.write_text("\n".join(lines_out), encoding="utf-8")
    print(f"  wrote {out_path}  ({out_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    src_dir = Path(r"C:\Users\Mao\.claude\projects\C--Users-Mao-Desktop-DRL-HW4")
    dst_dir = Path(r"C:\Users\Mao\Desktop\DRL\HW4\AI_CHAT")
    mapping = {
        "ae59040c-acbf-4f65-8b26-89373650517c.jsonl": "session_01_drl_survey_main.md",
        "cec245ee-7661-4c3f-8bfe-d411900c12ca.jsonl": "session_02_delivery_verification.md",
    }
    for src_name, dst_name in mapping.items():
        src = src_dir / src_name
        if not src.exists():
            print(f"  skip (missing): {src_name}")
            continue
        convert(src, dst_dir / dst_name)
    print("done.")
