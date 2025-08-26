"""FastAPI app wiring routers and exception handlers."""
from __future__ import annotations
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from mapper_api.interface.http.routers.taxonomy_mapper import router as taxonomy_router
from mapper_api.interface.http.routers.fivews_mapper import router as fivews_router
from mapper_api.interface.http.errors import validation_exception_handler, definitions_exception_handler, unhandled_exception_handler
from mapper_api.domain.errors import ValidationError, DefinitionsNotLoadedError
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

    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(DefinitionsNotLoadedError, definitions_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    return app


app = create_app()
