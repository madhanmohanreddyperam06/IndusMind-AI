"""Neo4j configuration and driver initialization."""

from neo4j import GraphDatabase
from typing import Optional
from app.config.settings import settings
from app.core.logging import setup_logging

logger = setup_logging()

# Neo4j driver
driver: Optional[GraphDatabase.driver] = None


def init_neo4j():
    """Initialize Neo4j connection with connection pooling.
    
    Raises:
        GraphConnectionError: If connection fails
    """
    global driver
    
    # Check if Neo4j is enabled
    if not settings.neo4j_enabled:
        logger.info("Neo4j integration is disabled in settings")
        return
    
    try:
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            max_connection_lifetime=settings.neo4j_max_connection_lifetime,
            max_connection_pool_size=settings.neo4j_max_connection_pool_size,
            connection_acquisition_timeout=settings.neo4j_connection_acquisition_timeout,
            encrypted=False  # Set to True for production with SSL
        )
        
        # Verify connection
        driver.verify_connectivity()
        
        logger.info(f"Neo4j connection established: {settings.neo4j_uri}")
        
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        raise GraphConnectionError(f"Failed to connect to Neo4j: {str(e)}")


def get_neo4j() -> GraphDatabase.driver:
    """Get Neo4j driver instance.
    
    Returns:
        Neo4j driver instance
        
    Raises:
        GraphConnectionError: If driver is not initialized
    """
    global driver
    
    if driver is None:
        init_neo4j()
    
    return driver


def close_neo4j():
    """Close Neo4j connection gracefully."""
    global driver
    
    if driver is not None:
        try:
            driver.close()
            logger.info("Neo4j connection closed")
        except Exception as e:
            logger.error(f"Error closing Neo4j connection: {e}")
        finally:
            driver = None


def check_neo4j_health() -> bool:
    """Check Neo4j connection health.
    
    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        neo4j_driver = get_neo4j()
        neo4j_driver.verify_connectivity()
        
        # Run a simple query
        with neo4j_driver.session(database=settings.neo4j_database) as session:
            result = session.run("RETURN 1 as test")
            result.single()
            
        return True
    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")
        return False


# Import exception for use in this module
from app.modules.knowledge_graph.exceptions import GraphConnectionError
