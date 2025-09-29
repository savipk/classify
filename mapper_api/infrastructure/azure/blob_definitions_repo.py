"""Azure Blob adapter to load taxonomy.json and 5ws.json once at startup."""
from __future__ import annotations
import json
from typing import Sequence, Dict, Any, Optional, List
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from mapper_api.domain.repositories.definitions import DefinitionsRepository
from mapper_api.domain.entities.cluster import Cluster
from mapper_api.domain.entities.taxonomy import Taxonomy
from mapper_api.domain.entities.risk_theme import RiskTheme
from mapper_api.domain.services.taxonomy_service import TaxonomyService


class BlobDefinitionsRepository(DefinitionsRepository):
    def __init__(
        self,
        *,
        account_name: str,
        container_name: str,
        tenant_id: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        self._credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        self._service = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=self._credential,
        )
        self._container = self._service.get_container_client(container_name)
        self._fivews: Optional[Sequence[Dict[str, Any]]] = None
        self._taxonomy_service = TaxonomyService()
        self._domain_hierarchy: Optional[Dict[str, List]] = None
        self._load()

    def _load(self) -> None:
        self._fivews = self._load_fivews()
        # Load raw theme data and convert to domain entities
        raw_themes = self._load_raw_themes()
        if raw_themes:
            self._domain_hierarchy = self._taxonomy_service.build_domain_hierarchy(raw_themes)

    def _load_raw_themes(self):
        """Load raw theme data from blob storage."""
        from mapper_api.domain.repositories.definitions import ThemeRow  # Import only for internal use
        
        blob = self._container.get_blob_client("taxonomy.json")
        data = blob.download_blob().readall()
        rows = json.loads(data)
        result: list[ThemeRow] = []
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
        blob = self._container.get_blob_client("5ws.json")
        data = blob.download_blob().readall()
        obj = json.loads(data)
        order = ["who", "what", "when", "where", "why"]
        return [{"name": k, "description": obj[k]} for k in order if k in obj]

    def get_fivews_rows(self) -> Sequence[Dict[str, Any]]:
        return self._fivews or []

    # Domain-oriented methods
    def get_clusters(self) -> List[Cluster]:
        """Return all clusters as domain entities."""
        if not self._domain_hierarchy:
            return []
        return self._domain_hierarchy["clusters"]

    def get_taxonomies(self) -> List[Taxonomy]:
        """Return all taxonomies as domain entities."""
        if not self._domain_hierarchy:
            return []
        return self._domain_hierarchy["taxonomies"]

    def get_risk_themes(self) -> List[RiskTheme]:
        """Return all risk themes as domain entities."""
        if not self._domain_hierarchy:
            return []
        return self._domain_hierarchy["risk_themes"]
