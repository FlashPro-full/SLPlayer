"""
Animation engine using PyQt5's QPropertyAnimation framework
Supports all HDPlayer animation effects with hardware acceleration
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import math
import random

from PyQt5.QtCore import QObject, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtCore import pyqtProperty  # type: ignore
from PyQt5.QtGui import QColor

from config.animation_effects import (
    AnimationEffect, ANIMATION_NAME_TO_INDEX, get_animation_index
)


class AnimationState(QObject):
    """Animation state object with properties that can be animated"""
    
    # Signals for value changes
    opacity_changed = pyqtSignal(float)
    offset_x_changed = pyqtSignal(int)
    offset_y_changed = pyqtSignal(int)
    scale_x_changed = pyqtSignal(float)
    scale_y_changed = pyqtSignal(float)
    rotation_changed = pyqtSignal(float)
    progress_changed = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        self._offset_x = 0
        self._offset_y = 0
        self._scale_x = 1.0
        self._scale_y = 1.0
        self._rotation = 0.0
        self._progress = 0.0
        self._clip_rect: Optional[Tuple[int, int, int, int]] = None
    
    # Opacity property
    def get_opacity(self) -> float:
        return self._opacity
    
    def set_opacity(self, value: float):
        if self._opacity != value:
            self._opacity = value
            self.opacity_changed.emit(value)
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    # Offset X property
    def get_offset_x(self) -> int:
        return self._offset_x
    
    def set_offset_x(self, value: int):
        if self._offset_x != value:
            self._offset_x = value
            self.offset_x_changed.emit(value)
    
    offset_x = pyqtProperty(int, get_offset_x, set_offset_x)
    
    # Offset Y property
    def get_offset_y(self) -> int:
        return self._offset_y
    
    def set_offset_y(self, value: int):
        if self._offset_y != value:
            self._offset_y = value
            self.offset_y_changed.emit(value)
    
    offset_y = pyqtProperty(int, get_offset_y, set_offset_y)
    
    # Scale X property
    def get_scale_x(self) -> float:
        return self._scale_x
    
    def set_scale_x(self, value: float):
        if abs(self._scale_x - value) > 0.001:
            self._scale_x = value
            self.scale_x_changed.emit(value)
    
    scale_x = pyqtProperty(float, get_scale_x, set_scale_x)
    
    # Scale Y property
    def get_scale_y(self) -> float:
        return self._scale_y
    
    def set_scale_y(self, value: float):
        if abs(self._scale_y - value) > 0.001:
            self._scale_y = value
            self.scale_y_changed.emit(value)
    
    scale_y = pyqtProperty(float, get_scale_y, set_scale_y)
    
    # Rotation property
    def get_rotation(self) -> float:
        return self._rotation
    
    def set_rotation(self, value: float):
        if abs(self._rotation - value) > 0.1:
            self._rotation = value
            self.rotation_changed.emit(value)
    
    rotation = pyqtProperty(float, get_rotation, set_rotation)
    
    # Progress property (0.0 to 1.0)
    def get_progress(self) -> float:
        return self._progress
    
    def set_progress(self, value: float):
        if abs(self._progress - value) > 0.001:
            self._progress = value
            self.progress_changed.emit(value)
    
    progress = pyqtProperty(float, get_progress, set_progress)
    
    def get_clip_rect(self) -> Optional[Tuple[int, int, int, int]]:
        return self._clip_rect
    
    def set_clip_rect(self, value: Optional[Tuple[int, int, int, int]]):
        self._clip_rect = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format compatible with existing code"""
        result: Dict[str, Any] = {
            "opacity": self._opacity,
            "offset_x": self._offset_x,
            "offset_y": self._offset_y,
            "scale_x": self._scale_x,
            "scale_y": self._scale_y,
            "rotation": self._rotation,
            "clip_rect": self._clip_rect
        }
        return result


