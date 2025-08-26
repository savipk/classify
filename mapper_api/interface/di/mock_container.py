"""Mock container wiring local file definitions and static LLM."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from mapper_api.domain.repositories.definitions import DefinitionsRepository
from mapper_api.mock.definitions_repo import LocalFileDefinitionsRepository
from mapper_api.mock.llm_client import StaticLLMClient
from mapper_api.application.ports.llm import LLMClient


@dataclass
class MockSettings:
    AZURE_OPENAI_DEPLOYMENT: str = 'mock-deployment'


@dataclass
class MockContainer:
    settings: MockSettings
    definitions_repo: DefinitionsRepository
    llm_client: LLMClient
    definitions_loaded: bool


def build_mock_container() -> MockContainer:
    repo = LocalFileDefinitionsRepository()
    llm: LLMClient = StaticLLMClient()
    return MockContainer(settings=MockSettings(), definitions_repo=repo, llm_client=llm,
                         definitions_loaded=bool(repo.get_theme_rows()) and bool(repo.get_fivews_rows()))
