"""APPLIES_TO relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class AppliesToExtractor(BaseRelationshipExtractor):
    """Extractor for APPLIES_TO relationships (Regulation -> Equipment)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.APPLIES_TO
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract APPLIES_TO relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get regulation and equipment entities
        regulation_entities = [e for e in entities if e.entity_type == EntityType.REGULATION]
        equipment_entities = [e for e in entities if e.entity_type == EntityType.EQUIPMENT]
        
        for regulation in regulation_entities:
            for equipment in equipment_entities:
                if self._are_related(regulation, equipment, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=regulation.name,
                        target_entity_name=equipment.name,
                        source_entity_type=regulation.entity_type,
                        target_entity_type=equipment.entity_type,
                        relationship_type=RelationshipType.APPLIES_TO,
                        confidence_score=0.7,
                        page_number=regulation.page_number,
                        paragraph=regulation.paragraph,
                        evidence_text=self._get_evidence_text(context, regulation, equipment),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, regulation, equipment, text: str, context: ExtractionContext) -> bool:
        """Check if regulation and equipment are related."""
        if hasattr(regulation, 'start_offset') and hasattr(equipment, 'start_offset'):
            distance = abs(regulation.start_offset - equipment.start_offset)
            if distance > 500:
                return False
        
        window = self._get_window_text(text, regulation, equipment)
        relationship_keywords = ['applies to', 'applicable to', 'covers', 'governs', 'regulates']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        return True
    
    def _get_window_text(self, text: str, regulation, equipment, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(regulation, 'start_offset') or not hasattr(equipment, 'start_offset'):
            return ""
        start = min(regulation.start_offset, equipment.start_offset)
        end = max(regulation.start_offset, equipment.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, regulation, equipment) -> str:
        """Get evidence text for the relationship."""
        if hasattr(regulation, 'context') and regulation.context:
            return regulation.context
        if hasattr(equipment, 'context') and equipment.context:
            return equipment.context
        return ""
