import pytest
from pydantic import ValidationError

from mapper_api.infrastructure.azure.blob_definitions_repo import BlobDefinitionsRepository
from mapper_api.config.settings import Settings


@pytest.mark.integration
def test_blob_definitions_repo_live_reads_from_azure():
    try:
        settings = Settings()
    except ValidationError as e:
        # Skip test if required environment variables are not set
        missing_fields = [error['loc'][0] for error in e.errors() if error['type'] == 'missing']
        pytest.skip(f"Missing env vars for live Azure blob test: {', '.join(missing_fields)}")

    repo = BlobDefinitionsRepository(
        account_name=settings.STORAGE_ACCOUNT_NAME,
        container_name=settings.STORAGE_CONTAINER_NAME,
        tenant_id=settings.AZURE_TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET,
    )

    risk_themes = repo.get_risk_themes()
    fivews = repo.get_fivews_rows()

    assert isinstance(themes, (list, tuple))
    assert isinstance(fivews, (list, tuple))

    # Expect non-empty datasets if the blobs exist
    assert len(themes) > 0, "taxonomy.json should yield at least one row"
    assert len(fivews) == 5, "5ws.json should yield exactly five definitions"

    # Validate one theme row has expected attributes
    row = themes[0]
    assert hasattr(row, 'cluster_id') and isinstance(row.cluster_id, int)
    assert hasattr(row, 'taxonomy_id') and isinstance(row.taxonomy_id, int)
    assert hasattr(row, 'taxonomy') and isinstance(row.taxonomy, str)
    assert hasattr(row, 'risk_theme_id') and isinstance(row.risk_theme_id, int)
    assert hasattr(row, 'risk_theme') and isinstance(row.risk_theme, str)

    # Validate fivews order and keys
    order = ["who", "what", "when", "where", "why"]
    assert [i['name'] for i in fivews] == order
    assert all('description' in i and isinstance(i['description'], str) for i in fivews)



