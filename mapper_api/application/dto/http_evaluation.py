"""HTTP DTOs for evaluation requests and responses."""
from __future__ import annotations
from typing import Union, List
from pydantic import BaseModel, Field, field_validator
from mapper_api.application.dto.http_common import CommonHeader, ResponseHeader


# ============================================================================
# Evaluation Request DTOs
# ============================================================================

class EvaluationRequestData(BaseModel):
    """Data payload for evaluation request."""
    metricType: Union[str, List[str]] = Field(..., description="Metric type(s) to evaluate. Can be a single string, list of strings, or 'all' for all metrics")
    nRecords: int = Field(None, description="Number of records to test for latency metrics (optional)")
    
    @field_validator('metricType')
    @classmethod
    def validate_metric_type(cls, v):
        if isinstance(v, str):
            return v
        elif isinstance(v, list):
            if not v:
                raise ValueError("metricType list cannot be empty")
            return v
        else:
            raise ValueError("metricType must be a string or list of strings")


class EvaluationHttpRequest(BaseModel):
    """Complete HTTP request for evaluation endpoint."""
    header: CommonHeader
    data: EvaluationRequestData


# ============================================================================
# Evaluation Response DTOs
# ============================================================================

class MetricResult(BaseModel):
    """Result for a single metric evaluation."""
    metric_type: str = Field(..., description="Type of metric evaluated")
    file_path: str = Field(..., description="Path to the metric result file in blob storage")
    total_records: int = Field(..., description="Total number of records evaluated")
    status: str = Field(..., description="Status: 'success' or 'error'")
    error_message: str = Field(None, description="Error message if status is 'error'")


class EvaluationResponse(BaseModel):
    """Complete evaluation response."""
    header: ResponseHeader
    results: List[MetricResult] = Field(..., description="Results for each evaluated metric")
    directory_path: str = Field(..., description="Directory path containing all result files")
    message: str = Field(..., description="Overall success or error message")
