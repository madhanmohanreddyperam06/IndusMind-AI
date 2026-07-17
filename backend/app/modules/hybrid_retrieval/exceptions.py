"""Custom exceptions for hybrid retrieval."""


class HybridRetrievalError(Exception):
    """Base exception for hybrid retrieval errors."""
    pass


class QueryAnalysisException(HybridRetrievalError):
    """Exception raised when query analysis fails."""
    
    def __init__(self, message: str, query: str = None):
        self.query = query
        self.message = message
        super().__init__(self.message)


class QueryExpansionException(HybridRetrievalError):
    """Exception raised when query expansion fails."""
    
    def __init__(self, message: str, query: str = None):
        self.query = query
        self.message = message
        super().__init__(self.message)


class RetrievalException(HybridRetrievalError):
    """Exception raised when retrieval fails."""
    
    def __init__(self, message: str, source: str = None):
        self.source = source
        self.message = message
        super().__init__(self.message)


class VectorRetrievalException(RetrievalException):
    """Exception raised when vector retrieval fails."""
    
    def __init__(self, message: str):
        super().__init__(message, source="vector")


class GraphRetrievalException(RetrievalException):
    """Exception raised when graph retrieval fails."""
    
    def __init__(self, message: str):
        super().__init__(message, source="graph")


class KeywordRetrievalException(RetrievalException):
    """Exception raised when keyword retrieval fails."""
    
    def __init__(self, message: str):
        super().__init__(message, source="keyword")


class MetadataRetrievalException(RetrievalException):
    """Exception raised when metadata retrieval fails."""
    
    def __init__(self, message: str):
        super().__init__(message, source="metadata")


class SearchTimeoutException(HybridRetrievalError):
    """Exception raised when search times out."""
    
    def __init__(self, message: str, source: str = None, timeout: float = None):
        self.source = source
        self.timeout = timeout
        self.message = message
        super().__init__(self.message)


class RankingException(HybridRetrievalError):
    """Exception raised when ranking fails."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ContextBuildException(HybridRetrievalError):
    """Exception raised when context building fails."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class EvidenceMergeException(HybridRetrievalError):
    """Exception raised when evidence merging fails."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DeduplicationException(HybridRetrievalError):
    """Exception raised when deduplication fails."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidQueryException(HybridRetrievalError):
    """Exception raised for invalid queries."""
    
    def __init__(self, message: str, query: str = None):
        self.query = query
        self.message = message
        super().__init__(self.message)


class NoResultsException(HybridRetrievalError):
    """Exception raised when no results are found."""
    
    def __init__(self, message: str, query: str = None):
        self.query = query
        self.message = message
        super().__init__(self.message)
