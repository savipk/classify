"""Local file-based definitions repository for development and testing."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Sequence, Dict, Any, List
from mapper_api.domain.repositories.definitions import DefinitionsRepository
from mapper_api.domain.entities.cluster import Cluster
from mapper_api.domain.entities.taxonomy import Taxonomy
from mapper_api.domain.entities.risk_theme import RiskTheme


class MockDefinitionsRepository(DefinitionsRepository):
    def __init__(self) -> None:
        self._fivews = self._load_fivews()
        # Load raw theme data and convert to domain entities
        raw_themes = self._load_raw_themes()
        self._domain_hierarchy = self._build_domain_hierarchy(raw_themes)

    def _load_raw_themes(self):
        """Load raw theme data from mock files."""
        from mapper_api.domain.repositories.definitions import ThemeRow  # Import only for internal use
        
        current_dir = Path(__file__).parent
        taxonomy_file = current_dir / "data" / "taxonomy.json"
        
        with open(taxonomy_file, "r") as f:
            rows = json.load(f)
        
        result = []
        for r in rows:
            result.append(
                ThemeRow(
                    cluster_id=int(r["cluster_id"]),
                    cluster=r["cluster"],
                    taxonomy_id=int(r["taxonomy_id"]),
                    taxonomy=r["nfr_taxonomy"],
                    taxonomy_description=r["taxonomy_description"],
                    risk_theme_id=int(r["risk_theme_id"]),
                    risk_theme=r["risk_theme"],
                    risk_theme_description=r["risk_theme_description"],
                    mapping_considerations=r["mapping_considerations"],
                )
            )
        return result

    def _build_domain_hierarchy(self, theme_rows) -> Dict[str, List]:
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

    def _load_fivews(self) -> Sequence[Dict[str, Any]]:
        current_dir = Path(__file__).parent
        fivews_file = current_dir / "data" / "5ws.json"
        
        with open(fivews_file, "r") as f:
            obj = json.load(f)
        
        order = ["who", "what", "when", "where", "why"]
        return [{"name": k, "description": obj[k]} for k in order if k in obj]

    def get_fivews_rows(self) -> Sequence[Dict[str, Any]]:
        return self._fivews

    # Domain-oriented methods
    def get_clusters(self) -> List[Cluster]:
        """Return all clusters as domain entities."""
        return self._domain_hierarchy["clusters"]

    def get_taxonomies(self) -> List[Taxonomy]:
        """Return all taxonomies as domain entities."""
        return self._domain_hierarchy["taxonomies"]

    def get_risk_themes(self) -> List[RiskTheme]:
        """Return all risk themes as domain entities."""
        return self._domain_hierarchy["risk_themes"]
