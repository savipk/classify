"""Prompt builders for taxonomy mapping. System + user with full catalog."""
from __future__ import annotations
from typing import Sequence
from mapper_api.domain.repositories.definitions import ThemeRow


SYSTEM = (
    "You are a careful classifier. Output ONLY valid JSON matching the provided JSON Schema. "
    "Use ONLY the provided Risk Theme catalog. Match names exactly."
)


def build_user_prompt(control_text: str, rows: Sequence[ThemeRow]) -> str:
    lines = ["Catalog of Risk Themes:"]
    for r in rows:
        lines.append(
            f"- risk_theme: {r.risk_theme} (id={r.risk_theme_id}) | taxonomy: {r.taxonomy} (id={r.taxonomy_id}) | taxonomy_description: {r.taxonomy_description} | mapping_considerations: {r.mapping_considerations}"
        )
    lines.append("")
    lines.append("Control description:")
    lines.append(control_text)
    lines.append("")
    lines.append("Return JSON with exactly 3 items in taxonomy.")
    return "\n".join(lines)


class TaxonomyPrompt:
    def __init__(self, rows: Sequence[ThemeRow]) -> None:
        self._rows = list(rows)

    def build(self, *, record_id: str, control_description: str) -> tuple[str, str]:
        # the system is static for now; could be extended to embed trace
        system = SYSTEM
        user = build_user_prompt(control_description, self._rows)
        return system, user
