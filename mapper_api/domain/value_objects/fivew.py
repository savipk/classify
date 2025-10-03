"""Domain value objects for 5Ws: simplified enums only.

Note: FiveWFinding and FiveWsSet were removed as they were unused in production code.
Use simple dictionaries for 5Ws data handling instead.
"""
from enum import Enum


class FiveWName(str, Enum):
    """5W category names."""
    WHO = "who"
    WHAT = "what"
    WHEN = "when"
    WHERE = "where"
    WHY = "why"


class FiveWStatus(str, Enum):
    """5W presence status."""
    PRESENT = "present"
    MISSING = "missing"
