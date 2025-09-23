"""Domain entities for evaluation results."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List
from mapper_api.domain.value_objects.metric import (
    MetricType, 
    IndividualRecall, 
    SummaryRecall
)


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Complete evaluation result for a specific metric type."""
    metric_type: MetricType
    individual_recalls: List[IndividualRecall]
    summary_recall: SummaryRecall
    
    def __post_init__(self) -> None:
        """Validate that summary matches individual results."""
        if len(self.individual_recalls) != self.summary_recall.total_records:
            raise ValueError(
                f"Summary total_records ({self.summary_recall.total_records}) "
                f"doesn't match individual recalls count ({len(self.individual_recalls)})"
            )
