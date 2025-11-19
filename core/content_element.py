from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

from config.constants import ContentType


class ContentElement:
    
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
            "duration": 5.0,
            "transition_in": "none",
            "transition_out": "none",
            "transition_duration_in": 1.0,
            "transition_duration_out": 1.0,
            "display_order": 0
        }


class SingleLineTextElement(ContentElement):
    
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


class VideoElement(ContentElement):
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 640, height: int = 360):
        super().__init__(ContentType.VIDEO, x, y, width, height)
        self.properties = {
            "file_path": "",
            "loop": True,
            "volume": 100,
            "autoplay": True,
            "display_order": 0
        }


class PhotoElement(ContentElement):
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 400, height: int = 300):
        super().__init__(ContentType.PHOTO, x, y, width, height)
        self.properties = {
            "file_path": "",
            "fit_mode": "stretch",
            "transparency": 100,
            "brightness": 0,
            "contrast": 0,
            "saturation": 0,
            "filter": "none",
            "duration": 5.0,
            "transition_in": "none",
            "transition_out": "none",
            "transition_duration_in": 1.0,
            "transition_duration_out": 1.0,
            "display_order": 0
        }


class ClockElement(ContentElement):
    
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


class AnimationElement(ContentElement):
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 200):
        super().__init__(ContentType.ANIMATION, x, y, width, height)
        self.properties = {
            "animation_type": "none",
            "speed": 1.0,
            "loop": True
        }


class TimerElement(ContentElement):
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 100):
        super().__init__(ContentType.TIMING, x, y, width, height)
        self.properties = {
            "mode": "countdown",
            "duration": 60,
            "format": "HH:mm:ss",
            "font_family": "Arial",
            "font_size": 48,
            "color": "#000000",
            "auto_start": True
        }


class WeatherElement(ContentElement):
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 150):
        super().__init__(ContentType.WEATHER, x, y, width, height)
        self.properties = {
            "api_key": "",
            "city": "London",
            "units": "metric",
            "format": "{city}: {temperature}°C, {description}",
            "update_interval": 3600,
            "font_size": 24,
            "color": "#000000",
            "show_icon": True
        }


class SensorElement(ContentElement):
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 100):
        super().__init__(ContentType.SENSOR, x, y, width, height)
        self.properties = {
            "sensor_type": "temperature",
            "unit": "celsius",
            "font_size": 24,
            "color": "#000000"
        }


class HtmlElement(ContentElement):
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 100):
        super().__init__(ContentType.HTML, x, y, width, height)
        self.properties = {
            "url": "https://www.google.com",
            "display_order": 0
        }

class HdmiElement(ContentElement):
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 100):
        super().__init__(ContentType.HDMI, x, y, width, height)
        self.properties = {
            "display_order": 0
        }

def create_element(content_type: ContentType, x: int = 0, y: int = 0) -> ContentElement:
    default_sizes = {
        ContentType.TEXT: (200, 100),
        ContentType.SINGLE_LINE_TEXT: (200, 50),
        ContentType.VIDEO: (640, 360),
        ContentType.PHOTO: (400, 300),
        ContentType.CLOCK: (200, 100),
        ContentType.ANIMATION: (200, 200),
        ContentType.TIMING: (200, 100),
        ContentType.WEATHER: (200, 150),
        ContentType.SENSOR: (200, 100),
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
    elif content_type == ContentType.ANIMATION:
        return AnimationElement(x, y, width, height)
    elif content_type == ContentType.TIMING:
        return TimerElement(x, y, width, height)
    elif content_type == ContentType.WEATHER:
        return WeatherElement(x, y, width, height)
    elif content_type == ContentType.SENSOR:
        return SensorElement(x, y, width, height)
    else:
        return ContentElement(content_type, x, y, width, height)

