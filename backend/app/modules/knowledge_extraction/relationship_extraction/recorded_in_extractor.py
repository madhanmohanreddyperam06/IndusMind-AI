"""RECORDED_IN relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class RecordedInExtractor(BaseRelationshipExtractor):
    """Extractor for RECORDED_IN relationships (Failure -> Document)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.RECORDED_IN
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract RECORDED_IN relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get failure and document reference entities
        failure_entities = [e for e in entities if e.entity_type == EntityType.FAILURE]
        doc_entities = [e for e in entities if e.entity_type == EntityType.DOCUMENT_REFERENCE]
        
        for failure in failure_entities:
            for doc in doc_entities:
                if self._are_related(failure, doc, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=failure.name,
                        target_entity_name=doc.name,
                        source_entity_type=failure.entity_type,
                        target_entity_type=doc.entity_type,
                        relationship_type=RelationshipType.RECORDED_IN,
                        confidence_score=0.7,
                        page_number=failure.page_number,
                        paragraph=failure.paragraph,
                        evidence_text=self._get_evidence_text(context, failure, doc),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, failure, doc, text: str, context: ExtractionContext) -> bool:
        """Check if failure and document are related."""
        if hasattr(failure, 'start_offset') and hasattr(doc, 'start_offset'):
            distance = abs(failure.start_offset - doc.start_offset)
            if distance > 500:
                return False
        
        window = self._get_window_text(text, failure, doc)
        relationship_keywords = ['recorded in', 'documented in', 'reported in', 'mentioned in']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        return True
    
    def _get_window_text(self, text: str, failure, doc, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(failure, 'start_offset') or not hasattr(doc, 'start_offset'):
            return ""
        start = min(failure.start_offset, doc.start_offset)
        end = max(failure.start_offset, doc.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, failure, doc) -> str:
        """Get evidence text for the relationship."""
        if hasattr(failure, 'context') and failure.context:
            return failure.context
        if hasattr(doc, 'context') and doc.context:
            return doc.context
        return ""
