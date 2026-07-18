from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings using Pydantic v2."""
    
    # Application
    app_name: str = Field(default="IndusMind AI", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Security
    secret_key: str = Field(default="your-secret-key-here", description="Secret key for JWT")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration time")
    
    # MySQL
    mysql_url: str = Field(
        default="mysql+pymysql://root:Madhanreddy%40123@localhost:3306/indusmind",
        description="MySQL connection URL"
    )
    mysql_host: str = Field(default="localhost", description="MySQL host")
    mysql_port: int = Field(default=3306, description="MySQL port")
    mysql_user: str = Field(default="root", description="MySQL username")
    mysql_password: str = Field(default="Madhanreddy@123", description="MySQL password")
    mysql_database: str = Field(default="indusmind", description="MySQL database name")
    
    # Neo4j
    neo4j_enabled: bool = Field(default=False, description="Enable Neo4j integration")
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(default="indusmind123", description="Neo4j password")
    neo4j_database: str = Field(default="neo4j", description="Neo4j database name")
    neo4j_max_connection_lifetime: int = Field(default=3600, description="Neo4j max connection lifetime (seconds)")
    neo4j_max_connection_pool_size: int = Field(default=50, description="Neo4j max connection pool size")
    neo4j_connection_acquisition_timeout: int = Field(default=60, description="Neo4j connection acquisition timeout (seconds)")
    
    # Qdrant
    qdrant_enabled: bool = Field(default=False, description="Enable Qdrant integration")
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant URL")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant API key")
    qdrant_collection_name: str = Field(default="industrial_documents", description="Qdrant collection name")
    qdrant_timeout: int = Field(default=60, description="Qdrant request timeout (seconds)")
    qdrant_grpc_port: int = Field(default=6334, description="Qdrant gRPC port")
    
    # Embedding Model
    embedding_model_name: str = Field(default="BAAI/bge-small-en-v1.5", description="Embedding model name")
    embedding_device: str = Field(default="cpu", description="Embedding model device (cpu/cuda)")
    embedding_batch_size: int = Field(default=32, description="Embedding batch size")
    embedding_cache_enabled: bool = Field(default=True, description="Enable embedding cache")
    
    # Chunking
    default_chunk_size: int = Field(default=500, description="Default chunk size (tokens)")
    default_chunk_overlap: int = Field(default=50, description="Default chunk overlap (tokens)")
    min_chunk_size: int = Field(default=100, description="Minimum chunk size (tokens)")
    max_chunk_size: int = Field(default=1000, description="Maximum chunk size (tokens)")
    preserve_sentence_boundaries: bool = Field(default=True, description="Preserve sentence boundaries")
    preserve_section_hierarchy: bool = Field(default=True, description="Preserve section hierarchy")
    
    # Search
    default_search_limit: int = Field(default=10, description="Default search limit")
    max_search_limit: int = Field(default=100, description="Maximum search limit")
    default_score_threshold: float = Field(default=0.7, description="Default similarity score threshold")
    
    # AI Services
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    
    # RAG Engine
    llm_provider: str = Field(default="gemini", description="LLM provider (gemini/openai/ollama/mock)")
    gemini_model: str = Field(default="gemini-pro", description="Gemini model name")
    openai_model: str = Field(default="gpt-4", description="OpenAI model name")
    ollama_model: str = Field(default="llama2", description="Ollama model name")
    ollama_url: str = Field(default="http://localhost:11434", description="Ollama server URL")
    max_context_tokens: int = Field(default=4000, description="Maximum context tokens")
    max_response_tokens: int = Field(default=2000, description="Maximum response tokens")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="LLM top-p sampling")
    
    # MinIO
    minio_endpoint: str = Field(default="localhost:9000", description="MinIO endpoint")
    minio_access_key: str = Field(default="minioadmin", description="MinIO access key")
    minio_secret_key: str = Field(default="minioadmin", description="MinIO secret key")
    minio_bucket: str = Field(default="indusmind", description="MinIO bucket name")
    minio_secure: bool = Field(default=False, description="Use HTTPS for MinIO")
    
    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
        description="CORS allowed origins"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_file: str = Field(default="logs/app.log", description="Log file path")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
