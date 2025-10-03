"""HTTP router for POST /evaluator."""
from __future__ import annotations
from fastapi import APIRouter

from mapper_api.application.dto.http_evaluation import EvaluationHttpRequest
from mapper_api.application.dto.http_evaluation import EvaluationResponse
from mapper_api.config.settings import Settings
from mapper_api.infrastructure.azure.blob_definitions_repo import BlobDefinitionsRepository
from mapper_api.infrastructure.azure.blob_ground_truth_repo import BlobGroundTruthRepository
from mapper_api.infrastructure.azure.blob_evaluation_results_writer import BlobEvaluationResultsWriter
from mapper_api.infrastructure.azure.openai_client import AzureOpenAILLMClient
from mapper_api.application.use_cases.map_control_to_themes import ClassifyControlToThemes
from mapper_api.application.use_cases.map_control_to_5ws import ClassifyControlTo5Ws
from mapper_api.application.use_cases.evaluate_mapper import EvaluateMapper
from mapper_api.domain.services.evaluation_service import EvaluationService
from mapper_api.interface.controllers.evaluation_controller import EvaluationController

router = APIRouter()


def get_evaluation_controller() -> EvaluationController:
    """
    Factory to create evaluation controller with dependencies.
    Following EcomApp's pattern of in-place dependency assembly.
    """
    # Load settings
    settings = Settings()
    
    # Create infrastructure adapters
    definitions_repo = BlobDefinitionsRepository(
        account_name=settings.STORAGE_ACCOUNT_NAME,
        container_name=settings.STORAGE_CONTAINER_NAME,
        tenant_id=settings.AZURE_TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET,
    )
    
    ground_truth_repo = BlobGroundTruthRepository(
        account_name=settings.STORAGE_ACCOUNT_NAME,
        container_name=settings.STORAGE_CONTAINER_NAME,
        tenant_id=settings.AZURE_TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET,
    )
    
    results_writer = BlobEvaluationResultsWriter(
        account_name=settings.STORAGE_ACCOUNT_NAME,
        container_name=settings.STORAGE_CONTAINER_NAME,
        tenant_id=settings.AZURE_TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET,
    )
    
    llm_client = AzureOpenAILLMClient(
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
    )
    
    # Create domain service
    evaluation_service = EvaluationService()
    
    # Create existing use cases for making predictions
    taxonomy_classifier = ClassifyControlToThemes.from_defs(
        repo=definitions_repo,
        llm=llm_client
    )
    
    fivews_classifier = ClassifyControlTo5Ws.from_defs(
        repo=definitions_repo,
        llm=llm_client
    )
    
    # Create evaluation use case with dependencies
    evaluate_use_case = EvaluateMapper(
        ground_truth_repo=ground_truth_repo,
        evaluation_service=evaluation_service,
        taxonomy_classifier=taxonomy_classifier,
        fivews_classifier=fivews_classifier,
        llm_client=llm_client
    )
    
    # Create and return controller
    return EvaluationController(
        evaluate_use_case=evaluate_use_case,
        results_writer=results_writer
    )


@router.post('/evaluator', response_model=EvaluationResponse)
async def evaluator(req: EvaluationHttpRequest) -> EvaluationResponse:
    """
    Evaluate mapper predictions against ground truth data.
    
    Dependencies are created right here where they're used, making the flow
    transparent and easy to follow. This follows EcomApp's pattern.
    """
    controller = get_evaluation_controller()
    return controller.handle_evaluation(req)
