"""Azure OpenAI client calling Chat Completions with response_format json_schema."""
from __future__ import annotations
import time
from typing import Mapping, Any, Optional
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import logging


class AzureOpenAILLMClient:
    def __init__(self, *, endpoint: str, api_key: str, api_version: str) -> None:
        self._client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version)
        self._logger = logging.getLogger("mapper.llm")

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.3, min=0.3, max=2.0))
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
        start = time.perf_counter()
        model_name = deployment if deployment else ""
        
        # Azure requires additionalProperties=false at root level for strict mode
        schema = dict(schema)
        schema.setdefault("additionalProperties", False)

        resp = self._client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "schema": schema,
                    "strict": True,
                },
            },
            temperature=temperature,
            top_p=1.0,
            max_tokens=max_tokens,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        usage = getattr(resp, "usage", None)
        try:
            self._logger.info(
                "llm.chat.json_schema",
                extra={
                    "traceId": (context or {}).get("trace_id"),
                    "deployment": model_name,
                    "latencyMs": latency_ms,
                    "promptTokens": getattr(usage, "prompt_tokens", None) if usage else None,
                    "completionTokens": getattr(usage, "completion_tokens", None) if usage else None,
                    "totalTokens": getattr(usage, "total_tokens", None) if usage else None,
                },
            )
        except Exception:
            pass
        content = resp.choices[0].message.content  # type: ignore[attr-defined]
        return content
