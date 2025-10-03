"""Use case request DTOs for clear contracts between layers."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class TaxonomyMappingRequest:
    """Request object for taxonomy mapping use case."""
    record_id: str
    control_description: str


@dataclass(frozen=True)
class FiveWsMappingRequest:
    """Request object for 5Ws mapping use case."""
    record_id: str
    control_description: str
