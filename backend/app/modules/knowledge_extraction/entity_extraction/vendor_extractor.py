"""Vendor entity extractor using spaCy NLP."""
from typing import List
from app.modules.knowledge_extraction.entity_extraction.base_extractor import BaseEntityExtractor
from app.modules.knowledge_extraction.schemas import ExtractedEntity, ExtractionContext
from app.modules.knowledge_extraction.enums import EntityType, ExtractionMethod


class VendorExtractor(BaseEntityExtractor):
    """Extractor for vendor/supplier entities using spaCy NER."""
    
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
            print("spaCy not installed, VendorExtractor will not work")
        except Exception as e:
            print(f"Error loading spaCy model: {e}")
    
    def get_entity_type(self) -> EntityType:
        return EntityType.VENDOR
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.SPACY_NER
    
    def extract(self, context: ExtractionContext) -> List[ExtractedEntity]:
        """Extract vendor entities using spaCy NER."""
        entities = []
        
        if not self.nlp:
            return entities
        
        text = context.text
        doc = self.nlp(text)
        
        for ent in doc.ents:
            if ent.label_ in ["ORG", "COMPANY"]:
                org_name = ent.text.strip()
                start_offset = ent.start_char
                end_offset = ent.end_char
                
                # Check if context suggests vendor/supplier
                context_text = self._get_context_text(text, start_offset, end_offset)
                if self._is_vendor_context(context_text):
                    page_number = self._find_page_number(context, start_offset)
                    section = self._find_section(context, start_offset)
                    confidence = self._calculate_confidence(org_name, context_text)
                    
                    entity = ExtractedEntity(
                        name=org_name,
                        entity_type=EntityType.VENDOR,
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
    
    def _is_vendor_context(self, context: str) -> bool:
        """Check if context suggests vendor/supplier."""
        context_lower = context.lower()
        vendor_keywords = ['vendor', 'supplier', 'manufacturer', 'oem', 'contractor', 'service provider']
        return any(keyword in context_lower for keyword in vendor_keywords)
    
    def _calculate_confidence(self, vendor_name: str, context: str) -> float:
        confidence = 0.6
        if self._is_vendor_context(context):
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
