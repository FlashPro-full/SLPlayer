"""
Resource manager for loading images and assets from resources folder
"""
from pathlib import Path
from typing import Optional, List
from PyQt5.QtGui import QPixmap, QImage


class ResourceManager:
    """Manages application resources (images, icons, etc.)"""
    
    def __init__(self):
        self.resources_path = Path(__file__).parent.parent / "resources"
        self.reference_path = self.resources_path / "Reference"
        self.images_path = self.reference_path / "images" if self.reference_path.exists() else None
    
    def get_frame_image(self, frame_id: int) -> Optional[QPixmap]:
        """Get frame border image by ID"""
        if not self.images_path:
            return None
        
        border_path = self.images_path / "Border"
        if not border_path.exists():
            return None
        
        # Frame IDs are 0-35 based on the file list
        frame_file = border_path / f"{frame_id:03d}.png"
        if frame_file.exists():
            pixmap = QPixmap(str(frame_file))
            return pixmap if not pixmap.isNull() else None
        
        return None
    
    def get_background_image(self, bg_id: int) -> Optional[QPixmap]:
        """Get background image by ID"""
        if not self.images_path:
            return None
        
        backdef_path = self.images_path / "BackDef"
        if not backdef_path.exists():
            return None
        
        # Background GIF files
        bg_file = backdef_path / f"{bg_id:03d}.gif"
        if bg_file.exists():
            pixmap = QPixmap(str(bg_file))
            return pixmap if not pixmap.isNull() else None
        
        return None
    
    def get_neon_background(self, index: int) -> Optional[QPixmap]:
        """Get neon GIF background by index"""
        if not self.resources_path:
            return None
        
        neon_path = self.resources_path / "Reference" / "neon_gif_background"
        if not neon_path.exists():
            return None
        
        neon_file = neon_path / f"neon_gif_{index}.gif"
        if neon_file.exists():
            pixmap = QPixmap(str(neon_file))
            return pixmap if not pixmap.isNull() else None
        
        return None
    
    def get_colorful_word_image(self, word_id: int) -> Optional[QPixmap]:
        """Get colorful word image by ID"""
        if not self.images_path:
            return None
        
        colorful_path = self.images_path / "Colorfulwords"
        if not colorful_path.exists():
            return None
        
        word_file = colorful_path / f"{word_id:03d}.gif"
        if word_file.exists():
            pixmap = QPixmap(str(word_file))
            return pixmap if not pixmap.isNull() else None
        
        return None
    
    def list_available_frames(self) -> List[int]:
        """List all available frame IDs"""
        if not self.images_path:
            return []
        
        border_path = self.images_path / "Border"
        if not border_path.exists():
            return []
        
        frames = []
        for file in border_path.glob("*.png"):
            try:
                frame_id = int(file.stem)
                frames.append(frame_id)
            except ValueError:
                continue
        
        return sorted(frames)
    
    def list_available_backgrounds(self) -> List[int]:
        """List all available background IDs"""
        if not self.images_path:
            return []
        
        backdef_path = self.images_path / "BackDef"
        if not backdef_path.exists():
            return []
        
        backgrounds = []
        for file in backdef_path.glob("*.gif"):
            try:
                bg_id = int(file.stem)
                backgrounds.append(bg_id)
            except ValueError:
                continue
        
        return sorted(backgrounds)


# Global resource manager instance
resource_manager = ResourceManager()

