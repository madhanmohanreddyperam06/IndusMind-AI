"""OCR engine with PaddleOCR primary and Tesseract fallback."""
from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from pathlib import Path
from PIL import Image
import numpy as np
from app.modules.document_processing.exceptions import OCRException
from app.modules.document_processing.enums import OCRProvider


class BaseOCREngine(ABC):
    """Abstract base class for OCR engines."""
    
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """Extract text from image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
            
        Raises:
            OCRException: If OCR fails
        """
        pass
    
    @abstractmethod
    def extract_text_with_boxes(self, image_path: str) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        """Extract text with bounding boxes.
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of (text, bounding_box) tuples
            
        Raises:
            OCRException: If OCR fails
        """
        pass


class PaddleOCREngine(BaseOCREngine):
    """PaddleOCR engine - primary OCR provider."""
    
    def __init__(self):
        """Initialize PaddleOCR engine."""
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
            self.available = True
        except ImportError:
            self.available = False
        except Exception as e:
            self.available = False
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using PaddleOCR.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
            
        Raises:
            OCRException: If OCR fails
        """
        if not self.available:
            raise OCRException("PaddleOCR is not available")
        
        try:
            result = self.ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                return ""
            
            # Extract text from results
            text_lines = []
            for line in result[0]:
                if line and len(line) > 0:
                    text_lines.append(line[1][0])
            
            return '\n'.join(text_lines)
            
        except Exception as e:
            raise OCRException(f"PaddleOCR failed: {str(e)}")
    
    def extract_text_with_boxes(self, image_path: str) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        """Extract text with bounding boxes using PaddleOCR.
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of (text, bounding_box) tuples
            
        Raises:
            OCRException: If OCR fails
        """
        if not self.available:
            raise OCRException("PaddleOCR is not available")
        
        try:
            result = self.ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                return []
            
            # Extract text with bounding boxes
            text_boxes = []
            for line in result[0]:
                if line and len(line) > 0:
                    text = line[1][0]
                    box = line[0]
                    # Convert box to simple bounding box (x0, y0, x1, y1)
                    x_coords = [point[0] for point in box]
                    y_coords = [point[1] for point in box]
                    bbox = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
                    text_boxes.append((text, bbox))
            
            return text_boxes
            
        except Exception as e:
            raise OCRException(f"PaddleOCR failed: {str(e)}")


class TesseractOCREngine(BaseOCREngine):
    """Tesseract OCR engine - fallback OCR provider."""
    
    def __init__(self):
        """Initialize Tesseract OCR engine."""
        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.available = True
        except ImportError:
            self.available = False
        except Exception as e:
            self.available = False
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using Tesseract.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
            
        Raises:
            OCRException: If OCR fails
        """
        if not self.available:
            raise OCRException("Tesseract is not available")
        
        try:
            text = self.pytesseract.image_to_string(Image.open(image_path))
            return text
        except Exception as e:
            raise OCRException(f"Tesseract failed: {str(e)}")
    
    def extract_text_with_boxes(self, image_path: str) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        """Extract text with bounding boxes using Tesseract.
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of (text, bounding_box) tuples
            
        Raises:
            OCRException: If OCR fails
        """
        if not self.available:
            raise OCRException("Tesseract is not available")
        
        try:
            data = self.pytesseract.image_to_data(Image.open(image_path), output_type=self.pytesseract.Output.DICT)
            
            text_boxes = []
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    bbox = (x, y, x + w, y + h)
                    text_boxes.append((text, bbox))
            
            return text_boxes
            
        except Exception as e:
            raise OCRException(f"Tesseract failed: {str(e)}")


class OCREngine:
    """OCR engine with fallback support."""
    
    def __init__(self, primary: OCRProvider = OCRProvider.PADDLE_OCR):
        """Initialize OCR engine with primary provider.
        
        Args:
            primary: Primary OCR provider
        """
        self.primary_provider = primary
        self.primary_engine = self._create_engine(primary)
        self.fallback_engine = self._create_fallback_engine()
    
    def _create_engine(self, provider: OCRProvider) -> BaseOCREngine:
        """Create OCR engine for provider.
        
        Args:
            provider: OCR provider
            
        Returns:
            OCR engine instance
        """
        if provider == OCRProvider.PADDLE_OCR:
            return PaddleOCREngine()
        elif provider == OCRProvider.TESSERACT:
            return TesseractOCREngine()
        else:
            raise OCRException(f"Unknown OCR provider: {provider}")
    
    def _create_fallback_engine(self) -> Optional[BaseOCREngine]:
        """Create fallback OCR engine.
        
        Returns:
            Fallback OCR engine or None
        """
        if self.primary_provider == OCRProvider.PADDLE_OCR:
            return TesseractOCREngine()
        elif self.primary_provider == OCRProvider.TESSERACT:
            return PaddleOCREngine()
        return None
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image with fallback.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
            
        Raises:
            OCRException: If all OCR engines fail
        """
        # Try primary engine
        try:
            return self.primary_engine.extract_text(image_path)
        except OCRException as e:
            if self.fallback_engine:
                try:
                    return self.fallback_engine.extract_text(image_path)
                except OCRException:
                    pass
            raise OCRException(f"All OCR engines failed: {str(e)}")
    
    def extract_text_with_boxes(self, image_path: str) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        """Extract text with bounding boxes with fallback.
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of (text, bounding_box) tuples
            
        Raises:
            OCRException: If all OCR engines fail
        """
        # Try primary engine
        try:
            return self.primary_engine.extract_text_with_boxes(image_path)
        except OCRException as e:
            if self.fallback_engine:
                try:
                    return self.fallback_engine.extract_text_with_boxes(image_path)
                except OCRException:
                    pass
            raise OCRException(f"All OCR engines failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if any OCR engine is available.
        
        Returns:
            True if at least one engine is available
        """
        return self.primary_engine.available or (self.fallback_engine and self.fallback_engine.available)
