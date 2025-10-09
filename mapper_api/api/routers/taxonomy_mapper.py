"""HTTP router for POST /taxonomy_mapper."""
from __future__ import annotations
from fastapi import APIRouter
from mapper_api.application.dto.http_common import CommonRequest
from mapper_api.application.dto.http_common import TaxonomyResponse
from mapper_api.config.settings import Settings
from mapper_api.infrastructure.azure.blob_definitions_repo import BlobDefinitionsRepository
from mapper_api.infrastructure.azure.openai_client import AzureOpenAILLMClient
from mapper_api.application.use_cases.map_control_to_themes import ClassifyControlToThemes
from mapper_api.interface.controllers.taxonomy_controller import TaxonomyController

router = APIRouter()


def get_taxonomy_controller() -> TaxonomyController:
    """
    Factory to create taxonomy controller with dependencies.
    Following EcomApp's pattern of in-place dependency assembly.
    """
    # Load settings
    settings = Settings()
    
    # Create infrastructure adapters
    definitions_repo = BlobDefinitionsRepository(
        account_name=settings.STORAGE_ACCOUNT_NAME,
        container_name=settings.STORAGE_CONTAINER_NAME,
        tenant_id=settings.AZURE_TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET,
    )
    
    llm_client = AzureOpenAILLMClient(
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
    )
    
    # Create use case with dependencies
    classify_use_case = ClassifyControlToThemes.from_defs(
        repo=definitions_repo,
        llm=llm_client,
        deployment_name=settings.AZURE_OPENAI_DEPLOYMENT
    )
    
    # Create and return controller
    return TaxonomyController(
        classify_use_case=classify_use_case
    )

controller = get_taxonomy_controller()

@router.post('/taxonomy_mapper', response_model=TaxonomyResponse)
async def taxonomy_mapper(req: CommonRequest) -> TaxonomyResponse:
    """
    Map control description to taxonomy themes using in-place dependency assembly.
    
    Dependencies are created right here where they're used, making the flow
    transparent and easy to follow. This follows EcomApp's pattern.
    """
    return controller.handle_taxonomy_mapping(req)
