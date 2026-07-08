from neo4j import GraphDatabase
from app.config.settings import settings

# Neo4j driver placeholder
driver = None


def init_neo4j():
    """Initialize Neo4j connection. Placeholder for future implementation."""
    global driver
    
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password)
    )


def get_neo4j():
    """Get Neo4j driver. Placeholder for future implementation."""
    if driver is None:
        init_neo4j()
    
    return driver


def close_neo4j():
    """Close Neo4j connection. Placeholder for future implementation."""
    global driver
    
    if driver is not None:
        driver.close()
        driver = None
