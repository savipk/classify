"""Domain value objects for classification results."""

from dataclasses import dataclass
from typing import Dict, Any
from mapper_api.domain.value_objects.score import Score


@dataclass(frozen=True, slots=True)
class ThemeClassification:
    """Value object holding classification metadata for a RiskTheme."""
    name: str
    id: int
    score: Score
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "name": self.name,
            "id": self.id,
            "score": float(self.score.value),
            "reasoning": self.reasoning,
        }
