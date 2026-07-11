"""Formatting helpers for the Prompt Preview node."""
from __future__ import annotations


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _section(title: str, value: str, empty_text: str) -> list[str]:
    return [title, "─" * 42, value or empty_text]


def format_prompt_preview(positive: str, negative: str = "", debug: str = "") -> str:
    """Build a readable, model-independent prompt preview."""
    positive = _clean(positive)
    negative = _clean(negative)
    debug = _clean(debug)

    lines = ["PROMPT PREVIEW", "═" * 42, ""]
    lines.extend(_section("POSITIVE", positive, "(empty)"))
    lines.extend(["", ""])
    lines.extend(_section("NEGATIVE", negative, "(not connected or empty)"))
    lines.extend(["", ""])
    lines.extend(_section("DEBUG / METADATA", debug, "(not connected or empty)"))
    lines.extend(
        [
            "",
            "",
            "STATISTICS",
            "─" * 42,
            f"Positive: {len(positive)} characters / {len(positive.split())} words",
            f"Negative: {len(negative)} characters / {len(negative.split())} words",
        ]
    )
    return "\n".join(lines)
