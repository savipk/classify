"""Port/Protocol for LLM client capable of json_schema_chat."""
from __future__ import annotations
from typing import Protocol, Mapping, Any, Optional


class LLMClient(Protocol):
    def json_schema_chat(
        self,
        *,
        system: str,
        user: str,
        schema_name: str,
        schema: Mapping[str, Any],
        max_tokens: int,
        temperature: float = 0.1,
        context: Optional[dict] = None,
        deployment: Optional[str] = None,
    ) -> str:
        """Return raw JSON string validated by the model against provided JSON Schema."""
        ...
