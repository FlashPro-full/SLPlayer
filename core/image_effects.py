"""
Image effects processor for brightness, contrast, and filters
"""
from typing import Optional
from PyQt5.QtGui import QImage, QPixmap
from utils.logger import get_logger

logger = get_logger(__name__)


class ImageEffects:
    """Apply effects to images"""
    
    @staticmethod
    def apply_brightness_contrast(pixmap: QPixmap, brightness: int = 0, contrast: int = 0) -> QPixmap:
        """
        Apply brightness and contrast adjustments to a pixmap.
        brightness: -100 to 100 (0 = no change)
        contrast: -100 to 100 (0 = no change)
        """
        if pixmap.isNull():
            return pixmap
        
        image = pixmap.toImage()
        if image.isNull():
            return pixmap
        
        # Convert brightness/contrast to factors
        brightness_factor = (brightness + 100) / 100.0
        contrast_factor = (contrast + 100) / 100.0
        
        # Apply to each pixel
        try:
            for y in range(image.height()):
                for x in range(image.width()):
                    try:
                        pixel = image.pixel(x, y)
                        r = (pixel >> 16) & 0xFF
                        g = (pixel >> 8) & 0xFF
                        b = pixel & 0xFF
                        a = (pixel >> 24) & 0xFF
                        
                        # Apply brightness
                        r = int(r * brightness_factor)
                        g = int(g * brightness_factor)
                        b = int(b * brightness_factor)
                        
                        # Apply contrast (center around 128)
                        r = int(128 + (r - 128) * contrast_factor)
                        g = int(128 + (g - 128) * contrast_factor)
                        b = int(128 + (b - 128) * contrast_factor)
                        
                        # Clamp values
                        r = max(0, min(255, r))
                        g = max(0, min(255, g))
                        b = max(0, min(255, b))
                        
                        # Reconstruct pixel
                        new_pixel = (a << 24) | (r << 16) | (g << 8) | b
                        image.setPixel(x, y, new_pixel)
                    except Exception as e:
                        logger.warning(f"Error processing pixel at ({x}, {y}): {e}")
                        continue
        except Exception as e:
            logger.error(f"Error applying brightness/contrast: {e}")
            return pixmap  # Return original on error
        
        return QPixmap.fromImage(image)
    
    @staticmethod
    def apply_saturation(pixmap: QPixmap, saturation: int = 0) -> QPixmap:
        """
        Apply saturation adjustment.
        saturation: -100 to 100 (0 = no change, -100 = grayscale)
        """
        if pixmap.isNull():
            return pixmap
        
        image = pixmap.toImage()
        if image.isNull():
            return pixmap
        
        saturation_factor = (saturation + 100) / 100.0
        
        try:
            for y in range(image.height()):
                for x in range(image.width()):
                    try:
                        pixel = image.pixel(x, y)
                        r = (pixel >> 16) & 0xFF
                        g = (pixel >> 8) & 0xFF
                        b = pixel & 0xFF
                        a = (pixel >> 24) & 0xFF
                        
                        # Convert to grayscale
                        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                        
                        # Interpolate between grayscale and original
                        r = int(gray + (r - gray) * saturation_factor)
                        g = int(gray + (g - gray) * saturation_factor)
                        b = int(gray + (b - gray) * saturation_factor)
                        
                        # Clamp values
                        r = max(0, min(255, r))
                        g = max(0, min(255, g))
                        b = max(0, min(255, b))
                        
                        new_pixel = (a << 24) | (r << 16) | (g << 8) | b
                        image.setPixel(x, y, new_pixel)
                    except Exception as e:
                        logger.warning(f"Error processing pixel at ({x}, {y}): {e}")
                        continue
        except Exception as e:
            logger.error(f"Error applying saturation: {e}")
            return pixmap  # Return original on error
        
        return QPixmap.fromImage(image)
    
    @staticmethod
    def apply_filter(pixmap: QPixmap, filter_type: str = "none") -> QPixmap:
        """
        Apply a filter effect.
        filter_type: "none", "grayscale", "sepia", "invert"
        """
        if pixmap.isNull() or filter_type == "none":
            return pixmap
        
        image = pixmap.toImage()
        if image.isNull():
            return pixmap
        
        try:
            for y in range(image.height()):
                for x in range(image.width()):
                    try:
                        pixel = image.pixel(x, y)
                        r = (pixel >> 16) & 0xFF
                        g = (pixel >> 8) & 0xFF
                        b = pixel & 0xFF
                        a = (pixel >> 24) & 0xFF
                        
                        if filter_type == "grayscale":
                            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                            r = g = b = gray
                        elif filter_type == "sepia":
                            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                            r = min(255, tr)
                            g = min(255, tg)
                            b = min(255, tb)
                        elif filter_type == "invert":
                            r = 255 - r
                            g = 255 - g
                            b = 255 - b
                        
                        new_pixel = (a << 24) | (r << 16) | (g << 8) | b
                        image.setPixel(x, y, new_pixel)
                    except Exception as e:
                        logger.warning(f"Error processing pixel at ({x}, {y}): {e}")
                        continue
        except Exception as e:
            logger.error(f"Error applying filter '{filter_type}': {e}")
            return pixmap  # Return original on error
        
        return QPixmap.fromImage(image)

