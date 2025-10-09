"""Use case: map control to Risk Themes"""
from dataclasses import dataclass

from mapper_api.domain.entities.control import Control
from mapper_api.domain.repositories.definitions import DefinitionsRepository
from mapper_api.domain.errors import ControlValidationError, DefinitionsUnavailableError
from mapper_api.application.dto.llm_schemas import build_taxonomy_models
from mapper_api.application.prompts.taxonomy import TaxonomyPrompt
from mapper_api.domain.value_objects.classification import ThemeClassification
from mapper_api.domain.value_objects.score import Score
from mapper_api.application.ports.llm import LLMClient
from mapper_api.application.dto.domain_mapping import TaxonomyMappingRequest
from mapper_api.application.services.embedding_service import embed_text
from mapper_api.application.services.mapping_threshold import compute_combined_score
from mapper_api.config.scoring_config import ScoringConfig


@dataclass
class ClassifyControlToThemes:
    """
    Use case for classifying controls to risk themes
    """
    repo: DefinitionsRepository
    llm: LLMClient
    prompt: TaxonomyPrompt
    TaxonomyOut: type
    deployment_name: str

    @classmethod
    def from_defs(cls, repo: DefinitionsRepository, llm: LLMClient, deployment_name: str):
        # Use domain entities
        risk_themes = repo.get_risk_themes()
        if not risk_themes:
            raise DefinitionsUnavailableError("taxonomy definitions not loaded")

        # schema building
        allowed_names = [theme.name for theme in risk_themes]
        _, TaxonomyOut = build_taxonomy_models(allowed_names)
        prompt = TaxonomyPrompt(risk_themes)

        return cls(
            repo=repo,
            llm=llm,
            prompt=prompt,
            TaxonomyOut=TaxonomyOut,
            deployment_name=deployment_name
        )

    def execute(self, request: TaxonomyMappingRequest) -> list:
        """
        Execute taxonomy mapping use case
        """
        # Validate control
        ctrl = Control(text=request.control_description)
        ctrl.validate_all()

        # Get domain entities
        risk_themes = self.repo.get_risk_themes()

        # LLM call
        system, user = self.prompt.build(
            record_id=request.record_id, 
            control_description=ctrl.text
        )
        schema = self.TaxonomyOut.model_json_schema()

        raw = self.llm.json_schema_chat(
            system=system,
            user=user,
            schema_name="TaxonomyMapperResponse",
            schema=schema,
            max_tokens=600,
            temperature=0.1,
            context={"trace_id": request.record_id},
            deployment=self.deployment_name
        )

        try:
            data = self.TaxonomyOut.model_validate_json(raw)
        except Exception as e:
            raise ControlValidationError(f"LLM output validation failed: {e}")

        config = ScoringConfig()
        if config.params["risk_theme_scoring"]["method"] == "composite":
            # Compute combine score
            control_vec = embed_text(ctrl.text)
            for item in data.taxonomy:
                taxonomy_vec = embed_text(item.name)
                item.score = compute_combined_score(item.score, control_vec, taxonomy_vec)

        # Process results
        SCORE_THRESHOLD = config.params["risk_theme_scoring"]["score_threshold"]
        items = sorted(data.taxonomy, key=lambda x: x.score, reverse=True)[:3]
        valid_items = [item for item in items if item.score >= SCORE_THRESHOLD]

        classifications = [
            ThemeClassification(
                name=i.name, 
                id=i.id, 
                score=Score(value=i.score), 
                reasoning=i.reasoning
            )
            for i in valid_items
        ]

        return [classification.to_dict() for classification in classifications]