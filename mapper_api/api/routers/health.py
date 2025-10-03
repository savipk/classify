"""Health check endpoints for Azure service connectivity."""
from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel

from mapper_api.config.settings import Settings
from mapper_api.infrastructure.azure.blob_definitions_repo import BlobDefinitionsRepository
from mapper_api.infrastructure.azure.openai_client import AzureOpenAILLMClient

router = APIRouter()


class HealthStatus(BaseModel):
    status: str
    services: str


@router.get('/health', response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint."""
    return HealthStatus(
        status="healthy",
        services="api: running"
    )


@router.get('/health/azure', response_model=HealthStatus)
async def azure_health_check():
    """Comprehensive Azure services health check."""
    services_status = []
    overall_status = "healthy"
    
    try:
        settings = Settings()
        services_status.append("config: ok - Settings loaded successfully")
    except Exception as e:
        services_status.append(f"config: error - Settings error: {str(e)}")
        overall_status = "unhealthy"
        
    # Test Blob Storage
    try:
        repo = BlobDefinitionsRepository(
            account_name=settings.STORAGE_ACCOUNT_NAME,
            container_name=settings.STORAGE_CONTAINER_NAME,
            tenant_id=settings.AZURE_TENANT_ID,
            client_id=settings.AZURE_CLIENT_ID,
            client_secret=settings.AZURE_CLIENT_SECRET,
        )
        
        risk_themes = repo.get_risk_themes()
        fivews = repo.get_fivews_rows()
        
        services_status.append(f"blob_storage: ok - Connected - {len(risk_themes)} themes, {len(fivews)} 5Ws definitions loaded")
    except Exception as e:
        services_status.append(f"blob_storage: error - Connection failed: {type(e).__name__}: {str(e)}")
        overall_status = "unhealthy"
    
    # Test Azure OpenAI
    try:
        client = AzureOpenAILLMClient(
            endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )
        
        # Minimal connectivity test
        response = client.json_schema_chat(
            system="Test",
            user="ok",
            schema_name="Test",
            schema={ "type": "object", "properties": {"test": {"type": "string"}}, "required": ["test"], "additionalProperties": False }
            max_tokens=5,
            deployment=settings.AZURE_OPENAI_DEPLOYMENT
        )
        
        services_status.append(f"azure_openai: ok - Connected to deployment {settings.AZURE_OPENAI_DEPLOYMENT}")
    except Exception as e:
        services_status.append(f"azure_openai: error - Connection failed: {type(e).__name__}: {str(e)}")
        overall_status = "unhealthy"
    
    status_response = HealthStatus(
        status=overall_status,
        services=" | ".join(services_status)
    )
    
    return status_response
