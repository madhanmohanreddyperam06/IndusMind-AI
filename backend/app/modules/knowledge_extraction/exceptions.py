"""Custom exceptions for knowledge extraction module."""


class KnowledgeExtractionException(Exception):
    """Base exception for knowledge extraction module."""
    pass


class EntityExtractionException(KnowledgeExtractionException):
    """Exception raised during entity extraction."""
    pass


class RelationshipExtractionException(KnowledgeExtractionException):
    """Exception raised during relationship extraction."""
    pass


class NormalizationException(KnowledgeExtractionException):
    """Exception raised during entity normalization."""
    pass


class DeduplicationException(KnowledgeExtractionException):
    """Exception raised during entity deduplication."""
    pass


class OrchestratorException(KnowledgeExtractionException):
    """Exception raised during extraction orchestration."""
    pass


class ExtractorLoadException(KnowledgeExtractionException):
    """Exception raised when an extractor fails to load."""
    pass


class ExtractorExecutionException(KnowledgeExtractionException):
    """Exception raised when an extractor fails during execution."""
    pass


class ModelLoadException(KnowledgeExtractionException):
    """Exception raised when an NLP model fails to load."""
    pass


class DictionaryLoadException(KnowledgeExtractionException):
    """Exception raised when a dictionary fails to load."""
    pass


class PatternCompilationException(KnowledgeExtractionException):
    """Exception raised when a regex pattern fails to compile."""
    pass


class ConfidenceScoreException(KnowledgeExtractionException):
    """Exception raised when confidence score is invalid."""
    pass


class DocumentNotFoundException(KnowledgeExtractionException):
    """Exception raised when a document is not found."""
    pass


class ProcessedDocumentNotFoundException(KnowledgeExtractionException):
    """Exception raised when a processed document is not found."""
    pass
