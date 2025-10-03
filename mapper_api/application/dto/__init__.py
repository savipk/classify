"""Application Data Transfer Objects.

Provides DTOs for different layers:
- domain_mapping: Internal domain mapping contracts  
- domain_evaluation: Internal evaluation contracts
- http_common: Common HTTP API contracts
- http_evaluation: HTTP evaluation API contracts
- llm_schemas: LLM JSON schema contracts
"""
from .domain_mapping import TaxonomyMappingRequest, FiveWsMappingRequest
from .http_common import CommonRequest, CommonHeader, CommonData, TaxonomyResponse, FiveWResponse
from .llm_schemas import build_taxonomy_models, FiveWOut

__all__ = [
    "TaxonomyMappingRequest", "FiveWsMappingRequest",
    "CommonRequest", "CommonHeader", "CommonData", 
    "TaxonomyResponse", "FiveWResponse",
    "build_taxonomy_models", "FiveWOut"
]
