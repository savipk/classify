"""Prompt builders for 5Ws extraction. System + user with definitions."""
from __future__ import annotations
from typing import Sequence, Mapping

SYSTEM = (
    "Extract presence of who, what, when, where, why. Output ONLY valid JSON matching the provided JSON Schema. "
    "Use ONLY the provided definitions. Names must be exactly one of who, what, when, where, why."
)


def build_user_prompt(control_text: str, fivews_defs: Sequence[Mapping[str, str]]) -> str:
    lines = ["Definitions:"]
    for row in fivews_defs:
        lines.append(f"- {row['name']}: {row['description']}")
    lines.append("")
    lines.append("Control description:")
    lines.append(control_text)
    lines.append("")
    lines.append("Return JSON with exactly 5 items covering who, what, when, where, why.")
    return "\n".join(lines)
