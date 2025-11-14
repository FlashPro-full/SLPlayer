"""
Animation engine for text and element animations
"""
from typing import Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import math


class AnimationType(Enum):
    """Types of animations"""
    SCROLL_LEFT = "scroll_left"
    SCROLL_RIGHT = "scroll_right"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    MARQUEE = "marquee"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    FADE_IN_OUT = "fade_in_out"
    TYPEWRITER = "typewriter"
    BOUNCE = "bounce"
    FLASH = "flash"


class AnimationEngine:
    """Engine for animating content elements"""
    
    def __init__(self):
        self.animations: Dict[str, Dict[str, Any]] = {}
        self.start_times: Dict[str, float] = {}
    
    def add_animation(self, element_id: str, animation_type: AnimationType, 
                     duration: float = 5.0, speed: float = 1.0, 
                     properties: Optional[Dict] = None):
        """Add animation to an element"""
        self.animations[element_id] = {
            "type": animation_type,
            "duration": duration,
            "speed": speed,
            "properties": properties or {},
            "start_time": datetime.now().timestamp()
        }
        self.start_times[element_id] = datetime.now().timestamp()
    
    def remove_animation(self, element_id: str):
        """Remove animation from an element"""
        if element_id in self.animations:
            del self.animations[element_id]
        if element_id in self.start_times:
            del self.start_times[element_id]
    
    def update_animation(self, element_id: str, current_time: float) -> Dict[str, Any]:
        """Update animation and return transformation properties"""
        if element_id not in self.animations:
            return {}
        
        anim = self.animations[element_id]
        elapsed = (current_time - self.start_times[element_id]) * anim["speed"]
        anim_type = anim["type"]
        duration = anim["duration"]
        
        # Normalize elapsed time to 0-1 range
        progress = (elapsed % duration) / duration if duration > 0 else 0
        
        result = {}
        
        if anim_type == AnimationType.SCROLL_LEFT:
            result["offset_x"] = -int(progress * 1000) % 1000
            result["offset_y"] = 0
        
        elif anim_type == AnimationType.SCROLL_RIGHT:
            result["offset_x"] = int(progress * 1000) % 1000
            result["offset_y"] = 0
        
        elif anim_type == AnimationType.SCROLL_UP:
            result["offset_x"] = 0
            result["offset_y"] = -int(progress * 1000) % 1000
        
        elif anim_type == AnimationType.SCROLL_DOWN:
            result["offset_x"] = 0
            result["offset_y"] = int(progress * 1000) % 1000
        
        elif anim_type == AnimationType.MARQUEE:
            # Continuous scrolling
            result["offset_x"] = int(progress * 2000) % 2000 - 1000
            result["offset_y"] = 0
        
        elif anim_type == AnimationType.FADE_IN:
            result["opacity"] = progress
        
        elif anim_type == AnimationType.FADE_OUT:
            result["opacity"] = 1.0 - progress
        
        elif anim_type == AnimationType.FADE_IN_OUT:
            if progress < 0.5:
                result["opacity"] = progress * 2
            else:
                result["opacity"] = 2 - (progress * 2)
        
        elif anim_type == AnimationType.TYPEWRITER:
            result["typewriter_progress"] = progress
        
        elif anim_type == AnimationType.BOUNCE:
            result["offset_y"] = -abs(math.sin(progress * math.pi * 2)) * 20
        
        elif anim_type == AnimationType.FLASH:
            result["opacity"] = 1.0 if int(progress * 10) % 2 == 0 else 0.3
        
        return result
    
    def get_animated_text(self, element_id: str, text: str, current_time: float) -> str:
        """Get animated text for typewriter effect"""
        if element_id not in self.animations:
            return text
        
        anim = self.animations[element_id]
        if anim["type"] != AnimationType.TYPEWRITER:
            return text
        
        elapsed = (current_time - self.start_times[element_id]) * anim["speed"]
        duration = anim["duration"]
        progress = min(elapsed / duration, 1.0) if duration > 0 else 1.0
        
        chars_to_show = int(len(text) * progress)
        return text[:chars_to_show]
    
    def clear_all(self):
        """Clear all animations"""
        self.animations.clear()
        self.start_times.clear()


