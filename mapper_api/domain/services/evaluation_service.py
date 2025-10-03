"""Domain service for evaluation metric calculations."""
from __future__ import annotations
import time
import statistics
from typing import List, Set, Dict, Any, Callable
from mapper_api.domain.value_objects.metric import (
    Score, 
    IndividualRecall, 
    SummaryRecall,
    Score,
    IndividualAccuracy,
    SummaryAccuracy,
    Score,
    IndividualLLMJudge,
    SummaryLLMJudge,
    ConfidenceLevel,
    UnmatchedTheme,
    IndividualUnmatchedAnalysis,
    LatencyScore,
    IndividualLatency,
    SummaryLatency
)
from mapper_api.domain.repositories.ground_truth import (
    FiveWGroundTruthRecord,
    RiskThemeGroundTruthRecord
)
from mapper_api.application.ports.llm import LLMClient


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
            recall=Score(value=recall_value),
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
            recall=Score(value=recall_value),
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
            average_recall=Score(value=sum(recall_values) / len(recall_values)),
            min_recall=Score(value=min(recall_values)),
            max_recall=Score(value=max(recall_values))
        )
    
    def calculate_top1_accuracy_risk_theme(
        self,
        ground_truth_record: RiskThemeGroundTruthRecord,
        predicted_themes: List[Dict[str, Any]]
    ) -> IndividualAccuracy:
        """
        Calculate Top-1 Accuracy for risk themes.
        
        Top-1 Accuracy: Whether the top-ranked AI prediction is present in ground truth.
        """
        # Extract ground truth theme names
        gt_theme_names = {theme.name for theme in ground_truth_record.risk_theme}
        
        # Get top-1 predicted theme
        if not predicted_themes:
            accuracy_value = 0.0
            top1_theme = None
        else:
            top1_theme = predicted_themes[0]["name"]
            accuracy_value = 1.0 if top1_theme in gt_theme_names else 0.0
        
        return IndividualAccuracy(
            control_id=ground_truth_record.control_id,
            accuracy=Score(value=accuracy_value),
            details={
                "ground_truth_themes": list(gt_theme_names),
                "top1_predicted_theme": top1_theme,
                "is_correct": accuracy_value == 1.0,
                "gt_count": len(gt_theme_names),
                "predicted_count": len(predicted_themes)
            }
        )
    
    def calculate_llm_judge_risk_theme_reasoning(
        self,
        ground_truth_record: RiskThemeGroundTruthRecord,
        predicted_themes: List[Dict[str, Any]],
        llm_client: LLMClient
    ) -> IndividualLLMJudge:
        """
        Calculate LLM-as-a-Judge score for risk theme reasoning quality.
        
        Evaluates reasoning based on: Groundness, Relevance, Consistency, Specificity, Clarity.
        """
        if not predicted_themes:
            return IndividualLLMJudge(
                control_id=ground_truth_record.control_id,
                llm_judge_score=Score(value=0.0),
                details={
                    "error": "No predictions to evaluate",
                    "dimensions": {}
                }
            )
        
        # Use top prediction for reasoning evaluation
        top_prediction = predicted_themes[0]
        control_description = ground_truth_record.control_description
        predicted_theme = top_prediction["name"]
        reasoning = top_prediction.get("reasoning", "")
        
        # Create LLM prompt for reasoning evaluation
        system_prompt = """You are an expert evaluator assessing the quality of risk theme reasoning. 
        Evaluate the reasoning on these 5 dimensions (0-1 scale):
        
        1. Groundness: Uses only details from the control description, no external information
        2. Relevance: Highlights salient risk cues that justify the chosen theme
        3. Consistency: Reasoning is logical and supports the chosen theme
        4. Specificity: Relies on concrete evidence (terms, actions, processes), avoids generic statements
        5. Clarity: Concise, coherent, and non-contradictory
        
        Return ONLY a JSON object with dimension scores and overall average."""
        
        user_prompt = f"""Control Description: {control_description}

Predicted Risk Theme: {predicted_theme}

Reasoning to Evaluate: {reasoning}

Evaluate the reasoning quality and return JSON in this exact format:
{{
    "groundness": 0.8,
    "relevance": 0.7,
    "consistency": 0.9,
    "specificity": 0.6,
    "clarity": 0.8,
    "overall_average": 0.76
}}"""
        
        try:
            # Call LLM for evaluation
            response = llm_client.json_schema_chat(
                system=system_prompt,
                user=user_prompt,
                schema_name="ReasoningEvaluation",
                schema={
                    "type": "object",
                    "properties": {
                        "groundness": {"type": "number", "minimum": 0, "maximum": 1},
                        "relevance": {"type": "number", "minimum": 0, "maximum": 1},
                        "consistency": {"type": "number", "minimum": 0, "maximum": 1},
                        "specificity": {"type": "number", "minimum": 0, "maximum": 1},
                        "clarity": {"type": "number", "minimum": 0, "maximum": 1},
                        "overall_average": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["groundness", "relevance", "consistency", "specificity", "clarity", "overall_average"],
                    "additionalProperties": False
                },
                max_tokens=200,
                temperature=0.1,
                context={"trace_id": ground_truth_record.control_id},
                deployment="gpt-4o"  # Use from settings in actual implementation
            )
            
            import json
            evaluation = json.loads(response)
            overall_score = evaluation["overall_average"]
            
        except Exception as e:
            # Fallback to 0.5 if LLM evaluation fails
            overall_score = 0.5
            evaluation = {
                "error": f"LLM evaluation failed: {str(e)}",
                "groundness": 0.5,
                "relevance": 0.5,
                "consistency": 0.5,
                "specificity": 0.5,
                "clarity": 0.5,
                "overall_average": 0.5
            }
        
        return IndividualLLMJudge(
            control_id=ground_truth_record.control_id,
            llm_judge_score=Score(value=overall_score),
            details={
                "predicted_theme": predicted_theme,
                "reasoning": reasoning,
                "dimensions": evaluation,
                "control_description": control_description
            }
        )
    
    def calculate_llm_judge_risk_theme_unmatched(
        self,
        ground_truth_record: RiskThemeGroundTruthRecord,
        predicted_themes: List[Dict[str, Any]],
        llm_client: LLMClient
    ) -> IndividualUnmatchedAnalysis:
        """
        Calculate LLM-as-a-Judge confidence scores for unmatched risk themes.
        """
        gt_theme_names = {theme.name for theme in ground_truth_record.risk_theme}
        ai_theme_names = {theme["name"] for theme in predicted_themes}
        
        only_in_gt = gt_theme_names - ai_theme_names
        only_in_ai = ai_theme_names - gt_theme_names
        
        control_description = ground_truth_record.control_description
        
        def evaluate_theme_confidence(theme_name: str, is_gt_theme: bool) -> UnmatchedTheme:
            """Evaluate confidence for a single unmatched theme."""
            context = "ground truth" if is_gt_theme else "AI prediction"
            
            system_prompt = f"""You are an expert evaluator assessing how well a risk theme fits a control description.
            Rate the confidence (0-1) that this risk theme is appropriate for the given control description.
            Consider relevance, specificity, and logical connection."""
            
            user_prompt = f"""Control Description: {control_description}

Risk Theme: {theme_name}
Context: This theme was found in {context}

Rate confidence (0-1) that this risk theme is appropriate for this control description.
Return ONLY a JSON object with the confidence score:
{{"confidence": 0.85}}"""
            
            try:
                response = llm_client.json_schema_chat(
                    system=system_prompt,
                    user=user_prompt,
                    schema_name="ThemeConfidence",
                    schema={
                        "type": "object",
                        "properties": {
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                        },
                        "required": ["confidence"],
                        "additionalProperties": False
                    },
                    max_tokens=50,
                    temperature=0.1,
                    context={"trace_id": ground_truth_record.control_id},
                    deployment="gpt-4o"
                )
                
                import json
                result = json.loads(response)
                confidence_score = result["confidence"]
                
            except Exception:
                # Fallback confidence
                confidence_score = 0.5
            
            confidence_level = ConfidenceLevel.from_score(confidence_score)
            
            # Determine if needs attention
            if is_gt_theme:
                # GT theme missing in AI - needs attention if confidence is low
                needs_attention = confidence_score < 0.4
            else:
                # AI theme missing in GT - needs attention if confidence is high
                needs_attention = confidence_score > 0.6
            
            return UnmatchedTheme(
                name=theme_name,
                confidence_score=confidence_score,
                confidence_level=confidence_level,
                needs_attention=needs_attention
            )
        
        # Evaluate all unmatched themes
        only_in_gt_evaluated = [
            evaluate_theme_confidence(theme, True) for theme in only_in_gt
        ]
        only_in_ai_evaluated = [
            evaluate_theme_confidence(theme, False) for theme in only_in_ai
        ]
        
        return IndividualUnmatchedAnalysis(
            control_id=ground_truth_record.control_id,
            control_description=control_description,
            ground_truth_themes=list(gt_theme_names),
            ai_predicted_themes=list(ai_theme_names),
            only_in_gt=only_in_gt_evaluated,
            only_in_ai=only_in_ai_evaluated
        )
    
    def calculate_latency_risk_theme_mapper(
        self,
        ground_truth_records: List[RiskThemeGroundTruthRecord],
        mapper_function: Callable[[str, str], List[Dict[str, Any]]],
        n_records: int = None
    ) -> List[IndividualLatency]:
        """
        Calculate latency metrics for risk theme mapper.
        
        Args:
            ground_truth_records: Ground truth data
            mapper_function: Function that takes (record_id, control_description) and returns predictions
            n_records: Number of records to test (None for all)
        """
        records_to_test = ground_truth_records[:n_records] if n_records else ground_truth_records
        individual_latencies = []
        
        for record in records_to_test:
            start_time = time.time()
            
            try:
                # Call the mapper function
                _ = mapper_function(record.control_id, record.control_description)
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                individual_latencies.append(IndividualLatency(
                    control_id=record.control_id,
                    latency=LatencyScore(value_ms=latency_ms),
                    details={
                        "start_time": start_time,
                        "end_time": end_time,
                        "success": True
                    }
                ))
                
            except Exception as e:
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                individual_latencies.append(IndividualLatency(
                    control_id=record.control_id,
                    latency=LatencyScore(value_ms=latency_ms),
                    details={
                        "start_time": start_time,
                        "end_time": end_time,
                        "success": False,
                        "error": str(e)
                    }
                ))
        
        return individual_latencies
    
    def calculate_llm_judge_5ws_reasoning(
        self,
        ground_truth_record: FiveWGroundTruthRecord,
        predicted_5ws: List[Dict[str, Any]],
        llm_client: LLMClient
    ) -> IndividualLLMJudge:
        """
        Calculate LLM-as-a-Judge score for 5Ws reasoning quality.
        
        Evaluates if reasoning faithfully captures ground truth, is grounded, and has no hallucinations.
        """
        if not predicted_5ws:
            return IndividualLLMJudge(
                control_id=ground_truth_record.control_id,
                llm_judge_score=Score(value=0.0),
                details={
                    "error": "No predictions to evaluate",
                    "evaluations": []
                }
            )
        
        control_description = ground_truth_record.control_description
        gt_present_ws = {
            w.name: w for w in ground_truth_record.gt_5ws 
            if w.status == "present"
        }
        
        evaluations = []
        total_score = 0.0
        
        for predicted_w in predicted_5ws:
            if predicted_w["status"] != "present":
                continue
                
            w_name = predicted_w["name"]
            reasoning = predicted_w.get("reasoning", "")
            
            # Check if this W is in ground truth
            is_in_gt = w_name in gt_present_ws
            gt_reasoning = gt_present_ws[w_name].reasoning if is_in_gt else ""
            
            system_prompt = """You are an expert evaluator assessing 5W reasoning quality.
            Evaluate if the reasoning:
            1. Faithfully captures the ground truth understanding
            2. Is grounded in the control description
            3. Has no hallucinations or unsupported additions
            
            Return a score 0-1 and brief explanation."""
            
            user_prompt = f"""Control Description: {control_description}

W Category: {w_name}
Ground Truth Present: {is_in_gt}
{f"Ground Truth Reasoning: {gt_reasoning}" if is_in_gt else ""}

Predicted Reasoning: {reasoning}

Evaluate the reasoning quality and return JSON:
{{"score": 0.8, "explanation": "Brief explanation"}}"""
            
            try:
                response = llm_client.json_schema_chat(
                    system=system_prompt,
                    user=user_prompt,
                    schema_name="FiveWsReasoningEvaluation",
                    schema={
                        "type": "object",
                        "properties": {
                            "score": {"type": "number", "minimum": 0, "maximum": 1},
                            "explanation": {"type": "string"}
                        },
                        "required": ["score", "explanation"],
                        "additionalProperties": False
                    },
                    max_tokens=150,
                    temperature=0.1,
                    context={"trace_id": ground_truth_record.control_id},
                    deployment="gpt-4o"
                )
                
                import json
                evaluation = json.loads(response)
                w_score = evaluation["score"]
                explanation = evaluation["explanation"]
                
            except Exception as e:
                w_score = 0.5
                explanation = f"Evaluation failed: {str(e)}"
            
            evaluations.append({
                "w_name": w_name,
                "score": w_score,
                "explanation": explanation,
                "is_in_gt": is_in_gt,
                "reasoning": reasoning
            })
            
            total_score += w_score
        
        # Average score across all present Ws
        overall_score = total_score / len(evaluations) if evaluations else 0.0
        
        return IndividualLLMJudge(
            control_id=ground_truth_record.control_id,
            llm_judge_score=Score(value=overall_score),
            details={
                "evaluations": evaluations,
                "total_present_ws": len(evaluations),
                "control_description": control_description
            }
        )
    
    def calculate_latency_5ws_mapper(
        self,
        ground_truth_records: List[FiveWGroundTruthRecord],
        mapper_function: Callable[[str, str], List[Dict[str, Any]]],
        n_records: int = None
    ) -> List[IndividualLatency]:
        """
        Calculate latency metrics for 5Ws mapper.
        
        Args:
            ground_truth_records: Ground truth data
            mapper_function: Function that takes (record_id, control_description) and returns predictions
            n_records: Number of records to test (None for all)
        """
        records_to_test = ground_truth_records[:n_records] if n_records else ground_truth_records
        individual_latencies = []
        
        for record in records_to_test:
            start_time = time.time()
            
            try:
                # Call the mapper function
                _ = mapper_function(record.control_id, record.control_description)
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                individual_latencies.append(IndividualLatency(
                    control_id=record.control_id,
                    latency=LatencyScore(value_ms=latency_ms),
                    details={
                        "start_time": start_time,
                        "end_time": end_time,
                        "success": True
                    }
                ))
                
            except Exception as e:
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                individual_latencies.append(IndividualLatency(
                    control_id=record.control_id,
                    latency=LatencyScore(value_ms=latency_ms),
                    details={
                        "start_time": start_time,
                        "end_time": end_time,
                        "success": False,
                        "error": str(e)
                    }
                ))
        
        return individual_latencies
    
    def calculate_summary_accuracy(
        self, 
        individual_accuracies: List[IndividualAccuracy]
    ) -> SummaryAccuracy:
        """Calculate summary statistics from individual accuracy scores."""
        if not individual_accuracies:
            raise ValueError("Cannot calculate summary for empty individual accuracies")
        
        accuracy_values = [ia.accuracy.value for ia in individual_accuracies]
        
        return SummaryAccuracy(
            total_records=len(individual_accuracies),
            average_accuracy=Score(value=sum(accuracy_values) / len(accuracy_values)),
            min_accuracy=Score(value=min(accuracy_values)),
            max_accuracy=Score(value=max(accuracy_values))
        )
    
    def calculate_summary_llm_judge(
        self, 
        individual_judges: List[IndividualLLMJudge]
    ) -> SummaryLLMJudge:
        """Calculate summary statistics from individual LLM judge scores."""
        if not individual_judges:
            raise ValueError("Cannot calculate summary for empty individual LLM judge scores")
        
        judge_values = [ij.llm_judge_score.value for ij in individual_judges]
        
        return SummaryLLMJudge(
            total_records=len(individual_judges),
            average_score=Score(value=sum(judge_values) / len(judge_values)),
            min_score=Score(value=min(judge_values)),
            max_score=Score(value=max(judge_values))
        )
    
    def calculate_summary_latency(
        self, 
        individual_latencies: List[IndividualLatency]
    ) -> SummaryLatency:
        """Calculate summary statistics from individual latency measurements."""
        if not individual_latencies:
            raise ValueError("Cannot calculate summary for empty individual latencies")
        
        latency_values = [il.latency.value_ms for il in individual_latencies]
        latency_values.sort()
        
        p95_index = int(0.95 * len(latency_values))
        p99_index = int(0.99 * len(latency_values))
        
        return SummaryLatency(
            total_records=len(individual_latencies),
            average_latency=LatencyScore(value_ms=sum(latency_values) / len(latency_values)),
            min_latency=LatencyScore(value_ms=min(latency_values)),
            max_latency=LatencyScore(value_ms=max(latency_values)),
            p95_latency=LatencyScore(value_ms=latency_values[p95_index]),
            p99_latency=LatencyScore(value_ms=latency_values[p99_index])
        )
