"""Repository protocol for loading taxonomy and 5Ws definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence, Dict, Any


@dataclass(frozen=True, slots=True)
class ThemeRow:
    cluster_id: int
    cluster: str
    taxonomy_id: int
    taxonomy: str
    taxonomy_description: str
    risk_theme_id: int
    risk_theme: str
    risk_theme_description: str
    mapping_considerations: str


class DefinitionsRepository(Protocol):
    def get_theme_rows(self) -> Sequence[ThemeRow]:
        """Return sequence of taxonomy theme rows."""
        ...

    def get_fivews_rows(self) -> Sequence[Dict[str, Any]]:
        """Return sequence of dict rows for 5Ws definitions with keys: name, description."""
        ...
