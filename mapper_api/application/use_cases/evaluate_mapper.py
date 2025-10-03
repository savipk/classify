"""Use case: evaluate mapper predictions against ground truth."""
from __future__ import annotations
import requests
from dataclasses import dataclass
from typing import List, Dict, Any

from mapper_api.domain.value_objects.evaluation_result import EvaluationResult
from mapper_api.domain.repositories.ground_truth import GroundTruthRepository
from mapper_api.domain.services.evaluation_service import EvaluationService
from mapper_api.domain.value_objects.metric import MetricType
from mapper_api.domain.errors import DefinitionsUnavailableError
from mapper_api.application.dto.domain_evaluation import EvaluationRequest
from mapper_api.application.dto.domain_mapping import TaxonomyMappingRequest, FiveWsMappingRequest
from mapper_api.application.use_cases.map_control_to_themes import ClassifyControlToThemes
from mapper_api.application.use_cases.map_control_to_5ws import ClassifyControlTo5Ws
from mapper_api.application.ports.llm import LLMClient
from mapper_api.config.settings import Settings


@dataclass
class EvaluateMapper:
    """
    Use case for evaluating mapper predictions against ground truth data.
    
    Optimized for multiple metric evaluation with efficient data loading.
    """
    ground_truth_repo: GroundTruthRepository
    evaluation_service: EvaluationService
    taxonomy_classifier: ClassifyControlToThemes
    fivews_classifier: ClassifyControlTo5Ws
    llm_client: LLMClient

    def execute(self, request: EvaluationRequest) -> Dict[MetricType, EvaluationResult]:
        """Execute evaluation for the specified metric types."""
        results = {}
        
        # Pre-load ground truth data to avoid multiple loads
        risk_theme_gt = None
        fivews_gt = None
        
        for metric_type in request.metric_types:
            try:
                # Load ground truth data only when needed
                if metric_type in [
                    MetricType.RECALL_K3_RISK_THEME,
                    MetricType.TOP1_ACCURACY_RISK_THEME,
                    MetricType.LLM_JUDGE_RISK_THEME_REASONING,
                    MetricType.LLM_JUDGE_RISK_THEME_UNMATCHED,
                    MetricType.LATENCY_RISK_THEME_MAPPER
                ]:
                    if risk_theme_gt is None:
                        risk_theme_gt = self.ground_truth_repo.get_risk_themes_ground_truth()
                        if not risk_theme_gt:
                            raise DefinitionsUnavailableError("Risk theme ground truth data not loaded")
                
                elif metric_type in [
                    MetricType.RECALL_K5_5WS,
                    MetricType.LLM_JUDGE_5WS_REASONING,
                    MetricType.LATENCY_5WS_MAPPER
                ]:
                    if fivews_gt is None:
                        fivews_gt = self.ground_truth_repo.get_fivews_ground_truth()
                        if not fivews_gt:
                            raise DefinitionsUnavailableError("5Ws ground truth data not loaded")
                
                # Execute the specific metric evaluation
                result = self._execute_single_metric(metric_type, request, risk_theme_gt, fivews_gt)
                results[metric_type] = result
                
            except Exception as e:
                # Create error result for failed metrics
                results[metric_type] = self._create_error_result(metric_type, str(e))
        
        return results
    
    def _execute_single_metric(
        self, 
        metric_type: MetricType, 
        request: EvaluationRequest,
        risk_theme_gt: List = None,
        fivews_gt: List = None
    ) -> EvaluationResult:
        """Execute evaluation for a single metric type."""
        if metric_type == MetricType.RECALL_K3_RISK_THEME:
            return self._evaluate_recall_k3_risk_theme(risk_theme_gt)
        elif metric_type == MetricType.RECALL_K5_5WS:
            return self._evaluate_recall_k5_5ws(fivews_gt)
        elif metric_type == MetricType.TOP1_ACCURACY_RISK_THEME:
            return self._evaluate_top1_accuracy_risk_theme(risk_theme_gt)
        elif metric_type == MetricType.LLM_JUDGE_RISK_THEME_REASONING:
            return self._evaluate_llm_judge_risk_theme_reasoning(risk_theme_gt)
        elif metric_type == MetricType.LLM_JUDGE_RISK_THEME_UNMATCHED:
            return self._evaluate_llm_judge_risk_theme_unmatched(risk_theme_gt)
        elif metric_type == MetricType.LATENCY_RISK_THEME_MAPPER:
            return self._evaluate_latency_risk_theme_mapper(risk_theme_gt, request.n_records)
        elif metric_type == MetricType.LLM_JUDGE_5WS_REASONING:
            return self._evaluate_llm_judge_5ws_reasoning(fivews_gt)
        elif metric_type == MetricType.LATENCY_5WS_MAPPER:
            return self._evaluate_latency_5ws_mapper(fivews_gt, request.n_records)
        else:
            raise ValueError(f"Unsupported metric type: {metric_type}")
    
    def _create_error_result(self, metric_type: MetricType, error_message: str) -> EvaluationResult:
        """Create an error result for a failed metric evaluation."""
        return EvaluationResult(
            metric_type=metric_type,
            individual_results=[],
            summary_result=None
        )

    def _evaluate_recall_k3_risk_theme(self, gt_records) -> EvaluationResult:
        """Evaluate recall K=3 for risk themes."""
        individual_recalls = []
        
        for gt_record in gt_records:
            taxonomy_request = TaxonomyMappingRequest(
                record_id=gt_record.control_id,
                control_description=gt_record.control_description
            )
            predicted_themes = self.taxonomy_classifier.execute(taxonomy_request)
            
            individual_recall = self.evaluation_service.calculate_recall_k3_risk_theme(
                gt_record, predicted_themes
            )
            individual_recalls.append(individual_recall)

        summary_recall = self.evaluation_service.calculate_summary_recall(individual_recalls)
        
        return EvaluationResult(
            metric_type=MetricType.RECALL_K3_RISK_THEME,
            individual_results=individual_recalls,
            summary_result=summary_recall
        )

    def _evaluate_recall_k5_5ws(self, gt_records) -> EvaluationResult:
        """Evaluate recall K=5 for 5Ws."""
        individual_recalls = []
        
        for gt_record in gt_records:
            fivews_request = FiveWsMappingRequest(
                record_id=gt_record.control_id,
                control_description=gt_record.control_description
            )
            predicted_5ws = self.fivews_classifier.execute(fivews_request)
            
            individual_recall = self.evaluation_service.calculate_recall_k5_5ws(
                gt_record, predicted_5ws
            )
            individual_recalls.append(individual_recall)

        summary_recall = self.evaluation_service.calculate_summary_recall(individual_recalls)
        
        return EvaluationResult(
            metric_type=MetricType.RECALL_K5_5WS,
            individual_results=individual_recalls,
            summary_result=summary_recall
        )

    def _evaluate_top1_accuracy_risk_theme(self, gt_records) -> EvaluationResult:
        """Evaluate Top-1 Accuracy for risk themes."""
        individual_accuracies = []
        
        for gt_record in gt_records:
            taxonomy_request = TaxonomyMappingRequest(
                record_id=gt_record.control_id,
                control_description=gt_record.control_description
            )
            predicted_themes = self.taxonomy_classifier.execute(taxonomy_request)
            
            individual_accuracy = self.evaluation_service.calculate_top1_accuracy_risk_theme(
                gt_record, predicted_themes
            )
            individual_accuracies.append(individual_accuracy)

        summary_accuracy = self.evaluation_service.calculate_summary_accuracy(individual_accuracies)
        
        return EvaluationResult(
            metric_type=MetricType.TOP1_ACCURACY_RISK_THEME,
            individual_results=individual_accuracies,
            summary_result=summary_accuracy
        )

    def _evaluate_llm_judge_risk_theme_reasoning(self, gt_records) -> EvaluationResult:
        """Evaluate LLM-as-a-Judge scores for risk theme reasoning."""
        individual_judges = []
        
        for gt_record in gt_records:
            taxonomy_request = TaxonomyMappingRequest(
                record_id=gt_record.control_id,
                control_description=gt_record.control_description
            )
            predicted_themes = self.taxonomy_classifier.execute(taxonomy_request)
            
            individual_judge = self.evaluation_service.calculate_llm_judge_risk_theme_reasoning(
                gt_record, predicted_themes, self.llm_client
            )
            individual_judges.append(individual_judge)

        summary_judge = self.evaluation_service.calculate_summary_llm_judge(individual_judges)
        
        return EvaluationResult(
            metric_type=MetricType.LLM_JUDGE_RISK_THEME_REASONING,
            individual_results=individual_judges,
            summary_result=summary_judge
        )

    def _evaluate_llm_judge_risk_theme_unmatched(self, gt_records) -> EvaluationResult:
        """Evaluate LLM-as-a-Judge confidence for unmatched risk themes."""
        individual_analyses = []
        
        for gt_record in gt_records:
            taxonomy_request = TaxonomyMappingRequest(
                record_id=gt_record.control_id,
                control_description=gt_record.control_description
            )
            predicted_themes = self.taxonomy_classifier.execute(taxonomy_request)
            
            individual_analysis = self.evaluation_service.calculate_llm_judge_risk_theme_unmatched(
                gt_record, predicted_themes, self.llm_client
            )
            individual_analyses.append(individual_analysis)

        return EvaluationResult(
            metric_type=MetricType.LLM_JUDGE_RISK_THEME_UNMATCHED,
            individual_results=individual_analyses,
            summary_result=None
        )

    def _evaluate_latency_risk_theme_mapper(self, gt_records, n_records: int = None) -> EvaluationResult:
        """Evaluate latency for risk theme mapper via HTTP calls."""
        settings = Settings()
        base_url = f"http://localhost:{settings.PORT}"
        
        def http_mapper_function(record_id: str, control_description: str) -> List[Dict[str, Any]]:
            """HTTP wrapper for taxonomy mapper."""
            payload = {
                "header": {"recordId": record_id},
                "data": {"controlDescription": control_description}
            }
            
            response = requests.post(f"{base_url}/taxonomy_mapper", json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["data"]["taxonomyItems"]

        individual_latencies = self.evaluation_service.calculate_latency_risk_theme_mapper(
            gt_records, http_mapper_function, n_records
        )

        summary_latency = self.evaluation_service.calculate_summary_latency(individual_latencies)
        
        return EvaluationResult(
            metric_type=MetricType.LATENCY_RISK_THEME_MAPPER,
            individual_results=individual_latencies,
            summary_result=summary_latency
        )

    def _evaluate_llm_judge_5ws_reasoning(self, gt_records) -> EvaluationResult:
        """Evaluate LLM-as-a-Judge scores for 5Ws reasoning."""
        individual_judges = []
        
        for gt_record in gt_records:
            fivews_request = FiveWsMappingRequest(
                record_id=gt_record.control_id,
                control_description=gt_record.control_description
            )
            predicted_5ws = self.fivews_classifier.execute(fivews_request)
            
            individual_judge = self.evaluation_service.calculate_llm_judge_5ws_reasoning(
                gt_record, predicted_5ws, self.llm_client
            )
            individual_judges.append(individual_judge)

        summary_judge = self.evaluation_service.calculate_summary_llm_judge(individual_judges)
        
        return EvaluationResult(
            metric_type=MetricType.LLM_JUDGE_5WS_REASONING,
            individual_results=individual_judges,
            summary_result=summary_judge
        )

    def _evaluate_latency_5ws_mapper(self, gt_records, n_records: int = None) -> EvaluationResult:
        """Evaluate latency for 5Ws mapper via HTTP calls."""
        settings = Settings()
        base_url = f"http://localhost:{settings.PORT}"
        
        def http_mapper_function(record_id: str, control_description: str) -> List[Dict[str, Any]]:
            """HTTP wrapper for 5Ws mapper."""
            payload = {
                "header": {"recordId": record_id},
                "data": {"controlDescription": control_description}
            }
            
            response = requests.post(f"{base_url}/5ws_mapper", json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["data"]["fiveWs"]

        individual_latencies = self.evaluation_service.calculate_latency_5ws_mapper(
            gt_records, http_mapper_function, n_records
        )

        summary_latency = self.evaluation_service.calculate_summary_latency(individual_latencies)
        
        return EvaluationResult(
            metric_type=MetricType.LATENCY_5WS_MAPPER,
            individual_results=individual_latencies,
            summary_result=summary_latency
        )
