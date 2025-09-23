"""Domain service for evaluation metric calculations."""
from __future__ import annotations
from typing import List, Set, Dict, Any
from mapper_api.domain.value_objects.metric import (
    RecallScore, 
    IndividualRecall, 
    SummaryRecall
)
from mapper_api.domain.repositories.ground_truth import (
    FiveWGroundTruthRecord,
    RiskThemeGroundTruthRecord
)


class EvaluationService:
    """Domain service for calculating evaluation metrics."""
    
    def calculate_recall_k3_risk_theme(
        self,
        ground_truth_record: RiskThemeGroundTruthRecord,
        predicted_themes: List[Dict[str, Any]]  # List of {name, id, score, reasoning}
    ) -> IndividualRecall:
        """
        Calculate Recall@K=3 for risk themes.
        
        Recall K=3: The fraction of ground truth risk themes that were captured 
        in the top 3 AI response.
        """
        # Extract ground truth theme names
        gt_theme_names = {theme.name for theme in ground_truth_record.risk_theme}
        
        # Extract top 3 predicted theme names (already limited to top 3 in use case)
        predicted_names = {theme["name"] for theme in predicted_themes[:3]}
        
        # Calculate recall
        if not gt_theme_names:
            # No ground truth themes - perfect recall by definition
            recall_value = 1.0
            matched_themes = set()
        else:
            matched_themes = gt_theme_names.intersection(predicted_names)
            recall_value = len(matched_themes) / len(gt_theme_names)
        
        return IndividualRecall(
            control_id=ground_truth_record.control_id,
            recall=RecallScore(recall_value),
            details={
                "ground_truth_themes": list(gt_theme_names),
                "predicted_themes": list(predicted_names),
                "matched_themes": list(matched_themes),
                "gt_count": len(gt_theme_names),
                "predicted_count": len(predicted_names),
                "matched_count": len(matched_themes)
            }
        )
    
    def calculate_recall_k5_5ws(
        self,
        ground_truth_record: FiveWGroundTruthRecord,
        predicted_5ws: List[Dict[str, Any]]  # List of {name, status, reasoning}
    ) -> IndividualRecall:
        """
        Calculate Recall@K=5 for 5Ws.
        
        Recall K=5: Fraction of the Ws present in the ground truth that are 
        also present in the AI response.
        """
        # Extract ground truth present Ws
        gt_present_ws = {
            w.name for w in ground_truth_record.gt_5ws 
            if w.status == "present"
        }
        
        # Extract predicted present Ws
        predicted_present_ws = {
            w["name"] for w in predicted_5ws 
            if w["status"] == "present"
        }
        
        # Calculate recall
        if not gt_present_ws:
            # No ground truth present Ws - perfect recall by definition
            recall_value = 1.0
            matched_ws = set()
        else:
            matched_ws = gt_present_ws.intersection(predicted_present_ws)
            recall_value = len(matched_ws) / len(gt_present_ws)
        
        return IndividualRecall(
            control_id=ground_truth_record.control_id,
            recall=RecallScore(recall_value),
            details={
                "ground_truth_present_ws": list(gt_present_ws),
                "predicted_present_ws": list(predicted_present_ws),
                "matched_ws": list(matched_ws),
                "gt_present_count": len(gt_present_ws),
                "predicted_present_count": len(predicted_present_ws),
                "matched_count": len(matched_ws)
            }
        )
    
    def calculate_summary_recall(
        self, 
        individual_recalls: List[IndividualRecall]
    ) -> SummaryRecall:
        """Calculate summary statistics from individual recall scores."""
        if not individual_recalls:
            raise ValueError("Cannot calculate summary for empty individual recalls")
        
        recall_values = [ir.recall.value for ir in individual_recalls]
        
        return SummaryRecall(
            total_records=len(individual_recalls),
            average_recall=RecallScore(sum(recall_values) / len(recall_values)),
            min_recall=RecallScore(min(recall_values)),
            max_recall=RecallScore(max(recall_values))
        )
