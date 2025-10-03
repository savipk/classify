"""Value objects for evaluation results."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Union, Dict, Any
from mapper_api.domain.value_objects.metric import (
    MetricType, 
    IndividualRecall, 
    SummaryRecall,
    IndividualAccuracy,
    SummaryAccuracy,
    IndividualLLMJudge,
    SummaryLLMJudge,
    IndividualUnmatchedAnalysis,
    IndividualLatency,
    SummaryLatency
)


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Complete evaluation result for a specific metric type."""
    metric_type: MetricType
    individual_results: List[Union[
        IndividualRecall, 
        IndividualAccuracy, 
        IndividualLLMJudge, 
        IndividualUnmatchedAnalysis, 
        IndividualLatency
    ]]
    summary_result: Union[
        SummaryRecall, 
        SummaryAccuracy, 
        SummaryLLMJudge, 
        SummaryLatency,
        None  # For unmatched analysis which doesn't have summary
    ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "metric_type": self.metric_type.value,
            "individual_results": [individual.to_dict() for individual in self.individual_results],
            "summary_result": self.summary_result.to_dict() if self.summary_result else None
        }
        return result
