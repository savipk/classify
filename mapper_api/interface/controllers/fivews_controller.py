"""Controller for 5Ws mapping operations following EcomApp pattern."""
from __future__ import annotations
from dataclasses import dataclass

from mapper_api.application.dto.requests import CommonRequest
from mapper_api.application.dto.responses import FiveWResponse, ResponseHeader, FiveWData
from mapper_api.application.dto.use_case_requests import FiveWsMappingRequest
from mapper_api.application.use_cases.map_control_to_5ws import ClassifyControlTo5Ws
from mapper_api.domain.errors import ControlValidationError


@dataclass
class FiveWsController:
    """
    Controller for handling 5Ws mapping requests and responses.
    
    Follows EcomApp's pattern of simple, transparent dependency management.
    The controller receives pre-configured use cases and focuses only on
    request/response transformation.
    """
    classify_use_case: ClassifyControlTo5Ws
    deployment: str

    def handle_fivews_mapping(self, request: CommonRequest) -> FiveWResponse:
        """
        Handle 5Ws mapping request with clear separation of concerns.
        
        Args:
            request: Incoming HTTP request data
            
        Returns:
            FiveWResponse: Formatted response for HTTP layer
            
        Raises:
            ControlValidationError: When control description validation fails
        """
        # Transform web request to use case request
        use_case_request = FiveWsMappingRequest(
            record_id=request.header.recordId,
            control_description=request.data.controlDescription,
            deployment=self.deployment
        )
        
        # Execute use case (already configured with dependencies)
        try:
            result = self.classify_use_case.execute(use_case_request)
        except Exception as e:
            raise ControlValidationError(f"Failed to process control description: {str(e)}")
        
        # Transform use case result to web response
        return FiveWResponse(
            header=ResponseHeader(recordId=use_case_request.record_id),
            data=FiveWData(fivews=result)
        )
