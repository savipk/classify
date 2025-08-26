"""FastAPI dependency to access the DI container."""
from __future__ import annotations
from functools import lru_cache
from mapper_api.interface.di.container import Container, build_container


@lru_cache(maxsize=1)
def get_container() -> Container:
    return build_container()
