"""Use case request DTOs for clear contracts between layers using Pydantic V2."""
from __future__ import annotations
from pydantic import BaseModel, Field


class TaxonomyMappingRequest(BaseModel):
    """Request object for taxonomy mapping use case."""
    model_config = {"frozen": True}
    
    record_id: str = Field(..., description="Record ID for mapping request")
    control_description: str = Field(..., description="Control description to map")


class FiveWsMappingRequest(BaseModel):
    """Request object for 5Ws mapping use case."""
    model_config = {"frozen": True}
    
    record_id: str = Field(..., description="Record ID for mapping request")
    control_description: str = Field(..., description="Control description to analyze")
