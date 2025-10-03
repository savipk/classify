"""Controller for taxonomy mapping operations following EcomApp pattern."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

from mapper_api.application.dto.http_common import CommonRequest
from mapper_api.application.dto.http_common import TaxonomyResponse, ResponseHeader, TaxonomyData
from mapper_api.application.dto.domain_mapping import TaxonomyMappingRequest
from mapper_api.application.use_cases.map_control_to_themes import ClassifyControlToThemes
from mapper_api.domain.errors import ControlValidationError


@dataclass
class TaxonomyController:
    """
    Controller for handling taxonomy mapping requests and responses.
    
    Follows EcomApp's pattern of simple, transparent dependency management.
    The controller receives pre-configured use cases and focuses only on
    request/response transformation.
    """
    classify_use_case: ClassifyControlToThemes

    def handle_taxonomy_mapping(self, request: CommonRequest) -> TaxonomyResponse:
        """
        Handle taxonomy mapping request with clear separation of concerns.
        
        Args:
            request: Incoming HTTP request data
            
        Returns:
            TaxonomyResponse: Formatted response for HTTP layer
            
        Raises:
            ControlValidationError: When control description validation fails
        """
        # Transform web request to use case request
        use_case_request = TaxonomyMappingRequest(
            record_id=request.header.recordId,
            control_description=request.data.controlDescription
        )
        
        # Execute use case (already configured with dependencies)
        try:
            result = self.classify_use_case.execute(use_case_request)
        except Exception as e:
            # Provide more specific error information for debugging
            error_type = type(e).__name__
            error_msg = str(e)
            raise ControlValidationError(f"Failed to process control description: {error_type}: {error_msg}")
        
        # Transform use case result to web response
        return TaxonomyResponse(
            header=ResponseHeader(recordId=use_case_request.record_id),
            data=TaxonomyData(taxonomy=result)
        )
