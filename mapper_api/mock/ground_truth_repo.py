"""Mock GroundTruthRepository that reads local JSON files from mock/data."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Sequence
from mapper_api.domain.repositories.ground_truth import (
    GroundTruthRepository,
    FiveWGroundTruthRecord,
    FiveWGroundTruth,
    RiskThemeGroundTruthRecord,
    RiskThemeGroundTruth,
)


class LocalFileGroundTruthRepository(GroundTruthRepository):
    """Mock implementation that reads ground truth from local JSON files."""
    
    def __init__(self, base_dir: str | Path = None) -> None:
        self._base = Path(base_dir) if base_dir else Path(__file__).parent / 'data'
        self._fivews_gt = self._load_fivews_ground_truth()
        self._risk_themes_gt = self._load_risk_themes_ground_truth()

    def _load_fivews_ground_truth(self) -> Sequence[FiveWGroundTruthRecord]:
        """Load 5Ws ground truth from gt_5ws.json."""
        data = json.loads((self._base / 'gt_5ws.json').read_text())
        
        result: list[FiveWGroundTruthRecord] = []
        for record in data:
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
        data = json.loads((self._base / 'gt_risk_themes.json').read_text())
        
        result: list[RiskThemeGroundTruthRecord] = []
        for record in data:
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
        return self._fivews_gt

    def get_risk_themes_ground_truth(self) -> Sequence[RiskThemeGroundTruthRecord]:
        """Return risk themes ground truth records."""
        return self._risk_themes_gt
