"""Mock definitions repository for testing."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Sequence, Dict, Any, List
from mapper_api.domain.repositories.definitions import DefinitionsRepository
from mapper_api.domain.entities.cluster import Cluster
from mapper_api.domain.entities.taxonomy import Taxonomy
from mapper_api.domain.entities.risk_theme import RiskTheme
from mapper_api.domain.services.taxonomy_service import TaxonomyService


class MockDefinitionsRepository(DefinitionsRepository):
    def __init__(self) -> None:
        self._fivews = self._load_fivews()
        # Load raw theme data and convert to domain entities
        raw_themes = self._load_raw_themes()
        self._taxonomy_service = TaxonomyService()
        self._domain_hierarchy = self._taxonomy_service.build_domain_hierarchy(raw_themes)

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
