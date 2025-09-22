"""Mock DefinitionsRepository that reads local JSON files from mock/data."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Sequence, Dict, Any, List
from mapper_api.domain.repositories.definitions import DefinitionsRepository, ThemeRow
from mapper_api.domain.entities.cluster import Cluster
from mapper_api.domain.entities.taxonomy import Taxonomy
from mapper_api.domain.entities.risk_theme import RiskTheme
from mapper_api.domain.services.taxonomy_service import TaxonomyService


class LocalFileDefinitionsRepository(DefinitionsRepository):
    def __init__(self, base_dir: str | Path = None) -> None:
        self._base = Path(base_dir) if base_dir else Path(__file__).parent / 'data'
        self._themes = self._load_themes()
        self._fivews = self._load_fivews()
        self._taxonomy_service = TaxonomyService()
        self._domain_hierarchy = self._taxonomy_service.build_domain_hierarchy(self._themes)

    def _load_themes(self) -> Sequence[ThemeRow]:
        data = json.loads((self._base / 'taxonomy.json').read_text())
        result: list[ThemeRow] = []
        for r in data:
            result.append(ThemeRow(
                cluster_id=int(r['cluster_id']),
                cluster=r['cluster'],
                taxonomy_id=int(r['taxonomy_id']),
                taxonomy=r['nfr_taxonomy'],
                taxonomy_description=r['taxonomy_description'],
                risk_theme_id=int(r['risk_theme_id']),
                risk_theme=r['risk_theme'],
                risk_theme_description=r['risk_theme_description'],
                mapping_considerations=r['mapping_considerations'],
            ))
        return result

    def _load_fivews(self) -> Sequence[Dict[str, Any]]:
        obj = json.loads((self._base / '5ws.json').read_text())
        order = ["who", "what", "when", "where", "why"]
        return [{"name": k, "description": obj[k]} for k in order if k in obj]

    def get_theme_rows(self) -> Sequence[ThemeRow]:
        return self._themes

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
