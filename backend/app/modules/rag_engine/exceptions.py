"""Custom exceptions for RAG Engine module."""


class PromptBuildException(Exception):
    """Exception raised when prompt building fails."""
    pass


class ProviderException(Exception):
    """Exception raised when LLM provider operations fail."""
    pass


class GenerationException(Exception):
    """Exception raised when response generation fails."""
    pass


class HallucinationException(Exception):
    """Exception raised when hallucination is detected."""
    pass


class CitationException(Exception):
    """Exception raised when citation processing fails."""
    pass


class ConfidenceException(Exception):
    """Exception raised when confidence estimation fails."""
    pass


class ConversationException(Exception):
    """Exception raised when conversation operations fail."""
    pass


class ContextFormatException(Exception):
    """Exception raised when context formatting fails."""
    pass


class ResponseFormatException(Exception):
    """Exception raised when response formatting fails."""
    pass


class ProviderUnavailableException(ProviderException):
    """Exception raised when LLM provider is unavailable."""
    pass


class InsufficientEvidenceException(GenerationException):
    """Exception raised when there's insufficient evidence for generation."""
    pass


class ConflictingEvidenceException(GenerationException):
    """Exception raised when evidence conflicts are detected."""
    pass
