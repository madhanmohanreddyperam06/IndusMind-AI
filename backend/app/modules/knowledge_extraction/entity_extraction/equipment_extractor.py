"""Equipment entity extractor."""
import re
from typing import List
from app.modules.knowledge_extraction.entity_extraction.base_extractor import BaseEntityExtractor
from app.modules.knowledge_extraction.schemas import ExtractedEntity, ExtractionContext
from app.modules.knowledge_extraction.enums import EntityType, ExtractionMethod
from app.modules.knowledge_extraction.constants import EQUIPMENT_PATTERNS, EQUIPMENT_PREFIXES


class EquipmentExtractor(BaseEntityExtractor):
    """Extractor for industrial equipment entities.
    
    Extracts equipment like pumps, valves, compressors, motors, etc.
    with their tag numbers (e.g., P-101, V-204, C-301).
    """
    
    def __init__(self):
        """Initialize the equipment extractor."""
        super().__init__()
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for equipment extraction."""
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in EQUIPMENT_PATTERNS]
    
    def get_entity_type(self) -> EntityType:
        """Return the entity type."""
        return EntityType.EQUIPMENT
    
    def get_extraction_method(self) -> ExtractionMethod:
        """Return the extraction method."""
        return ExtractionMethod.PATTERN_MATCHING
    
    def extract(self, context: ExtractionContext) -> List[ExtractedEntity]:
        """Extract equipment entities from the context.
        
        Args:
            context: Extraction context
            
        Returns:
            List of extracted equipment entities
        """
        entities = []
        text = context.text
        
        for pattern in self.patterns:
            matches = pattern.finditer(text)
            
            for match in matches:
                tag = match.group()
                equipment_type = self._infer_equipment_type(tag)
                name = self._format_equipment_name(tag, equipment_type)
                
                # Get position information
                start_offset = match.start()
                end_offset = match.end()
                
                # Find page number if available
                page_number = self._find_page_number(context, start_offset)
                
                # Find section if available
                section = self._find_section(context, start_offset)
                
                # Get context text
                context_text = self._get_context_text(text, start_offset, end_offset)
                
                # Calculate confidence
                confidence = self._calculate_confidence(tag, context_text)
                
                entity = ExtractedEntity(
                    name=name,
                    entity_type=EntityType.EQUIPMENT,
                    confidence_score=confidence,
                    page_number=page_number,
                    section=section,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    context=context_text,
                    extraction_method=self.get_extraction_method(),
                    metadata={
                        "tag": tag,
                        "equipment_type": equipment_type,
                        "pattern_matched": pattern.pattern
                    }
                )
                
                if self.validate_entity(entity):
                    entities.append(entity)
        
        return entities
    
    def _infer_equipment_type(self, tag: str) -> str:
        """Infer equipment type from tag prefix.
        
        Args:
            tag: Equipment tag
            
        Returns:
            Equipment type
        """
        # Extract prefix (first letter(s) before number)
        match = re.match(r'^([A-Z]+)', tag.upper())
        if match:
            prefix = match.group(1)
            # Check single letter prefix
            if len(prefix) == 1 and prefix in EQUIPMENT_PREFIXES:
                return EQUIPMENT_PREFIXES[prefix]
            # Check two letter prefix
            elif len(prefix) == 2:
                first_letter = prefix[0]
                if first_letter in EQUIPMENT_PREFIXES:
                    return EQUIPMENT_PREFIXES[first_letter]
        
        return "Equipment"
    
    def _format_equipment_name(self, tag: str, equipment_type: str) -> str:
        """Format equipment name.
        
        Args:
            tag: Equipment tag
            equipment_type: Equipment type
            
        Returns:
            Formatted equipment name
        """
        # Normalize tag format (e.g., P101 -> P-101)
        normalized_tag = re.sub(r'([A-Z])(\d+)', r'\1-\2', tag.upper())
        return f"{equipment_type} {normalized_tag}"
    
    def _calculate_confidence(self, tag: str, context: str) -> float:
        """Calculate confidence score for the entity.
        
        Args:
            tag: Equipment tag
            context: Context text
            
        Returns:
            Confidence score
        """
        confidence = 0.7
        
        # Higher confidence for standard format (X-XXX)
        if re.match(r'^[A-Z]-\d{3,4}$', tag.upper()):
            confidence += 0.2
        
        # Check if context contains equipment-related words
        context_lower = context.lower()
        equipment_keywords = ['pump', 'valve', 'motor', 'compressor', 'tank', 'heater']
        if any(keyword in context_lower for keyword in equipment_keywords):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _find_page_number(self, context: ExtractionContext, offset: int) -> int:
        """Find page number for the given offset.
        
        Args:
            context: Extraction context
            offset: Text offset
            
        Returns:
            Page number or None
        """
        if not context.paragraphs:
            return None
        
        for para in context.paragraphs:
            if para.get('start_offset') and offset >= para['start_offset']:
                if para.get('end_offset') and offset <= para['end_offset']:
                    return para.get('page_number')
        
        return None
    
    def _find_section(self, context: ExtractionContext, offset: int) -> str:
        """Find section for the given offset.
        
        Args:
            context: Extraction context
            offset: Text offset
            
        Returns:
            Section title or None
        """
        if not context.sections:
            return None
        
        for section in context.sections:
            if section.get('start_offset') and offset >= section['start_offset']:
                if section.get('end_offset') and offset <= section['end_offset']:
                    return section.get('title')
        
        return None
    
    def _get_context_text(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get context text around the match.
        
        Args:
            text: Full text
            start: Match start offset
            end: Match end offset
            window: Window size for context
            
        Returns:
            Context text
        """
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
