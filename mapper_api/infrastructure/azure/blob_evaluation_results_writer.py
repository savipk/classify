"""Azure Blob adapter to write evaluation results to blob storage."""
from __future__ import annotations
import json
from datetime import datetime
from typing import Dict, Any
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from mapper_api.domain.value_objects.evaluation_result import EvaluationResult


class BlobEvaluationResultsWriter:
    """Azure Blob Storage writer for evaluation results."""
    
    def __init__(
        self,
        *,
        account_name: str,
        container_name: str,
        tenant_id: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        self._credential = ClientSecretCredential(
            tenant_id=tenant_id, 
            client_id=client_id, 
            client_secret=client_secret
        )
        self._service = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=self._credential,
        )
        self._container = self._service.get_container_client(container_name)

    def write_evaluation_result(
        self, 
        record_id: str, 
        timestamp: str,
        metric_type: str,
        evaluation_result: EvaluationResult
    ) -> str:
        """
        Write evaluation result to blob storage.
        
        Args:
            record_id: The record ID from the evaluation request
            timestamp: Timestamp string for directory naming
            metric_type: The metric type for file naming
            evaluation_result: The evaluation result to write
            
        Returns:
            str: The blob path where the result was written
        """
        # Create blob path: evaluation/results/{record_id}_{timestamp}/{metric_type}.json
        blob_path = f"evaluation/results/{record_id}_{timestamp}/{metric_type}.json"
        
        # Convert evaluation result to JSON-serializable format
        result_data = self._serialize_evaluation_result(evaluation_result)
        
        # Write to blob storage
        blob_client = self._container.get_blob_client(blob_path)
        blob_client.upload_blob(
            json.dumps(result_data, indent=2),
            overwrite=True,
            content_type="application/json"
        )
        
        return blob_path
    
    def get_directory_path(self, record_id: str, timestamp: str) -> str:
        """Get the directory path for evaluation results."""
        return f"evaluation/results/{record_id}_{timestamp}"

    def _serialize_evaluation_result(self, result: EvaluationResult) -> Dict[str, Any]:
        """Convert EvaluationResult to JSON-serializable dictionary."""
        return result.to_dict()

