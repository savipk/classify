"""Test use cases with mocks."""
import json
from typing import Sequence, Dict, Any, List
import pytest
from mapper_api.domain.repositories.definitions import DefinitionsRepository
from mapper_api.domain.entities.cluster import Cluster
from mapper_api.domain.entities.taxonomy import Taxonomy
from mapper_api.domain.entities.risk_theme import RiskTheme
from mapper_api.application.ports.llm import LLMClient
from mapper_api.application.use_cases.map_control_to_themes import ClassifyControlToThemes
from mapper_api.application.use_cases.map_control_to_5ws import ClassifyControlTo5Ws
from mapper_api.application.dto.domain_mapping import TaxonomyMappingRequest, FiveWsMappingRequest


class FakeRepo(DefinitionsRepository):
    def __init__(self):
        from mapper_api.domain.services.taxonomy_service import TaxonomyService
        from mapper_api.domain.repositories.definitions import ThemeRow
        
        # Create raw theme data internally
        theme_rows = [
            ThemeRow(cluster_id=1, cluster='A', taxonomy_id=1, taxonomy='NFR1', taxonomy_description='d',
                     risk_theme_id=10, risk_theme='Theme A', risk_theme_description='d', mapping_considerations='m'),
            ThemeRow(cluster_id=2, cluster='B', taxonomy_id=2, taxonomy='NFR2', taxonomy_description='d',
                     risk_theme_id=20, risk_theme='Theme B', risk_theme_description='d', mapping_considerations='m'),
            ThemeRow(cluster_id=3, cluster='C', taxonomy_id=3, taxonomy='NFR3', taxonomy_description='d',
                     risk_theme_id=30, risk_theme='Theme C', risk_theme_description='d', mapping_considerations='m'),
        ]
        
        self._service = TaxonomyService()
        self._hierarchy = self._service.build_domain_hierarchy(theme_rows)

    def get_fivews_rows(self):
        return [
            {"name": "who", "description": "Who is responsible?"},
            {"name": "what", "description": "What is being done?"},
            {"name": "when", "description": "When is it done?"},
            {"name": "where", "description": "Where is it done?"},
            {"name": "why", "description": "Why is it done?"},
        ]

    def get_clusters(self):
        return self._hierarchy["clusters"]

    def get_taxonomies(self):
        return self._hierarchy["taxonomies"]

    def get_risk_themes(self):
        return self._hierarchy["risk_themes"]


class FakeLLM(LLMClient):
    def json_schema_chat(self, *, system: str, user: str, schema: dict, **kwargs) -> str:
        response_dict = {
            "taxonomy": [
                {"name": "Theme A", "id": 10, "score": 0.9, "reasoning": "test"},
                {"name": "Theme B", "id": 20, "score": 0.8, "reasoning": "test"},
                {"name": "Theme C", "id": 30, "score": 0.7, "reasoning": "test"},
            ]
        }
        return json.dumps(response_dict)


class Fake5WsLLM(LLMClient):
    def json_schema_chat(self, *, system: str, user: str, schema: dict, **kwargs) -> str:
        response_dict = {
            "fivews": [
                {"name": "who", "status": "present", "reasoning": "test"},
                {"name": "what", "status": "present", "reasoning": "test"},
                {"name": "when", "status": "missing", "reasoning": "test"},
                {"name": "where", "status": "present", "reasoning": "test"},
                {"name": "why", "status": "missing", "reasoning": "test"},
            ]
        }
        return json.dumps(response_dict)


def test_classify_control_to_themes():
    repo = FakeRepo()
    llm = FakeLLM()
    use_case = ClassifyControlToThemes.from_defs(repo, llm)
    
    request = TaxonomyMappingRequest(
        record_id="test-123",
        control_description="This is a test control description that is long enough to pass validation and is written in English."
    )
    
    result = use_case.execute(request)
    
    assert len(result) == 3
    assert result[0]["name"] == "Theme A"
    assert result[0]["score"] == 0.9


def test_classify_control_to_5ws():
    repo = FakeRepo()
    llm = Fake5WsLLM()
    use_case = ClassifyControlTo5Ws.from_defs(repo, llm)
    
    request = FiveWsMappingRequest(
        record_id="test-123",
        control_description="This is a test control description that is long enough to pass validation and is written in English."
    )
    
    result = use_case.execute(request)
    
    assert len(result) == 5
    assert result[0]["name"] == "who"
    assert result[0]["status"] == "present"


def test_control_validation_empty():
    repo = FakeRepo()
    llm = FakeLLM()
    use_case = ClassifyControlToThemes.from_defs(repo, llm)
    
    request = TaxonomyMappingRequest(
        record_id="test-123",
        control_description=""
    )
    
    with pytest.raises(ValueError, match="control description must not be empty"):
        use_case.execute(request)


def test_control_validation_too_short():
    repo = FakeRepo()
    llm = FakeLLM()
    use_case = ClassifyControlToThemes.from_defs(repo, llm)
    
    request = TaxonomyMappingRequest(
        record_id="test-123",
        control_description="Short"
    )
    
    with pytest.raises(ValueError, match="control description must be at least 50 characters long"):
        use_case.execute(request)


def test_control_validation_non_english():
    repo = FakeRepo()
    llm = FakeLLM()
    use_case = ClassifyControlToThemes.from_defs(repo, llm)
    
    request = TaxonomyMappingRequest(
        record_id="test-123",
        control_description="Este es un texto en español que es lo suficientemente largo para pasar la validación de longitud mínima pero no está en inglés."
    )
    
    with pytest.raises(ValueError, match="control description must be in English"):
        use_case.execute(request)


def test_score_thresholding():
    """Test that only themes above the score threshold are returned."""
    
    class LowScoreLLM(LLMClient):
        def json_schema_chat(self, *, system: str, user: str, schema: dict, **kwargs) -> str:
            response_dict = {
                "taxonomy": [
                    {"name": "Theme A", "id": 10, "score": 0.9, "reasoning": "high score"},
                    {"name": "Theme B", "id": 20, "score": 0.1, "reasoning": "low score"},
                    {"name": "Theme C", "id": 30, "score": 0.05, "reasoning": "very low score"},
                ]
            }
            return json.dumps(response_dict)
    
    repo = FakeRepo()
    llm = LowScoreLLM()
    use_case = ClassifyControlToThemes.from_defs(repo, llm)
    
    request = TaxonomyMappingRequest(
        record_id="test-123",
        control_description="This is a test control description that is long enough to pass validation and is written in English."
    )
    
    result = use_case.execute(request)
    
    # Only Theme A should be returned (score 0.9 > 0.2 threshold)
    assert len(result) == 1
    assert result[0]["name"] == "Theme A"
    assert result[0]["score"] == 0.9
