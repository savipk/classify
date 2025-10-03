"""Request DTOs for evaluation operations using Pydantic V2."""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from mapper_api.domain.value_objects.metric import MetricType


class EvaluationRequest(BaseModel):
    """Use case request for evaluation operations."""
    model_config = {"frozen": True}
    
    record_id: str = Field(..., description="Record ID for evaluation")
    metric_types: List[MetricType] = Field(..., description="List of metrics to evaluate")
    n_records: Optional[int] = Field(None, description="Number of records to test for latency metrics")
