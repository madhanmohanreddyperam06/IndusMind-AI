from qdrant_client import QdrantClient
from app.config.settings import settings

# Qdrant client placeholder
qdrant_client = None


def init_qdrant():
    """Initialize Qdrant connection. Placeholder for future implementation."""
    global qdrant_client
    
    qdrant_client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key
    )


def get_qdrant():
    """Get Qdrant client. Placeholder for future implementation."""
    if qdrant_client is None:
        init_qdrant()
    
    return qdrant_client
