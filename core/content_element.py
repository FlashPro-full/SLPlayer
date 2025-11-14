"""
Content element definitions for different content types
"""
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

from config.constants import ContentType


class ContentElement:
    """Base class for content elements on the canvas"""
    
    def __init__(self, content_type: ContentType, x: int = 0, y: int = 0, 
                 width: int = 200, height: int = 100):
        self.id = f"element_{datetime.now().timestamp()}_{id(self)}"
        self.type = content_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.properties: Dict[str, Any] = {}
        self.created = datetime.now().isoformat()
        self.modified = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert element to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "properties": self.properties,
            "created": self.created,
            "modified": self.modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ContentElement':
        """Create element from dictionary"""
        content_type = ContentType(data.get("type", "text"))
        element = cls(content_type, 
                     data.get("x", 0),
                     data.get("y", 0),
                     data.get("width", 200),
                     data.get("height", 100))
        element.id = data.get("id", element.id)
        element.properties = data.get("properties", {})
        element.created = data.get("created", element.created)
        element.modified = data.get("modified", element.modified)
        return element


class TextElement(ContentElement):
    """Text content element"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 100):
        super().__init__(ContentType.TEXT, x, y, width, height)
        self.properties = {
            "text": "New Text",
            "font_family": "Arial",
            "font_size": 24,
            "color": "#000000",
            "alignment": "left",
            "bold": False,
            "italic": False,
            "underline": False,
            "animation": "None",
            "animation_speed": 1.0,
            # Text effects
            "text_shadow": False,
            "shadow_color": "#000000",
            "shadow_offset_x": 2,
            "shadow_offset_y": 2,
            "shadow_blur": 0,
            "text_outline": False,
            "outline_color": "#000000",
            "outline_width": 2,
            "text_gradient": False,
            "gradient_color1": "#000000",
            "gradient_color2": "#FFFFFF",
            "gradient_direction": "horizontal",
            # Element timing
            "duration": 5.0,  # Duration in seconds
            "transition_in": "none",  # Transition IN effect
            "transition_out": "none",  # Transition OUT effect
            "transition_duration_in": 1.0,  # Transition IN duration
            "transition_duration_out": 1.0,  # Transition OUT duration
            "display_order": 0  # Display order
        }


class SingleLineTextElement(ContentElement):
    """Single line scrolling text element"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 50):
        super().__init__(ContentType.SINGLE_LINE_TEXT, x, y, width, height)
        self.properties = {
            "text": "Scrolling Text",
            "font_family": "Arial",
            "font_size": 24,
            "color": "#000000",
            "speed": 5,
            "direction": "left"
        }


class Text3DElement(ContentElement):
    """3D text element"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 100):
        super().__init__(ContentType.TEXT_3D, x, y, width, height)
        self.properties = {
            "text": "3D Text",
            "font_family": "Arial",
            "font_size": 48,
            "color": "#000000",
            "depth": 10.0,  # 3D extrusion depth
            "rotation_x": 0.0,  # Rotation in degrees
            "rotation_y": 0.0,
            "rotation_z": 0.0,
            "lighting": True,
            "material": "default"  # Material type
        }


class VideoElement(ContentElement):
    """Video content element"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 640, height: int = 360):
        super().__init__(ContentType.VIDEO, x, y, width, height)
        self.properties = {
            "file_path": "",
            "loop": True,
            "volume": 100,
            "autoplay": True,
            # Element timing (for overlay)
            "display_order": 0  # Display order
        }


class PhotoElement(ContentElement):
    """Photo/image content element"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 400, height: int = 300):
        super().__init__(ContentType.PHOTO, x, y, width, height)
        self.properties = {
            "file_path": "",
            "fit_mode": "stretch",  # stretch, contain, cover
            "transparency": 100,
            # Image effects
            "brightness": 0,  # -100 to 100
            "contrast": 0,  # -100 to 100
            "saturation": 0,  # -100 to 100
            "filter": "none",  # "none", "grayscale", "sepia", "invert"
            # Element timing
            "duration": 5.0,  # Duration in seconds
            "transition_in": "none",  # Transition IN effect
            "transition_out": "none",  # Transition OUT effect
            "transition_duration_in": 1.0,  # Transition IN duration
            "transition_duration_out": 1.0,  # Transition OUT duration
            "display_order": 0  # Display order
        }


class ClockElement(ContentElement):
    """Clock widget element"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 100):
        super().__init__(ContentType.CLOCK, x, y, width, height)
        self.properties = {
            "format": "HH:mm:ss",
            "font_family": "Arial",
            "font_size": 48,
            "color": "#000000",
            "show_date": False,
            "date_format": "yyyy-MM-dd"
        }


