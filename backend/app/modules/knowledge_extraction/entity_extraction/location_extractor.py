"""Location entity extractor using spaCy NLP."""
from typing import List
from app.modules.knowledge_extraction.entity_extraction.base_extractor import BaseEntityExtractor
from app.modules.knowledge_extraction.schemas import ExtractedEntity, ExtractionContext
from app.modules.knowledge_extraction.enums import EntityType, ExtractionMethod


class LocationExtractor(BaseEntityExtractor):
    """Extractor for location entities using spaCy NER."""
    
    def __init__(self):
        super().__init__()
        self.nlp = None
        self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load spaCy NLP model."""
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.nlp = spacy.load("en_core_web_lg")
        except ImportError:
            print("spaCy not installed, LocationExtractor will not work")
        except Exception as e:
            print(f"Error loading spaCy model: {e}")
    
    def get_entity_type(self) -> EntityType:
        return EntityType.LOCATION
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.SPACY_NER
    
    def extract(self, context: ExtractionContext) -> List[ExtractedEntity]:
        """Extract location entities using spaCy NER."""
        entities = []
        
        if not self.nlp:
            return entities
        
        text = context.text
        doc = self.nlp(text)
        
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC", "FAC"]:
                location_name = ent.text.strip()
                start_offset = ent.start_char
                end_offset = ent.end_char
                
                page_number = self._find_page_number(context, start_offset)
                section = self._find_section(context, start_offset)
                context_text = self._get_context_text(text, start_offset, end_offset)
                confidence = self._calculate_confidence(location_name, context_text)
                
                entity = ExtractedEntity(
                    name=location_name,
                    entity_type=EntityType.LOCATION,
                    confidence_score=confidence,
                    page_number=page_number,
                    section=section,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    context=context_text,
                    extraction_method=self.get_extraction_method(),
                    metadata={"spacy_label": ent.label_}
                )
                
                if self.validate_entity(entity):
                    entities.append(entity)
        
        return entities
    
    def _calculate_confidence(self, location_name: str, context: str) -> float:
        confidence = 0.7
        context_lower = context.lower()
        loc_keywords = ['plant', 'site', 'facility', 'unit', 'area', 'zone', 'location']
        if any(keyword in context_lower for keyword in loc_keywords):
            confidence += 0.1
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
