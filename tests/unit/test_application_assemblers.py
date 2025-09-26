"""Tests for application assemblers."""
import pytest
from mapper_api.application.mappers.assemblers import assemble_taxonomy_items
from mapper_api.domain.value_objects.score import Score
from mapper_api.domain.value_objects.classification import ThemeClassification


class TestAssembleTaxonomyItems:
    """Test assembler for taxonomy classifications."""
    
    def test_assemble_single_classification(self):
        classification = ThemeClassification(
            name="Data Encryption",
            id=101,
            score=Score(0.85),
            reasoning="Strong match for encryption requirements"
        )
        
        result = assemble_taxonomy_items([classification])
        
        assert len(result) == 1
        assert result[0] == {
            "name": "Data Encryption",
            "id": 101,
            "score": 0.85,
            "reasoning": "Strong match for encryption requirements"
        }
    
    def test_assemble_multiple_classifications(self):
        classifications = [
            ThemeClassification(
                name="Data Encryption",
                id=101,
                score=Score(0.85),
                reasoning="Strong match"
            ),
            ThemeClassification(
                name="Access Control",
                id=102,
                score=Score(0.72),
                reasoning="Moderate match"
            ),
            ThemeClassification(
                name="Audit Logging",
                id=103,
                score=Score(0.45),
                reasoning="Weak match"
            ),
        ]
        
        result = assemble_taxonomy_items(classifications)
        
        assert len(result) == 3
        assert result[0]["name"] == "Data Encryption"
        assert result[0]["score"] == 0.85
        assert result[1]["name"] == "Access Control"
        assert result[1]["score"] == 0.72
        assert result[2]["name"] == "Audit Logging"
        assert result[2]["score"] == 0.45
    
    def test_assemble_empty_list(self):
        result = assemble_taxonomy_items([])
        assert result == []
    
    def test_score_conversion_to_float(self):
        classification = ThemeClassification(
            name="Test Theme",
            id=1,
            score=Score(0.123456789),  # High precision
            reasoning="test"
        )
        
        result = assemble_taxonomy_items([classification])
        
        # Should be converted to float
        assert isinstance(result[0]["score"], float)
        assert result[0]["score"] == 0.123456789
    
    def test_score_boundary_values(self):
        classifications = [
            ThemeClassification(
                name="Min Score",
                id=1,
                score=Score(0.0),
                reasoning="minimum"
            ),
            ThemeClassification(
                name="Max Score",
                id=2,
                score=Score(1.0),
                reasoning="maximum"
            ),
        ]
        
        result = assemble_taxonomy_items(classifications)
        
        assert result[0]["score"] == 0.0
        assert result[1]["score"] == 1.0
    
    def test_preserve_all_fields(self):
        classification = ThemeClassification(
            name="Complex Theme Name with Special Chars éñ🔒",
            id=999,
            score=Score(0.5),
            reasoning="Complex reasoning with special chars éñ🔒 and multiple lines\nSecond line"
        )
        
        result = assemble_taxonomy_items([classification])
        
        assert result[0]["name"] == "Complex Theme Name with Special Chars éñ🔒"
        assert result[0]["id"] == 999
        assert result[0]["score"] == 0.5
        assert result[0]["reasoning"] == "Complex reasoning with special chars éñ🔒 and multiple lines\nSecond line"
    
    def test_preserves_order(self):
        classifications = [
            ThemeClassification(name="Third", id=3, score=Score(0.3), reasoning="third"),
            ThemeClassification(name="First", id=1, score=Score(0.1), reasoning="first"), 
            ThemeClassification(name="Second", id=2, score=Score(0.2), reasoning="second"),
        ]
        
        result = assemble_taxonomy_items(classifications)
        
        # Should preserve the input order (not sort by score)
        assert result[0]["name"] == "Third"
        assert result[1]["name"] == "First"
        assert result[2]["name"] == "Second"
    
    def test_large_number_of_classifications(self):
        classifications = []
        for i in range(100):
            classifications.append(
                ThemeClassification(
                    name=f"Theme {i}",
                    id=i,
                    score=Score(i / 100.0),  # Score from 0.0 to 0.99
                    reasoning=f"reasoning {i}"
                )
            )
        
        result = assemble_taxonomy_items(classifications)
        
        assert len(result) == 100
        assert result[0]["name"] == "Theme 0"
        assert result[99]["name"] == "Theme 99"
        assert result[99]["score"] == 0.99
    
    def test_return_type_is_list_of_dicts(self):
        classification = ThemeClassification(
            name="Test",
            id=1,
            score=Score(0.5),
            reasoning="test"
        )
        
        result = assemble_taxonomy_items([classification])
        
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert all(key in result[0] for key in ["name", "id", "score", "reasoning"])
    
    def test_iterator_compatibility(self):
        """Test that it works with any iterable, not just lists."""
        classifications = (
            ThemeClassification(name=f"Theme {i}", id=i, score=Score(0.5), reasoning="test")
            for i in range(3)  # Generator
        )
        
        result = assemble_taxonomy_items(classifications)
        
        assert len(result) == 3
        assert result[0]["name"] == "Theme 0"
        assert result[1]["name"] == "Theme 1"
        assert result[2]["name"] == "Theme 2"
