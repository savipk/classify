# Mapper API

FastAPI service that maps control descriptions to top Risk Themes and extracts 5Ws presence using Azure OpenAI with strict JSON.

## Run locally
1. Create `.env` with required variables (see below).
2. Install deps: `pip install -e .` or install from `pyproject.toml`.
3. Start API: `uvicorn mapper_api.interface.http.api:app --reload`.

## .env example
```
APP_ENV=dev
PORT=8000

AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=MyPolicies-DEV-GPT4o

STORAGE_ACCOUNT_NAME=stoat48090dev
STORAGE_CONTAINER_NAME=libra-ai
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
```

## Endpoints
- POST `/taxonomy_mapper`
- POST `/5ws_mapper`
