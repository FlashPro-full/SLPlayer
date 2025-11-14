"""
Transition engine for element IN/OUT effects
"""
from typing import Dict, Optional, Any
from enum import Enum
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class TransitionType(Enum):
    """Transition effect types"""
    NONE = "none"
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    ROTATE = "rotate"
    BLUR = "blur"


class TransitionEngine:
    """Manages element transitions (IN/OUT effects)"""
    
    def __init__(self):
        self.transitions: Dict[str, Dict] = {}  # element_id -> transition state
    
    def add_transition(self, element_id: str, transition_in: str, transition_out: str,
                      duration_in: float = 1.0, duration_out: float = 1.0):
        """Add transition for an element"""
        self.transitions[element_id] = {
            "transition_in": transition_in,
            "transition_out": transition_out,
            "duration_in": duration_in,
            "duration_out": duration_out,
            "start_time": None,
            "end_time": None,
            "state": "idle"  # idle, transitioning_in, active, transitioning_out
        }
    
    def start_transition_in(self, element_id: str, start_time: float):
        """Start transition IN effect"""
        if element_id in self.transitions:
            self.transitions[element_id]["start_time"] = start_time
            self.transitions[element_id]["end_time"] = start_time + self.transitions[element_id]["duration_in"]
            self.transitions[element_id]["state"] = "transitioning_in"
    
    def start_transition_out(self, element_id: str, start_time: float):
        """Start transition OUT effect"""
        if element_id in self.transitions:
            self.transitions[element_id]["start_time"] = start_time
            self.transitions[element_id]["end_time"] = start_time + self.transitions[element_id]["duration_out"]
            self.transitions[element_id]["state"] = "transitioning_out"
    
    def get_transition_state(self, element_id: str, current_time: float) -> Dict[str, Any]:
        """
        Get current transition state for element.
        Returns: {
            "opacity": 0.0-1.0,
            "offset_x": int,
            "offset_y": int,
            "scale": 1.0,
            "rotation": 0.0,
            "blur": 0.0
        }
        """
        if element_id not in self.transitions:
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0.0, "blur": 0.0}
        
        transition = self.transitions[element_id]
        state = transition["state"]
        
        if state == "idle" or state == "active":
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0.0, "blur": 0.0}
        
        if state not in ["transitioning_in", "transitioning_out"]:
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0.0, "blur": 0.0}
        
        start_time = transition.get("start_time")
        end_time = transition.get("end_time")
        duration = transition.get("duration_in") if state == "transitioning_in" else transition.get("duration_out")
        
        if start_time is None or end_time is None:
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0.0, "blur": 0.0}
        
        if current_time < start_time:
            if state == "transitioning_in":
                return {"opacity": 0.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0.0, "blur": 0.0}
            else:
                return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0.0, "blur": 0.0}
        
        if current_time >= end_time:
            if state == "transitioning_in":
                transition["state"] = "active"
                return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0.0, "blur": 0.0}
            else:
                transition["state"] = "idle"
                return {"opacity": 0.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0.0, "blur": 0.0}
        
        # Calculate progress (0.0 to 1.0)
        progress = (current_time - start_time) / duration if duration > 0 else 1.0
        progress = max(0.0, min(1.0, progress))
        
        # Get transition type
        transition_type_str = transition.get("transition_in" if state == "transitioning_in" else "transition_out", "none")
        try:
            transition_type = TransitionType(transition_type_str.lower().replace(" ", "_"))
        except ValueError:
            transition_type = TransitionType.NONE
        
        # Apply easing (ease-in-out)
        if state == "transitioning_in":
            eased_progress = progress * progress * (3.0 - 2.0 * progress)  # Smoothstep
        else:
            eased_progress = 1.0 - (1.0 - progress) * (1.0 - progress) * (3.0 - 2.0 * (1.0 - progress))
        
        # Calculate transition effects
        result = {
            "opacity": 1.0,
            "offset_x": 0,
            "offset_y": 0,
            "scale": 1.0,
            "rotation": 0.0,
            "blur": 0.0
        }
        
        if transition_type == TransitionType.FADE:
            if state == "transitioning_in":
                result["opacity"] = eased_progress
            else:
                result["opacity"] = 1.0 - eased_progress
        
        elif transition_type == TransitionType.SLIDE_LEFT:
            offset = 200 * (1.0 - eased_progress) if state == "transitioning_in" else 200 * eased_progress
            result["offset_x"] = -int(offset) if state == "transitioning_in" else int(offset)
            result["opacity"] = eased_progress if state == "transitioning_in" else 1.0 - eased_progress
        
        elif transition_type == TransitionType.SLIDE_RIGHT:
            offset = 200 * (1.0 - eased_progress) if state == "transitioning_in" else 200 * eased_progress
            result["offset_x"] = int(offset) if state == "transitioning_in" else -int(offset)
            result["opacity"] = eased_progress if state == "transitioning_in" else 1.0 - eased_progress
        
        elif transition_type == TransitionType.SLIDE_UP:
            offset = 200 * (1.0 - eased_progress) if state == "transitioning_in" else 200 * eased_progress
            result["offset_y"] = -int(offset) if state == "transitioning_in" else int(offset)
            result["opacity"] = eased_progress if state == "transitioning_in" else 1.0 - eased_progress
        
        elif transition_type == TransitionType.SLIDE_DOWN:
            offset = 200 * (1.0 - eased_progress) if state == "transitioning_in" else 200 * eased_progress
            result["offset_y"] = int(offset) if state == "transitioning_in" else -int(offset)
            result["opacity"] = eased_progress if state == "transitioning_in" else 1.0 - eased_progress
        
        elif transition_type == TransitionType.ZOOM_IN:
            if state == "transitioning_in":
                result["scale"] = 0.3 + 0.7 * eased_progress
                result["opacity"] = eased_progress
            else:
                result["scale"] = 1.0 - 0.7 * eased_progress
                result["opacity"] = 1.0 - eased_progress
        
        elif transition_type == TransitionType.ZOOM_OUT:
            if state == "transitioning_in":
                result["scale"] = 1.3 - 0.3 * eased_progress
                result["opacity"] = eased_progress
            else:
                result["scale"] = 1.0 + 0.3 * eased_progress
                result["opacity"] = 1.0 - eased_progress
        
        elif transition_type == TransitionType.ROTATE:
            if state == "transitioning_in":
                result["rotation"] = 360.0 * (1.0 - eased_progress)
                result["opacity"] = eased_progress
            else:
                result["rotation"] = 360.0 * eased_progress
                result["opacity"] = 1.0 - eased_progress
        
        elif transition_type == TransitionType.BLUR:
            if state == "transitioning_in":
                result["blur"] = 10.0 * (1.0 - eased_progress)
                result["opacity"] = eased_progress
            else:
                result["blur"] = 10.0 * eased_progress
                result["opacity"] = 1.0 - eased_progress
        
        return result
    
    def clear_transition(self, element_id: str):
        """Clear transition for element"""
        if element_id in self.transitions:
            del self.transitions[element_id]
    
    def clear_all(self):
        """Clear all transitions"""
        self.transitions.clear()

