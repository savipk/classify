"""Domain entity representing a Taxonomy. Framework-free.

Represents the middle layer in the hierarchy: Cluster -> Taxonomy -> RiskTheme
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Taxonomy:
    """Taxonomy category belonging to a Cluster"""
    id: int
    name: str
    description: str
    cluster_id: int


