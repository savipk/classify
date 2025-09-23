"""Response DTOs for evaluation operations."""
from __future__ import annotations
from typing import List, Dict, Any
from pydantic import BaseModel, Field, confloat
from mapper_api.application.dto.http_responses import ResponseHeader


class IndividualRecallData(BaseModel):
    """Individual recall result for a single control."""
    controlId: str = Field(..., description="Control ID")
    recall: confloat(ge=0.0, le=1.0) = Field(..., description="Recall score")  # type: ignore[valid-type]
    details: Dict[str, Any] = Field(..., description="Additional details")


class SummaryRecallData(BaseModel):
    """Summary recall statistics."""
    totalRecords: int = Field(..., description="Total number of records evaluated")
    averageRecall: confloat(ge=0.0, le=1.0) = Field(..., description="Average recall score")  # type: ignore[valid-type]
    minRecall: confloat(ge=0.0, le=1.0) = Field(..., description="Minimum recall score")  # type: ignore[valid-type]
    maxRecall: confloat(ge=0.0, le=1.0) = Field(..., description="Maximum recall score")  # type: ignore[valid-type]


class EvaluationData(BaseModel):
    """Evaluation response data."""
    metricType: str = Field(..., description="Type of metric evaluated")
    individualRecalls: List[IndividualRecallData] = Field(..., description="Individual recall scores")
    summaryRecall: SummaryRecallData = Field(..., description="Summary recall statistics")


class EvaluationResponse(BaseModel):
    """Complete evaluation response."""
    header: ResponseHeader
    data: EvaluationData
