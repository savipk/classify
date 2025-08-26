import json
from typing import Mapping, Any, Optional, Sequence
from mapper_api.application.use_cases.map_control_to_themes import map_control_to_themes
from mapper_api.application.use_cases.map_control_to_5ws import map_control_to_5ws
from mapper_api.domain.repositories.definitions import DefinitionsRepository, ThemeRow


class FakeRepo(DefinitionsRepository):
    def get_theme_rows(self) -> Sequence[ThemeRow]:
        return [
            ThemeRow(cluster_id=1, cluster='A', taxonomy_id=1, taxonomy='NFR1', taxonomy_description='d',
                     risk_theme_id=10, risk_theme='Theme A', risk_theme_description='d', mapping_considerations='m'),
            ThemeRow(cluster_id=2, cluster='B', taxonomy_id=2, taxonomy='NFR2', taxonomy_description='d',
                     risk_theme_id=20, risk_theme='Theme B', risk_theme_description='d', mapping_considerations='m'),
            ThemeRow(cluster_id=3, cluster='C', taxonomy_id=3, taxonomy='NFR3', taxonomy_description='d',
                     risk_theme_id=30, risk_theme='Theme C', risk_theme_description='d', mapping_considerations='m'),
        ]

    def get_fivews_rows(self):
        return [
            {"name": "who", "description": ""},
            {"name": "what", "description": ""},
            {"name": "when", "description": ""},
            {"name": "where", "description": ""},
            {"name": "why", "description": ""},
        ]


class FakeLLM:
    def json_schema_chat(self, *, system: str, user: str, schema_name: str, schema: Mapping[str, Any], max_tokens: int, temperature: float = 0.1, context: Optional[dict] = None, deployment: Optional[str] = None) -> str:
        if 'taxonomy' in schema.get('properties', {}):
            return json.dumps({
                'taxonomy': [
                    {'name': 'Theme C', 'id': 30, 'score': 0.33, 'reasoning': 'r'},
                    {'name': 'Theme A', 'id': 10, 'score': 0.87, 'reasoning': 'r'},
                    {'name': 'Theme B', 'id': 20, 'score': 0.44, 'reasoning': 'r'},
                ]
            })
        else:
            return json.dumps({
                'fivews': [
                    {'name': 'who', 'status': 'present', 'reasoning': 'r'},
                    {'name': 'what', 'status': 'present', 'reasoning': 'r'},
                    {'name': 'when', 'status': 'missing', 'reasoning': 'r'},
                    {'name': 'where', 'status': 'present', 'reasoning': 'r'},
                    {'name': 'why', 'status': 'present', 'reasoning': 'r'},
                ]
            })


def test_map_control_to_themes_sorts_and_limits():
    out = map_control_to_themes(
        record_id='r1', control_description='text', repo=FakeRepo(), llm=FakeLLM(), deployment='d'
    )
    assert isinstance(out, list)
    assert len(out) == 3
    scores = [i['score'] for i in out]
    assert scores == sorted(scores, reverse=True)


def test_map_control_to_5ws_order_and_alias():
    out = map_control_to_5ws(
        record_id='r2', control_description='text', repo=FakeRepo(), llm=FakeLLM(), deployment='d'
    )
    assert isinstance(out, list)
    assert [item['name'] for item in out] == ['who', 'what', 'when', 'where', 'why']
