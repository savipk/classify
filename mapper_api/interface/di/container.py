"""Simple DI container assembling adapters, prompts, and use cases. Loads definitions once."""
from __future__ import annotations
from dataclasses import dataclass
from mapper_api.config.settings import Settings
from mapper_api.infrastructure.azure.blob_definitions_repo import BlobDefinitionsRepository
from mapper_api.infrastructure.azure.openai_client import AzureOpenAILLMClient
from mapper_api.application.ports.llm import LLMClient
from mapper_api.domain.repositories.definitions import DefinitionsRepository


@dataclass
class Container:
    settings: Settings
    definitions_repo: DefinitionsRepository
    llm_client: LLMClient
    definitions_loaded: bool


def build_container() -> Container:
    settings = Settings()
    repo = BlobDefinitionsRepository(
        account_name=settings.STORAGE_ACCOUNT_NAME,
        container_name=settings.STORAGE_CONTAINER_NAME,
        tenant_id=settings.AZURE_TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET,
    )
    defs_loaded = bool(repo.get_theme_rows()) and bool(repo.get_fivews_rows())
    llm: LLMClient = AzureOpenAILLMClient(
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
    )
    return Container(settings=settings, definitions_repo=repo, llm_client=llm, definitions_loaded=defs_loaded)
