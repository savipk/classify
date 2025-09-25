"""Tests for domain entities."""
import pytest
from mapper_api.domain.entities.control import Control
from mapper_api.domain.entities.cluster import Cluster
from mapper_api.domain.entities.taxonomy import Taxonomy
from mapper_api.domain.entities.risk_theme import RiskTheme


class TestControl:
    """Test Control entity."""
    
    def test_valid_creation_with_text_only(self):
        control = Control(text="This is a control description")
        assert control.text == "This is a control description"
        assert control.id is None
    
    def test_valid_creation_with_text_and_id(self):
        control = Control(text="Control description", id="CTRL-001")
        assert control.text == "Control description"
        assert control.id == "CTRL-001"
    
    def test_ensure_not_empty_valid(self):
        control = Control(text="Valid control text")
        # Should not raise
        control.ensure_not_empty()
    
    def test_ensure_not_empty_fails_on_empty_string(self):
        control = Control(text="")
        with pytest.raises(ValueError, match="control description must not be empty"):
            control.ensure_not_empty()
    
    def test_ensure_not_empty_fails_on_whitespace_only(self):
        control = Control(text="   \t\n  ")
        with pytest.raises(ValueError, match="control description must not be empty"):
            control.ensure_not_empty()
    
    def test_immutability(self):
        control = Control(text="test")
        with pytest.raises(AttributeError):
            control.text = "changed"  # type: ignore
    
    def test_long_text(self):
        long_text = "A" * 10000
        control = Control(text=long_text)
        assert control.text == long_text
        control.ensure_not_empty()  # Should not raise
    
    def test_special_characters(self):
        special_text = "Control with émojis 🔒 and ñumbers 123 & symbols!@#$%"
        control = Control(text=special_text)
        assert control.text == special_text
        control.ensure_not_empty()  # Should not raise


class TestCluster:
    """Test Cluster entity."""
    
    def test_valid_creation(self):
        cluster = Cluster(id=1, name="Test Cluster")
        assert cluster.id == 1
        assert cluster.name == "Test Cluster"
    
    def test_immutability(self):
        cluster = Cluster(id=1, name="Test")
        with pytest.raises(AttributeError):
            cluster.id = 2  # type: ignore
        with pytest.raises(AttributeError):
            cluster.name = "Changed"  # type: ignore
    
    def test_equality(self):
        cluster1 = Cluster(id=1, name="Test")
        cluster2 = Cluster(id=1, name="Test")
        cluster3 = Cluster(id=2, name="Test")
        
        assert cluster1 == cluster2
        assert cluster1 != cluster3


class TestTaxonomy:
    """Test Taxonomy entity."""
    
    def test_valid_creation(self):
        taxonomy = Taxonomy(
            id=101,
            name="NFR-Authentication",
            description="Authentication requirements",
            cluster_id=1
        )
        assert taxonomy.id == 101
        assert taxonomy.name == "NFR-Authentication"
        assert taxonomy.description == "Authentication requirements"
        assert taxonomy.cluster_id == 1
    
    def test_immutability(self):
        taxonomy = Taxonomy(id=1, name="Test", description="desc", cluster_id=1)
        with pytest.raises(AttributeError):
            taxonomy.name = "Changed"  # type: ignore
    
    def test_equality(self):
        tax1 = Taxonomy(id=1, name="Test", description="desc", cluster_id=1)
        tax2 = Taxonomy(id=1, name="Test", description="desc", cluster_id=1)
        tax3 = Taxonomy(id=2, name="Test", description="desc", cluster_id=1)
        
        assert tax1 == tax2
        assert tax1 != tax3


