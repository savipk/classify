"""Assemblers to convert domain outputs to response DTO dicts."""
from __future__ import annotations
from typing import Iterable, List, Dict
from mapper_api.domain.value_objects.score import ThemeClassification


def assemble_taxonomy_items(classifications: Iterable[ThemeClassification]) -> List[Dict]:
    return [
        {
            "name": c.name,
            "id": c.id,
            "score": float(c.score.value),
            "reasoning": c.reasoning,
        }
        for c in classifications
    ]
