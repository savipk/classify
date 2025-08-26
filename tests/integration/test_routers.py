import json
from typing import Mapping, Any, Optional, Sequence
from fastapi.testclient import TestClient
from mapper_api.interface.http.api import create_app
from mapper_api.interface.http.state import get_container
from mapper_api.interface.di.container import Container
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


def test_routers_with_override():
    app = create_app()

    def override_container():
        return Container(
            settings=type('S', (), {'AZURE_OPENAI_DEPLOYMENT': 'd'})(),
            definitions_repo=FakeRepo(),
            llm_client=FakeLLM(),
            definitions_loaded=True,
        )

    app.dependency_overrides[get_container] = override_container
    c = TestClient(app)

    r = c.post('/taxonomy_mapper', json={
        'header': {'recordId': 'r1'},
        'data': {'controlDescription': 'text'}
    })
    assert r.status_code == 200
    assert len(r.json()['data']['taxonomy']) == 3

    r = c.post('/5ws_mapper', json={
        'header': {'recordId': 'r2'},
        'data': {'controlDescription': 'text'}
    })
    assert r.status_code == 200
    assert list(item['name'] for item in r.json()['data']['5ws']) == ['who', 'what', 'when', 'where', 'why']