class AnimationEngine:
    """Animation engine using PyQt5 QPropertyAnimation framework"""
    
    def __init__(self):
        self.animations: Dict[str, Dict[str, Any]] = {}
        self.animation_states: Dict[str, AnimationState] = {}
        self.animation_groups: Dict[str, QPropertyAnimation] = {}
        self.element_dimensions: Dict[str, Tuple[int, int]] = {}
        self.start_times: Dict[str, float] = {}
    
    def add_entrance_animation(self, element_id: str, animation_name: str, 
                             duration: float = 1.0, speed: int = 4,
                             width: int = 100, height: int = 100):
        """Add entrance animation to an element"""
        # Handle Random - pick a random animation
        if animation_name == "Random":
            animation_name = random.choice([
                "Fade", "Fly In", "Wipe", "Zoom", "Box", "Circle", 
                "Dissolve", "Bounce", "Grow & Turn", "Spiral"
            ])
        
        animation_index = get_animation_index(animation_name)
        
        # Create animation state
        state = AnimationState()
        self.animation_states[element_id] = state
        self.element_dimensions[element_id] = (width, height)
        
        # Store animation info
        self.animations[element_id] = {
            "type": "entrance",
            "animation_name": animation_name,
            "animation_index": animation_index,
            "duration": duration,
            "speed": speed,
            "is_exit": False
        }
        
        # Start animation immediately
        self.start_times[element_id] = datetime.now().timestamp()
        self._setup_animation(element_id, animation_index, duration, False)
    
    def add_exit_animation(self, element_id: str, animation_name: str,
                          duration: float = 1.0, speed: int = 4,
                          width: int = 100, height: int = 100):
        """Add exit animation to an element"""
        # Handle Random
        if animation_name == "Random":
            animation_name = random.choice([
                "Fade", "Fly Out", "Wipe", "Zoom", "Box", "Circle",
                "Dissolve", "Bounce", "Grow & Turn", "Spiral"
            ])
        
        animation_index = get_animation_index(animation_name)
        
        # Create animation state
        state = AnimationState()
        self.animation_states[element_id] = state
        self.element_dimensions[element_id] = (width, height)
        
        # Store animation info
        self.animations[element_id] = {
            "type": "exit",
            "animation_name": animation_name,
            "animation_index": animation_index,
            "duration": duration,
            "speed": speed,
            "is_exit": True
        }
        
        # Don't start exit animation yet - it will be triggered when element is cleared
        self.start_times[element_id] = 0
    
    def start_exit_animation(self, element_id: str):
        """Start exit animation for an element"""
        if element_id not in self.animations:
            return
        
        anim = self.animations[element_id]
        if not anim.get("is_exit", False):
            return
        
        self.start_times[element_id] = datetime.now().timestamp()
        self._setup_animation(
            element_id, 
            anim["animation_index"], 
            anim["duration"], 
            True
        )
    
    def _setup_animation(self, element_id: str, effect_index: int, 
                        duration: float, is_exit: bool):
        """Setup QPropertyAnimation for the effect"""
        if element_id not in self.animation_states:
            return
        
        state = self.animation_states[element_id]
        width, height = self.element_dimensions.get(element_id, (100, 100))
        
        # Stop any existing animation
        if element_id in self.animation_groups:
            self.animation_groups[element_id].stop()
        
        # Create progress animation (0.0 to 1.0)
        progress_anim = QPropertyAnimation(state, b"progress")
        progress_anim.setDuration(int(duration * 1000))  # Convert to milliseconds
        progress_anim.setStartValue(0.0)
        progress_anim.setEndValue(1.0)
        progress_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Connect progress to effect calculation
        def update_effect(progress_value: float):
            self._apply_effect_to_state(state, effect_index, progress_value, width, height, is_exit)
        
        state.progress_changed.connect(update_effect)
        
        # Start animation
        progress_anim.start()
        self.animation_groups[element_id] = progress_anim
    
    def _apply_effect_to_state(self, state: AnimationState, effect_index: int,
                              progress: float, width: int, height: int, is_exit: bool):
        """Apply animation effect to state based on progress"""
        # Reverse direction for exit animations
        direction = -1 if is_exit else 1
        
        # Apply easing
        eased_progress = self._ease_in_out(progress)
        
        # Reset state
        state.set_opacity(1.0)
        state.set_offset_x(0)
        state.set_offset_y(0)
        state.set_scale_x(1.0)
        state.set_scale_y(1.0)
        state.set_rotation(0.0)
        state.set_clip_rect(None)
        
        # Apply effect based on index
        if effect_index == AnimationEffect.NONE:
            state.set_opacity(1.0)
        
        elif effect_index == AnimationEffect.FADE:
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.FLY_IN:
            # Fly in from direction
            offset = int((1.0 - eased_progress) * width * direction)
            state.set_offset_x(offset)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.WIPE:
            # Wipe from left
            wipe_width = int(eased_progress * width)
            state.set_clip_rect((0, 0, wipe_width, height))
            state.set_opacity(1.0)
        
        elif effect_index == AnimationEffect.FLOAT_IN:
            # Float in from bottom
            offset_y = int((1.0 - eased_progress) * height * direction)
            state.set_offset_y(offset_y)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.RISE_UP:
            # Rise up from bottom
            offset_y = int((1.0 - eased_progress) * height * direction)
            state.set_offset_y(offset_y)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.SPLIT:
            # Split from center
            center_x = width // 2
            left_width = int(eased_progress * center_x)
            right_width = int(eased_progress * (width - center_x))
            state.set_clip_rect((center_x - left_width, 0, left_width + right_width, height))
            state.set_opacity(1.0)
        
        elif effect_index == AnimationEffect.STRIPS:
            # Strips reveal
            strip_count = 8
            strip_height = height // strip_count
            revealed_height = int(eased_progress * height)
            state.set_clip_rect((0, 0, width, revealed_height))
            state.set_opacity(1.0)
        
        elif effect_index == AnimationEffect.CIRCLE:
            # Circular reveal from center
            center_x, center_y = width // 2, height // 2
            max_radius = math.sqrt(center_x**2 + center_y**2)
            radius = int(eased_progress * max_radius)
            # Use clip rect for circular reveal
            x = max(0, center_x - radius)
            y = max(0, center_y - radius)
            clip_width = min(width, radius * 2)
            clip_height = min(height, radius * 2)
            state.set_clip_rect((x, y, clip_width, clip_height))
            state.set_opacity(1.0)
        
        elif effect_index == AnimationEffect.BOX:
            # Box reveal from center
            center_x, center_y = width // 2, height // 2
            box_width = int(eased_progress * width)
            box_height = int(eased_progress * height)
            x = center_x - box_width // 2
            y = center_y - box_height // 2
            state.set_clip_rect((x, y, box_width, box_height))
            state.set_opacity(1.0)
        
        elif effect_index == AnimationEffect.PLUS:
            # Plus reveal
            center_x, center_y = width // 2, height // 2
            cross_width = int(eased_progress * width)
            cross_height = int(eased_progress * height)
            # Simplified plus shape
            state.set_clip_rect((center_x - cross_width//2, 0, cross_width, height))
            state.set_opacity(1.0)
        
        elif effect_index == AnimationEffect.CHECKERBOARD:
            # Checkerboard reveal
            revealed = int(eased_progress * width)
            state.set_clip_rect((0, 0, revealed, height))
            state.set_opacity(1.0)
        
        elif effect_index == AnimationEffect.BLINDS:
            # Blinds reveal
            blind_count = 8
            blind_height = height // blind_count
            revealed = int(eased_progress * blind_height)
            state.set_clip_rect((0, 0, width, revealed * blind_count))
            state.set_opacity(1.0)
        
        elif effect_index == AnimationEffect.DIAMOND:
            # Diamond reveal
            center_x, center_y = width // 2, height // 2
            diamond_size = int(eased_progress * max(width, height))
            x = center_x - diamond_size // 2
            y = center_y - diamond_size // 2
            state.set_clip_rect((x, y, diamond_size, diamond_size))
            state.set_opacity(1.0)
        
        elif effect_index == AnimationEffect.DISSOLVE:
            # Dissolve (random pixels)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.PEEK:
            # Peek (slide from side)
            offset = int((1.0 - eased_progress) * width * direction)
            state.set_offset_x(offset)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.ZOOM:
            # Zoom in/out
            scale = eased_progress if not is_exit else (2.0 - eased_progress)
            state.set_scale_x(scale)
            state.set_scale_y(scale)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.WHEEL:
            # Wheel (rotating reveal)
            angle = eased_progress * 360.0 * direction
            state.set_rotation(angle)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.SPIRAL:
            # Spiral reveal
            angle = eased_progress * 720.0 * direction
            spiral_radius = eased_progress * max(width, height) * 0.5
            state.set_offset_x(int(math.cos(math.radians(angle)) * spiral_radius))
            state.set_offset_y(int(math.sin(math.radians(angle)) * spiral_radius))
            state.set_rotation(angle)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.SWIVEL:
            # Swivel (3D rotation)
            state.set_rotation(eased_progress * 180.0 * direction)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.UNFOLD:
            # Unfold
            scale_x = eased_progress
            state.set_scale_x(scale_x)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.PINWHEEL:
            # Pinwheel
            angle = eased_progress * 360.0 * direction
            state.set_rotation(angle)
            scale = 0.5 + eased_progress * 0.5
            state.set_scale_x(scale)
            state.set_scale_y(scale)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.FADE_AND_ZOOM:
            # Fade & Zoom
            scale = eased_progress
            state.set_scale_x(scale)
            state.set_scale_y(scale)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.ZOOM_AND_FADE:
            # Zoom & Fade
            scale = 0.5 + eased_progress * 0.5
            state.set_scale_x(scale)
            state.set_scale_y(scale)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.ZOOM_AND_TURN:
            # Zoom & Turn
            scale = eased_progress
            angle = eased_progress * 360.0 * direction
            state.set_scale_x(scale)
            state.set_scale_y(scale)
            state.set_rotation(angle)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.GROW_AND_TURN:
            # Grow & Turn
            scale = eased_progress
            angle = eased_progress * 180.0 * direction
            state.set_scale_x(scale)
            state.set_scale_y(scale)
            state.set_rotation(angle)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.BOUNCE:
            # Bounce
            bounce_progress = self._bounce_easing(eased_progress)
            offset_y = int((1.0 - bounce_progress) * height * direction)
            state.set_offset_y(offset_y)
            state.set_opacity(eased_progress)
        
        elif effect_index == AnimationEffect.FLASH:
            # Flash
            flash_opacity = 1.0 if (int(eased_progress * 10) % 2 == 0) else 0.3
            state.set_opacity(flash_opacity)
        
        elif effect_index == AnimationEffect.SWING:
            # Swing
            swing_angle = math.sin(eased_progress * math.pi) * 30.0 * direction
            state.set_rotation(swing_angle)
            state.set_opacity(eased_progress)
        
        else:
            # Default: fade
            state.set_opacity(eased_progress)
    
    def _ease_in_out(self, t: float) -> float:
        """Easing function for smooth animation"""
        return t * t * (3.0 - 2.0 * t)
    
    def _bounce_easing(self, t: float) -> float:
        """Bounce easing function"""
        if t < 0.5:
            return 2.0 * t * t
        else:
            return 1.0 - 2.0 * (1.0 - t) * (1.0 - t)
    
    def update_animation(self, element_id: str, current_time: float) -> Dict[str, Any]:
        """
        Update animation and return transformation properties.
        Returns dict with: opacity, offset_x, offset_y, scale_x, scale_y, rotation, clip_rect
        """
        if element_id not in self.animation_states:
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, 
                   "scale_x": 1.0, "scale_y": 1.0, "rotation": 0.0, "clip_rect": None}
        
        # Get current state
        state = self.animation_states[element_id]
        return state.to_dict()
    
    def remove_animation(self, element_id: str):
        """Remove animation for an element"""
        if element_id in self.animation_groups:
            self.animation_groups[element_id].stop()
            del self.animation_groups[element_id]
        
        if element_id in self.animation_states:
            self.animation_states[element_id].deleteLater()
            del self.animation_states[element_id]
        
        if element_id in self.animations:
            del self.animations[element_id]
        
        if element_id in self.start_times:
            del self.start_times[element_id]
        
        if element_id in self.element_dimensions:
            del self.element_dimensions[element_id]
