"""REFERENCES relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class ReferencesExtractor(BaseRelationshipExtractor):
    """Extractor for REFERENCES relationships (Document -> Equipment)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.REFERENCES
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract REFERENCES relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get document reference and equipment entities
        doc_entities = [e for e in entities if e.entity_type == EntityType.DOCUMENT_REFERENCE]
        equipment_entities = [e for e in entities if e.entity_type == EntityType.EQUIPMENT]
        
        for doc in doc_entities:
            for equipment in equipment_entities:
                if self._are_related(doc, equipment, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=doc.name,
                        target_entity_name=equipment.name,
                        source_entity_type=doc.entity_type,
                        target_entity_type=equipment.entity_type,
                        relationship_type=RelationshipType.REFERENCES,
                        confidence_score=0.7,
                        page_number=doc.page_number,
                        paragraph=doc.paragraph,
                        evidence_text=self._get_evidence_text(context, doc, equipment),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, doc, equipment, text: str, context: ExtractionContext) -> bool:
        """Check if document and equipment are related."""
        if hasattr(doc, 'start_offset') and hasattr(equipment, 'start_offset'):
            distance = abs(doc.start_offset - equipment.start_offset)
            if distance > 500:
                return False
        
        window = self._get_window_text(text, doc, equipment)
        relationship_keywords = ['references', 'refers to', 'mentions', 'describes', 'covers']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        return True
    
    def _get_window_text(self, text: str, doc, equipment, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(doc, 'start_offset') or not hasattr(equipment, 'start_offset'):
            return ""
        start = min(doc.start_offset, equipment.start_offset)
        end = max(doc.start_offset, equipment.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, doc, equipment) -> str:
        """Get evidence text for the relationship."""
        if hasattr(doc, 'context') and doc.context:
            return doc.context
        if hasattr(equipment, 'context') and equipment.context:
            return equipment.context
        return ""
