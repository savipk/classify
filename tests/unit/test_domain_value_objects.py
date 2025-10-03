"""Tests for domain value objects."""
import pytest
from pydantic import ValidationError
from mapper_api.domain.value_objects.fivew import FiveWName, FiveWStatus
from mapper_api.domain.value_objects.score import Score
from mapper_api.domain.value_objects.classification import ThemeClassification


class TestFiveWEnums:
    """Test 5W enum values."""
    
    def test_fivew_name_values(self):
        """Test all FiveWName enum values."""
        assert FiveWName.WHO == "who"
        assert FiveWName.WHAT == "what"
        assert FiveWName.WHEN == "when"
        assert FiveWName.WHERE == "where"
        assert FiveWName.WHY == "why"
    
    def test_fivew_status_values(self):
        """Test all FiveWStatus enum values."""
        assert FiveWStatus.PRESENT == "present"
        assert FiveWStatus.MISSING == "missing"


class TestScore:
    """Test Score value object with Pydantic V2 validation."""
    
    def test_valid_scores(self):
        """Test valid score creation."""
        assert Score(value=0.0).value == 0.0
        assert Score(value=1.0).value == 1.0
        assert Score(value=0.5).value == 0.5
        assert Score(value=0.99).value == 0.99
        assert Score(value=0.01).value == 0.01
    
    def test_invalid_score_negative(self):
        """Test validation of negative scores."""
        with pytest.raises(ValidationError):
            Score(value=-0.1)
        
        with pytest.raises(ValidationError):
            Score(value=-1.0)
    
    def test_invalid_score_too_high(self):
        """Test validation of scores above 1.0."""
        with pytest.raises(ValidationError):
            Score(value=1.1)
        
        with pytest.raises(ValidationError):
            Score(value=2.0)
    
    def test_immutability(self):
        """Test that Score objects are immutable."""
        score = Score(value=0.5)
        with pytest.raises(ValidationError):
            score.value = 0.8  # type: ignore
    
    def test_equality(self):
        """Test Score equality comparison."""
        assert Score(value=0.5) == Score(value=0.5)
        assert Score(value=0.5) != Score(value=0.6)
    
    def test_float_conversion(self):
        """Test Score to float conversion."""
        score = Score(value=0.75)
        assert float(score) == 0.75
    
    def test_to_dict(self):
        """Test Score serialization."""
        score = Score(value=0.85)
        expected = {"value": 0.85}
        assert score.to_dict() == expected


class TestThemeClassification:
    """Test ThemeClassification value object with Pydantic V2."""
    
    def test_valid_creation(self):
        """Test valid ThemeClassification creation."""
        score = Score(value=0.85)
        classification = ThemeClassification(
            name="Data Privacy Risk",
            id=123,
            score=score,
            reasoning="Strong indicators of data privacy concerns"
        )
        
        assert classification.name == "Data Privacy Risk"
        assert classification.id == 123
        assert classification.score == score
        assert classification.reasoning == "Strong indicators of data privacy concerns"
    
    def test_immutability(self):
        """Test that ThemeClassification objects are immutable."""
        score = Score(value=0.85)
        classification = ThemeClassification(
            name="Test Theme",
            id=1,
            score=score,
            reasoning="Test reasoning"
        )
        
        with pytest.raises(ValidationError):
            classification.name = "Modified Theme"  # type: ignore
    
    def test_to_dict(self):
        """Test ThemeClassification serialization."""
        score = Score(value=0.75)
        classification = ThemeClassification(
            name="Security Risk",
            id=456,
            score=score,
            reasoning="Security indicators found"
        )
        
        expected = {
            "name": "Security Risk",
            "id": 456,
            "score": 0.75,
            "reasoning": "Security indicators found"
        }
        assert classification.to_dict() == expected
    
    def test_with_invalid_score(self):
        """Test ThemeClassification with invalid score."""
        with pytest.raises(ValidationError):
            ThemeClassification(
                name="Test Theme",
                id=1,
                score=Score(value=1.5),  # This should fail at Score level
                reasoning="Test reasoning"
            )