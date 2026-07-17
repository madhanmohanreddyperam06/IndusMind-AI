"""HAS_COMPONENT relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class HasComponentExtractor(BaseRelationshipExtractor):
    """Extractor for HAS_COMPONENT relationships (Equipment -> Component)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.HAS_COMPONENT
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract HAS_COMPONENT relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get equipment and component entities
        equipment_entities = [e for e in entities if e.entity_type == EntityType.EQUIPMENT]
        component_entities = [e for e in entities if e.entity_type == EntityType.COMPONENT]
        
        # Find relationships based on proximity and keywords
        for equipment in equipment_entities:
            for component in component_entities:
                # Check if they appear in the same sentence/paragraph
                if self._are_related(equipment, component, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=equipment.name,
                        target_entity_name=component.name,
                        source_entity_type=equipment.entity_type,
                        target_entity_type=component.entity_type,
                        relationship_type=RelationshipType.HAS_COMPONENT,
                        confidence_score=0.7,
                        page_number=equipment.page_number,
                        paragraph=equipment.paragraph,
                        evidence_text=self._get_evidence_text(context, equipment, component),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, equipment, component, text: str, context: ExtractionContext) -> bool:
        """Check if equipment and component are related."""
        # Check proximity
        if hasattr(equipment, 'start_offset') and hasattr(component, 'start_offset'):
            distance = abs(equipment.start_offset - component.start_offset)
            if distance > 500:  # Too far apart
                return False
        
        # Check for relationship keywords
        window = self._get_window_text(text, equipment, component)
        relationship_keywords = ['contains', 'includes', 'has', 'with', 'consists of', 'comprises']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        # Default: if they're close, assume relationship
        return True
    
    def _get_window_text(self, text: str, equipment, component, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(equipment, 'start_offset') or not hasattr(component, 'start_offset'):
            return ""
        
        start = min(equipment.start_offset, component.start_offset)
        end = max(equipment.start_offset, component.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, equipment, component) -> str:
        """Get evidence text for the relationship."""
        if hasattr(equipment, 'context') and equipment.context:
            return equipment.context
        if hasattr(component, 'context') and component.context:
            return component.context
        return ""
