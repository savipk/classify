"""Domain value objects for 5Ws: names enum and finding set with invariants.

- FiveWName Enum
- FiveWFinding(name, status, reasoning)
- FiveWsSet(items: tuple[FiveWFinding, ...]) enforces exactly five unique names in order [who, what, when, where, why]
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple


class FiveWName(str, Enum):
    WHO = "who"
    WHAT = "what"
    WHEN = "when"
    WHERE = "where"
    WHY = "why"


class FiveWStatus(str, Enum):
    PRESENT = "present"
    MISSING = "missing"


@dataclass(frozen=True, slots=True)
class FiveWFinding:
    name: FiveWName
    status: FiveWStatus
    reasoning: str


@dataclass(frozen=True, slots=True)
class FiveWsSet:
    items: Tuple[FiveWFinding, ...]

    ORDER = (FiveWName.WHO, FiveWName.WHAT, FiveWName.WHEN, FiveWName.WHERE, FiveWName.WHY)

    def __post_init__(self) -> None:
        names = [f.name for f in self.items]
        if len(self.items) != 5:
            raise ValueError("FiveWsSet must contain exactly five findings")
        if names != list(self.ORDER):
            raise ValueError("FiveWsSet items must be in order [who, what, when, where, why]")
        if len(set(names)) != 5:
            raise ValueError("FiveWsSet names must be unique")
