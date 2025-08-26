"""Use case: extract 5Ws presence with reasoning using LLM with strict JSON."""
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Sequence
from mapper_api.application.dto.output_schemas import FiveWOut
from mapper_api.application.ports.llm import LLMClient
from mapper_api.application.prompts import fivews as fivews_prompts
from mapper_api.domain.entities.control import Control
from mapper_api.domain.repositories.definitions import DefinitionsRepository
from mapper_api.domain.errors import ValidationError, DefinitionsNotLoadedError

_ORDER = ["who", "what", "when", "where", "why"]


@dataclass
class ClassifyControlToFiveWs:
    repo: DefinitionsRepository
    llm: LLMClient

    def run(self, *, record_id: str, control_description: str, deployment: str):
        ctrl = Control(text=control_description)
        if not ctrl.text or not ctrl.text.strip():
            raise ValidationError("controlDescription must not be empty")

        defs = self.repo.get_fivews_rows()
        if not defs:
            raise DefinitionsNotLoadedError("5Ws definitions not loaded")

        schema = FiveWOut.model_json_schema()
        system_prompt = fivews_prompts.SYSTEM
        user_prompt = fivews_prompts.build_user_prompt(ctrl.text, defs)

        raw = self.llm.json_schema_chat(
            system=system_prompt,
            user=user_prompt,
            schema_name="FiveWsResponse",
            schema=schema,
            max_tokens=400,
            temperature=0.1,
            context={"trace_id": record_id},
            deployment=deployment,
        )

        try:
            data = FiveWOut.model_validate_json(raw)
        except Exception as e:
            raise ValidationError(f"LLM output validation failed: {e}")

        ordered = sorted(data.fivews, key=lambda x: _ORDER.index(x.name))
        return [
            {"name": i.name, "status": i.status, "reasoning": i.reasoning}
            for i in ordered
        ]


def map_control_to_5ws(
    *,
    record_id: str,
    control_description: str,
    repo: DefinitionsRepository,
    llm: LLMClient,
    deployment: str,
) -> dict:
    use_case = ClassifyControlToFiveWs(repo=repo, llm=llm)
    return use_case.run(record_id=record_id, control_description=control_description, deployment=deployment)
