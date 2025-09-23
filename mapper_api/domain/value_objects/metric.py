"""Value objects for evaluation metrics."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any


class MetricType(Enum):
    """Supported evaluation metric types."""
    RECALL_K3_RISK_THEME = "recall_k3_risktheme"
    RECALL_K5_5WS = "recall_k5_5ws"


@dataclass(frozen=True, slots=True)
class RecallScore:
    """Value object for recall score with validation."""
    value: float
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Recall score must be between 0.0 and 1.0, got {self.value}")


@dataclass(frozen=True, slots=True)
class IndividualRecall:
    """Recall score for a single control/record."""
    control_id: str
    recall: RecallScore
    details: Dict[str, Any]  # Additional details specific to the metric


@dataclass(frozen=True, slots=True)
class SummaryRecall:
    """Summary recall across all evaluated records."""
    total_records: int
    average_recall: RecallScore
    min_recall: RecallScore
    max_recall: RecallScore
