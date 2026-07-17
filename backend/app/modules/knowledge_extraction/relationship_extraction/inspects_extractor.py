"""INSPECTS relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class InspectsExtractor(BaseRelationshipExtractor):
    """Extractor for INSPECTS relationships (Inspection -> Equipment)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.INSPECTS
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract INSPECTS relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get inspection and equipment entities
        inspection_entities = [e for e in entities if e.entity_type == EntityType.INSPECTION]
        equipment_entities = [e for e in entities if e.entity_type == EntityType.EQUIPMENT]
        
        for inspection in inspection_entities:
            for equipment in equipment_entities:
                if self._are_related(inspection, equipment, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=inspection.name,
                        target_entity_name=equipment.name,
                        source_entity_type=inspection.entity_type,
                        target_entity_type=equipment.entity_type,
                        relationship_type=RelationshipType.INSPECTS,
                        confidence_score=0.7,
                        page_number=inspection.page_number,
                        paragraph=inspection.paragraph,
                        evidence_text=self._get_evidence_text(context, inspection, equipment),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, inspection, equipment, text: str, context: ExtractionContext) -> bool:
        """Check if inspection and equipment are related."""
        if hasattr(inspection, 'start_offset') and hasattr(equipment, 'start_offset'):
            distance = abs(inspection.start_offset - equipment.start_offset)
            if distance > 500:
                return False
        
        window = self._get_window_text(text, inspection, equipment)
        relationship_keywords = ['inspects', 'inspected', 'inspection of', 'checked']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        return True
    
    def _get_window_text(self, text: str, inspection, equipment, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(inspection, 'start_offset') or not hasattr(equipment, 'start_offset'):
            return ""
        start = min(inspection.start_offset, equipment.start_offset)
        end = max(inspection.start_offset, equipment.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, inspection, equipment) -> str:
        """Get evidence text for the relationship."""
        if hasattr(inspection, 'context') and inspection.context:
            return inspection.context
        if hasattr(equipment, 'context') and equipment.context:
            return equipment.context
        return ""
