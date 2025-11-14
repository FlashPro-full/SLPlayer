"""
Media processor for handling various media types
"""
from typing import Optional, Dict, List
from pathlib import Path
from PyQt6.QtGui import QPixmap, QImage
from config.constants import ContentType
from utils.logger import get_logger

logger = get_logger(__name__)


class MediaProcessor:
    """Processes and manages media files"""
    
    def __init__(self):
        self.media_cache: Dict[str, QPixmap] = {}
    
    def load_image(self, file_path: str) -> Optional[QPixmap]:
        """Load image file"""
        if not file_path or not Path(file_path).exists():
            return None
        
        # Check cache
        if file_path in self.media_cache:
            return self.media_cache[file_path]
        
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.media_cache[file_path] = pixmap
                return pixmap
        except Exception as e:
            logger.exception(f"Error loading image {file_path}: {e}")
        
        return None
    
    def get_image_info(self, file_path: str) -> Optional[Dict]:
        """Get image file information"""
        if not file_path or not Path(file_path).exists():
            return None
        
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                return {
                    "width": pixmap.width(),
                    "height": pixmap.height(),
                    "format": Path(file_path).suffix.lower()
                }
        except Exception as e:
            logger.exception(f"Error getting image info {file_path}: {e}")
        
        return None
    
    def validate_media_file(self, file_path: str, content_type: ContentType) -> bool:
        """Validate media file for content type"""
        if not file_path or not Path(file_path).exists():
            return False
        
        if content_type == ContentType.PHOTO:
            ext = Path(file_path).suffix.lower()
            return ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        elif content_type == ContentType.VIDEO:
            ext = Path(file_path).suffix.lower()
            return ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        
        return False
    
    def clear_cache(self):
        """Clear media cache"""
        self.media_cache.clear()

