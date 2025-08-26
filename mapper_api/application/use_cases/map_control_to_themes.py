"""Use case: map control to top 3 Risk Themes using LLM with strict JSON."""
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Sequence
from mapper_api.domain.entities.control import Control
from mapper_api.domain.repositories.definitions import DefinitionsRepository
from mapper_api.domain.errors import ValidationError, DefinitionsNotLoadedError
from mapper_api.application.dto.output_schemas import build_taxonomy_models
from mapper_api.application.prompts.taxonomy import TaxonomyPrompt
from mapper_api.application.mappers.assemblers import assemble_taxonomy_items
from mapper_api.domain.value_objects.score import ThemeClassification, Score
from mapper_api.application.ports.llm import LLMClient
from mapper_api.application.prompts import taxonomy as taxonomy_prompts


@dataclass
class ClassifyControlToThemes:
    repo: DefinitionsRepository
    llm: LLMClient
    prompt: TaxonomyPrompt
    TaxonomyOut: type

    @classmethod
    def from_defs(cls, repo: DefinitionsRepository, llm: LLMClient):
        rows = repo.get_theme_rows()
        if not rows:
            raise DefinitionsNotLoadedError("taxonomy definitions not loaded")
        allowed_names = [r.risk_theme for r in rows]
        _, TaxonomyOut = build_taxonomy_models(allowed_names)
        prompt = TaxonomyPrompt(rows)
        return cls(repo=repo, llm=llm, prompt=prompt, TaxonomyOut=TaxonomyOut)

    def run(self, *, record_id: str, control_description: str, deployment: str):
        ctrl = Control(text=control_description)
        if not ctrl.text or not ctrl.text.strip():
            raise ValidationError("controlDescription must not be empty")
        system, user = self.prompt.build(record_id=record_id, control_description=ctrl.text)
        schema = self.TaxonomyOut.model_json_schema()
        raw = self.llm.json_schema_chat(
            system=system,
            user=user,
            schema_name="TaxonomyMapperResponse",
            schema=schema,
            max_tokens=600,
            temperature=0.1,
            context={"trace_id": record_id},
            deployment=deployment,
        )
        try:
            data = self.TaxonomyOut.model_validate_json(raw)
        except Exception as e:
            raise ValidationError(f"LLM output validation failed: {e}")
        items = sorted(data.taxonomy, key=lambda x: x.score, reverse=True)[:3]
        classifications = [
            ThemeClassification(name=i.name, id=i.id, score=Score(i.score), reasoning=i.reasoning)
            for i in items
        ]
        return assemble_taxonomy_items(classifications)


def map_control_to_themes(
    *,
    record_id: str,
    control_description: str,
    repo: DefinitionsRepository,
    llm: LLMClient,
    deployment: str,
) -> dict:
    use_case = ClassifyControlToThemes.from_defs(repo, llm)
    return use_case.run(record_id=record_id, control_description=control_description, deployment=deployment)
