"""Use case: map control to top 3 Risk Themes using LLM with strict JSON."""
from __future__ import annotations
from dataclasses import dataclass
from mapper_api.domain.entities.control import Control
from mapper_api.domain.repositories.definitions import DefinitionsRepository
from mapper_api.domain.services.taxonomy_service import TaxonomyService
from mapper_api.domain.errors import ControlValidationError, DefinitionsUnavailableError
from mapper_api.application.dto.llm_schemas import build_taxonomy_models
from mapper_api.application.prompts.taxonomy import TaxonomyPrompt
from mapper_api.application.mappers.assemblers import assemble_taxonomy_items
from mapper_api.domain.value_objects.score import Score
from mapper_api.domain.value_objects.classification import ThemeClassification
from mapper_api.application.ports.llm import LLMClient
from mapper_api.application.dto.use_case_requests import TaxonomyMappingRequest
from mapper_api.config.settings import Settings


@dataclass
class ClassifyControlToThemes:
    """
    Use case for classifying controls to risk themes using domain entities.
    
    Following EcomApp's pattern of injecting services and keeping business logic clean.
    """
    repo: DefinitionsRepository
    llm: LLMClient
    taxonomy_service: TaxonomyService
    prompt: TaxonomyPrompt
    TaxonomyOut: type

    @classmethod
    def from_defs(cls, repo: DefinitionsRepository, llm: LLMClient):
        # Use domain entities instead of raw rows
        risk_themes = repo.get_risk_themes()
        if not risk_themes:
            raise DefinitionsUnavailableError("taxonomy definitions not loaded")
        
        # Extract theme names for schema building
        allowed_names = [theme.name for theme in risk_themes]
        _, TaxonomyOut = build_taxonomy_models(allowed_names)
        
        # Build prompt using domain entities (consistent with domain-driven design)
        prompt = TaxonomyPrompt(risk_themes)
        
        taxonomy_service = TaxonomyService()
        return cls(
            repo=repo, 
            llm=llm, 
            taxonomy_service=taxonomy_service,
            prompt=prompt, 
            TaxonomyOut=TaxonomyOut
        )

    def execute(self, request: TaxonomyMappingRequest) -> list:
        """
        Execute the taxonomy mapping use case using domain entities.
        
        This method demonstrates how to use domain services and entities
        to create more maintainable business logic.
        """
        # Validate control using domain entity
        ctrl = Control(text=request.control_description)
        ctrl.validate_all()
        
        # Get domain entities for potential business logic use
        risk_themes = self.repo.get_risk_themes()
        
        # Build and execute LLM call
        system, user = self.prompt.build(record_id=request.record_id, control_description=ctrl.text)
        schema = self.TaxonomyOut.model_json_schema()
        settings = Settings()
        raw = self.llm.json_schema_chat(
            system=system,
            user=user,
            schema_name="TaxonomyMapperResponse",
            schema=schema,
            max_tokens=600,
            temperature=0.1,
            context={"trace_id": request.record_id},
            deployment=settings.AZURE_OPENAI_DEPLOYMENT,
        )
        
        try:
            data = self.TaxonomyOut.model_validate_json(raw)
        except Exception as e:
            raise ControlValidationError(f"LLM output validation failed: {e}")
        
        # Process results using domain logic with score thresholding
        SCORE_THRESHOLD = 0.2
        all_items = sorted(data.taxonomy, key=lambda x: x.score, reverse=True)
        items = [item for item in all_items if item.score >= SCORE_THRESHOLD][:3]
        classifications = [
            ThemeClassification(name=i.name, id=i.id, score=Score(i.score), reasoning=i.reasoning)
            for i in items
        ]
        
        return assemble_taxonomy_items(classifications)


