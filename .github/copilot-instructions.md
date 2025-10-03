# Copilot Instructions for mapper-api

## Architecture & Structure
- Follows Clean Architecture: `domain` is framework-free and contains core business logic.
- Use Pydantic only at boundaries (DTOs in `application/dto/` and LLM validation).
- API layer is in `mapper_api/api/` and routers in `mapper_api/api/routers/`.
- Services, mappers, and use cases are in `mapper_api/application/`.
- Configuration is in `mapper_api/config/`.
- Data loads once at startup from Azure Blob (see `infrastructure/azure/`). No hot reloads.
- Folder and filenames must match the provided structure exactly.

## External Integrations
- Uses Azure OpenAI with strict JSON schema validation (`response_format.json_schema`, `strict=true`).
- API contracts must match exactly as specified in DTOs and routers.

## Developer Workflows
- Main entry point: `main.py`.
- Tests are in `tests/unit/` and `tests/integration/`. Use `pytest` for running tests.
- No custom build steps; standard Python workflows apply.
- Debug scripts: `debug_azure_connections.py`, `debug_env_check.py`.

## Patterns & Conventions
- Domain logic is pure Python, no framework dependencies.
- Pydantic models are only for input/output boundaries, not internal logic.
- All external service calls (LLM, Azure) are wrapped in adapters in `infrastructure/`.
- API endpoints are defined in routers, with DTOs for request/response validation.
- Strict separation between domain, application, and infrastructure layers.

## Examples
- To add a new API endpoint: create a router in `api/routers/`, define DTOs in `application/dto/`, and implement logic in `application/use_cases/`.
- To update contracts: change DTOs and ensure routers match the new schema.
- For LLM integration: use Azure OpenAI client in `infrastructure/azure/` and validate responses with Pydantic schemas.

## References
- `.cursorrules` for architecture and integration rules.
- `README.md` is currently empty; see this file for agent instructions.

---
For questions or unclear conventions, ask for clarification or examples from maintainers.
