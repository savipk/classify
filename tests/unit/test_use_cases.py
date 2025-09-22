import json
import pytest
from typing import Mapping, Any, Optional, Sequence
from mapper_api.application.use_cases.map_control_to_themes import ClassifyControlToThemes
from mapper_api.application.use_cases.map_control_to_5ws import ClassifyControlTo5Ws
from mapper_api.application.dto.use_case_requests import TaxonomyMappingRequest, FiveWsMappingRequest
from mapper_api.domain.repositories.definitions import DefinitionsRepository, ThemeRow
from mapper_api.domain.errors import ControlValidationError, DefinitionsUnavailableError


class FakeRepo(DefinitionsRepository):
    def __init__(self):
        from mapper_api.domain.services.taxonomy_service import TaxonomyService
        self._service = TaxonomyService()
        theme_rows = self.get_theme_rows()
        self._hierarchy = self._service.build_domain_hierarchy(theme_rows)
    
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
            {"name": "who", "description": "who desc"},
            {"name": "what", "description": "what desc"},
            {"name": "when", "description": "when desc"},
            {"name": "where", "description": "where desc"},
            {"name": "why", "description": "why desc"},
        ]
    
    # Domain-oriented methods
    def get_clusters(self):
        return self._hierarchy["clusters"]
    
    def get_taxonomies(self):
        return self._hierarchy["taxonomies"]
        
    def get_risk_themes(self):
        return self._hierarchy["risk_themes"]


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


def test_map_control_to_5ws():
    request = FiveWsMappingRequest(
        record_id='r2', 
        control_description='text', 
        deployment='d'
    )
    use_case = ClassifyControlTo5Ws(repo=FakeRepo(), llm=FakeLLM())
    out = use_case.execute(request)
    assert isinstance(out, list)
    assert [item['name'] for item in out] == ['who', 'what', 'when', 'where', 'why']
    assert len(out) == 5  # 5Ws should have 5 items, not 3
    # Check that all items have the expected fields for 5Ws
    for item in out:
        assert 'name' in item
        assert 'status' in item
        assert 'reasoning' in item


# Additional edge case tests for themes mapping
class TestMapControlToThemesEdgeCases:
    """Test edge cases and error handling for themes mapping."""
    
    def test_empty_control_description_raises_validation_error(self):
        with pytest.raises(ValueError, match="control description must not be empty"):
            request = TaxonomyMappingRequest(
                record_id='r1', 
                control_description='', 
                deployment='d'
            )
            use_case = ClassifyControlToThemes.from_defs(FakeRepo(), FakeLLM())
            use_case.execute(request)
    
    def test_whitespace_only_control_description_raises_validation_error(self):
        with pytest.raises(ValueError, match="control description must not be empty"):
            request = TaxonomyMappingRequest(
                record_id='r1', 
                control_description='   \t\n  ', 
                deployment='d'
            )
            use_case = ClassifyControlToThemes.from_defs(FakeRepo(), FakeLLM())
            use_case.execute(request)
    
    def test_empty_theme_rows_raises_definitions_not_loaded(self):
        class EmptyRepo(DefinitionsRepository):
            def get_theme_rows(self):
                return []
            def get_fivews_rows(self):
                return []
        
        with pytest.raises(DefinitionsUnavailableError, match="taxonomy definitions not loaded"):
            request = TaxonomyMappingRequest(
                record_id='r1',
                control_description='valid text',
                deployment='d'
            )
            use_case = ClassifyControlToThemes.from_defs(EmptyRepo(), FakeLLM())
            use_case.execute(request)
    
    def test_llm_invalid_json_raises_validation_error(self):
        class BadLLM:
            def json_schema_chat(self, **kwargs):
                return "invalid json"
        
        with pytest.raises(ControlValidationError, match="LLM output validation failed"):
            request = TaxonomyMappingRequest(
                record_id='r1',
                control_description='valid text',
                deployment='d'
            )
            use_case = ClassifyControlToThemes.from_defs(FakeRepo(), BadLLM())
            use_case.execute(request)
    
    def test_long_control_description_handled(self):
        long_text = "A" * 5000  # Very long control description
        request = TaxonomyMappingRequest(
            record_id='r1',
            control_description=long_text,
            deployment='d'
        )
        use_case = ClassifyControlToThemes.from_defs(FakeRepo(), FakeLLM())
        result = use_case.execute(request)
        assert isinstance(result, list)
        assert len(result) == 3  # Should still limit to top 3


