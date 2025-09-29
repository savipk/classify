from mapper_api.application.prompts import taxonomy, fivews
from mapper_api.domain.entities.risk_theme import RiskTheme


def test_taxonomy_prompt_contains_rows_and_control():
    risk_themes = [
        RiskTheme(
            cluster_id=1, cluster='A', taxonomy_id=1, taxonomy='NFR1', taxonomy_description='desc',
            id=10, name='Theme A', description='d', mapping_considerations='m'
        ),
        RiskTheme(
            cluster_id=2, cluster='B', taxonomy_id=2, taxonomy='NFR2', taxonomy_description='desc',
            id=20, name='Theme B', description='d', mapping_considerations='m'
        ),
    ]
    prompt = taxonomy.build_user_prompt('control text', risk_themes)
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
