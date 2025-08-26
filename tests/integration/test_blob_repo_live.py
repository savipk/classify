import os
import pytest

from mapper_api.infrastructure.azure.blob_definitions_repo import BlobDefinitionsRepository


def _env(name: str) -> str | None:
    v = os.environ.get(name)
    return v if v and v.strip() else None


@pytest.mark.integration
def test_blob_definitions_repo_live_reads_from_azure():
    required = {
        'STORAGE_ACCOUNT_NAME': _env('STORAGE_ACCOUNT_NAME'),
        'STORAGE_CONTAINER_NAME': _env('STORAGE_CONTAINER_NAME'),
        'AZURE_TENANT_ID': _env('AZURE_TENANT_ID'),
        'AZURE_CLIENT_ID': _env('AZURE_CLIENT_ID'),
        'AZURE_CLIENT_SECRET': _env('AZURE_CLIENT_SECRET'),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        pytest.skip(f"Missing env vars for live Azure blob test: {', '.join(missing)}")

    repo = BlobDefinitionsRepository(
        account_name=required['STORAGE_ACCOUNT_NAME'],
        container_name=required['STORAGE_CONTAINER_NAME'],
        tenant_id=required['AZURE_TENANT_ID'],
        client_id=required['AZURE_CLIENT_ID'],
        client_secret=required['AZURE_CLIENT_SECRET'],
    )

    themes = repo.get_theme_rows()
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



