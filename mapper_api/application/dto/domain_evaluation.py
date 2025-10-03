"""Request DTOs for evaluation operations."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List
from mapper_api.domain.value_objects.metric import MetricType


@dataclass(frozen=True, slots=True)
class EvaluationRequest:
    """Use case request for evaluation operations."""
    record_id: str
    metric_types: List[MetricType]
    n_records: int = None  # For latency testing - number of records to test
