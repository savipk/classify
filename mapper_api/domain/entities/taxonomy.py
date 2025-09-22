"""Domain entity representing a Taxonomy. Framework-free.

Represents the middle layer in the hierarchy: Cluster -> Taxonomy -> RiskTheme
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Taxonomy:
    """Taxonomy category belonging to a Cluster."""
    id: int
    name: str
    description: str
    cluster_id: int

    def __post_init__(self):
        """Validate taxonomy data on creation."""
        if self.id <= 0:
            raise ValueError("Taxonomy ID must be positive")
        if self.cluster_id <= 0:
            raise ValueError("Cluster ID must be positive")
        if not self.name or not self.name.strip():
            raise ValueError("Taxonomy name cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("Taxonomy description cannot be empty")

    def belongs_to_cluster(self, cluster_id: int) -> bool:
        """Check if this taxonomy belongs to the specified cluster."""
        return self.cluster_id == cluster_id

