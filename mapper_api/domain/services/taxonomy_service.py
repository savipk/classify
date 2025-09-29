"""Simple domain service for converting flat data to domain entities."""
from __future__ import annotations
from typing import Dict, List, Sequence

from mapper_api.domain.entities.cluster import Cluster
from mapper_api.domain.entities.taxonomy import Taxonomy
from mapper_api.domain.entities.risk_theme import RiskTheme
from mapper_api.domain.repositories.definitions import ThemeRow


class TaxonomyService:
    """
    Simple service to convert flat database rows to domain entities.
    
    Keeps it minimal - just the conversion logic we actually need.
    """

    def build_domain_hierarchy(self, theme_rows: Sequence[ThemeRow]) -> Dict[str, List]:
        """Convert flat ThemeRow data into proper domain entities."""
        clusters = {}
        taxonomies = {}
        risk_themes = []

        for row in theme_rows:
            # Build cluster (deduplicated)
            if row.cluster_id not in clusters:
                clusters[row.cluster_id] = Cluster(
                    id=row.cluster_id,
                    name=row.cluster
                )

            # Build taxonomy (deduplicated)
            if row.taxonomy_id not in taxonomies:
                taxonomies[row.taxonomy_id] = Taxonomy(
                    id=row.taxonomy_id,
                    name=row.taxonomy,
                    description=row.taxonomy_description,
                    cluster_id=row.cluster_id
                )

            # Build risk theme (each row = one theme) with all fields
            risk_theme = RiskTheme(
                id=row.risk_theme_id,
                name=row.risk_theme,
                description=row.risk_theme_description,
                taxonomy_id=row.taxonomy_id,
                taxonomy=row.taxonomy,
                taxonomy_description=row.taxonomy_description,
                cluster=row.cluster,
                cluster_id=row.cluster_id,
                mapping_considerations=row.mapping_considerations
            )
            risk_themes.append(risk_theme)

        return {
            "clusters": list(clusters.values()),
            "taxonomies": list(taxonomies.values()),
            "risk_themes": risk_themes
        }
