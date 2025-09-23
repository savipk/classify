"""Repository protocol for loading ground truth data."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence, Dict, Any, List


@dataclass(frozen=True, slots=True)
class FiveWGroundTruth:
    """Ground truth for a single 5W element."""
    name: str
    status: str  # "present" or "missing"
    reasoning: str


@dataclass(frozen=True, slots=True)
class FiveWGroundTruthRecord:
    """Ground truth record for 5Ws evaluation."""
    control_id: str
    control_description: str
    gt_5ws: List[FiveWGroundTruth]


@dataclass(frozen=True, slots=True)
class RiskThemeGroundTruth:
    """Ground truth for a single risk theme."""
    name: str
    id: int
    reasoning: str


@dataclass(frozen=True, slots=True)
class RiskThemeGroundTruthRecord:
    """Ground truth record for risk theme evaluation."""
    control_id: str
    control_description: str
    risk_theme: List[RiskThemeGroundTruth]


class GroundTruthRepository(Protocol):
    """Repository for accessing ground truth data from storage."""
    
    def get_fivews_ground_truth(self) -> Sequence[FiveWGroundTruthRecord]:
        """Return sequence of 5Ws ground truth records from storage."""
        ...

    def get_risk_themes_ground_truth(self) -> Sequence[RiskThemeGroundTruthRecord]:
        """Return sequence of risk theme ground truth records from storage."""
        ...
