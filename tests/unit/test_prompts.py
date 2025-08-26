from mapper_api.application.prompts import taxonomy, fivews
from mapper_api.domain.repositories.definitions import ThemeRow


def test_taxonomy_prompt_contains_rows_and_control():
    rows = [
        ThemeRow(cluster_id=1, cluster='A', taxonomy_id=1, taxonomy='NFR1', taxonomy_description='desc',
                 risk_theme_id=10, risk_theme='Theme A', risk_theme_description='d', mapping_considerations='m'),
        ThemeRow(cluster_id=2, cluster='B', taxonomy_id=2, taxonomy='NFR2', taxonomy_description='desc',
                 risk_theme_id=20, risk_theme='Theme B', risk_theme_description='d', mapping_considerations='m'),
    ]
    prompt = taxonomy.build_user_prompt('control text', rows)
    assert 'Theme A' in prompt and 'Theme B' in prompt
    assert 'control text' in prompt


def test_fivews_prompt_contains_defs_and_control():
    defs = [
        {"name": "who", "description": "who desc"},
        {"name": "what", "description": "what desc"},
    ]
    prompt = fivews.build_user_prompt('control text', defs)
    assert 'who desc' in prompt and 'what desc' in prompt
    assert 'control text' in prompt
