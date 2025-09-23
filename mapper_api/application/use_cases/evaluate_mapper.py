"""Use case: evaluate mapper predictions against ground truth."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List

from mapper_api.domain.entities.evaluation import EvaluationResult
from mapper_api.domain.repositories.ground_truth import GroundTruthRepository
from mapper_api.domain.services.evaluation_service import EvaluationService
from mapper_api.domain.value_objects.metric import MetricType, IndividualRecall
from mapper_api.domain.errors import DefinitionsUnavailableError
from mapper_api.application.dto.evaluation_requests import EvaluationRequest
from mapper_api.application.dto.use_case_requests import TaxonomyMappingRequest, FiveWsMappingRequest
from mapper_api.application.use_cases.map_control_to_themes import ClassifyControlToThemes
from mapper_api.application.use_cases.map_control_to_5ws import ClassifyControlTo5Ws


@dataclass
class EvaluateMapper:
    """
    Use case for evaluating mapper predictions against ground truth data.
    
    This use case orchestrates:
    1. Loading ground truth data
    2. Making predictions using existing mappers
    3. Calculating evaluation metrics
    """
    ground_truth_repo: GroundTruthRepository
    evaluation_service: EvaluationService
    taxonomy_classifier: ClassifyControlToThemes
    fivews_classifier: ClassifyControlTo5Ws

    def execute(self, request: EvaluationRequest) -> EvaluationResult:
        """Execute evaluation for the specified metric type."""
        if request.metric_type == MetricType.RECALL_K3_RISK_THEME:
            return self._evaluate_recall_k3_risk_theme(request)
        elif request.metric_type == MetricType.RECALL_K5_5WS:
            return self._evaluate_recall_k5_5ws(request)
        else:
            raise ValueError(f"Unsupported metric type: {request.metric_type}")

    def _evaluate_recall_k3_risk_theme(self, request: EvaluationRequest) -> EvaluationResult:
        """Evaluate recall K=3 for risk themes."""
        # Load ground truth data
        gt_records = self.ground_truth_repo.get_risk_themes_ground_truth()
        if not gt_records:
            raise DefinitionsUnavailableError("Risk theme ground truth data not loaded")

        individual_recalls: List[IndividualRecall] = []
        
        for gt_record in gt_records:
            # Make prediction using existing taxonomy classifier
            taxonomy_request = TaxonomyMappingRequest(
                record_id=gt_record.control_id,
                control_description=gt_record.control_description
            )
            predicted_themes = self.taxonomy_classifier.execute(taxonomy_request)
            
            # Calculate recall for this record
            individual_recall = self.evaluation_service.calculate_recall_k3_risk_theme(
                gt_record, predicted_themes
            )
            individual_recalls.append(individual_recall)

        # Calculate summary
        summary_recall = self.evaluation_service.calculate_summary_recall(individual_recalls)
        
        return EvaluationResult(
            metric_type=request.metric_type,
            individual_recalls=individual_recalls,
            summary_recall=summary_recall
        )

    def _evaluate_recall_k5_5ws(self, request: EvaluationRequest) -> EvaluationResult:
        """Evaluate recall K=5 for 5Ws."""
        # Load ground truth data
        gt_records = self.ground_truth_repo.get_fivews_ground_truth()
        if not gt_records:
            raise DefinitionsUnavailableError("5Ws ground truth data not loaded")

        individual_recalls: List[IndividualRecall] = []
        
        for gt_record in gt_records:
            # Make prediction using existing 5Ws classifier
            fivews_request = FiveWsMappingRequest(
                record_id=gt_record.control_id,
                control_description=gt_record.control_description
            )
            predicted_5ws = self.fivews_classifier.execute(fivews_request)
            
            # Calculate recall for this record
            individual_recall = self.evaluation_service.calculate_recall_k5_5ws(
                gt_record, predicted_5ws
            )
            individual_recalls.append(individual_recall)

        # Calculate summary
        summary_recall = self.evaluation_service.calculate_summary_recall(individual_recalls)
        
        return EvaluationResult(
            metric_type=request.metric_type,
            individual_recalls=individual_recalls,
            summary_recall=summary_recall
        )
