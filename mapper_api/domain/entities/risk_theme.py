"""Domain entity representing a Risk Theme with taxonomy metadata. Framework-free.

Implements: RiskTheme(id: int, name: str, description: str, taxonomy_id: int, taxonomy: str, cluster: str, cluster_id: int, mapping_considerations: str)
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RiskTheme:
    """Risk Theme with complete taxonomy metadata for prompt building."""
    id: int
    name: str
    description: str
    taxonomy_id: int
    taxonomy: str
    taxonomy_description: str
    cluster: str
    cluster_id: int
    mapping_considerations: str

    def __post_init__(self):
        """Validate risk theme data on creation."""
        if self.id <= 0:
            raise ValueError("RiskTheme ID must be positive")
        if self.taxonomy_id <= 0:
            raise ValueError("Taxonomy ID must be positive")
        if self.cluster_id <= 0:
            raise ValueError("Cluster ID must be positive")
        if not self.name or not self.name.strip():
            raise ValueError("RiskTheme name cannot be empty")
        if not self.taxonomy or not self.taxonomy.strip():
            raise ValueError("Taxonomy name cannot be empty")
        if not self.cluster or not self.cluster.strip():
            raise ValueError("Cluster name cannot be empty")

    def belongs_to_taxonomy(self, taxonomy_id: int) -> bool:
        """Check if this risk theme belongs to the specified taxonomy."""
        return self.taxonomy_id == taxonomy_id

    def belongs_to_cluster(self, cluster_id: int) -> bool:
        """Check if this risk theme belongs to the specified cluster."""
        return self.cluster_id == cluster_id
