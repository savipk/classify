"""HTTP router for POST /taxonomy_mapper."""
from __future__ import annotations
from fastapi import APIRouter, Depends
from mapper_api.application.dto.requests import CommonRequest
from mapper_api.application.dto.responses import TaxonomyResponse
from mapper_api.interface.di.container import Container
from mapper_api.interface.http.state import get_container
from mapper_api.domain.errors import DefinitionsNotLoadedError
from mapper_api.application.use_cases.map_control_to_themes import map_control_to_themes

router = APIRouter()


@router.post('/taxonomy_mapper', response_model=TaxonomyResponse)
async def taxonomy_mapper(req: CommonRequest, container: Container = Depends(get_container)):
    if not container.definitions_loaded:
        raise DefinitionsNotLoadedError("definitions not loaded")
    record_id = req.header.recordId
    items = map_control_to_themes(
        record_id=record_id,
        control_description=req.data.controlDescription,
        repo=container.definitions_repo,
        llm=container.llm_client,
        deployment=container.settings.AZURE_OPENAI_DEPLOYMENT,
    )
    return {
        "header": {"recordId": record_id},
        "data": {"taxonomy": items},
    }
