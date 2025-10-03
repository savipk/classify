from pathlib import Path
import json


class ScoringConfig:
    def __init__(self):
        self._load_config()

    def _load_config(self) -> None:
        config_path = Path(__file__).parent.parent.parent / "params.json"
        try:
            with open(config_path, 'r') as f:
                self.params = json.load(f)
                # print(self.params)
        except Exception as e:
            raise ValueError(f"could not load params.json: {e}")