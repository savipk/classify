"""End-to-end integration tests without external dependencies."""

import pytest
from mapper_api.domain.entities.control import Control
from mapper_api.infrastructure.local.definitions_repo import MockDefinitionsRepository
from mapper_api.infrastructure.local.llm_client import StaticLLMClient
from mapper_api.application.use_cases.map_control_to_themes import ClassifyControlToThemes
from mapper_api.application.use_cases.map_control_to_5ws import ClassifyControlTo5Ws
from mapper_api.interface.controllers.taxonomy_controller import TaxonomyController
from mapper_api.interface.controllers.fivews_controller import FiveWsController
from mapper_api.application.dto.http_common import CommonRequest, CommonHeader, CommonData


def test_complete_taxonomy_flow():
    """Test complete flow from request to response for taxonomy mapping."""
    # Setup dependencies
    repo = MockDefinitionsRepository()
    llm = StaticLLMClient()
    
    # Create use case
    use_case = ClassifyControlToThemes.from_defs(repo, llm)
    
    # Create controller
    controller = TaxonomyController(
        classify_use_case=use_case,
    )
    
    # Create request
    request = CommonRequest(
        header=CommonHeader(recordId='test-taxonomy-123'),
        data=CommonData(controlDescription='Authentication controls must ensure secure access to systems and data through proper verification mechanisms')
    )
    
    # Execute
    response = controller.handle_taxonomy_mapping(request)
    
    # Verify response structure
    assert response.header.recordId == 'test-taxonomy-123'
    assert hasattr(response.data, 'taxonomy')
    assert len(response.data.taxonomy) == 3
    
    # Verify each taxonomy item has required fields
    for item in response.data.taxonomy:
        assert hasattr(item, 'name')
        assert hasattr(item, 'id')
        assert hasattr(item, 'score')
        assert hasattr(item, 'reasoning')
        assert 0.0 <= item.score <= 1.0


def test_complete_fivews_flow():
    """Test complete flow from request to response for 5Ws mapping."""
    # Setup dependencies
    repo = MockDefinitionsRepository()
    llm = StaticLLMClient()
    
    # Create use case
    use_case = ClassifyControlTo5Ws.from_defs(repo, llm)
    
    # Create controller
    controller = FiveWsController(
        classify_use_case=use_case,
    )
    
    # Create request
    request = CommonRequest(
        header=CommonHeader(recordId='test-5ws-456'),
        data=CommonData(controlDescription='All employees must complete security training annually')
    )
    
    # Execute
    response = controller.handle_fivews_mapping(request)
    
    # Verify response structure
    assert response.header.recordId == 'test-5ws-456'
    assert hasattr(response.data, 'fivews')
    assert len(response.data.fivews) == 5
    
    # Verify 5Ws are in correct order
    expected_names = ['who', 'what', 'when', 'where', 'why']
    actual_names = [item.name for item in response.data.fivews]
    assert actual_names == expected_names
    
    # Verify each 5W item has required fields
    for item in response.data.fivews:
        assert item.name in expected_names
        assert item.status in ['present', 'missing']
        assert isinstance(item.reasoning, str)
        assert len(item.reasoning) > 0


def test_domain_validation_errors():
    """Test that domain validation errors are properly handled."""
    from mapper_api.domain.errors import ControlValidationError
    
    # Setup dependencies
    repo = MockDefinitionsRepository()
    llm = StaticLLMClient()
    use_case = ClassifyControlToThemes.from_defs(repo, llm)
    controller = TaxonomyController(classify_use_case=use_case)
    
    # Test empty control description
    request = CommonRequest(
        header=CommonHeader(recordId='test-empty'),
        data=CommonData(controlDescription='')
    )
    
    with pytest.raises(ControlValidationError, match="Failed to process control description"):
        controller.handle_taxonomy_mapping(request)
    
    # Test whitespace-only control description  
    request = CommonRequest(
        header=CommonHeader(recordId='test-whitespace'),
        data=CommonData(controlDescription='   \t\n   ')
    )
    
    with pytest.raises(ControlValidationError, match="Failed to process control description"):
        controller.handle_taxonomy_mapping(request)


def test_api_app_structure():
    """Test that the FastAPI app is properly configured."""
    from mapper_api.api.api import app
    
    # Check app is created
    assert app is not None
    assert hasattr(app, 'routes')
    
    # Check routes are registered
    route_paths = [route.path for route in app.routes if hasattr(route, 'path')]
    
    # Should have our main routes
    assert '/v2024-12/taxonomy_mapper' in route_paths
    assert '/v2024-12/5ws_mapper' in route_paths
    
    # Should have OpenAPI docs
    assert '/docs' in route_paths or any('openapi' in path for path in route_paths)


def test_repository_domain_entities():
    """Test that repository correctly builds domain entities."""
    repo = MockDefinitionsRepository()
    
    # Test clusters
    clusters = repo.get_clusters()
    assert len(clusters) > 0
    for cluster in clusters:
        assert hasattr(cluster, 'id')
        assert hasattr(cluster, 'name')
        assert cluster.id > 0
        assert len(cluster.name.strip()) > 0
    
    # Test taxonomies
    taxonomies = repo.get_taxonomies()
    assert len(taxonomies) > 0
    for taxonomy in taxonomies:
        assert hasattr(taxonomy, 'id')
        assert hasattr(taxonomy, 'name')
        assert hasattr(taxonomy, 'description')
        assert hasattr(taxonomy, 'cluster_id')
        assert taxonomy.id > 0
        assert len(taxonomy.name.strip()) > 0
    
    # Test risk themes
    risk_themes = repo.get_risk_themes()
    assert len(risk_themes) > 0
    for theme in risk_themes:
        assert hasattr(theme, 'id')
        assert hasattr(theme, 'name')
        assert hasattr(theme, 'taxonomy_id')
        assert hasattr(theme, 'cluster_id')
        assert theme.id > 0
        assert len(theme.name.strip()) > 0
