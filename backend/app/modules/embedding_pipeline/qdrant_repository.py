"""Qdrant repository for vector storage and retrieval."""

from typing import List, Dict, Any, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue,
    MatchAny, MatchText, SearchRequest, FilterSelector, UpdateStatus
)
from qdrant_client.http.exceptions import UnexpectedResponse
from app.config.qdrant import get_qdrant
from app.config.settings import settings
from app.modules.embedding_pipeline.exceptions import (
    VectorStorageError,
    CollectionNotFoundError,
    QdrantConnectionError
)
from app.modules.embedding_pipeline.constants import COLLECTION_CONFIG
from app.core.logging import setup_logging

logger = setup_logging()


class QdrantRepository:
    """Repository for Qdrant vector database operations."""
    
    def __init__(self, collection_name: str = None):
        """Initialize Qdrant repository.
        
        Args:
            collection_name: Name of the collection (uses default if not provided)
        """
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.client: QdrantClient = None
        self._connect()
    
    def _connect(self):
        """Connect to Qdrant client.
        
        Raises:
            QdrantConnectionError: If connection fails
        """
        try:
            self.client = get_qdrant()
            logger.info(f"Connected to Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise QdrantConnectionError(str(e), settings.qdrant_url)
    
    # ============================================================================
    # Collection Management
    # ============================================================================
    
    def create_collection(self, recreate: bool = False) -> bool:
        """Create a new collection for document embeddings.
        
        Args:
            recreate: If True, delete and recreate existing collection
            
        Returns:
            True if successful
            
        Raises:
            VectorStorageError: If collection creation fails
        """
        try:
            # Check if collection exists
            if self.collection_exists():
                if recreate:
                    logger.info(f"Recreating collection: {self.collection_name}")
                    self.delete_collection()
                else:
                    logger.info(f"Collection already exists: {self.collection_name}")
                    return True
            
            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=COLLECTION_CONFIG["vectors"]["size"],
                    distance=Distance[COLLECTION_CONFIG["vectors"]["distance"]]
                ),
                optimizers_config=COLLECTION_CONFIG.get("optimizers_config"),
                hnsw_config=COLLECTION_CONFIG.get("index_params", {}).get("hnsw_config")
            )
            
            logger.info(f"Collection created successfully: {self.collection_name}")
            return True
            
        except UnexpectedResponse as e:
            logger.error(f"Failed to create collection: {e}")
            raise VectorStorageError(f"Failed to create collection: {str(e)}", self.collection_name)
        except Exception as e:
            logger.error(f"Unexpected error creating collection: {e}")
            raise VectorStorageError(f"Unexpected error: {str(e)}", self.collection_name)
    
    def delete_collection(self) -> bool:
        """Delete the collection.
        
        Returns:
            True if successful
            
        Raises:
            VectorStorageError: If deletion fails
        """
        try:
            if not self.collection_exists():
                logger.warning(f"Collection does not exist: {self.collection_name}")
                return True
            
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Collection deleted: {self.collection_name}")
            return True
            
        except UnexpectedResponse as e:
            logger.error(f"Failed to delete collection: {e}")
            raise VectorStorageError(f"Failed to delete collection: {str(e)}", self.collection_name)
        except Exception as e:
            logger.error(f"Unexpected error deleting collection: {e}")
            raise VectorStorageError(f"Unexpected error: {str(e)}", self.collection_name)
    
    def collection_exists(self) -> bool:
        """Check if collection exists.
        
        Returns:
            True if collection exists
        """
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            return self.collection_name in collection_names
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection.
        
        Returns:
            Collection information
            
        Raises:
            CollectionNotFoundError: If collection doesn't exist
        """
        try:
            if not self.collection_exists():
                raise CollectionNotFoundError(self.collection_name)
            
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.params.vectors.size,
                "vector_count": info.points_count,
                "indexed_vector_count": info.indexed_vector_count,
                "status": info.status,
                "optimizer_status": info.optimizer_status,
                "config": info.config.params.dict()
            }
            
        except CollectionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise VectorStorageError(f"Failed to get collection info: {str(e)}", self.collection_name)
    
    # ============================================================================
    # Vector Operations
    # ============================================================================
    
    def upsert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: List[str] = None
    ) -> bool:
        """Upsert vectors into the collection.
        
        Args:
            vectors: List of embedding vectors
            payloads: List of metadata payloads
            ids: Optional list of point IDs (generated if not provided)
            
        Returns:
            True if successful
            
        Raises:
            VectorStorageError: If upsert fails
        """
        try:
            if not self.collection_exists():
                self.create_collection()
            
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
            
            # Create points
            points = [
                PointStruct(
                    id=ids[i],
                    vector=vectors[i],
                    payload=payloads[i]
                )
                for i in range(len(vectors))
            ]
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
            
            logger.info(f"Upserted {len(points)} vectors to collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            raise VectorStorageError(f"Failed to upsert vectors: {str(e)}", self.collection_name)
    
    def insert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: List[str] = None
    ) -> bool:
        """Insert vectors into the collection (fail if exists).
        
        Args:
            vectors: List of embedding vectors
            payloads: List of metadata payloads
            ids: Optional list of point IDs
            
        Returns:
            True if successful
            
        Raises:
            VectorStorageError: If insert fails
        """
        try:
            if not self.collection_exists():
                self.create_collection()
            
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
            
            points = [
                PointStruct(
                    id=ids[i],
                    vector=vectors[i],
                    payload=payloads[i]
                )
                for i in range(len(vectors))
            ]
            
            self.client.insert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Inserted {len(points)} vectors to collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting vectors: {e}")
            raise VectorStorageError(f"Failed to insert vectors: {str(e)}", self.collection_name)
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors by IDs.
        
        Args:
            ids: List of point IDs to delete
            
        Returns:
            True if successful
            
        Raises:
            VectorStorageError: If deletion fails
        """
        try:
            if not self.collection_exists():
                logger.warning(f"Collection does not exist: {self.collection_name}")
                return True
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids
            )
            
            logger.info(f"Deleted {len(ids)} vectors from collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            raise VectorStorageError(f"Failed to delete vectors: {str(e)}", self.collection_name)
    
    def delete_vectors_by_filter(self, filter: Filter) -> bool:
        """Delete vectors by filter.
        
        Args:
            filter: Qdrant filter
            
        Returns:
            True if successful
            
        Raises:
            VectorStorageError: If deletion fails
        """
        try:
            if not self.collection_exists():
                return True
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=FilterSelector(filter=filter)
            )
            
            logger.info(f"Deleted vectors by filter from collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors by filter: {e}")
            raise VectorStorageError(f"Failed to delete vectors by filter: {str(e)}", self.collection_name)
    
    def delete_document_vectors(self, document_id: str) -> bool:
        """Delete all vectors for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if successful
        """
        filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
        return self.delete_vectors_by_filter(filter)
    
    # ============================================================================
    # Search Operations
    # ============================================================================
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = None,
        filter: Filter = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter: Optional filter for metadata
            
        Returns:
            List of search results with scores and payloads
            
        Raises:
            VectorStorageError: If search fails
        """
        try:
            if not self.collection_exists():
                raise CollectionNotFoundError(self.collection_name)
            
            search_params = {
                "collection_name": self.collection_name,
                "query_vector": query_vector,
                "limit": limit
            }
            
            if filter:
                search_params["query_filter"] = FilterSelector(filter=filter)
            
            results = self.client.search(**search_params)
            
            # Filter by score threshold
            if score_threshold:
                results = [r for r in results if r.score >= score_threshold]
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                    "vector": result.vector
                })
            
            logger.info(f"Search returned {len(formatted_results)} results")
            return formatted_results
            
        except CollectionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            raise VectorStorageError(f"Failed to search vectors: {str(e)}", self.collection_name)
    
    def search_batch(
        self,
        query_vectors: List[List[float]],
        limit: int = 10,
        score_threshold: float = None,
        filter: Filter = None
    ) -> List[List[Dict[str, Any]]]:
        """Batch search for multiple query vectors.
        
        Args:
            query_vectors: List of query embedding vectors
            limit: Maximum number of results per query
            score_threshold: Minimum similarity score
            filter: Optional filter for metadata
            
        Returns:
            List of search result lists
            
        Raises:
            VectorStorageError: If search fails
        """
        try:
            if not self.collection_exists():
                raise CollectionNotFoundError(self.collection_name)
            
            search_params = {
                "collection_name": self.collection_name,
                "queries": query_vectors,
                "limit": limit
            }
            
            if filter:
                search_params["query_filter"] = FilterSelector(filter=filter)
            
            results = self.client.search_batch(**search_params)
            
            # Format results
            formatted_results = []
            for query_results in results:
                query_formatted = []
                for result in query_results:
                    if score_threshold is None or result.score >= score_threshold:
                        query_formatted.append({
                            "id": result.id,
                            "score": result.score,
                            "payload": result.payload,
                            "vector": result.vector
                        })
                formatted_results.append(query_formatted)
            
            logger.info(f"Batch search returned results for {len(query_vectors)} queries")
            return formatted_results
            
        except CollectionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in batch search: {e}")
            raise VectorStorageError(f"Failed to perform batch search: {str(e)}", self.collection_name)
    
    def recommend(
        self,
        positive_ids: List[str] = None,
        negative_ids: List[str] = None,
        limit: int = 10,
        filter: Filter = None
    ) -> List[Dict[str, Any]]:
        """Recommend similar vectors based on positive/negative examples.
        
        Args:
            positive_ids: IDs of positive examples
            negative_ids: IDs of negative examples
            limit: Maximum number of results
            filter: Optional filter for metadata
            
        Returns:
            List of recommended results
            
        Raises:
            VectorStorageError: If recommendation fails
        """
        try:
            if not self.collection_exists():
                raise CollectionNotFoundError(self.collection_name)
            
            recommend_params = {
                "collection_name": self.collection_name,
                "limit": limit
            }
            
            if positive_ids:
                recommend_params["positive"] = positive_ids
            if negative_ids:
                recommend_params["negative"] = negative_ids
            if filter:
                recommend_params["query_filter"] = FilterSelector(filter=filter)
            
            results = self.client.recommend(**recommend_params)
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                    "vector": result.vector
                })
            
            logger.info(f"Recommendation returned {len(formatted_results)} results")
            return formatted_results
            
        except CollectionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in recommendation: {e}")
            raise VectorStorageError(f"Failed to recommend: {str(e)}", self.collection_name)
    
    # ============================================================================
    # Point Operations
    # ============================================================================
    
    def get_point(self, point_id: str) -> Optional[Dict[str, Any]]:
        """Get a point by ID.
        
        Args:
            point_id: Point ID
            
        Returns:
            Point data or None if not found
        """
        try:
            if not self.collection_exists():
                return None
            
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id]
            )
            
            if not points:
                return None
            
            point = points[0]
            return {
                "id": point.id,
                "payload": point.payload,
                "vector": point.vector
            }
            
        except Exception as e:
            logger.error(f"Error getting point: {e}")
            return None
    
    def scroll(
        self,
        limit: int = 100,
        offset: int = None,
        filter: Filter = None
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Scroll through points in the collection.
        
        Args:
            limit: Maximum number of points to return
            offset: Offset for pagination
            filter: Optional filter
            
        Returns:
            Tuple of (points, next_page_offset)
        """
        try:
            if not self.collection_exists():
                return [], None
            
            scroll_params = {
                "collection_name": self.collection_name,
                "limit": limit,
                "with_payload": True,
                "with_vectors": False
            }
            
            if offset:
                scroll_params["offset"] = offset
            if filter:
                scroll_params["query_filter"] = FilterSelector(filter=filter)
            
            points, next_offset = self.client.scroll(**scroll_params)
            
            formatted_points = []
            for point in points:
                formatted_points.append({
                    "id": point.id,
                    "payload": point.payload
                })
            
            return formatted_points, next_offset
            
        except Exception as e:
            logger.error(f"Error scrolling: {e}")
            return [], None
    
    # ============================================================================
    # Statistics
    # ============================================================================
    
    def count_points(self, filter: Filter = None) -> int:
        """Count points in the collection.
        
        Args:
            filter: Optional filter
            
        Returns:
            Number of points
        """
        try:
            if not self.collection_exists():
                return 0
            
            count_params = {"collection_name": self.collection_name}
            if filter:
                count_params["query_filter"] = FilterSelector(filter=filter)
            
            count = self.client.count(**count_params)
            return count.count
            
        except Exception as e:
            logger.error(f"Error counting points: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            if not self.collection_exists():
                return {
                    "exists": False,
                    "vector_count": 0,
                    "indexed_vector_count": 0
                }
            
            info = self.get_collection_info()
            return {
                "exists": True,
                "vector_count": info["vector_count"],
                "indexed_vector_count": info["indexed_vector_count"],
                "status": info["status"],
                "config": info["config"]
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "exists": False,
                "error": str(e)
            }
