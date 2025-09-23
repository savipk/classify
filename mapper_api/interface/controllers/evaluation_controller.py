"""Controller for evaluation operations following EcomApp pattern."""
from __future__ import annotations
from dataclasses import dataclass

from mapper_api.application.dto.http_evaluation_requests import EvaluationHttpRequest
from mapper_api.application.dto.evaluation_responses import (
    EvaluationResponse, 
    EvaluationData,
    IndividualRecallData,
    SummaryRecallData
)
from mapper_api.application.dto.http_responses import ResponseHeader
from mapper_api.application.dto.evaluation_requests import EvaluationRequest
from mapper_api.application.use_cases.evaluate_mapper import EvaluateMapper
from mapper_api.domain.value_objects.metric import MetricType
from mapper_api.domain.errors import ControlValidationError


@dataclass
class EvaluationController:
    """
    Controller for handling evaluation requests and responses.
    
    Follows EcomApp's pattern of simple, transparent dependency management.
    """
    evaluate_use_case: EvaluateMapper

    def handle_evaluation(self, request: EvaluationHttpRequest) -> EvaluationResponse:
        """
        Handle evaluation request with clear separation of concerns.
        
        Args:
            request: Incoming HTTP request data
            
        Returns:
            EvaluationResponse: Formatted response for HTTP layer
            
        Raises:
            ControlValidationError: When validation fails
        """
        # Validate and convert metric type
        try:
            metric_type = MetricType(request.data.metricType)
        except ValueError as e:
            raise ControlValidationError(f"Invalid metric type: {request.data.metricType}. {e}")
        
        # Transform web request to use case request
        use_case_request = EvaluationRequest(
            record_id=request.header.recordId,
            metric_type=metric_type
        )
        
        # Execute use case
        try:
            result = self.evaluate_use_case.execute(use_case_request)
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            raise ControlValidationError(f"Failed to evaluate mapper: {error_type}: {error_msg}")
        
        # Transform use case result to web response
        individual_recalls_data = [
            IndividualRecallData(
                controlId=ir.control_id,
                recall=ir.recall.value,
                details=ir.details
            )
            for ir in result.individual_recalls
        ]
        
        summary_recall_data = SummaryRecallData(
            totalRecords=result.summary_recall.total_records,
            averageRecall=result.summary_recall.average_recall.value,
            minRecall=result.summary_recall.min_recall.value,
            maxRecall=result.summary_recall.max_recall.value
        )
        
        return EvaluationResponse(
            header=ResponseHeader(recordId=use_case_request.record_id),
            data=EvaluationData(
                metricType=result.metric_type.value,
                individualRecalls=individual_recalls_data,
                summaryRecall=summary_recall_data
            )
        )
