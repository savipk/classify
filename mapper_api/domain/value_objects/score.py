"""Consolidated score value object using Pydantic V2."""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any


class Score(BaseModel):
    """Consolidated score value object for all score types (0.0 to 1.0)."""
    model_config = {"frozen": True}
    
    value: float = Field(..., ge=0.0, le=1.0, description="Score value between 0.0 and 1.0")
    
    @field_validator('value')
    @classmethod
    def validate_score_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {v}")
        return v
    
    def __float__(self) -> float:
        """Convert to float for convenience."""
        return self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {"value": self.value}
