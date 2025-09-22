"""Tests for domain errors and exceptions."""
import pytest
from mapper_api.domain.errors import MapperDomainError, ValidationError, DefinitionsNotLoadedError


class TestMapperDomainError:
    """Test base MapperDomainError exception."""
    
    def test_is_exception(self):
        assert issubclass(MapperDomainError, Exception)
    
    def test_can_be_raised_with_message(self):
        with pytest.raises(MapperDomainError, match="test message"):
            raise MapperDomainError("test message")
    

class TestValidationError:
    """Test ValidationError exception."""
    
    def test_inherits_from_domain_error(self):
        assert issubclass(ValidationError, MapperDomainError)
        assert issubclass(ValidationError, Exception)
    
    def test_can_be_raised_with_message(self):
        with pytest.raises(ValidationError, match="validation failed"):
            raise ValidationError("validation failed")
    

class TestDefinitionsNotLoadedError:
    """Test DefinitionsNotLoadedError exception."""
    
    def test_inherits_from_domain_error(self):
        assert issubclass(DefinitionsNotLoadedError, MapperDomainError)
        assert issubclass(DefinitionsNotLoadedError, Exception)
    
    def test_can_be_raised_with_message(self):
        with pytest.raises(DefinitionsNotLoadedError, match="definitions not available"):
            raise DefinitionsNotLoadedError("definitions not available")
  