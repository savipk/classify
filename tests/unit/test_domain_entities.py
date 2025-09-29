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
            description="Encryption of sensitive data",
            taxonomy_id=101,
            taxonomy="NFR-Authentication",
            taxonomy_description="Authentication requirements",
            cluster="Security",
            cluster_id=1,
            mapping_considerations="Consider data sensitivity"
        )
        assert risk_theme.id == 201
        assert risk_theme.name == "Data Encryption"
        assert risk_theme.taxonomy_id == 101
        assert risk_theme.taxonomy == "NFR-Authentication"
        assert risk_theme.cluster == "Security"
        assert risk_theme.cluster_id == 1
    
    def test_immutability(self):
        risk_theme = RiskTheme(
            id=1, 
            name="Test", 
            description="Test description",
            taxonomy_id=1, 
            taxonomy="Tax", 
            taxonomy_description="Tax desc",
            cluster="Cluster", 
            cluster_id=1,
            mapping_considerations="Test considerations"
        )
        with pytest.raises(AttributeError):
            risk_theme.name = "Changed"  # type: ignore
    
    def test_equality(self):
        theme1 = RiskTheme(
            id=1, name="Test", description="desc", taxonomy_id=1, taxonomy="Tax", 
            taxonomy_description="tax desc", cluster="Cluster", cluster_id=1, 
            mapping_considerations="considerations"
        )
        theme2 = RiskTheme(
            id=1, name="Test", description="desc", taxonomy_id=1, taxonomy="Tax", 
            taxonomy_description="tax desc", cluster="Cluster", cluster_id=1, 
            mapping_considerations="considerations"
        )
        theme3 = RiskTheme(
            id=2, name="Test", description="desc", taxonomy_id=1, taxonomy="Tax", 
            taxonomy_description="tax desc", cluster="Cluster", cluster_id=1, 
            mapping_considerations="considerations"
        )
        
        assert theme1 == theme2
        assert theme1 != theme3
    
    def test_relationships(self):
        """Test that foreign key relationships are preserved."""
        risk_theme = RiskTheme(
            id=1,
            name="Theme",
            description="Theme description",
            taxonomy_id=101,
            taxonomy="Tax Name",
            taxonomy_description="Tax description",
            cluster="Cluster Name",
            cluster_id=10,
            mapping_considerations="Mapping considerations"
        )
        
        assert risk_theme.belongs_to_taxonomy(101) is True
        assert risk_theme.belongs_to_taxonomy(999) is False
        assert risk_theme.belongs_to_cluster(10) is True
        assert risk_theme.belongs_to_cluster(999) is False

    def test_ensure_minimum_length_valid_exactly_50(self):
        """Test minimum length validation with exactly 50 characters."""
        text_50_chars = "This is exactly fifty characters long for testing."
        assert len(text_50_chars) == 50
        control = Control(text=text_50_chars)
        control.ensure_minimum_length()  # Should not raise

    def test_ensure_minimum_length_valid_over_50(self):
        """Test minimum length validation with more than 50 characters."""
        text_over_50 = "This is a much longer text that definitely exceeds the minimum required length of fifty characters."
        control = Control(text=text_over_50)
        control.ensure_minimum_length()  # Should not raise

    def test_ensure_minimum_length_fails_short(self):
        """Test minimum length validation fails for short text."""
        short_text = "Short"
        control = Control(text=short_text)
        with pytest.raises(ValueError, match="control description must be at least 50 characters long"):
            control.ensure_minimum_length()

    def test_ensure_minimum_length_with_whitespace(self):
        """Test minimum length validation handles whitespace correctly."""
        text_with_spaces = "   This text has leading and trailing spaces but is long enough   "
        control = Control(text=text_with_spaces)
        control.ensure_minimum_length()  # Should not raise (strips whitespace for length check)

    def test_ensure_is_english_valid(self):
        """Test English language validation with valid English text."""
        english_text = "This is a valid English control description that should pass language detection."
        control = Control(text=english_text)
        control.ensure_is_english()  # Should not raise

    def test_ensure_is_english_fails_spanish(self):
        """Test English language validation fails for Spanish text."""
        spanish_text = "Este es un texto en español que debería fallar la validación de idioma inglés."
        control = Control(text=spanish_text)
        with pytest.raises(ValueError, match="control description must be in English"):
            control.ensure_is_english()

    def test_ensure_is_english_fails_french(self):
        """Test English language validation fails for French text."""
        french_text = "Ceci est un texte en français qui devrait échouer à la validation de langue anglaise."
        control = Control(text=french_text)
        with pytest.raises(ValueError, match="control description must be in English"):
            control.ensure_is_english()

    def test_ensure_is_english_handles_mixed_content(self):
        """Test English language validation with mixed content."""
        mixed_text = "This English text contains some numbers 123 and symbols @#$ which should still be detected as English."
        control = Control(text=mixed_text)
        control.ensure_is_english()  # Should not raise

    def test_validate_all_success(self):
        """Test that validate_all passes for valid English text over 50 characters."""
        valid_text = "This is a comprehensive English control description that meets all validation requirements including minimum length."
        control = Control(text=valid_text)
        control.validate_all()  # Should not raise

    def test_validate_all_fails_empty(self):
        """Test that validate_all fails for empty text."""
        control = Control(text="")
        with pytest.raises(ValueError, match="control description must not be empty"):
            control.validate_all()

    def test_validate_all_fails_short(self):
        """Test that validate_all fails for text under 50 characters."""
        control = Control(text="Short English text")
        with pytest.raises(ValueError, match="control description must be at least 50 characters long"):
            control.validate_all()

    def test_validate_all_fails_non_english(self):
        """Test that validate_all fails for non-English text even if long enough."""
        spanish_text = "Este es un texto muy largo en español que tiene más de cincuenta caracteres pero no está en inglés."
        control = Control(text=spanish_text)
        with pytest.raises(ValueError, match="control description must be in English"):
            control.validate_all()

    def test_min_length_constant(self):
        """Test that MIN_LENGTH constant is properly defined."""
        assert Control.MIN_LENGTH == 50
