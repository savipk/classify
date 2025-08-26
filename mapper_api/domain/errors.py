"""Domain errors and exceptions used across layers."""
class DomainError(Exception):
    """Base domain error."""


class ValidationError(DomainError):
    """Raised when domain invariants are violated."""


class DefinitionsNotLoadedError(DomainError):
    """Raised when required definitions are not available."""
