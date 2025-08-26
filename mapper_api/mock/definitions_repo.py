"""Mock DefinitionsRepository that reads local JSON files from mock/data."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Sequence, Dict, Any
from mapper_api.domain.repositories.definitions import DefinitionsRepository, ThemeRow


class LocalFileDefinitionsRepository(DefinitionsRepository):
    def __init__(self, base_dir: str | Path = None) -> None:
        self._base = Path(base_dir) if base_dir else Path(__file__).parent / 'data'
        self._themes = self._load_themes()
        self._fivews = self._load_fivews()

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
