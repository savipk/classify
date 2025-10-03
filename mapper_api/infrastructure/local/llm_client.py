"""Static LLM client mock returning deterministic JSON matching provided schema."""
from __future__ import annotations
import json
from typing import Mapping, Any, Optional


class StaticLLMClient:
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
        props = schema.get('properties', {})
        if 'taxonomy' in props:
            # Try to extract allowed names from schema robustly
            allowed: list[str] = []

            def walk(node: Any):
                nonlocal allowed
                if isinstance(node, dict):
                    if 'enum' in node and isinstance(node['enum'], list) and all(isinstance(x, str) for x in node['enum']):
                        enum_vals = node['enum']
                        five_set = {"who", "what", "when", "where", "why"}
                        if set(enum_vals) != five_set and len(enum_vals) >= 3:
                            # Prefer the longest non-5Ws enum found
                            if len(enum_vals) > len(allowed):
                                allowed = list(enum_vals)
                    for v in node.values():
                        walk(v)
                elif isinstance(node, list):
                    for item in node:
                        walk(item)

            walk(schema)

            names = (allowed[:3] if len(allowed) >= 3 else ['Theme A', 'Theme B', 'Theme C'])
            out = {
                'taxonomy': [
                    {'name': names[0], 'id': 1, 'score': 0.87, 'reasoning': 'high relevance'},
                    {'name': names[1], 'id': 2, 'score': 0.44, 'reasoning': 'some relevance'},
                    {'name': names[2], 'id': 3, 'score': 0.33, 'reasoning': 'possible relevance'},
                ]
            }
            return json.dumps(out)
        # else assume 5ws
        out = {
            'fivews': [
                {'name': 'who', 'status': 'present', 'reasoning': 'explicit actor mentioned'},
                {'name': 'what', 'status': 'present', 'reasoning': 'action described'},
                {'name': 'when', 'status': 'missing', 'reasoning': 'no time given'},
                {'name': 'where', 'status': 'present', 'reasoning': 'location/asset context'},
                {'name': 'why', 'status': 'present', 'reasoning': 'purpose implied'},
            ]
        }
        return json.dumps(out)
