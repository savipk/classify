"""Tests for application DTO and schema classes."""
import pytest
import json
from pydantic import ValidationError
from mapper_api.application.dto.llm_schemas import build_taxonomy_models, FiveWItem, FiveWOut


class TestBuildTaxonomyModels:
    """Test dynamic taxonomy model building."""
    
    def test_build_with_valid_names(self):
        allowed_names = ["Theme A", "Theme B", "Theme C"]
        TaxonomyItem, TaxonomyOut = build_taxonomy_models(allowed_names)
        
        # Test valid item creation
        item = TaxonomyItem(
            name="Theme A",
            id=1,
            score=0.85,
            reasoning="Strong match"
        )
        assert item.name == "Theme A"
        assert item.score == 0.85
    
    def test_build_with_empty_names_list(self):
        # Empty names list should raise error during model creation
        allowed_names = []
        
        # Should fail to create the model since Literal[()] is invalid
        with pytest.raises(AssertionError, match='literal "expected" cannot be empty'):
            TaxonomyItem, TaxonomyOut = build_taxonomy_models(allowed_names)
    
    def test_taxonomy_item_rejects_invalid_name(self):
        allowed_names = ["Theme A", "Theme B"]
        TaxonomyItem, TaxonomyOut = build_taxonomy_models(allowed_names)
        
        # Should reject names not in allowed list
        with pytest.raises(ValidationError):
            TaxonomyItem(
                name="Theme C",  # Not in allowed list
                id=1,
                score=0.5,
                reasoning="test"
            )
    
    def test_taxonomy_item_score_validation(self):
        allowed_names = ["Theme A"]
        TaxonomyItem, TaxonomyOut = build_taxonomy_models(allowed_names)
        
        # Test score bounds
        with pytest.raises(ValidationError):
            TaxonomyItem(name="Theme A", id=1, score=-0.1, reasoning="test")
        
        with pytest.raises(ValidationError):
            TaxonomyItem(name="Theme A", id=1, score=1.1, reasoning="test")
        
        # Valid scores should work
        item1 = TaxonomyItem(name="Theme A", id=1, score=0.0, reasoning="test")
        item2 = TaxonomyItem(name="Theme A", id=1, score=1.0, reasoning="test")
        assert item1.score == 0.0
        assert item2.score == 1.0
    
    def test_taxonomy_out_requires_exactly_three_items(self):
        allowed_names = ["Theme A", "Theme B", "Theme C", "Theme D"]
        TaxonomyItem, TaxonomyOut = build_taxonomy_models(allowed_names)
        
        # Too few items
        with pytest.raises(ValidationError):
            TaxonomyOut(taxonomy=[
                TaxonomyItem(name="Theme A", id=1, score=0.5, reasoning="test")
            ])
        
        # Too many items
        with pytest.raises(ValidationError):
            TaxonomyOut(taxonomy=[
                TaxonomyItem(name="Theme A", id=1, score=0.5, reasoning="test"),
                TaxonomyItem(name="Theme B", id=2, score=0.4, reasoning="test"),
                TaxonomyItem(name="Theme C", id=3, score=0.3, reasoning="test"),
                TaxonomyItem(name="Theme D", id=4, score=0.2, reasoning="test"),  # Too many
            ])
        
        # Exactly three should work
        taxonomy_out = TaxonomyOut(taxonomy=[
            TaxonomyItem(name="Theme A", id=1, score=0.5, reasoning="test"),
            TaxonomyItem(name="Theme B", id=2, score=0.4, reasoning="test"),
            TaxonomyItem(name="Theme C", id=3, score=0.3, reasoning="test"),
        ])
        assert len(taxonomy_out.taxonomy) == 3
    
    def test_large_number_of_allowed_names(self):
        # Test performance with many allowed names
        allowed_names = [f"Theme {i}" for i in range(100)]
        TaxonomyItem, TaxonomyOut = build_taxonomy_models(allowed_names)
        
        # Should still work with valid names
        item = TaxonomyItem(
            name="Theme 42",
            id=42,
            score=0.5,
            reasoning="test"
        )
        assert item.name == "Theme 42"
    
    def test_special_characters_in_names(self):
        allowed_names = ["Théme Â", "Theme with 🔒", "Theme-with-dashes"]
        TaxonomyItem, TaxonomyOut = build_taxonomy_models(allowed_names)
        
        item = TaxonomyItem(
            name="Théme Â",
            id=1,
            score=0.5,
            reasoning="test"
        )
        assert item.name == "Théme Â"


