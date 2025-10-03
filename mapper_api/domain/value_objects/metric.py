"""Value objects for evaluation metrics."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any


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


@dataclass(frozen=True, slots=True)
class RecallScore:
    """Value object for recall score with validation."""
    value: float
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Recall score must be between 0.0 and 1.0, got {self.value}")


@dataclass(frozen=True, slots=True)
class IndividualRecall:
    """Recall score for a single control/record."""
    control_id: str
    recall: RecallScore
    details: Dict[str, Any]  # Additional details specific to the metric
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "control_id": self.control_id,
            "recall": self.recall.value,
            "details": self.details
        }


@dataclass(frozen=True, slots=True)
class SummaryRecall:
    """Summary recall across all evaluated records."""
    total_records: int
    average_recall: RecallScore
    min_recall: RecallScore
    max_recall: RecallScore
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_records": self.total_records,
            "average_recall": self.average_recall.value,
            "min_recall": self.min_recall.value,
            "max_recall": self.max_recall.value
        }


@dataclass(frozen=True, slots=True)
class AccuracyScore:
    """Value object for accuracy score with validation."""
    value: float
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Accuracy score must be between 0.0 and 1.0, got {self.value}")


@dataclass(frozen=True, slots=True)
class IndividualAccuracy:
    """Accuracy score for a single control/record."""
    control_id: str
    accuracy: AccuracyScore
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "control_id": self.control_id,
            "accuracy": self.accuracy.value,
            "details": self.details
        }


@dataclass(frozen=True, slots=True)
class SummaryAccuracy:
    """Summary accuracy across all evaluated records."""
    total_records: int
    average_accuracy: AccuracyScore
    min_accuracy: AccuracyScore
    max_accuracy: AccuracyScore
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_records": self.total_records,
            "average_accuracy": self.average_accuracy.value,
            "min_accuracy": self.min_accuracy.value,
            "max_accuracy": self.max_accuracy.value
        }


@dataclass(frozen=True, slots=True)
class LLMJudgeScore:
    """Value object for LLM judge score with validation."""
    value: float
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"LLM judge score must be between 0.0 and 1.0, got {self.value}")


@dataclass(frozen=True, slots=True)
class IndividualLLMJudge:
    """LLM judge score for a single control/record."""
    control_id: str
    llm_judge_score: LLMJudgeScore
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "control_id": self.control_id,
            "llm_judge_score": self.llm_judge_score.value,
            "details": self.details
        }


@dataclass(frozen=True, slots=True)
class SummaryLLMJudge:
    """Summary LLM judge scores across all evaluated records."""
    total_records: int
    average_score: LLMJudgeScore
    min_score: LLMJudgeScore
    max_score: LLMJudgeScore
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_records": self.total_records,
            "average_score": self.average_score.value,
            "min_score": self.min_score.value,
            "max_score": self.max_score.value
        }


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class UnmatchedTheme:
    """Details for an unmatched risk theme."""
    name: str
    confidence_score: float
    confidence_level: str
    needs_attention: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "confidence_score": self.confidence_score,
            "confidence_level": self.confidence_level,
            "needs_attention": self.needs_attention
        }


@dataclass(frozen=True, slots=True)
class IndividualUnmatchedAnalysis:
    """Unmatched analysis for a single control/record."""
    control_id: str
    control_description: str
    ground_truth_themes: List[str]
    ai_predicted_themes: List[str]
    only_in_gt: List[UnmatchedTheme]
    only_in_ai: List[UnmatchedTheme]
    
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


@dataclass(frozen=True, slots=True)
class LatencyScore:
    """Value object for latency in milliseconds."""
    value_ms: float
    
    def __post_init__(self) -> None:
        if self.value_ms < 0:
            raise ValueError(f"Latency must be non-negative, got {self.value_ms}")


@dataclass(frozen=True, slots=True)
class IndividualLatency:
    """Latency measurement for a single control/record."""
    control_id: str
    latency: LatencyScore
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "control_id": self.control_id,
            "latency_ms": self.latency.value_ms,
            "details": self.details
        }


@dataclass(frozen=True, slots=True)
class SummaryLatency:
    """Summary latency across all evaluated records."""
    total_records: int
    average_latency: LatencyScore
    min_latency: LatencyScore
    max_latency: LatencyScore
    p95_latency: LatencyScore
    p99_latency: LatencyScore
    
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
