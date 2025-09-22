"""Domain errors and exceptions used across layers."""


class MapperDomainError(Exception):
    """Base class for all domain-specific errors in the mapper application."""


class ControlValidationError(MapperDomainError):
    """Raised when control description validation fails."""


class DefinitionsUnavailableError(MapperDomainError):
    """Raised when required definitions are not loaded or available."""


class LLMProcessingError(MapperDomainError):
    """Raised when LLM processing fails or returns invalid data."""


# Keep original names for backward compatibility during transition
ValidationError = ControlValidationError
DefinitionsNotLoadedError = DefinitionsUnavailableError
