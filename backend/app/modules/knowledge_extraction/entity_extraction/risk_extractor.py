"""Risk entity extractor."""
import re
from typing import List
from app.modules.knowledge_extraction.entity_extraction.base_extractor import BaseEntityExtractor
from app.modules.knowledge_extraction.schemas import ExtractedEntity, ExtractionContext
from app.modules.knowledge_extraction.enums import EntityType, ExtractionMethod
from app.modules.knowledge_extraction.constants import RISK_TYPES


class RiskExtractor(BaseEntityExtractor):
    """Extractor for risk entities."""
    
    def __init__(self):
        super().__init__()
        self.risk_keywords = RISK_TYPES.copy()
    
    def get_entity_type(self) -> EntityType:
        return EntityType.RISK
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.DICTIONARY_MATCHING
    
    def extract(self, context: ExtractionContext) -> List[ExtractedEntity]:
        entities = []
        text = context.text
        text_lower = text.lower()
        
        for keyword in self.risk_keywords:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                risk_name = match.group().strip()
                start_offset = match.start()
                end_offset = match.end()
                
                page_number = self._find_page_number(context, start_offset)
                section = self._find_section(context, start_offset)
                context_text = self._get_context_text(text, start_offset, end_offset)
                confidence = self._calculate_confidence(risk_name, context_text)
                
                entity = ExtractedEntity(
                    name=risk_name.title(),
                    entity_type=EntityType.RISK,
                    confidence_score=confidence,
                    page_number=page_number,
                    section=section,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    context=context_text,
                    extraction_method=self.get_extraction_method(),
                    metadata={"keyword": keyword, "matched_text": risk_name}
                )
                
                if self.validate_entity(entity):
                    entities.append(entity)
        
        return entities
    
    def _calculate_confidence(self, risk_name: str, context: str) -> float:
        confidence = 0.7
        context_lower = context.lower()
        risk_keywords = ['risk', 'hazard', 'danger', 'assessment', 'mitigation']
        if any(keyword in context_lower for keyword in risk_keywords):
            confidence += 0.2
        return min(confidence, 1.0)
    
    def _find_page_number(self, context: ExtractionContext, offset: int) -> int:
        if not context.paragraphs:
            return None
        for para in context.paragraphs:
            if para.get('start_offset') and offset >= para['start_offset']:
                if para.get('end_offset') and offset <= para['end_offset']:
                    return para.get('page_number')
        return None
    
    def _find_section(self, context: ExtractionContext, offset: int) -> str:
        if not context.sections:
            return None
        for section in context.sections:
            if section.get('start_offset') and offset >= section['start_offset']:
                if section.get('end_offset') and offset <= section['end_offset']:
                    return section.get('title')
        return None
    
    def _get_context_text(self, text: str, start: int, end: int, window: int = 50) -> str:
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
