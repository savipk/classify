"""Tests for domain value objects."""
import pytest
from mapper_api.domain.value_objects.fivew import FiveWName, FiveWStatus, FiveWFinding, FiveWsSet
from mapper_api.domain.value_objects.score import Score, ThemeClassification


class TestFiveWFinding:
    """Test FiveWFinding value object."""
    
    def test_valid_creation(self):
        finding = FiveWFinding(
            name=FiveWName.WHO,
            status=FiveWStatus.PRESENT,
            reasoning="Valid reasoning"
        )
        assert finding.name == FiveWName.WHO
        assert finding.status == FiveWStatus.PRESENT
        assert finding.reasoning == "Valid reasoning"
    
    def test_immutability(self):
        finding = FiveWFinding(FiveWName.WHAT, FiveWStatus.MISSING, "test")
        with pytest.raises(AttributeError):
            finding.name = FiveWName.WHO  # type: ignore
    
    def test_enum_values(self):
        # Test all enum values work
        for name in FiveWName:
            for status in FiveWStatus:
                finding = FiveWFinding(name, status, "test")
                assert finding.name == name
                assert finding.status == status


class TestFiveWsSet:
    """Test FiveWsSet value object with invariants."""
    
    def test_valid_creation_correct_order(self):
        findings = tuple([
            FiveWFinding(FiveWName.WHO, FiveWStatus.PRESENT, "who reasoning"),
            FiveWFinding(FiveWName.WHAT, FiveWStatus.PRESENT, "what reasoning"),
            FiveWFinding(FiveWName.WHEN, FiveWStatus.MISSING, "when reasoning"),
            FiveWFinding(FiveWName.WHERE, FiveWStatus.PRESENT, "where reasoning"),
            FiveWFinding(FiveWName.WHY, FiveWStatus.PRESENT, "why reasoning"),
        ])
        fivews_set = FiveWsSet(findings)
        assert len(fivews_set.items) == 5
        assert fivews_set.items[0].name == FiveWName.WHO
        assert fivews_set.items[4].name == FiveWName.WHY
    
    def test_wrong_count_too_few(self):
        findings = tuple([
            FiveWFinding(FiveWName.WHO, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHAT, FiveWStatus.PRESENT, "reasoning"),
        ])
        with pytest.raises(ValueError, match="must contain exactly five findings"):
            FiveWsSet(findings)
    
    def test_wrong_count_too_many(self):
        findings = tuple([
            FiveWFinding(FiveWName.WHO, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHAT, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHEN, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHERE, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHY, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHO, FiveWStatus.PRESENT, "extra"),  # Extra item
        ])
        with pytest.raises(ValueError, match="must contain exactly five findings"):
            FiveWsSet(findings)
    
    def test_wrong_order(self):
        findings = tuple([
            FiveWFinding(FiveWName.WHAT, FiveWStatus.PRESENT, "reasoning"),  # Wrong order
            FiveWFinding(FiveWName.WHO, FiveWStatus.PRESENT, "reasoning"),   # Wrong order
            FiveWFinding(FiveWName.WHEN, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHERE, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHY, FiveWStatus.PRESENT, "reasoning"),
        ])
        with pytest.raises(ValueError, match="must be in order"):
            FiveWsSet(findings)
    
    def test_duplicate_names_validates_order_first(self):
        """Test that validation checks order before uniqueness."""
        findings = tuple([
            FiveWFinding(FiveWName.WHO, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHAT, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHEN, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHERE, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHO, FiveWStatus.MISSING, "different reasoning"),  # Duplicate WHO instead of WHY
        ])
        # Order check happens first, so we get order error even though names aren't unique
        with pytest.raises(ValueError, match="must be in order"):
            FiveWsSet(findings)
    
    def test_immutability(self):
        findings = tuple([
            FiveWFinding(FiveWName.WHO, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHAT, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHEN, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHERE, FiveWStatus.PRESENT, "reasoning"),
            FiveWFinding(FiveWName.WHY, FiveWStatus.PRESENT, "reasoning"),
        ])
        fivews_set = FiveWsSet(findings)
        with pytest.raises(AttributeError):
            fivews_set.items = tuple()  # type: ignore


class TestScore:
    """Test Score value object with validation."""
    
    def test_valid_scores(self):
        assert Score(0.0).value == 0.0
        assert Score(1.0).value == 1.0
        assert Score(0.5).value == 0.5
        assert Score(0.99).value == 0.99
        assert Score(0.01).value == 0.01
    
    def test_invalid_score_negative(self):
        with pytest.raises(ValueError, match="score must be between 0 and 1 inclusive"):
            Score(-0.1)
        
        with pytest.raises(ValueError, match="score must be between 0 and 1 inclusive"):
            Score(-1.0)
    
    def test_invalid_score_too_high(self):
        with pytest.raises(ValueError, match="score must be between 0 and 1 inclusive"):
            Score(1.1)
        
        with pytest.raises(ValueError, match="score must be between 0 and 1 inclusive"):
            Score(2.0)
    
    def test_immutability(self):
        score = Score(0.5)
        with pytest.raises(AttributeError):
            score.value = 0.8  # type: ignore
    
    def test_equality(self):
        assert Score(0.5) == Score(0.5)
        assert Score(0.5) != Score(0.6)


class TestThemeClassification:
    """Test ThemeClassification value object."""
    
    def test_valid_creation(self):
        classification = ThemeClassification(
            name="Test Theme",
            id=123,
            score=Score(0.85),
            reasoning="Strong match"
        )
        assert classification.name == "Test Theme"
        assert classification.id == 123
        assert classification.score.value == 0.85
        assert classification.reasoning == "Strong match"
    
    def test_immutability(self):
        classification = ThemeClassification("Test", 1, Score(0.5), "reasoning")
        with pytest.raises(AttributeError):
            classification.name = "Changed"  # type: ignore
    
    def test_with_invalid_score(self):
        with pytest.raises(ValueError, match="score must be between 0 and 1 inclusive"):
            ThemeClassification("Test", 1, Score(1.5), "reasoning")
