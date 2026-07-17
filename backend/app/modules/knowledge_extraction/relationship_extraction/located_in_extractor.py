"""LOCATED_IN relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class LocatedInExtractor(BaseRelationshipExtractor):
    """Extractor for LOCATED_IN relationships (Equipment -> Location)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.LOCATED_IN
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract LOCATED_IN relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get equipment and location entities
        equipment_entities = [e for e in entities if e.entity_type == EntityType.EQUIPMENT]
        location_entities = [e for e in entities if e.entity_type == EntityType.LOCATION]
        
        for equipment in equipment_entities:
            for location in location_entities:
                if self._are_related(equipment, location, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=equipment.name,
                        target_entity_name=location.name,
                        source_entity_type=equipment.entity_type,
                        target_entity_type=location.entity_type,
                        relationship_type=RelationshipType.LOCATED_IN,
                        confidence_score=0.7,
                        page_number=equipment.page_number,
                        paragraph=equipment.paragraph,
                        evidence_text=self._get_evidence_text(context, equipment, location),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, equipment, location, text: str, context: ExtractionContext) -> bool:
        """Check if equipment and location are related."""
        if hasattr(equipment, 'start_offset') and hasattr(location, 'start_offset'):
            distance = abs(equipment.start_offset - location.start_offset)
            if distance > 500:
                return False
        
        window = self._get_window_text(text, equipment, location)
        relationship_keywords = ['located in', 'located at', 'situated in', 'positioned in', 'installed in']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        return True
    
    def _get_window_text(self, text: str, equipment, location, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(equipment, 'start_offset') or not hasattr(location, 'start_offset'):
            return ""
        start = min(equipment.start_offset, location.start_offset)
        end = max(equipment.start_offset, location.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, equipment, location) -> str:
        """Get evidence text for the relationship."""
        if hasattr(equipment, 'context') and equipment.context:
            return equipment.context
        if hasattr(location, 'context') and location.context:
            return location.context
        return ""
