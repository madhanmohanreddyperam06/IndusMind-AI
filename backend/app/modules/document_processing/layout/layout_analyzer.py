"""Layout analyzer for document structure detection."""
from typing import List, Dict, Any, Optional
from app.modules.document_processing.schemas import ParagraphSchema, SectionSchema
from app.modules.document_processing.exceptions import LayoutAnalysisException


class LayoutAnalyzer:
    """Analyze document layout to identify structure."""
    
    def __init__(self):
        """Initialize layout analyzer."""
        self.min_heading_font_size = 14
        self.min_paragraph_font_size = 10
    
    def analyze_paragraphs(self, paragraphs: List[ParagraphSchema]) -> List[SectionSchema]:
        """Analyze paragraphs to identify sections and headings.
        
        Args:
            paragraphs: List of paragraph schemas
            
        Returns:
            List of identified sections
            
        Raises:
            LayoutAnalysisException: If analysis fails
        """
        try:
            sections = []
            current_section = None
            section_index = 0
            
            for para in paragraphs:
                # Check if this paragraph is a heading
                if self._is_heading(para):
                    # Save previous section if exists
                    if current_section:
                        sections.append(current_section)
                    
                    # Create new section
                    current_section = SectionSchema(
                        title=para.text,
                        level=self._determine_heading_level(para),
                        page_number=para.page,
                        paragraph_ids=[para.paragraph_id],
                        order_index=section_index
                    )
                    section_index += 1
                else:
                    # Add paragraph to current section
                    if current_section:
                        current_section.paragraph_ids.append(para.paragraph_id)
                    else:
                        # Create default section if no heading found yet
                        current_section = SectionSchema(
                            title="Introduction",
                            level=1,
                            page_number=para.page,
                            paragraph_ids=[para.paragraph_id],
                            order_index=section_index
                        )
                        section_index += 1
            
            # Don't forget the last section
            if current_section:
                sections.append(current_section)
            
            return sections
            
        except Exception as e:
            raise LayoutAnalysisException(f"Layout analysis failed: {str(e)}")
    
    def _is_heading(self, paragraph: ParagraphSchema) -> bool:
        """Determine if paragraph is a heading.
        
        Args:
            paragraph: Paragraph schema
            
        Returns:
            True if paragraph is a heading
        """
        # Check font size
        if paragraph.font_size and paragraph.font_size >= self.min_heading_font_size:
            return True
        
        # Check if explicitly marked as heading
        if paragraph.is_heading:
            return True
        
        # Check text characteristics
        text = paragraph.text.strip()
        
        # Short text likely heading
        if len(text) < 100 and len(text.split()) < 15:
            # All caps
            if text.isupper():
                return True
            
            # Numbered heading
            if text[0].isdigit() and (text[1] == '.' or text[1] == ' '):
                return True
            
            # Title case
            if text.istitle():
                return True
        
        return False
    
    def _determine_heading_level(self, paragraph: ParagraphSchema) -> int:
        """Determine heading level.
        
        Args:
            paragraph: Paragraph schema
            
        Returns:
            Heading level (1-6)
        """
        # Use explicit heading level if available
        if paragraph.heading_level:
            return paragraph.heading_level
        
        # Use font size to determine level
        if paragraph.font_size:
            if paragraph.font_size >= 24:
                return 1
            elif paragraph.font_size >= 20:
                return 2
            elif paragraph.font_size >= 18:
                return 3
            elif paragraph.font_size >= 16:
                return 4
            else:
                return 5
        
        # Use text pattern to determine level
        text = paragraph.text.strip()
        
        # Numbered heading (1., 2., etc.)
        if text[0].isdigit() and text[1] == '.':
            return 1
        
        # Numbered heading (1.1, 1.2, etc.)
        if '.' in text[:5]:
            parts = text.split('.')
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                return 2
        
        # Default to level 2
        return 2
    
    def detect_lists(self, paragraphs: List[ParagraphSchema]) -> Dict[str, List[str]]:
        """Detect list items in paragraphs.
        
        Args:
            paragraphs: List of paragraph schemas
            
        Returns:
            Dictionary with 'ordered' and 'unordered' lists
        """
        ordered_lists = []
        unordered_lists = []
        
        for para in paragraphs:
            text = para.text.strip()
            
            # Check for ordered list (1., 2., etc.)
            if text and text[0].isdigit() and (len(text) > 1 and text[1] in '.)'):
                ordered_lists.append(para.paragraph_id)
            
            # Check for unordered list (-, *, •, etc.)
            if text and text[0] in '-*•':
                unordered_lists.append(para.paragraph_id)
        
        return {
            'ordered': ordered_lists,
            'unordered': unordered_lists
        }
    
    def detect_page_breaks(self, paragraphs: List[ParagraphSchema]) -> List[int]:
        """Detect page breaks between paragraphs.
        
        Args:
            paragraphs: List of paragraph schemas
            
        Returns:
            List of paragraph indices where page breaks occur
        """
        page_breaks = []
        
        for i in range(1, len(paragraphs)):
            if paragraphs[i].page_number != paragraphs[i-1].page_number:
                page_breaks.append(i)
        
        return page_breaks
    
    def group_by_page(self, paragraphs: List[ParagraphSchema]) -> Dict[int, List[ParagraphSchema]]:
        """Group paragraphs by page number.
        
        Args:
            paragraphs: List of paragraph schemas
            
        Returns:
            Dictionary mapping page numbers to paragraph lists
        """
        pages = {}
        
        for para in paragraphs:
            page_num = para.page_number or 1
            if page_num not in pages:
                pages[page_num] = []
            pages[page_num].append(para)
        
        return pages
