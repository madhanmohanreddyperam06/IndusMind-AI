"""Image extractor for embedded images."""
from typing import List, Optional
from pathlib import Path
from PIL import Image
import uuid
from app.modules.document_processing.schemas import ImageSchema
from app.modules.document_processing.constants import EXTRACTED_IMAGES_STORAGE_DIR


class ImageExtractor:
    """Extract and save images from documents."""
    
    def __init__(self):
        """Initialize image extractor."""
        self.storage_dir = Path(EXTRACTED_IMAGES_STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_image(self, image_data: bytes, document_id: str, page_number: int, image_index: int) -> str:
        """Save image data to storage.
        
        Args:
            image_data: Image bytes
            document_id: Document ID
            page_number: Page number
            image_index: Image index on page
            
        Returns:
            Path to saved image
        """
        # Create storage path
        image_filename = f"{document_id}_page{page_number}_img{image_index}.png"
        image_path = self.storage_dir / image_filename
        
        # Save image
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        return str(image_path)
    
    def extract_image_info(self, image_data: bytes) -> dict:
        """Extract metadata from image data.
        
        Args:
            image_data: Image bytes
            
        Returns:
            Dictionary with image metadata
        """
        try:
            from io import BytesIO
            img = Image.open(BytesIO(image_data))
            
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode
            }
        except Exception:
            return {}
    
    def resize_image(self, image_path: str, max_width: int = 800, max_height: int = 800) -> str:
        """Resize image to max dimensions.
        
        Args:
            image_path: Path to image
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            Path to resized image
        """
        try:
            img = Image.open(image_path)
            
            # Calculate new dimensions
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save resized image
            resized_path = image_path.replace('.png', '_resized.png')
            img.save(resized_path, 'PNG')
            
            return resized_path
        except Exception:
            return image_path
