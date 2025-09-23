"""Response DTOs for evaluation operations."""
from __future__ import annotations
from typing import List, Dict, Any, Annotated
from pydantic import BaseModel, Field
from mapper_api.application.dto.http_responses import ResponseHeader


class IndividualRecallData(BaseModel):
    """Individual recall result for a single control."""
    controlId: str = Field(..., description="Control ID")
    recall: Annotated[float, Field(ge=0.0, le=1.0, description="Recall score")]
    details: Dict[str, Any] = Field(..., description="Additional details")


class SummaryRecallData(BaseModel):
    """Summary recall statistics."""
    totalRecords: int = Field(..., description="Total number of records evaluated")
    averageRecall: Annotated[float, Field(ge=0.0, le=1.0, description="Average recall score")]
    minRecall: Annotated[float, Field(ge=0.0, le=1.0, description="Minimum recall score")]
    maxRecall: Annotated[float, Field(ge=0.0, le=1.0, description="Maximum recall score")]


class EvaluationData(BaseModel):
    """Evaluation response data."""
    metricType: str = Field(..., description="Type of metric evaluated")
    individualRecalls: List[IndividualRecallData] = Field(..., description="Individual recall scores")
    summaryRecall: SummaryRecallData = Field(..., description="Summary recall statistics")


class EvaluationResponse(BaseModel):
    """Complete evaluation response."""
    header: ResponseHeader
    data: EvaluationData
