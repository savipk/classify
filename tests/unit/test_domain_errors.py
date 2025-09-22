"""Tests for domain errors and exceptions."""
import pytest
from mapper_api.domain.errors import MapperDomainError, ControlValidationError, DefinitionsUnavailableError


class TestMapperDomainError:
    """Test base MapperDomainError exception."""
    
    def test_is_exception(self):
        assert issubclass(MapperDomainError, Exception)
    
    def test_can_be_raised_with_message(self):
        with pytest.raises(MapperDomainError, match="test message"):
            raise MapperDomainError("test message")
    

class TestControlValidationError:
    """Test ControlValidationError exception."""
    
    def test_inherits_from_domain_error(self):
        assert issubclass(ControlValidationError, MapperDomainError)
        assert issubclass(ControlValidationError, Exception)
    
    def test_can_be_raised_with_message(self):
        with pytest.raises(ControlValidationError, match="validation failed"):
            raise ControlValidationError("validation failed")
    

class TestDefinitionsUnavailableError:
    """Test DefinitionsUnavailableError exception."""
    
    def test_inherits_from_domain_error(self):
        assert issubclass(DefinitionsUnavailableError, MapperDomainError)
        assert issubclass(DefinitionsUnavailableError, Exception)
    
    def test_can_be_raised_with_message(self):
        with pytest.raises(DefinitionsUnavailableError, match="definitions not available"):
            raise DefinitionsUnavailableError("definitions not available")
  