"""
Keyframe system for animation interpolation
"""
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from utils.logger import get_logger

logger = get_logger(__name__)


class InterpolationType(Enum):
    """Keyframe interpolation types"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    STEP = "step"  # No interpolation, instant change


class Keyframe:
    """Represents a single keyframe"""
    
    def __init__(self, time: float, properties: Dict[str, Any], 
                 interpolation: InterpolationType = InterpolationType.LINEAR):
        self.time = time
        self.properties = properties.copy()
        self.interpolation = interpolation
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "time": self.time,
            "properties": self.properties,
            "interpolation": self.interpolation.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Keyframe':
        """Create from dictionary"""
        interpolation = InterpolationType(data.get("interpolation", "linear"))
        return cls(
            data["time"],
            data.get("properties", {}),
            interpolation
        )


class KeyframeTrack:
    """Track containing keyframes for a single element"""
    
    def __init__(self, element_id: str):
        self.element_id = element_id
        self.keyframes: List[Keyframe] = []
    
    def add_keyframe(self, keyframe: Keyframe):
        """Add a keyframe"""
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda k: k.time)
    
    def remove_keyframe(self, time: float, tolerance: float = 0.1):
        """Remove keyframe at or near specified time"""
        self.keyframes = [k for k in self.keyframes if abs(k.time - time) > tolerance]
    
    def get_keyframe_at(self, time: float, tolerance: float = 0.1) -> Optional[Keyframe]:
        """Get keyframe at or near specified time"""
        for keyframe in self.keyframes:
            if abs(keyframe.time - time) < tolerance:
                return keyframe
        return None
    
    def get_interpolated_properties(self, time: float) -> Dict[str, Any]:
        """Get interpolated properties at specified time"""
        if not self.keyframes:
            return {}
        
        # Find surrounding keyframes
        before = None
        after = None
        
        for keyframe in self.keyframes:
            if keyframe.time <= time:
                before = keyframe
            elif keyframe.time > time:
                after = keyframe
                break
        
        # If before first keyframe, return first keyframe properties
        if before is None:
            return self.keyframes[0].properties.copy()
        
        # If after last keyframe, return last keyframe properties
        if after is None:
            return self.keyframes[-1].properties.copy()
        
        # If exactly on a keyframe, return that keyframe's properties
        if abs(before.time - time) < 0.001:
            return before.properties.copy()
        
        # Interpolate between keyframes
        t = (time - before.time) / (after.time - before.time)
        
        # Apply interpolation curve
        interpolation_type = before.interpolation
        if interpolation_type == InterpolationType.EASE_IN:
            t = t * t
        elif interpolation_type == InterpolationType.EASE_OUT:
            t = 1 - (1 - t) * (1 - t)
        elif interpolation_type == InterpolationType.EASE_IN_OUT:
            if t < 0.5:
                t = 2 * t * t
            else:
                t = 1 - 2 * (1 - t) * (1 - t)
        elif interpolation_type == InterpolationType.STEP:
            t = 0.0  # Use before keyframe
        
        # Interpolate each property
        result = {}
        for key in set(before.properties.keys()) | set(after.properties.keys()):
            before_val = before.properties.get(key)
            after_val = after.properties.get(key)
            
            if before_val is None:
                result[key] = after_val
            elif after_val is None:
                result[key] = before_val
            elif isinstance(before_val, (int, float)) and isinstance(after_val, (int, float)):
                # Numeric interpolation
                result[key] = before_val + (after_val - before_val) * t
            else:
                # Non-numeric: use step interpolation
                result[key] = before_val if t < 0.5 else after_val
        
        return result


class KeyframeSystem:
    """Manages keyframe-based animations"""
    
    def __init__(self):
        self.tracks: Dict[str, KeyframeTrack] = {}
    
    def add_track(self, element_id: str) -> KeyframeTrack:
        """Add a keyframe track for an element"""
        if element_id not in self.tracks:
            self.tracks[element_id] = KeyframeTrack(element_id)
        return self.tracks[element_id]
    
    def remove_track(self, element_id: str):
        """Remove keyframe track"""
        if element_id in self.tracks:
            del self.tracks[element_id]
    
    def get_track(self, element_id: str) -> Optional[KeyframeTrack]:
        """Get track for element"""
        return self.tracks.get(element_id)
    
    def add_keyframe(self, element_id: str, time: float, properties: Dict[str, Any],
                     interpolation: InterpolationType = InterpolationType.LINEAR):
        """Add a keyframe"""
        track = self.add_track(element_id)
        keyframe = Keyframe(time, properties, interpolation)
        track.add_keyframe(keyframe)
    
    def get_interpolated_properties(self, element_id: str, time: float) -> Dict[str, Any]:
        """Get interpolated properties for element at time"""
        track = self.tracks.get(element_id)
        if track:
            return track.get_interpolated_properties(time)
        return {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "tracks": {
                element_id: {
                    "keyframes": [k.to_dict() for k in track.keyframes]
                }
                for element_id, track in self.tracks.items()
            }
        }
    
    def from_dict(self, data: Dict):
        """Load from dictionary"""
        self.tracks.clear()
        for element_id, track_data in data.get("tracks", {}).items():
            track = self.add_track(element_id)
            for keyframe_data in track_data.get("keyframes", []):
                keyframe = Keyframe.from_dict(keyframe_data)
                track.add_keyframe(keyframe)

