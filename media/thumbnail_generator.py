"""
Background thumbnail generation for videos and images
"""
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
from PyQt5.QtGui import QPixmap, QImage
from pathlib import Path
from typing import Optional, Dict
from utils.logger import get_logger
import os

logger = get_logger(__name__)


class ThumbnailCache:
    """Simple in-memory cache for thumbnails"""
    _instance = None
    _cache: Dict[str, QPixmap] = {}
    _max_cache_size = 100
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get(self, file_path: str) -> Optional[QPixmap]:
        return self._cache.get(file_path)
    
    def set(self, file_path: str, pixmap: QPixmap):
        # Simple LRU: remove oldest if cache is full
        if len(self._cache) >= self._max_cache_size:
            # Remove first item (simple approach)
            first_key = next(iter(self._cache))
            self._cache.pop(first_key)
        self._cache[file_path] = pixmap
    
    def clear(self):
        self._cache.clear()


class VideoThumbnailThread(QThread):
    """Thread for generating video thumbnails in background"""
    finished = pyqtSignal(str, object)  # file_path, QPixmap or None
    
    def __init__(self, video_path: str):
        super().__init__()
        self.video_path = video_path
    
    def run(self):
        try:
            # Check cache first
            cache = ThumbnailCache()
            cached = cache.get(self.video_path)
            if cached:
                self.finished.emit(self.video_path, cached)
                return
            
            # Generate thumbnail
            pixmap = self._generate_thumbnail()
            if pixmap:
                cache.set(self.video_path, pixmap)
            self.finished.emit(self.video_path, pixmap)
        except Exception as e:
            logger.error(f"Error generating thumbnail for {self.video_path}: {e}", exc_info=True)
            self.finished.emit(self.video_path, None)
    
    def _generate_thumbnail(self) -> Optional[QPixmap]:
        """Generate thumbnail using OpenCV"""
        try:
            import cv2
            import numpy as np
            
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                return None
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = np.ascontiguousarray(frame_rgb)
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            q_image = q_image.copy()  # Make a copy since frame_rgb may be temporary
            return QPixmap.fromImage(q_image)
        except ImportError:
            logger.warning("OpenCV not available for thumbnail generation")
            return None
        except Exception as e:
            logger.error(f"Error in thumbnail generation: {e}", exc_info=True)
            return None


class ImageThumbnailThread(QThread):
    """Thread for loading image thumbnails in background"""
    finished = pyqtSignal(str, object)  # file_path, QPixmap or None
    
    def __init__(self, image_path: str, max_size: int = 200):
        super().__init__()
        self.image_path = image_path
        self.max_size = max_size
    
    def run(self):
        try:
            # Check cache first
            cache = ThumbnailCache()
            cached = cache.get(self.image_path)
            if cached:
                self.finished.emit(self.image_path, cached)
                return
            
            # Load and scale image
            pixmap = QPixmap(self.image_path)
            if pixmap.isNull():
                self.finished.emit(self.image_path, None)
                return
            
            # Scale down if too large
            if pixmap.width() > self.max_size or pixmap.height() > self.max_size:
                pixmap = pixmap.scaled(
                    self.max_size, self.max_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            
            cache.set(self.image_path, pixmap)
            self.finished.emit(self.image_path, pixmap)
        except Exception as e:
            logger.error(f"Error loading thumbnail for {self.image_path}: {e}", exc_info=True)
            self.finished.emit(self.image_path, None)

