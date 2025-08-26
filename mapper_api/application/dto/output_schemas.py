"""Pydantic models for strict JSON LLM outputs (dynamic taxonomy, fixed 5Ws)."""
from __future__ import annotations
from typing import Sequence, Literal
from pydantic import BaseModel, Field, ConfigDict


def build_taxonomy_models(allowed_names: Sequence[str]):
    NameLiteral = Literal[tuple(allowed_names)]

    class TaxonomyItem(BaseModel):
        model_config = ConfigDict(extra='forbid')
        
        name: NameLiteral
        id: int
        score: float = Field(ge=0.0, le=1.0)  
        reasoning: str

    class TaxonomyOut(BaseModel):
        model_config = ConfigDict(extra='forbid')
        
        taxonomy: list[TaxonomyItem] = Field(min_length=3, max_length=3)
    
    return TaxonomyItem, TaxonomyOut


class FiveWItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    name: Literal["who", "what", "when", "where", "why"]
    status: Literal["present", "missing"]
    reasoning: str


class FiveWOut(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    fivews: list[FiveWItem] = Field(min_length=5, max_length=5)
