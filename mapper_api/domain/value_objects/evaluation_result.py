"""Value objects for evaluation results using Pydantic V2."""
from __future__ import annotations
from typing import List, Union, Dict, Any, Optional
from pydantic import BaseModel, Field
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


class EvaluationResult(BaseModel):
    """Complete evaluation result for a specific metric type."""
    model_config = {"frozen": True}
    
    metric_type: MetricType = Field(..., description="Type of metric evaluated")
    individual_results: List[Union[
        IndividualRecall, 
        IndividualAccuracy, 
        IndividualLLMJudge, 
        IndividualUnmatchedAnalysis, 
        IndividualLatency
    ]] = Field(default_factory=list, description="Individual evaluation results")
    summary_result: Optional[Union[
        SummaryRecall, 
        SummaryAccuracy, 
        SummaryLLMJudge, 
        SummaryLatency
    ]] = Field(None, description="Summary result (None for unmatched analysis)")
    error_message: Optional[str] = Field(None, description="Error message if evaluation failed")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "metric_type": self.metric_type.value,
            "individual_results": [individual.to_dict() for individual in self.individual_results],
            "summary_result": self.summary_result.to_dict() if self.summary_result else None
        }
        if self.error_message:
            result["error_message"] = self.error_message
        return result
