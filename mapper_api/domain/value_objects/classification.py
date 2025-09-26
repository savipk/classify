"""Domain value objects for classification results."""

from dataclasses import dataclass
from mapper_api.domain.value_objects.score import Score


@dataclass(frozen=True, slots=True)
class ThemeClassification:
    """Value object holding classification metadata for a RiskTheme."""
    name: str
    id: int
    score: Score
    reasoning: str
