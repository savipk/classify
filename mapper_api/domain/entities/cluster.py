"""Domain entity for Cluster. Framework-free.

Top level in the hierarchy: Cluster -> Taxonomy -> RiskTheme
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cluster:
    """Top-level cluster grouping taxonomies and risk themes."""
    id: int
    name: str

    def __post_init__(self):


        """Validate cluster data on creation."""
        if self.id <= 0:
            raise ValueError("Cluster ID must be positive")
        if not self.name or not self.name.strip():
            raise ValueError("Cluster name cannot be empty")