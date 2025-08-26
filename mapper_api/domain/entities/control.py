"""Domain entity for Control. Framework-free. Holds textual description and optional external id.

Implements: Control(text: str, id: Optional[str])
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class Control:
    """Represents a control record to be mapped.

    Attributes:
        text: The control description text to analyze.
        id: Optional external identifier.
    """
    text: str
    id: Optional[str] = None

    def ensure_not_empty(self) -> None:
        if not self.text or not self.text.strip():
            raise ValueError("control description must not be empty")
