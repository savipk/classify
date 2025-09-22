"""HTTP router for POST /5ws_mapper."""
from __future__ import annotations
from fastapi import APIRouter
from mapper_api.application.dto.requests import CommonRequest
from mapper_api.application.dto.responses import FiveWResponse
from mapper_api.config.settings import Settings
from mapper_api.infrastructure.azure.blob_definitions_repo import BlobDefinitionsRepository
from mapper_api.infrastructure.azure.openai_client import AzureOpenAILLMClient
from mapper_api.application.use_cases.map_control_to_5ws import ClassifyControlTo5Ws
from mapper_api.interface.controllers.fivews_controller import FiveWsController

router = APIRouter()


def get_fivews_controller() -> FiveWsController:
    """
    Factory to create 5Ws controller with dependencies.
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
    classify_use_case = ClassifyControlTo5Ws.from_defs(
        repo=definitions_repo,
        llm=llm_client
    )
    
    # Create and return controller
    return FiveWsController(
        classify_use_case=classify_use_case,
        deployment=settings.AZURE_OPENAI_DEPLOYMENT
    )


@router.post('/5ws_mapper', response_model=FiveWResponse)
async def fivews_mapper(req: CommonRequest) -> FiveWResponse:
    """
    Map control description to 5Ws presence using in-place dependency assembly.
    
    Dependencies are created right here where they're used, making the flow
    transparent and easy to follow. This follows EcomApp's pattern.
    """
    controller = get_fivews_controller()
    return controller.handle_fivews_mapping(req)
