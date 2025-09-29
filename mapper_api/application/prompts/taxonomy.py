"""Prompt builders for taxonomy mapping. System + user with full catalog."""
from __future__ import annotations
from typing import List
from mapper_api.domain.entities.risk_theme import RiskTheme


SYSTEM = (
    "You are a careful classifier. Output ONLY valid JSON matching the provided JSON Schema. "
    "Use ONLY the provided Risk Theme catalog. Match names exactly."
)


def build_user_prompt(control_text: str, risk_themes: List[RiskTheme]) -> str:
    lines = ["Catalog of Risk Themes:"]
    for theme in risk_themes:
        lines.append(
            f"- risk_theme: {theme.name} (id={theme.id}) | taxonomy: {theme.taxonomy} (id={theme.taxonomy_id}) | taxonomy_description: {theme.taxonomy_description} | mapping_considerations: {theme.mapping_considerations}"
        )
    lines.append("")
    lines.append("Control description:")
    lines.append(control_text)
    lines.append("")
    lines.append("Return JSON with exactly 3 items in taxonomy.")
    return "\n".join(lines)


class TaxonomyPrompt:
    def __init__(self, risk_themes: List[RiskTheme]) -> None:
        self._risk_themes = list(risk_themes)

    def build(self, *, record_id: str, control_description: str) -> tuple[str, str]:
        # the system is static for now; could be extended to embed trace
        system = SYSTEM
        user = build_user_prompt(control_description, self._risk_themes)
        return system, user
