"""Relationship extraction orchestrator for managing multiple extractors."""
from typing import List, Dict, Optional
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import (
    ExtractedRelationship,
    ExtractionContext,
    ExtractionResult
)
from app.modules.knowledge_extraction.enums import RelationshipType
from app.modules.knowledge_extraction.exceptions import OrchestratorException
from app.core.logging import setup_logging

logger = setup_logging()


class RelationshipExtractionOrchestrator:
    """Orchestrator for managing and running relationship extractors.
    
    Responsibilities:
    - Load all extractors
    - Run extractors
    - Merge results
    - Remove duplicates
    - Normalize relationships
    - Return final relationship list
    """
    
    def __init__(self, parallel: bool = True, max_workers: int = 4):
        """Initialize the orchestrator.
        
        Args:
            parallel: Whether to run extractors in parallel
            max_workers: Maximum number of parallel workers
        """
        self.extractors: Dict[RelationshipType, BaseRelationshipExtractor] = {}
        self.parallel = parallel
        self.max_workers = max_workers
        self._load_extractors()
    
    def _load_extractors(self):
        """Load all available relationship extractors."""
        try:
            from app.modules.knowledge_extraction.relationship_extraction.has_component_extractor import HasComponentExtractor
            from app.modules.knowledge_extraction.relationship_extraction.failed_due_to_extractor import FailedDueToExtractor
            from app.modules.knowledge_extraction.relationship_extraction.caused_by_extractor import CausedByExtractor
            from app.modules.knowledge_extraction.relationship_extraction.performed_on_extractor import PerformedOnExtractor
            from app.modules.knowledge_extraction.relationship_extraction.performed_by_extractor import PerformedByExtractor
            from app.modules.knowledge_extraction.relationship_extraction.inspects_extractor import InspectsExtractor
            from app.modules.knowledge_extraction.relationship_extraction.references_extractor import ReferencesExtractor
            from app.modules.knowledge_extraction.relationship_extraction.applies_to_extractor import AppliesToExtractor
            from app.modules.knowledge_extraction.relationship_extraction.located_in_extractor import LocatedInExtractor
            from app.modules.knowledge_extraction.relationship_extraction.assigned_to_extractor import AssignedToExtractor
            from app.modules.knowledge_extraction.relationship_extraction.recorded_in_extractor import RecordedInExtractor
            
            # Register extractors
            self.register_extractor(HasComponentExtractor())
            self.register_extractor(FailedDueToExtractor())
            self.register_extractor(CausedByExtractor())
            self.register_extractor(PerformedOnExtractor())
            self.register_extractor(PerformedByExtractor())
            self.register_extractor(InspectsExtractor())
            self.register_extractor(ReferencesExtractor())
            self.register_extractor(AppliesToExtractor())
            self.register_extractor(LocatedInExtractor())
            self.register_extractor(AssignedToExtractor())
            self.register_extractor(RecordedInExtractor())
            
            logger.info(f"Loaded {len(self.extractors)} relationship extractors")
            
        except ImportError as e:
            logger.warning(f"Some relationship extractors could not be loaded: {e}")
    
    def register_extractor(self, extractor: BaseRelationshipExtractor):
        """Register a relationship extractor.
        
        Args:
            extractor: The extractor to register
        """
        relationship_type = extractor.get_relationship_type()
        self.extractors[relationship_type] = extractor
        logger.info(f"Registered relationship extractor: {extractor.extractor_name} for {relationship_type}")
    
    def get_extractor(self, relationship_type: RelationshipType) -> Optional[BaseRelationshipExtractor]:
        """Get an extractor by relationship type.
        
        Args:
            relationship_type: The relationship type
            
        Returns:
            The extractor if found, None otherwise
        """
        return self.extractors.get(relationship_type)
    
    def get_all_extractors(self) -> List[BaseRelationshipExtractor]:
        """Get all registered extractors.
        
        Returns:
            List of all extractors
        """
        return list(self.extractors.values())
    
    def run_extractors(
        self,
        context: ExtractionContext,
        entities: List,
        extractor_names: Optional[List[str]] = None
    ) -> List[ExtractionResult]:
        """Run relationship extractors on the given context.
        
        Args:
            context: Extraction context
            entities: List of extracted entities
            extractor_names: Specific extractors to run (None = all)
            
        Returns:
            List of extraction results
        """
        results = []
        
        # Filter extractors if specific names provided
        extractors_to_run = self.get_all_extractors()
        if extractor_names:
            extractors_to_run = [
                e for e in extractors_to_run
                if e.extractor_name in extractor_names
            ]
        
        if not extractors_to_run:
            logger.warning("No relationship extractors to run")
            return results
        
        # Run extractors
        if self.parallel and len(extractors_to_run) > 1:
            results = self._run_parallel(extractors_to_run, context, entities)
        else:
            results = self._run_sequential(extractors_to_run, context, entities)
        
        return results
    
    def _run_sequential(
        self,
        extractors: List[BaseRelationshipExtractor],
        context: ExtractionContext,
        entities: List
    ) -> List[ExtractionResult]:
        """Run extractors sequentially."""
        results = []
        
        for extractor in extractors:
            try:
                result = extractor.extract_with_result(context, entities)
                results.append(result)
                logger.info(f"{extractor.extractor_name}: {len(result.entities)} relationships, {result.extraction_time_seconds:.2f}s")
            except Exception as e:
                logger.error(f"Error running {extractor.extractor_name}: {e}")
                results.append(ExtractionResult(
                    entities=[],
                    extraction_time_seconds=0.0,
                    extractor_name=extractor.extractor_name,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def _run_parallel(
        self,
        extractors: List[BaseRelationshipExtractor],
        context: ExtractionContext,
        entities: List
    ) -> List[ExtractionResult]:
        """Run extractors in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_extractor = {
                executor.submit(e.extract_with_result, context, entities): e
                for e in extractors
            }
            
            for future in as_completed(future_to_extractor):
                extractor = future_to_extractor[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"{extractor.extractor_name}: {len(result.entities)} relationships, {result.extraction_time_seconds:.2f}s")
                except Exception as e:
                    logger.error(f"Error running {extractor.extractor_name}: {e}")
                    results.append(ExtractionResult(
                        entities=[],
                        extraction_time_seconds=0.0,
                        extractor_name=extractor.extractor_name,
                        success=False,
                        error_message=str(e)
                    ))
        
        return results
    
    def merge_results(self, results: List[ExtractionResult]) -> List[ExtractedRelationship]:
        """Merge extraction results from multiple extractors.
        
        Args:
            results: List of extraction results
            
        Returns:
            Merged list of relationships
        """
        relationships = []
        
        for result in results:
            relationships.extend(result.entities)  # Relationships stored in entities field
        
        return relationships
    
    def deduplicate_relationships(self, relationships: List[ExtractedRelationship]) -> List[ExtractedRelationship]:
        """Remove duplicate relationships.
        
        Args:
            relationships: List of relationships to deduplicate
            
        Returns:
            Deduplicated list of relationships
        """
        seen = {}
        deduplicated = []
        
        for relationship in relationships:
            # Create a key based on source, target, and relationship type
            key = (
                relationship.source_entity_name.lower(),
                relationship.target_entity_name.lower(),
                relationship.relationship_type
            )
            
            if key not in seen:
                seen[key] = relationship
                deduplicated.append(relationship)
            else:
                # Keep the relationship with higher confidence
                if relationship.confidence_score > seen[key].confidence_score:
                    idx = deduplicated.index(seen[key])
                    deduplicated[idx] = relationship
                    seen[key] = relationship
        
        logger.info(f"Deduplicated: {len(relationships)} -> {len(deduplicated)} relationships")
        return deduplicated
    
    def normalize_relationships(self, relationships: List[ExtractedRelationship]) -> List[ExtractedRelationship]:
        """Normalize relationship names.
        
        Args:
            relationships: List of relationships to normalize
            
        Returns:
            Normalized list of relationships
        """
        normalized = []
        
        for relationship in relationships:
            # Apply normalization - strip whitespace and capitalize
            relationship.source_entity_name = relationship.source_entity_name.strip().title()
            relationship.target_entity_name = relationship.target_entity_name.strip().title()
            normalized.append(relationship)
        
        return normalized
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Run full relationship extraction pipeline.
        
        Args:
            context: Extraction context
            entities: List of extracted entities
            
        Returns:
            Final list of extracted relationships
        """
        start_time = time.time()
        
        logger.info(f"Starting relationship extraction for document {context.document_id}")
        
        # Run extractors
        results = self.run_extractors(context, entities)
        
        # Merge results
        relationships = self.merge_results(results)
        logger.info(f"Merged {len(relationships)} relationships from {len(results)} extractors")
        
        # Normalize relationships
        relationships = self.normalize_relationships(relationships)
        
        # Deduplicate relationships
        relationships = self.deduplicate_relationships(relationships)
        
        extraction_time = time.time() - start_time
        logger.info(f"Relationship extraction completed in {extraction_time:.2f}s: {len(relationships)} final relationships")
        
        return relationships
    
    def get_extractor_statistics(self, results: List[ExtractionResult]) -> Dict[str, any]:
        """Get statistics about extractor performance.
        
        Args:
            results: List of extraction results
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_extractors": len(results),
            "successful_extractors": sum(1 for r in results if r.success),
            "failed_extractors": sum(1 for r in results if not r.success),
            "total_relationships": sum(len(r.entities) for r in results),
            "total_extraction_time": sum(r.extraction_time_seconds for r in results),
            "extractor_details": []
        }
        
        for result in results:
            stats["extractor_details"].append({
                "name": result.extractor_name,
                "success": result.success,
                "relationship_count": len(result.entities),
                "extraction_time": result.extraction_time_seconds,
                "error": result.error_message
            })
        
        return stats
