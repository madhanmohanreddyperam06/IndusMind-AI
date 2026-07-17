"""PERFORMED_ON relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class PerformedOnExtractor(BaseRelationshipExtractor):
    """Extractor for PERFORMED_ON relationships (Maintenance -> Equipment)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.PERFORMED_ON
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract PERFORMED_ON relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get maintenance and equipment entities
        maintenance_entities = [e for e in entities if e.entity_type == EntityType.MAINTENANCE_ACTIVITY]
        equipment_entities = [e for e in entities if e.entity_type == EntityType.EQUIPMENT]
        
        for maintenance in maintenance_entities:
            for equipment in equipment_entities:
                if self._are_related(maintenance, equipment, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=maintenance.name,
                        target_entity_name=equipment.name,
                        source_entity_type=maintenance.entity_type,
                        target_entity_type=equipment.entity_type,
                        relationship_type=RelationshipType.PERFORMED_ON,
                        confidence_score=0.7,
                        page_number=maintenance.page_number,
                        paragraph=maintenance.paragraph,
                        evidence_text=self._get_evidence_text(context, maintenance, equipment),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, maintenance, equipment, text: str, context: ExtractionContext) -> bool:
        """Check if maintenance and equipment are related."""
        if hasattr(maintenance, 'start_offset') and hasattr(equipment, 'start_offset'):
            distance = abs(maintenance.start_offset - equipment.start_offset)
            if distance > 500:
                return False
        
        window = self._get_window_text(text, maintenance, equipment)
        relationship_keywords = ['performed on', 'carried out on', 'done on', 'conducted on']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        return True
    
    def _get_window_text(self, text: str, maintenance, equipment, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(maintenance, 'start_offset') or not hasattr(equipment, 'start_offset'):
            return ""
        start = min(maintenance.start_offset, equipment.start_offset)
        end = max(maintenance.start_offset, equipment.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, maintenance, equipment) -> str:
        """Get evidence text for the relationship."""
        if hasattr(maintenance, 'context') and maintenance.context:
            return maintenance.context
        if hasattr(equipment, 'context') and equipment.context:
            return equipment.context
        return ""
