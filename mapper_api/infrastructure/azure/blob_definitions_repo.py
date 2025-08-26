"""Azure Blob adapter to load taxonomy.json and 5ws.json once at startup."""
from __future__ import annotations
import json
from typing import Sequence, Dict, Any, Optional
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from mapper_api.domain.repositories.definitions import DefinitionsRepository, ThemeRow


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
        self._themes: Optional[Sequence[ThemeRow]] = None
        self._fivews: Optional[Sequence[Dict[str, Any]]] = None
        self._load()

    def _load(self) -> None:
        self._themes = self._load_themes()
        self._fivews = self._load_fivews()

    def _load_themes(self) -> Sequence[ThemeRow]:
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

    def get_theme_rows(self) -> Sequence[ThemeRow]:
        return self._themes or []

    def get_fivews_rows(self) -> Sequence[Dict[str, Any]]:
        return self._fivews or []