class TestFiveWItem:
    """Test FiveWItem validation."""
    
    def test_valid_creation(self):
        item = FiveWItem(
            name="who",
            status="present",
            reasoning="Clear identification"
        )
        assert item.name == "who"
        assert item.status == "present"
        assert item.reasoning == "Clear identification"
    
    def test_all_valid_names(self):
        valid_names = ["who", "what", "when", "where", "why"]
        for name in valid_names:
            item = FiveWItem(name=name, status="present", reasoning="test")
            assert item.name == name
    
    def test_all_valid_statuses(self):
        valid_statuses = ["present", "missing"]
        for status in valid_statuses:
            item = FiveWItem(name="who", status=status, reasoning="test")
            assert item.status == status
    
    def test_invalid_name_rejected(self):
        with pytest.raises(ValidationError):
            FiveWItem(name="invalid", status="present", reasoning="test")
    
    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            FiveWItem(name="who", status="invalid", reasoning="test")
    
    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError):
            FiveWItem(
                name="who",
                status="present", 
                reasoning="test",
                extra_field="not allowed"  # type: ignore
            )


class TestFiveWOut:
    """Test FiveWOut validation."""
    
    def test_valid_creation_with_five_items(self):
        items = [
            FiveWItem(name="who", status="present", reasoning="test"),
            FiveWItem(name="what", status="present", reasoning="test"),
            FiveWItem(name="when", status="missing", reasoning="test"),
            FiveWItem(name="where", status="present", reasoning="test"),
            FiveWItem(name="why", status="present", reasoning="test"),
        ]
        five_w_out = FiveWOut(fivews=items)
        assert len(five_w_out.fivews) == 5
    
    def test_too_few_items_rejected(self):
        items = [
            FiveWItem(name="who", status="present", reasoning="test"),
            FiveWItem(name="what", status="present", reasoning="test"),
        ]
        with pytest.raises(ValidationError):
            FiveWOut(fivews=items)
    
    def test_too_many_items_rejected(self):
        items = [
            FiveWItem(name="who", status="present", reasoning="test"),
            FiveWItem(name="what", status="present", reasoning="test"),
            FiveWItem(name="when", status="missing", reasoning="test"),
            FiveWItem(name="where", status="present", reasoning="test"),
            FiveWItem(name="why", status="present", reasoning="test"),
            FiveWItem(name="who", status="present", reasoning="extra"),  # Too many
        ]
        with pytest.raises(ValidationError):
            FiveWOut(fivews=items)
    
    def test_json_schema_generation(self):
        schema = FiveWOut.model_json_schema()
        assert "fivews" in schema["properties"]
        assert schema["properties"]["fivews"]["minItems"] == 5
        assert schema["properties"]["fivews"]["maxItems"] == 5
    
    def test_json_serialization_deserialization(self):
        items = [
            FiveWItem(name="who", status="present", reasoning="test"),
            FiveWItem(name="what", status="present", reasoning="test"),
            FiveWItem(name="when", status="missing", reasoning="test"),
            FiveWItem(name="where", status="present", reasoning="test"),
            FiveWItem(name="why", status="present", reasoning="test"),
        ]
        five_w_out = FiveWOut(fivews=items)
        
        # Serialize to JSON
        json_str = five_w_out.model_dump_json()
        
        # Deserialize from JSON
        parsed = FiveWOut.model_validate_json(json_str)
        assert len(parsed.fivews) == 5
        assert parsed.fivews[0].name == "who"
    
    def test_extra_fields_forbidden(self):
        items = [
            FiveWItem(name="who", status="present", reasoning="test"),
            FiveWItem(name="what", status="present", reasoning="test"),
            FiveWItem(name="when", status="missing", reasoning="test"),
            FiveWItem(name="where", status="present", reasoning="test"),
            FiveWItem(name="why", status="present", reasoning="test"),
        ]
        
        # Test that extra fields in JSON are rejected
        json_data = {
            "fivews": [item.model_dump() for item in items],
            "extra_field": "not allowed"
        }
        
        with pytest.raises(ValidationError):
            FiveWOut.model_validate(json_data)
