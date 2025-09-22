"""HTTP error handling mapping domain/app errors to status codes."""
from __future__ import annotations
from fastapi import Request
from fastapi.responses import JSONResponse
from mapper_api.domain.errors import (
    MapperDomainError, 
    ControlValidationError, 
    DefinitionsUnavailableError,
    LLMProcessingError,
    # Keep old names for backward compatibility
    ValidationError, 
    DefinitionsNotLoadedError
)


async def control_validation_exception_handler(request: Request, exc: ControlValidationError):
    """Handle control validation errors with 400 status."""
    record_id = request.headers.get('x-trace-id')
    return JSONResponse(status_code=400, content={"error": str(exc), "traceId": record_id})


async def definitions_unavailable_exception_handler(request: Request, exc: DefinitionsUnavailableError):
    """Handle missing definitions with 503 status (service unavailable)."""
    record_id = request.headers.get('x-trace-id')
    return JSONResponse(status_code=503, content={"error": str(exc), "traceId": record_id})


async def llm_processing_exception_handler(request: Request, exc: LLMProcessingError):
    """Handle LLM processing errors with 502 status (bad gateway)."""
    record_id = request.headers.get('x-trace-id')
    return JSONResponse(status_code=502, content={"error": str(exc), "traceId": record_id})


async def domain_exception_handler(request: Request, exc: MapperDomainError):
    """Handle general domain errors with 400 status."""
    record_id = request.headers.get('x-trace-id')
    return JSONResponse(status_code=400, content={"error": str(exc), "traceId": record_id})


# Legacy handlers for backward compatibility
async def validation_exception_handler(request: Request, exc: ValidationError):
    record_id = request.headers.get('x-trace-id')
    return JSONResponse(status_code=400, content={"error": str(exc), "traceId": record_id})


async def definitions_exception_handler(request: Request, exc: DefinitionsNotLoadedError):
    record_id = request.headers.get('x-trace-id')
    return JSONResponse(status_code=503, content={"error": str(exc), "traceId": record_id})


async def unhandled_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    record_id = request.headers.get('x-trace-id')
    return JSONResponse(status_code=500, content={"error": "Internal Server Error", "traceId": record_id})
