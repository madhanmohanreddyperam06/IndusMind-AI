"""Qdrant client configuration and initialization."""

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from app.config.settings import settings
from app.core.logging import setup_logging

logger = setup_logging()

# Qdrant client singleton
qdrant_client: QdrantClient = None


def init_qdrant() -> QdrantClient:
    """Initialize Qdrant client with production-ready configuration.
    
    Returns:
        QdrantClient: Initialized Qdrant client
        
    Raises:
        Exception: If Qdrant connection fails
    """
    global qdrant_client
    
    try:
        logger.info(f"Initializing Qdrant client at {settings.qdrant_url}")
        
        qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=settings.qdrant_timeout,
            prefer_grpc=False  # Use REST by default, can be enabled for performance
        )
        
        # Verify connection
        collections = qdrant_client.get_collections()
        logger.info(f"Qdrant client initialized successfully. Found {len(collections.collections)} collections.")
        
        return qdrant_client
        
    except UnexpectedResponse as e:
        logger.error(f"Qdrant connection failed: {e}")
        raise Exception(f"Failed to connect to Qdrant at {settings.qdrant_url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error initializing Qdrant: {e}")
        raise


def get_qdrant() -> QdrantClient:
    """Get Qdrant client instance.
    
    Returns:
        QdrantClient: Qdrant client instance
        
    Raises:
        Exception: If client is not initialized
    """
    global qdrant_client
    
    if qdrant_client is None:
        logger.warning("Qdrant client not initialized, initializing now...")
        init_qdrant()
    
    return qdrant_client


def check_qdrant_health() -> bool:
    """Check Qdrant health status.
    
    Returns:
        bool: True if Qdrant is healthy, False otherwise
    """
    try:
        client = get_qdrant()
        collections = client.get_collections()
        logger.info("Qdrant health check passed")
        return True
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        return False


def close_qdrant():
    """Close Qdrant client connection gracefully."""
    global qdrant_client
    
    if qdrant_client is not None:
        try:
            logger.info("Closing Qdrant client connection")
            qdrant_client.close()
            qdrant_client = None
            logger.info("Qdrant client closed successfully")
        except Exception as e:
            logger.error(f"Error closing Qdrant client: {e}")

