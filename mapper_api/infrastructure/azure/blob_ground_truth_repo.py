"""Azure Blob adapter to load ground truth JSON files."""
from __future__ import annotations
import json
from typing import Sequence, Optional
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from mapper_api.domain.repositories.ground_truth import (
    GroundTruthRepository,
    FiveWGroundTruthRecord,
    FiveWGroundTruth,
    RiskThemeGroundTruthRecord,
    RiskThemeGroundTruth,
)


class BlobGroundTruthRepository(GroundTruthRepository):
    """Azure Blob implementation for ground truth data repository."""
    
    def __init__(
        self,
        *,
        account_name: str,
        container_name: str,
        tenant_id: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        self._credential = ClientSecretCredential(
            tenant_id=tenant_id, 
            client_id=client_id, 
            client_secret=client_secret
        )
        self._service = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=self._credential,
        )
        self._container = self._service.get_container_client(container_name)
        self._fivews_gt: Optional[Sequence[FiveWGroundTruthRecord]] = None
        self._risk_themes_gt: Optional[Sequence[RiskThemeGroundTruthRecord]] = None
        self._load()

    def _load(self) -> None:
        """Load all ground truth data at initialization."""
        self._fivews_gt = self._load_fivews_ground_truth()
        self._risk_themes_gt = self._load_risk_themes_ground_truth()

    def _load_fivews_ground_truth(self) -> Sequence[FiveWGroundTruthRecord]:
        """Load 5Ws ground truth from gt_5ws.json."""
        blob = self._container.get_blob_client("gt_5ws.json")
        data = blob.download_blob().readall()
        records = json.loads(data)
        
        result: list[FiveWGroundTruthRecord] = []
        for record in records:
            gt_5ws = [
                FiveWGroundTruth(
                    name=gt["name"],
                    status=gt["status"],
                    reasoning=gt["reasoning"]
                )
                for gt in record["gt_5ws"]
            ]
            
            result.append(
                FiveWGroundTruthRecord(
                    control_id=record["control_id"],
                    control_description=record["control_description"],
                    gt_5ws=gt_5ws
                )
            )
        return result

    def _load_risk_themes_ground_truth(self) -> Sequence[RiskThemeGroundTruthRecord]:
        """Load risk themes ground truth from gt_risk_themes.json."""
        blob = self._container.get_blob_client("gt_risk_themes.json")
        data = blob.download_blob().readall()
        records = json.loads(data)
        
        result: list[RiskThemeGroundTruthRecord] = []
        for record in records:
            risk_themes = [
                RiskThemeGroundTruth(
                    name=theme["name"],
                    id=theme["id"],
                    reasoning=theme["reasoning"]
                )
                for theme in record["risk_theme"]
            ]
            
            result.append(
                RiskThemeGroundTruthRecord(
                    control_id=record["control_id"],
                    control_description=record["control_description"],
                    risk_theme=risk_themes
                )
            )
        return result

    def get_fivews_ground_truth(self) -> Sequence[FiveWGroundTruthRecord]:
        """Return 5Ws ground truth records."""
        return self._fivews_gt or []

    def get_risk_themes_ground_truth(self) -> Sequence[RiskThemeGroundTruthRecord]:
        """Return risk themes ground truth records."""
        return self._risk_themes_gt or []
