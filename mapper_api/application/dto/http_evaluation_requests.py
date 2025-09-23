"""HTTP request DTOs for evaluation endpoint."""
from __future__ import annotations
from pydantic import BaseModel, Field
from mapper_api.application.dto.http_requests import CommonHeader


class EvaluationRequestData(BaseModel):
    """Data payload for evaluation request."""
    metricType: str = Field(..., description="Type of metric to evaluate (e.g., 'recall_k3_risktheme', 'recall_k5_5ws')")


class EvaluationHttpRequest(BaseModel):
    """Complete HTTP request for evaluation endpoint."""
    header: CommonHeader
    data: EvaluationRequestData
