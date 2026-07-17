"""Custom exceptions for knowledge graph operations."""


class GraphConnectionError(Exception):
    """Exception raised when Neo4j connection fails."""
    
    def __init__(self, message: str = "Failed to connect to Neo4j database"):
        self.message = message
        super().__init__(self.message)


class GraphSynchronizationError(Exception):
    """Exception raised when graph synchronization fails."""
    
    def __init__(self, message: str = "Graph synchronization failed"):
        self.message = message
        super().__init__(self.message)


class NodeNotFoundError(Exception):
    """Exception raised when a node is not found in the graph."""
    
    def __init__(self, node_id: str = None, message: str = None):
        if message:
            self.message = message
        elif node_id:
            self.message = f"Node with ID {node_id} not found"
        else:
            self.message = "Node not found"
        super().__init__(self.message)


class RelationshipNotFoundError(Exception):
    """Exception raised when a relationship is not found in the graph."""
    
    def __init__(self, relationship_id: str = None, message: str = None):
        if message:
            self.message = message
        elif relationship_id:
            self.message = f"Relationship with ID {relationship_id} not found"
        else:
            self.message = "Relationship not found"
        super().__init__(self.message)


class DuplicateNodeError(Exception):
    """Exception raised when attempting to create a duplicate node."""
    
    def __init__(self, node_id: str = None, message: str = None):
        if message:
            self.message = message
        elif node_id:
            self.message = f"Node with ID {node_id} already exists"
        else:
            self.message = "Duplicate node detected"
        super().__init__(self.message)


class DuplicateRelationshipError(Exception):
    """Exception raised when attempting to create a duplicate relationship."""
    
    def __init__(self, relationship_id: str = None, message: str = None):
        if message:
            self.message = message
        elif relationship_id:
            self.message = f"Relationship with ID {relationship_id} already exists"
        else:
            self.message = "Duplicate relationship detected"
        super().__init__(self.message)


class GraphQueryError(Exception):
    """Exception raised when a graph query fails."""
    
    def __init__(self, message: str = "Graph query execution failed"):
        self.message = message
        super().__init__(self.message)


class GraphBuilderError(Exception):
    """Exception raised when graph building operations fail."""
    
    def __init__(self, message: str = "Graph building operation failed"):
        self.message = message
        super().__init__(self.message)