class TestRiskTheme:
    """Test RiskTheme entity."""
    
    def test_valid_creation(self):
        risk_theme = RiskTheme(
            id=201,
            name="Data Encryption",
            taxonomy_id=101,
            taxonomy="NFR-Authentication",
            cluster="Security",
            cluster_id=1
        )
        assert risk_theme.id == 201
        assert risk_theme.name == "Data Encryption"
        assert risk_theme.taxonomy_id == 101
        assert risk_theme.taxonomy == "NFR-Authentication"
        assert risk_theme.cluster == "Security"
        assert risk_theme.cluster_id == 1
    
    def test_immutability(self):
        risk_theme = RiskTheme(
            id=1, name="Test", taxonomy_id=1, taxonomy="Tax", cluster="Cluster", cluster_id=1
        )
        with pytest.raises(AttributeError):
            risk_theme.name = "Changed"  # type: ignore
    
    def test_equality(self):
        theme1 = RiskTheme(id=1, name="Test", taxonomy_id=1, taxonomy="Tax", cluster="Cluster", cluster_id=1)
        theme2 = RiskTheme(id=1, name="Test", taxonomy_id=1, taxonomy="Tax", cluster="Cluster", cluster_id=1)
        theme3 = RiskTheme(id=2, name="Test", taxonomy_id=1, taxonomy="Tax", cluster="Cluster", cluster_id=1)
        
        assert theme1 == theme2
        assert theme1 != theme3
    
    def test_relationships(self):
        """Test that foreign key relationships are preserved."""
        risk_theme = RiskTheme(
            id=1,
            name="Theme",
            taxonomy_id=101,
            taxonomy="Tax Name",
            cluster="Cluster Name",
            cluster_id=10
        )
        # Verify the relationship fields are accessible
        assert risk_theme.taxonomy_id == 101
        assert risk_theme.cluster_id == 10

    def test_ensure_minimum_length_valid_exactly_50(self):
        """Test minimum length validation with exactly 50 characters."""
        control = Control(text="A" * 50)  # Exactly 50 chars
        control.ensure_minimum_length()  # Should not raise
    
    def test_ensure_minimum_length_valid_over_50(self):
        """Test minimum length validation with more than 50 characters."""
        control = Control(text="This is a control description that is definitely longer than fifty characters and should pass validation.")
        control.ensure_minimum_length()  # Should not raise
    
    def test_ensure_minimum_length_fails_short(self):
        """Test minimum length validation fails for short text."""
        control = Control(text="Short control description")  # Only 25 chars
        with pytest.raises(ValueError, match="must be at least 50 characters long, got 25"):
            control.ensure_minimum_length()
    
    def test_ensure_minimum_length_with_whitespace(self):
        """Test minimum length validation handles whitespace correctly."""
        control = Control(text="   Short   ")  # Only 5 chars after strip
        with pytest.raises(ValueError, match="must be at least 50 characters long, got 5"):
            control.ensure_minimum_length()
    
    def test_ensure_is_english_valid(self):
        """Test English language validation with valid English text."""
        control = Control(text="This is a valid English control description with proper length and grammar.")
        control.ensure_is_english()  # Should not raise
    
    def test_ensure_is_english_fails_spanish(self):
        """Test English language validation fails for Spanish text."""
        control = Control(text="Esta es una descripción de control en español que es suficientemente larga para cumplir con los requisitos.")
        with pytest.raises(ValueError, match="must be in English, detected language: es"):
            control.ensure_is_english()
    
    def test_ensure_is_english_fails_french(self):
        """Test English language validation fails for French text."""
        control = Control(text="Ceci est une description de contrôle en français qui est suffisamment longue pour répondre aux exigences.")
        with pytest.raises(ValueError, match="must be in English, detected language: fr"):
            control.ensure_is_english()
    
    def test_ensure_is_english_handles_mixed_content(self):
        """Test English validation with mostly English text containing few foreign words."""
        # This should pass as it's predominantly English
        control = Control(text="This is an English control description with occasional foreign terms like 'résumé' but is primarily English.")
        control.ensure_is_english()  # Should not raise
    
    def test_validate_all_success(self):
        """Test that validate_all passes for valid control description."""
        control = Control(text="This is a comprehensive English control description that meets all validation requirements including proper length and language.")
        control.validate_all()  # Should not raise
    
    def test_validate_all_fails_empty(self):
        """Test that validate_all fails for empty control description."""
        control = Control(text="")
        with pytest.raises(ValueError, match="control description must not be empty"):
            control.validate_all()
    
    def test_validate_all_fails_short(self):
        """Test that validate_all fails for short control description."""
        control = Control(text="Too short")
        with pytest.raises(ValueError, match="must be at least 50 characters long"):
            control.validate_all()
    
    def test_validate_all_fails_non_english(self):
        """Test that validate_all fails for non-English control description."""
        control = Control(text="Esta es una descripción de control muy completa en español que tiene la longitud suficiente.")
        with pytest.raises(ValueError, match="must be in English"):
            control.validate_all()
    
    def test_min_length_constant(self):
        """Test that MIN_LENGTH constant is properly set."""
        assert Control.MIN_LENGTH == 50
