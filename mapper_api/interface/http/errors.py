"""HTTP error handling mapping domain/app errors to status codes."""
from __future__ import annotations
from fastapi import Request
from fastapi.responses import JSONResponse
from mapper_api.domain.errors import ValidationError, DefinitionsNotLoadedError


async def validation_exception_handler(request: Request, exc: ValidationError):
    record_id = request.headers.get('x-trace-id')
    return JSONResponse(status_code=400, content={"error": str(exc), "traceId": record_id})


async def definitions_exception_handler(request: Request, exc: DefinitionsNotLoadedError):
    record_id = request.headers.get('x-trace-id')
    return JSONResponse(status_code=404, content={"error": str(exc), "traceId": record_id})


async def unhandled_exception_handler(request: Request, exc: Exception):
    record_id = request.headers.get('x-trace-id')
    return JSONResponse(status_code=500, content={"error": "Internal Server Error", "traceId": record_id})
