"""Controller for evaluation operations - optimized for multiple metrics."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union

from mapper_api.application.dto.http_evaluation import EvaluationHttpRequest
from mapper_api.application.dto.http_evaluation import EvaluationResponse, MetricResult
from mapper_api.application.dto.http_common import ResponseHeader
from mapper_api.application.dto.domain_evaluation import EvaluationRequest
from mapper_api.application.use_cases.evaluate_mapper import EvaluateMapper
from mapper_api.domain.value_objects.metric import MetricType
from mapper_api.domain.errors import ControlValidationError
from mapper_api.infrastructure.azure.blob_evaluation_results_writer import BlobEvaluationResultsWriter


@dataclass
class EvaluationController:
    """
    Controller for handling evaluation requests and responses.
    
    Optimized for multiple metric evaluation.
    """
    evaluate_use_case: EvaluateMapper
    results_writer: BlobEvaluationResultsWriter

    def handle_evaluation(self, request: EvaluationHttpRequest) -> EvaluationResponse:
        """
        Handle evaluation request with support for multiple metrics.
        
        Args:
            request: Incoming HTTP request data
            
        Returns:
            EvaluationResponse: Formatted response for HTTP layer
            
        Raises:
            ControlValidationError: When validation fails
        """
        # Parse and validate metric types
        metric_types = self._parse_metric_types(request.data.metricType)
        
        # Generate timestamp for directory naming
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        
        # Transform web request to use case request
        use_case_request = EvaluationRequest(
            record_id=request.header.recordId,
            metric_types=metric_types,
            n_records=request.data.nRecords
        )
        
        # Execute use case
        try:
            results = self.evaluate_use_case.execute(use_case_request)
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            raise ControlValidationError(f"Failed to evaluate mapper: {error_type}: {error_msg}")
        
        # Write results to blob storage and prepare response
        directory_path = self.results_writer.get_directory_path(
            request.header.recordId, 
            timestamp
        )
        
        metric_results = []
        successful_metrics = 0
        
        for metric_type, evaluation_result in results.items():
            # Check if the evaluation itself failed
            if evaluation_result.error_message:
                metric_results.append(MetricResult(
                    metric_type=metric_type.value,
                    file_path="",
                    total_records=len(evaluation_result.individual_results),
                    status="error",
                    error_message=evaluation_result.error_message
                ))
                continue
            
            try:
                file_path = self.results_writer.write_evaluation_result(
                    request.header.recordId,
                    timestamp,
                    metric_type.value,
                    evaluation_result
                )
                
                total_records = len(evaluation_result.individual_results)
                
                metric_results.append(MetricResult(
                    metric_type=metric_type.value,
                    file_path=file_path,
                    total_records=total_records,
                    status="success",
                    error_message=None
                ))
                successful_metrics += 1
                
            except Exception as e:
                metric_results.append(MetricResult(
                    metric_type=metric_type.value,
                    file_path="",
                    total_records=len(evaluation_result.individual_results),
                    status="error",
                    error_message=str(e)
                ))
        
        # Generate overall message
        total_metrics = len(metric_types)
        if successful_metrics == total_metrics:
            message = f"All {total_metrics} metrics evaluated successfully. Results saved to {directory_path}"
        else:
            failed_metrics = total_metrics - successful_metrics
            message = f"{successful_metrics}/{total_metrics} metrics evaluated successfully. {failed_metrics} failed. Results saved to {directory_path}"
        
        return EvaluationResponse(
            header=ResponseHeader(recordId=use_case_request.record_id),
            results=metric_results,
            directory_path=directory_path,
            message=message
        )
    
    def _parse_metric_types(self, metric_input: Union[str, List[str]]) -> List[MetricType]:
        """Parse metric types from input, handling 'all' case."""
        if isinstance(metric_input, str):
            if metric_input.lower() == "all":
                return list(MetricType)
            else:
                try:
                    return [MetricType(metric_input)]
                except ValueError as e:
                    raise ControlValidationError(f"Invalid metric type: {metric_input}. {e}")
        
        elif isinstance(metric_input, list):
            metric_types = []
            for metric_str in metric_input:
                if metric_str.lower() == "all":
                    return list(MetricType)  # If 'all' is in the list, return all metrics
                try:
                    metric_types.append(MetricType(metric_str))
                except ValueError as e:
                    raise ControlValidationError(f"Invalid metric type: {metric_str}. {e}")
            return metric_types
        
        else:
            raise ControlValidationError("metricType must be a string or list of strings")
