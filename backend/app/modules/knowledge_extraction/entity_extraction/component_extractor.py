"""Component entity extractor."""
import re
from typing import List
from app.modules.knowledge_extraction.entity_extraction.base_extractor import BaseEntityExtractor
from app.modules.knowledge_extraction.schemas import ExtractedEntity, ExtractionContext
from app.modules.knowledge_extraction.enums import EntityType, ExtractionMethod
from app.modules.knowledge_extraction.constants import EQUIPMENT_TYPES


class ComponentExtractor(BaseEntityExtractor):
    """Extractor for industrial component entities.
    
    Extracts components like bearings, seals, gaskets, impellers, etc.
    that are parts of larger equipment.
    """
    
    def __init__(self):
        """Initialize the component extractor."""
        super().__init__()
        self.component_keywords = {
            'bearing', 'seal', 'gasket', 'impeller', 'shaft', 'coupling',
            'piston', 'valve seat', 'valve stem', 'diaphragm', 'packing',
            'ring', 'bushing', 'liner', 'nozzle', 'orifice', 'strainer',
            'filter element', 'sensor', 'transmitter', 'switch', 'actuator',
            'motor', 'gearbox', 'belt', 'chain', 'pulley', 'sprocket',
            'bearing housing', 'casing', 'cover', 'plate', 'flange',
            'bolt', 'nut', 'washer', 'screw', 'pin', 'key', 'retainer'
        }
    
    def get_entity_type(self) -> EntityType:
        """Return the entity type."""
        return EntityType.COMPONENT
    
    def get_extraction_method(self) -> ExtractionMethod:
        """Return the extraction method."""
        return ExtractionMethod.DICTIONARY_MATCHING
    
    def extract(self, context: ExtractionContext) -> List[ExtractedEntity]:
        """Extract component entities from the context.
        
        Args:
            context: Extraction context
            
        Returns:
            List of extracted component entities
        """
        entities = []
        text = context.text
        text_lower = text.lower()
        
        for keyword in self.component_keywords:
            # Find all occurrences of the keyword
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                component_name = match.group().strip()
                start_offset = match.start()
                end_offset = match.end()
                
                # Get position information
                page_number = self._find_page_number(context, start_offset)
                section = self._find_section(context, start_offset)
                context_text = self._get_context_text(text, start_offset, end_offset)
                
                # Calculate confidence
                confidence = self._calculate_confidence(component_name, context_text)
                
                entity = ExtractedEntity(
                    name=component_name.title(),
                    entity_type=EntityType.COMPONENT,
                    confidence_score=confidence,
                    page_number=page_number,
                    section=section,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    context=context_text,
                    extraction_method=self.get_extraction_method(),
                    metadata={
                        "keyword": keyword,
                        "matched_text": component_name
                    }
                )
                
                if self.validate_entity(entity):
                    entities.append(entity)
        
        return entities
    
    def _calculate_confidence(self, component_name: str, context: str) -> float:
        """Calculate confidence score for the entity.
        
        Args:
            component_name: Component name
            context: Context text
            
        Returns:
            Confidence score
        """
        confidence = 0.6
        
        # Higher confidence if context contains equipment-related words
        context_lower = context.lower()
        equipment_keywords = ['equipment', 'pump', 'valve', 'motor', 'replace', 'install']
        if any(keyword in context_lower for keyword in equipment_keywords):
            confidence += 0.2
        
        # Higher confidence if context contains maintenance-related words
        maintenance_keywords = ['maintenance', 'repair', 'inspection', 'failure', 'wear']
        if any(keyword in context_lower for keyword in maintenance_keywords):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _find_page_number(self, context: ExtractionContext, offset: int) -> int:
        """Find page number for the given offset."""
        if not context.paragraphs:
            return None
        
        for para in context.paragraphs:
            if para.get('start_offset') and offset >= para['start_offset']:
                if para.get('end_offset') and offset <= para['end_offset']:
                    return para.get('page_number')
        
        return None
    
    def _find_section(self, context: ExtractionContext, offset: int) -> str:
        """Find section for the given offset."""
        if not context.sections:
            return None
        
        for section in context.sections:
            if section.get('start_offset') and offset >= section['start_offset']:
                if section.get('end_offset') and offset <= section['end_offset']:
                    return section.get('title')
        
        return None
    
    def _get_context_text(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get context text around the match."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
