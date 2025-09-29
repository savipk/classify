"""Repository protocol for loading taxonomy and 5Ws definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence, Dict, Any, List

from mapper_api.domain.entities.cluster import Cluster
from mapper_api.domain.entities.taxonomy import Taxonomy
from mapper_api.domain.entities.risk_theme import RiskTheme


@dataclass(frozen=True, slots=True)
class ThemeRow:
    """Raw data row from external storage - used internally for building domain entities."""
    cluster_id: int
    cluster: str
    taxonomy_id: int
    taxonomy: str
    taxonomy_description: str
    risk_theme_id: int
    risk_theme: str
    risk_theme_description: str
    mapping_considerations: str


class DefinitionsRepository(Protocol):
    """Repository for accessing taxonomy definitions and converting to domain entities."""

    def get_fivews_rows(self) -> Sequence[Dict[str, Any]]:
        """Return sequence of dict rows for 5Ws definitions with keys: name, description."""
        ...
    
    # Domain-oriented methods - the clean public interface
    def get_clusters(self) -> List[Cluster]:
        """Return all clusters as domain entities."""
        ...
    
    def get_taxonomies(self) -> List[Taxonomy]:
        """Return all taxonomies as domain entities."""
        ...
    
    def get_risk_themes(self) -> List[RiskTheme]:
        """Return all risk themes as domain entities."""
        ...
