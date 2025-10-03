"""Value objects for evaluation metrics using Pydantic V2."""
from __future__ import annotations
from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from mapper_api.domain.value_objects.score import Score


class MetricType(Enum):
    """Supported evaluation metric types."""
    RECALL_K3_RISK_THEME = "recall_k3_risktheme"
    RECALL_K5_5WS = "recall_k5_5ws"
    TOP1_ACCURACY_RISK_THEME = "top1_accuracy_risktheme_class"
    LLM_JUDGE_RISK_THEME_REASONING = "llm_judge_risktheme_reasoning"
    LLM_JUDGE_RISK_THEME_UNMATCHED = "llm_judge_risktheme_unmatched_classes"
    LATENCY_RISK_THEME_MAPPER = "latency_risktheme_mapper"
    LLM_JUDGE_5WS_REASONING = "llm_judge_5ws_reasoning"
    LATENCY_5WS_MAPPER = "latency_5ws_mapper"


# Individual Metric Results
class IndividualRecall(BaseModel):
    """Recall score for a single control/record."""
    model_config = {"frozen": True}
    
    control_id: str = Field(..., description="Control ID")
    recall: Score = Field(..., description="Recall score")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "control_id": self.control_id,
            "recall": self.recall.value,
            "details": self.details
        }


class IndividualAccuracy(BaseModel):
    """Accuracy score for a single control/record."""
    model_config = {"frozen": True}
    
    control_id: str = Field(..., description="Control ID")
    accuracy: Score = Field(..., description="Accuracy score")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "control_id": self.control_id,
            "accuracy": self.accuracy.value,
            "details": self.details
        }


class IndividualLLMJudge(BaseModel):
    """LLM judge score for a single control/record."""
    model_config = {"frozen": True}
    
    control_id: str = Field(..., description="Control ID")
    llm_judge_score: Score = Field(..., description="LLM judge score")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "control_id": self.control_id,
            "llm_judge_score": self.llm_judge_score.value,
            "details": self.details
        }


class LatencyScore(BaseModel):
    """Value object for latency in milliseconds."""
    model_config = {"frozen": True}
    
    value_ms: float = Field(..., ge=0.0, description="Latency in milliseconds")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {"value_ms": self.value_ms}


class IndividualLatency(BaseModel):
    """Latency measurement for a single control/record."""
    model_config = {"frozen": True}
    
    control_id: str = Field(..., description="Control ID")
    latency: LatencyScore = Field(..., description="Latency measurement")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "control_id": self.control_id,
            "latency_ms": self.latency.value_ms,
            "details": self.details
        }


# Unmatched Analysis (no score validation needed)
class ConfidenceLevel:
    """Confidence level categorization."""
    HIGH = "high"
    MEDIUM_HIGH = "medium_high"
    MEDIUM = "medium"
    MEDIUM_LOW = "medium_low"
    LOW = "low"
    
    @classmethod
    def from_score(cls, score: float) -> str:
        """Convert confidence score to level."""
        if score > 0.8:
            return cls.HIGH
        elif score > 0.6:
            return cls.MEDIUM_HIGH
        elif score > 0.4:
            return cls.MEDIUM
        elif score > 0.2:
            return cls.MEDIUM_LOW
        else:
            return cls.LOW


class UnmatchedTheme(BaseModel):
    """Details for an unmatched risk theme."""
    model_config = {"frozen": True}
    
    name: str = Field(..., description="Theme name")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    confidence_level: str = Field(..., description="Confidence level")
    needs_attention: bool = Field(..., description="Whether needs SME attention")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "confidence_score": self.confidence_score,
            "confidence_level": self.confidence_level,
            "needs_attention": self.needs_attention
        }


class IndividualUnmatchedAnalysis(BaseModel):
    """Unmatched analysis for a single control/record."""
    model_config = {"frozen": True}
    
    control_id: str = Field(..., description="Control ID")
    control_description: str = Field(..., description="Control description")
    ground_truth_themes: List[str] = Field(default_factory=list, description="Ground truth themes")
    ai_predicted_themes: List[str] = Field(default_factory=list, description="AI predicted themes")
    only_in_gt: List[UnmatchedTheme] = Field(default_factory=list, description="Themes only in ground truth")
    only_in_ai: List[UnmatchedTheme] = Field(default_factory=list, description="Themes only in AI predictions")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "control_id": self.control_id,
            "control_description": self.control_description,
            "ground_truth_themes": self.ground_truth_themes,
            "ai_predicted_themes": self.ai_predicted_themes,
            "only_in_gt": [theme.to_dict() for theme in self.only_in_gt],
            "only_in_ai": [theme.to_dict() for theme in self.only_in_ai]
        }


# Summary Results
class SummaryRecall(BaseModel):
    """Summary recall across all evaluated records."""
    model_config = {"frozen": True}
    
    total_records: int = Field(..., ge=0, description="Total number of records")
    average_recall: Score = Field(..., description="Average recall score")
    min_recall: Score = Field(..., description="Minimum recall score")
    max_recall: Score = Field(..., description="Maximum recall score")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_records": self.total_records,
            "average_recall": self.average_recall.value,
            "min_recall": self.min_recall.value,
            "max_recall": self.max_recall.value
        }


class SummaryAccuracy(BaseModel):
    """Summary accuracy across all evaluated records."""
    model_config = {"frozen": True}
    
    total_records: int = Field(..., ge=0, description="Total number of records")
    average_accuracy: Score = Field(..., description="Average accuracy score")
    min_accuracy: Score = Field(..., description="Minimum accuracy score")
    max_accuracy: Score = Field(..., description="Maximum accuracy score")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_records": self.total_records,
            "average_accuracy": self.average_accuracy.value,
            "min_accuracy": self.min_accuracy.value,
            "max_accuracy": self.max_accuracy.value
        }


class SummaryLLMJudge(BaseModel):
    """Summary LLM judge scores across all evaluated records."""
    model_config = {"frozen": True}
    
    total_records: int = Field(..., ge=0, description="Total number of records")
    average_score: Score = Field(..., description="Average LLM judge score")
    min_score: Score = Field(..., description="Minimum LLM judge score")
    max_score: Score = Field(..., description="Maximum LLM judge score")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_records": self.total_records,
            "average_score": self.average_score.value,
            "min_score": self.min_score.value,
            "max_score": self.max_score.value
        }


class SummaryLatency(BaseModel):
    """Summary latency across all evaluated records."""
    model_config = {"frozen": True}
    
    total_records: int = Field(..., ge=0, description="Total number of records")
    average_latency: LatencyScore = Field(..., description="Average latency")
    min_latency: LatencyScore = Field(..., description="Minimum latency")
    max_latency: LatencyScore = Field(..., description="Maximum latency")
    p95_latency: LatencyScore = Field(..., description="95th percentile latency")
    p99_latency: LatencyScore = Field(..., description="99th percentile latency")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_records": self.total_records,
            "average_latency_ms": self.average_latency.value_ms,
            "min_latency_ms": self.min_latency.value_ms,
            "max_latency_ms": self.max_latency.value_ms,
            "p95_latency_ms": self.p95_latency.value_ms,
            "p99_latency_ms": self.p99_latency.value_ms
        }

