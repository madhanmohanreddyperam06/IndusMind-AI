"""Entity extraction orchestrator for managing multiple extractors."""
from typing import List, Dict, Type, Optional
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.modules.knowledge_extraction.entity_extraction.base_extractor import BaseEntityExtractor
from app.modules.knowledge_extraction.schemas import (
    ExtractedEntity,
    ExtractionContext,
    ExtractionResult
)
from app.modules.knowledge_extraction.enums import EntityType
from app.modules.knowledge_extraction.exceptions import OrchestratorException
from app.core.logging import setup_logging

logger = setup_logging()


class EntityExtractionOrchestrator:
    """Orchestrator for managing and running entity extractors.
    
    Responsibilities:
    - Load all extractors
    - Run extractors
    - Merge results
    - Remove duplicates
    - Normalize entities
    - Return final entity list
    """
    
    def __init__(self, parallel: bool = True, max_workers: int = 4):
        """Initialize the orchestrator.
        
        Args:
            parallel: Whether to run extractors in parallel
            max_workers: Maximum number of parallel workers
        """
        self.extractors: Dict[EntityType, BaseEntityExtractor] = {}
        self.parallel = parallel
        self.max_workers = max_workers
        self._load_extractors()
    
    def _load_extractors(self):
        """Load all available entity extractors."""
        try:
            from app.modules.knowledge_extraction.entity_extraction.equipment_extractor import EquipmentExtractor
            from app.modules.knowledge_extraction.entity_extraction.component_extractor import ComponentExtractor
            from app.modules.knowledge_extraction.entity_extraction.failure_extractor import FailureExtractor
            from app.modules.knowledge_extraction.entity_extraction.cause_extractor import CauseExtractor
            from app.modules.knowledge_extraction.entity_extraction.maintenance_activity_extractor import MaintenanceActivityExtractor
            from app.modules.knowledge_extraction.entity_extraction.inspection_extractor import InspectionExtractor
            from app.modules.knowledge_extraction.entity_extraction.work_order_extractor import WorkOrderExtractor
            from app.modules.knowledge_extraction.entity_extraction.regulation_extractor import RegulationExtractor
            from app.modules.knowledge_extraction.entity_extraction.standard_extractor import StandardExtractor
            from app.modules.knowledge_extraction.entity_extraction.document_reference_extractor import DocumentReferenceExtractor
            from app.modules.knowledge_extraction.entity_extraction.person_extractor import PersonExtractor
            from app.modules.knowledge_extraction.entity_extraction.department_extractor import DepartmentExtractor
            from app.modules.knowledge_extraction.entity_extraction.organization_extractor import OrganizationExtractor
            from app.modules.knowledge_extraction.entity_extraction.vendor_extractor import VendorExtractor
            from app.modules.knowledge_extraction.entity_extraction.location_extractor import LocationExtractor
            from app.modules.knowledge_extraction.entity_extraction.measurement_extractor import MeasurementExtractor
            from app.modules.knowledge_extraction.entity_extraction.date_extractor import DateExtractor
            from app.modules.knowledge_extraction.entity_extraction.process_parameter_extractor import ProcessParameterExtractor
            from app.modules.knowledge_extraction.entity_extraction.risk_extractor import RiskExtractor
            from app.modules.knowledge_extraction.entity_extraction.safety_extractor import SafetyExtractor
            from app.modules.knowledge_extraction.entity_extraction.quality_extractor import QualityExtractor
            
            # Register extractors
            self.register_extractor(EquipmentExtractor())
            self.register_extractor(ComponentExtractor())
            self.register_extractor(FailureExtractor())
            self.register_extractor(CauseExtractor())
            self.register_extractor(MaintenanceActivityExtractor())
            self.register_extractor(InspectionExtractor())
            self.register_extractor(WorkOrderExtractor())
            self.register_extractor(RegulationExtractor())
            self.register_extractor(StandardExtractor())
            self.register_extractor(DocumentReferenceExtractor())
            self.register_extractor(PersonExtractor())
            self.register_extractor(DepartmentExtractor())
            self.register_extractor(OrganizationExtractor())
            self.register_extractor(VendorExtractor())
            self.register_extractor(LocationExtractor())
            self.register_extractor(MeasurementExtractor())
            self.register_extractor(DateExtractor())
            self.register_extractor(ProcessParameterExtractor())
            self.register_extractor(RiskExtractor())
            self.register_extractor(SafetyExtractor())
            self.register_extractor(QualityExtractor())
            
            logger.info(f"Loaded {len(self.extractors)} entity extractors")
            
        except ImportError as e:
            logger.warning(f"Some extractors could not be loaded: {e}")
    
    def register_extractor(self, extractor: BaseEntityExtractor):
        """Register an entity extractor.
        
        Args:
            extractor: The extractor to register
        """
        entity_type = extractor.get_entity_type()
        self.extractors[entity_type] = extractor
        logger.info(f"Registered extractor: {extractor.extractor_name} for {entity_type}")
    
    def get_extractor(self, entity_type: EntityType) -> Optional[BaseEntityExtractor]:
        """Get an extractor by entity type.
        
        Args:
            entity_type: The entity type
            
        Returns:
            The extractor if found, None otherwise
        """
        return self.extractors.get(entity_type)
    
    def get_all_extractors(self) -> List[BaseEntityExtractor]:
        """Get all registered extractors.
        
        Returns:
            List of all extractors
        """
        return list(self.extractors.values())
    
    def run_extractors(
        self,
        context: ExtractionContext,
        extractor_names: Optional[List[str]] = None
    ) -> List[ExtractionResult]:
        """Run entity extractors on the given context.
        
        Args:
            context: Extraction context
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
            logger.warning("No extractors to run")
            return results
        
        # Run extractors
        if self.parallel and len(extractors_to_run) > 1:
            results = self._run_parallel(extractors_to_run, context)
        else:
            results = self._run_sequential(extractors_to_run, context)
        
        return results
    
    def _run_sequential(
        self,
        extractors: List[BaseEntityExtractor],
        context: ExtractionContext
    ) -> List[ExtractionResult]:
        """Run extractors sequentially.
        
        Args:
            extractors: List of extractors to run
            context: Extraction context
            
        Returns:
            List of extraction results
        """
        results = []
        
        for extractor in extractors:
            try:
                result = extractor.extract_with_result(context)
                results.append(result)
                logger.info(f"{extractor.extractor_name}: {len(result.entities)} entities, {result.extraction_time_seconds:.2f}s")
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
        extractors: List[BaseEntityExtractor],
        context: ExtractionContext
    ) -> List[ExtractionResult]:
        """Run extractors in parallel.
        
        Args:
            extractors: List of extractors to run
            context: Extraction context
            
        Returns:
            List of extraction results
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_extractor = {
                executor.submit(e.extract_with_result, context): e
                for e in extractors
            }
            
            for future in as_completed(future_to_extractor):
                extractor = future_to_extractor[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"{extractor.extractor_name}: {len(result.entities)} entities, {result.extraction_time_seconds:.2f}s")
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
    
    def merge_results(self, results: List[ExtractionResult]) -> List[ExtractedEntity]:
        """Merge extraction results from multiple extractors.
        
        Args:
            results: List of extraction results
            
        Returns:
            Merged list of entities
        """
        entities = []
        
        for result in results:
            entities.extend(result.entities)
        
        return entities
    
    def deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove duplicate entities.
        
        Args:
            entities: List of entities to deduplicate
            
        Returns:
            Deduplicated list of entities
        """
        seen = {}
        deduplicated = []
        
        for entity in entities:
            # Create a key based on normalized name and entity type
            key = (entity.normalized_name.lower(), entity.entity_type)
            
            if key not in seen:
                seen[key] = entity
                deduplicated.append(entity)
            else:
                # Keep the entity with higher confidence
                if entity.confidence_score > seen[key].confidence_score:
                    # Replace with higher confidence entity
                    idx = deduplicated.index(seen[key])
                    deduplicated[idx] = entity
                    seen[key] = entity
        
        logger.info(f"Deduplicated: {len(entities)} -> {len(deduplicated)} entities")
        return deduplicated
    
    def normalize_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Normalize entity names.
        
        Args:
            entities: List of entities to normalize
            
        Returns:
            Normalized list of entities
        """
        normalized = []
        
        for entity in entities:
            # Apply normalization from the extractor
            normalized_name = entity.name  # Extractors should handle normalization
            entity.normalized_name = normalized_name
            normalized.append(entity)
        
        return normalized
    
    def extract(self, context: ExtractionContext) -> List[ExtractedEntity]:
        """Run full extraction pipeline.
        
        Args:
            context: Extraction context
            
        Returns:
            Final list of extracted entities
        """
        start_time = time.time()
        
        logger.info(f"Starting entity extraction for document {context.document_id}")
        
        # Run extractors
        results = self.run_extractors(context)
        
        # Merge results
        entities = self.merge_results(results)
        logger.info(f"Merged {len(entities)} entities from {len(results)} extractors")
        
        # Normalize entities
        entities = self.normalize_entities(entities)
        
        # Deduplicate entities
        entities = self.deduplicate_entities(entities)
        
        extraction_time = time.time() - start_time
        logger.info(f"Entity extraction completed in {extraction_time:.2f}s: {len(entities)} final entities")
        
        return entities
    
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
            "total_entities": sum(len(r.entities) for r in results),
            "total_extraction_time": sum(r.extraction_time_seconds for r in results),
            "extractor_details": []
        }
        
        for result in results:
            stats["extractor_details"].append({
                "name": result.extractor_name,
                "success": result.success,
                "entity_count": len(result.entities),
                "extraction_time": result.extraction_time_seconds,
                "error": result.error_message
            })
        
        return stats
