"""Use case: extract 5Ws presence with reasoning using LLM with strict JSON."""
from __future__ import annotations
from dataclasses import dataclass
from mapper_api.application.dto.llm_schemas import FiveWOut
from mapper_api.application.ports.llm import LLMClient
from mapper_api.application.prompts import fivews as fivews_prompts
from mapper_api.domain.entities.control import Control
from mapper_api.domain.repositories.definitions import DefinitionsRepository
from mapper_api.domain.errors import ControlValidationError, DefinitionsUnavailableError
from mapper_api.application.dto.use_case_requests import FiveWsMappingRequest
from mapper_api.config.settings import Settings

_ORDER = ["who", "what", "when", "where", "why"]


@dataclass
class ClassifyControlTo5Ws:
    """
    Use case for extracting 5Ws presence from controls.
    
    Following EcomApp's pattern of injecting services and keeping business logic clean.
    """
    repo: DefinitionsRepository
    llm: LLMClient

    @classmethod
    def from_defs(cls, repo: DefinitionsRepository, llm: LLMClient):
        """Factory method to create use case instance."""
        return cls(repo=repo, llm=llm)

    def execute(self, request: FiveWsMappingRequest) -> list:
        """
        Execute the 5Ws extraction use case.
        
        Validates control text and extracts presence/absence of 5Ws elements
        with reasoning using LLM.
        """
        # Validate control using domain entity
        ctrl = Control(text=request.control_description)
        ctrl.validate_all()

        # Get 5Ws definitions
        defs = self.repo.get_fivews_rows()
        if not defs:
            raise DefinitionsUnavailableError("5Ws definitions not loaded")

        # Build LLM request
        schema = FiveWOut.model_json_schema()
        system_prompt = fivews_prompts.SYSTEM
        user_prompt = fivews_prompts.build_user_prompt(ctrl.text, defs)
        settings = Settings()

        raw = self.llm.json_schema_chat(
            system=system_prompt,
            user=user_prompt,
            schema_name="FiveWsResponse",
            schema=schema,
            max_tokens=400,
            temperature=0.1,
            context={"trace_id": request.record_id},
            deployment=settings.AZURE_OPENAI_DEPLOYMENT,
        )

        try:
            data = FiveWOut.model_validate_json(raw)
        except Exception as e:
            raise ControlValidationError(f"LLM output validation failed: {e}")

        ordered = sorted(data.fivews, key=lambda x: _ORDER.index(x.name))
        return [
            {"name": i.name, "status": i.status, "reasoning": i.reasoning}
            for i in ordered
        ]

