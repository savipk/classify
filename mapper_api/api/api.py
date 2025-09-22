"""FastAPI app wiring routers and exception handlers."""
from __future__ import annotations
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from mapper_api.api.routers.taxonomy_mapper import router as taxonomy_router
from mapper_api.api.routers.fivews_mapper import router as fivews_router
from mapper_api.api.routers.health import router as health_router
from mapper_api.api.errors import (
    control_validation_exception_handler,
    definitions_unavailable_exception_handler, 
    llm_processing_exception_handler,
    domain_exception_handler,
    unhandled_exception_handler
)
from mapper_api.domain.errors import (
    MapperDomainError,
    ControlValidationError,
    DefinitionsUnavailableError,
    LLMProcessingError
)
from mapper_api.config.settings import Settings


def create_app() -> FastAPI:
    settings = Settings()
    
    app = FastAPI(
        title="Mapper API",
        version=settings.API_VERSION,
        root_path="/mapper-api"
    )
    
    # Include routers with version prefix
    app.include_router(taxonomy_router, prefix=f"/{settings.API_VERSION}")
    app.include_router(fivews_router, prefix=f"/{settings.API_VERSION}")
    app.include_router(health_router, prefix=f"/{settings.API_VERSION}")

    # Exception handlers
    app.add_exception_handler(ControlValidationError, control_validation_exception_handler)
    app.add_exception_handler(DefinitionsUnavailableError, definitions_unavailable_exception_handler)
    app.add_exception_handler(LLMProcessingError, llm_processing_exception_handler)
    app.add_exception_handler(MapperDomainError, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, control_validation_exception_handler)
    
    # Catch-all handler
    app.add_exception_handler(Exception, unhandled_exception_handler)
    return app


app = create_app()
