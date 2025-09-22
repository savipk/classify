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
