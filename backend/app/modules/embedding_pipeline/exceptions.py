"""Custom exceptions for embedding pipeline."""


class EmbeddingPipelineError(Exception):
    """Base exception for embedding pipeline errors."""
    pass


class EmbeddingGenerationError(EmbeddingPipelineError):
    """Exception raised when embedding generation fails."""
    
    def __init__(self, message: str, document_id: str = None, chunk_id: str = None):
        self.document_id = document_id
        self.chunk_id = chunk_id
        self.message = message
        super().__init__(self.message)


class ChunkingError(EmbeddingPipelineError):
    """Exception raised when document chunking fails."""
    
    def __init__(self, message: str, document_id: str = None):
        self.document_id = document_id
        self.message = message
        super().__init__(self.message)


class VectorStorageError(EmbeddingPipelineError):
    """Exception raised when vector storage operations fail."""
    
    def __init__(self, message: str, collection_name: str = None, chunk_id: str = None):
        self.collection_name = collection_name
        self.chunk_id = chunk_id
        self.message = message
        super().__init__(self.message)


class CollectionNotFoundError(EmbeddingPipelineError):
    """Exception raised when a Qdrant collection is not found."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.message = f"Collection '{collection_name}' not found"
        super().__init__(self.message)


class SearchError(EmbeddingPipelineError):
    """Exception raised when semantic search fails."""
    
    def __init__(self, message: str, query: str = None):
        self.query = query
        self.message = message
        super().__init__(self.message)


class SynchronizationError(EmbeddingPipelineError):
    """Exception raised when synchronization operations fail."""
    
    def __init__(self, message: str, document_id: str = None, operation: str = None):
        self.document_id = document_id
        self.operation = operation
        self.message = message
        super().__init__(self.message)


class ModelLoadError(EmbeddingPipelineError):
    """Exception raised when embedding model fails to load."""
    
    def __init__(self, message: str, model_name: str = None):
        self.model_name = model_name
        self.message = message
        super().__init__(self.message)


class QdrantConnectionError(EmbeddingPipelineError):
    """Exception raised when Qdrant connection fails."""
    
    def __init__(self, message: str, host: str = None, port: int = None):
        self.host = host
        self.port = port
        self.message = message
        super().__init__(self.message)


class InvalidChunkError(EmbeddingPipelineError):
    """Exception raised when a chunk is invalid."""
    
    def __init__(self, message: str, chunk_id: str = None):
        self.chunk_id = chunk_id
        self.message = message
        super().__init__(self.message)


class EmbeddingValidationError(EmbeddingPipelineError):
    """Exception raised when embedding validation fails."""
    
    def __init__(self, message: str, expected_dim: int = None, actual_dim: int = None):
        self.expected_dim = expected_dim
        self.actual_dim = actual_dim
        self.message = message
        super().__init__(self.message)
