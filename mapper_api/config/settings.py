"""Settings via Pydantic BaseSettings for envs and Azure config."""
from __future__ import annotations
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    APP_ENV: Literal['dev', 'uat', 'prod']
    PORT: int = Field(default=8000)
    API_VERSION: str = Field(default='v2024-12')  # Change this for each release

    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_VERSION: str = Field(default='2024-12-01-preview')
    AZURE_OPENAI_DEPLOYMENT: str

    STORAGE_ACCOUNT_NAME: str
    STORAGE_CONTAINER_NAME: str = Field(default='libra-ai')
    AZURE_TENANT_ID: str
    AZURE_CLIENT_ID: str
    AZURE_CLIENT_SECRET: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
