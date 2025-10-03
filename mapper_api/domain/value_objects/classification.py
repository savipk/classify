"""Domain value objects for classification results using Pydantic V2."""

from pydantic import BaseModel, Field
from typing import Dict, Any
from mapper_api.domain.value_objects.score import Score


class ThemeClassification(BaseModel):
    """Value object holding classification metadata for a RiskTheme."""
    model_config = {"frozen": True}
    
    name: str = Field(..., description="Risk theme name")
    id: int = Field(..., description="Risk theme ID")
    score: Score = Field(..., description="Classification score")
    reasoning: str = Field(..., description="Classification reasoning")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "name": self.name,
            "id": self.id,
            "score": float(self.score.value),
            "reasoning": self.reasoning,
        }