# Additional edge case tests for 5Ws mapping
class TestMapControlToFiveWsEdgeCases:
    """Test edge cases and error handling for 5Ws mapping."""
    
    def test_empty_control_description_raises_validation_error(self):
        with pytest.raises(ValueError, match="control description must not be empty"):
            request = FiveWsMappingRequest(
                record_id='r1', 
                control_description='', 
                deployment='d'
            )
            use_case = ClassifyControlTo5Ws(repo=FakeRepo(), llm=FakeLLM())
            use_case.execute(request)
    
    def test_whitespace_only_control_description_raises_validation_error(self):
        with pytest.raises(ValueError, match="control description must not be empty"):
            request = FiveWsMappingRequest(
                record_id='r1', 
                control_description='   \t\n  ', 
                deployment='d'
            )
            use_case = ClassifyControlTo5Ws(repo=FakeRepo(), llm=FakeLLM())
            use_case.execute(request)
    
    def test_empty_fivews_definitions_raises_error(self):
        class EmptyRepo(DefinitionsRepository):
            def get_theme_rows(self):
                return []
            def get_fivews_rows(self):
                return []
        
        with pytest.raises(DefinitionsUnavailableError, match="5Ws definitions not loaded"):
            request = FiveWsMappingRequest(
                record_id='r1',
                control_description='valid text',
                deployment='d'
            )
            use_case = ClassifyControlTo5Ws(repo=EmptyRepo(), llm=FakeLLM())
            use_case.execute(request)
    
    def test_llm_invalid_json_raises_validation_error(self):
        class BadLLM:
            def json_schema_chat(self, **kwargs):
                return "invalid json"
        
        with pytest.raises(ControlValidationError, match="LLM output validation failed"):
            request = FiveWsMappingRequest(
                record_id='r1',
                control_description='valid text',
                deployment='d'
            )
            use_case = ClassifyControlTo5Ws(repo=FakeRepo(), llm=BadLLM())
            use_case.execute(request)
    
    def test_llm_missing_fivews_field_raises_validation_error(self):
        class BadLLM:
            def json_schema_chat(self, **kwargs):
                return json.dumps({"wrong_field": []})
        
        with pytest.raises(ControlValidationError, match="LLM output validation failed"):
            request = FiveWsMappingRequest(
                record_id='r1',
                control_description='valid text',
                deployment='d'
            )
            use_case = ClassifyControlTo5Ws(repo=FakeRepo(), llm=BadLLM())
            use_case.execute(request)
    
    def test_ordering_maintained_despite_llm_disorder(self):
        class DisorderedLLM:
            def json_schema_chat(self, **kwargs):
                # Return 5Ws in wrong order
                return json.dumps({
                    'fivews': [
                        {'name': 'why', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'where', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'who', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'when', 'status': 'missing', 'reasoning': 'r'},
                        {'name': 'what', 'status': 'present', 'reasoning': 'r'},
                    ]
                })
        
        request = FiveWsMappingRequest(
            record_id='r1',
            control_description='valid text',
            deployment='d'
        )
        use_case = ClassifyControlTo5Ws(repo=FakeRepo(), llm=DisorderedLLM())
        result = use_case.execute(request)
        
        # Should be reordered correctly
        names = [item['name'] for item in result]
        assert names == ['who', 'what', 'when', 'where', 'why']
    
    def test_context_trace_id_passed_to_llm(self):
        class TraceLLM:
            def __init__(self):
                self.last_context = None
            
            def json_schema_chat(self, **kwargs):
                self.last_context = kwargs.get('context')
                return json.dumps({
                    'fivews': [
                        {'name': 'who', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'what', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'when', 'status': 'missing', 'reasoning': 'r'},
                        {'name': 'where', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'why', 'status': 'present', 'reasoning': 'r'},
                    ]
                })
        
        trace_llm = TraceLLM()
        request = FiveWsMappingRequest(
            record_id='test-trace-123',
            control_description='valid text',
            deployment='d'
        )
        use_case = ClassifyControlTo5Ws(repo=FakeRepo(), llm=trace_llm)
        use_case.execute(request)
        
        assert trace_llm.last_context == {"trace_id": "test-trace-123"}


# Tests for the use case classes directly
class TestClassifyControlToThemesClass:
    """Test ClassifyControlToThemes class directly."""
    
    def test_from_defs_creates_instance(self):
        use_case = ClassifyControlToThemes.from_defs(FakeRepo(), FakeLLM())
        assert isinstance(use_case, ClassifyControlToThemes)
        assert use_case.repo is not None
        assert use_case.llm is not None
    
    def test_from_defs_with_empty_repo_raises_error(self):
        class EmptyRepo(DefinitionsRepository):
            def get_theme_rows(self):
                return []
            def get_fivews_rows(self):
                return []
        
        with pytest.raises(DefinitionsUnavailableError):
            ClassifyControlToThemes.from_defs(EmptyRepo(), FakeLLM())


class TestClassifyControlToFiveWsClass:
    """Test ClassifyControlToFiveWs class directly."""
    
    def test_run_method_direct_call(self):
        use_case = ClassifyControlTo5Ws(repo=FakeRepo(), llm=FakeLLM())
        from mapper_api.application.dto.use_case_requests import FiveWsMappingRequest
        request = FiveWsMappingRequest(
            record_id='direct-test',
            control_description='test control',
            deployment='test-deployment'
        )
        result = use_case.execute(request)
        assert isinstance(result, list)
        assert len(result) == 5
        assert [item['name'] for item in result] == ['who', 'what', 'when', 'where', 'why']