class WeatherElement(ContentElement):
    """Weather widget element"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 150):
        super().__init__(ContentType.WEATHER, x, y, width, height)
        self.properties = {
            "api_key": "",  # OpenWeatherMap API key
            "city": "London",
            "units": "metric",  # "metric" or "imperial"
            "format": "{city}: {temperature}°C, {description}",
            "update_interval": 3600,  # seconds
            "font_size": 24,
            "color": "#000000",
            "show_icon": True
        }


class CalendarElement(ContentElement):
    """Calendar widget element"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 300, height: int = 300):
        super().__init__(ContentType.CALENDAR, x, y, width, height)
        self.properties = {
            "show_week_numbers": False,
            "first_day_of_week": "Monday",
            "highlight_today": True
        }


class NeonElement(ContentElement):
    """Neon sign effect element"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 100):
        super().__init__(ContentType.NEON, x, y, width, height)
        self.properties = {
            "neon_index": 0,
            "intensity": 100
        }


class TimerElement(ContentElement):
    """Timer/countdown widget element"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 100):
        super().__init__(ContentType.TIMING, x, y, width, height)
        self.properties = {
            "mode": "countdown",  # "countdown" or "timer"
            "duration": 60,  # Duration in seconds
            "format": "HH:mm:ss",  # Display format
            "font_family": "Arial",
            "font_size": 48,
            "color": "#000000",
            "auto_start": True
        }


def create_element(content_type: ContentType, x: int = 0, y: int = 0) -> ContentElement:
    """Factory function to create content elements"""
    default_sizes = {
        ContentType.TEXT: (200, 100),
        ContentType.SINGLE_LINE_TEXT: (200, 50),
        ContentType.VIDEO: (640, 360),
        ContentType.PHOTO: (400, 300),
        ContentType.CLOCK: (200, 100),
        ContentType.CALENDAR: (300, 300),
        ContentType.ANIMATION: (200, 200),
        ContentType.TEXT_3D: (200, 100),
        ContentType.TIMING: (200, 100),
        ContentType.WEATHER: (200, 150),
        ContentType.SENSOR: (200, 100),
        ContentType.NEON: (200, 100),
        ContentType.WPS: (400, 300),
        ContentType.TABLE: (400, 300),
        ContentType.OFFICE: (400, 300),
        ContentType.DIGITAL_WATCH: (200, 100),
        ContentType.HTML: (400, 300),
        ContentType.LIVESTREAM: (640, 360),
        ContentType.QR_CODE: (200, 200),
        ContentType.HDMI: (640, 360),
    }
    
    width, height = default_sizes.get(content_type, (200, 100))
    
    if content_type == ContentType.TEXT:
        return TextElement(x, y, width, height)
    elif content_type == ContentType.SINGLE_LINE_TEXT:
        return SingleLineTextElement(x, y, width, height)
    elif content_type == ContentType.VIDEO:
        return VideoElement(x, y, width, height)
    elif content_type == ContentType.PHOTO:
        return PhotoElement(x, y, width, height)
    elif content_type == ContentType.CLOCK:
        return ClockElement(x, y, width, height)
    elif content_type == ContentType.CALENDAR:
        return CalendarElement(x, y, width, height)
    elif content_type == ContentType.NEON:
        return NeonElement(x, y, width, height)
    elif content_type == ContentType.TIMING:
        return TimerElement(x, y, width, height)
    elif content_type == ContentType.WEATHER:
        return WeatherElement(x, y, width, height)
    elif content_type == ContentType.TEXT_3D:
        return Text3DElement(x, y, width, height)
    else:
        # Default element for other types
        return ContentElement(content_type, x, y, width, height)

