"""Health check endpoints for Azure service connectivity."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from mapper_api.config.settings import Settings
from mapper_api.infrastructure.azure.blob_definitions_repo import BlobDefinitionsRepository
from mapper_api.infrastructure.azure.openai_client import AzureOpenAILLMClient

router = APIRouter()


class HealthStatus(BaseModel):
    status: str
    services: Dict[str, Any]
    timestamp: str


@router.get('/health', response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint."""
    from datetime import datetime
    
    return HealthStatus(
        status="healthy",
        services={"api": "running"},
        timestamp=datetime.utcnow().isoformat()
    )


@router.get('/health/azure', response_model=HealthStatus)
async def azure_health_check():
    """Comprehensive Azure services health check."""
    from datetime import datetime
    
    services = {}
    overall_status = "healthy"
    
    try:
        settings = Settings()
        services["config"] = {"status": "ok", "message": "Settings loaded successfully"}
    except Exception as e:
        services["config"] = {"status": "error", "message": f"Settings error: {str(e)}"}
        overall_status = "unhealthy"
        
    # Test Blob Storage
    try:
        settings = Settings()
        repo = BlobDefinitionsRepository(
            account_name=settings.STORAGE_ACCOUNT_NAME,
            container_name=settings.STORAGE_CONTAINER_NAME,
            tenant_id=settings.AZURE_TENANT_ID,
            client_id=settings.AZURE_CLIENT_ID,
            client_secret=settings.AZURE_CLIENT_SECRET,
        )
        
        themes = repo.get_theme_rows()
        fivews = repo.get_fivews_rows()
        
        services["blob_storage"] = {
            "status": "ok",
            "message": f"Connected - {len(themes)} themes, {len(fivews)} 5Ws definitions loaded"
        }
    except Exception as e:
        services["blob_storage"] = {
            "status": "error", 
            "message": f"Connection failed: {type(e).__name__}: {str(e)}"
        }
        overall_status = "unhealthy"
    
    # Test Azure OpenAI
    try:
        settings = Settings()
        client = AzureOpenAILLMClient(
            endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )
        
        # Simple connectivity test
        response = client.json_schema_chat(
            system="You are a test assistant.",
            user="Reply with just 'ok'",
            schema_name="HealthTest",
            schema={
                "type": "object",
                "properties": {"status": {"type": "string"}},
                "required": ["status"],
                "additionalProperties": False
            },
            max_tokens=10,
            deployment=settings.AZURE_OPENAI_DEPLOYMENT
        )
        
        services["azure_openai"] = {
            "status": "ok",
            "message": f"Connected - Test response received",
            "deployment": settings.AZURE_OPENAI_DEPLOYMENT
        }
    except Exception as e:
        services["azure_openai"] = {
            "status": "error",
            "message": f"Connection failed: {type(e).__name__}: {str(e)}"
        }
        overall_status = "unhealthy"
    
    status_response = HealthStatus(
        status=overall_status,
        services=services,
        timestamp=datetime.utcnow().isoformat()
    )
    
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=status_response.dict())
    
    return status_response
