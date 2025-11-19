"""
Animation effects configuration and mapping
Maps animation names to numeric indices used in XML export
"""
from enum import IntEnum


class AnimationEffect(IntEnum):
    """Animation effect indices matching HDPlayer format"""
    RANDOM = -1
    NONE = 0
    FADE = 1
    FLY_IN = 2
    FLY_OUT = 2  # Same index, direction handled separately
    WIPE = 3
    SPLIT = 4
    STRIPS = 5
    CIRCLE = 6
    WHEEL = 7
    ZOOM = 8
    BOX = 9
    PLUS = 10
    CHECKERBOARD = 11
    BLINDS = 12
    DIAMOND = 13
    DISSOLVE = 14
    PEEK = 15
    BOUNCE = 16
    FLASH = 17
    GROW_AND_TURN = 18
    SPIRAL = 19
    SWIVEL = 20
    UNFOLD = 21
    FADE_AND_ZOOM = 22
    FLOAT_IN = 23
    FLOAT_OUT = 23  # Same index
    PINWHEEL = 24
    RISE_UP = 25
    SWING = 26
    ZOOM_AND_FADE = 27
    ZOOM_AND_TURN = 28


# Mapping from UI string names to animation indices
ANIMATION_NAME_TO_INDEX = {
    "Random": AnimationEffect.RANDOM,
    "None": AnimationEffect.NONE,
    "Fade": AnimationEffect.FADE,
    "Fly In": AnimationEffect.FLY_IN,
    "Fly Out": AnimationEffect.FLY_OUT,
    "Wipe": AnimationEffect.WIPE,
    "Split": AnimationEffect.SPLIT,
    "Strips": AnimationEffect.STRIPS,
    "Circle": AnimationEffect.CIRCLE,
    "Wheel": AnimationEffect.WHEEL,
    "Zoom": AnimationEffect.ZOOM,
    "Box": AnimationEffect.BOX,
    "Plus": AnimationEffect.PLUS,
    "Checkerboard": AnimationEffect.CHECKERBOARD,
    "Blinds": AnimationEffect.BLINDS,
    "Diamond": AnimationEffect.DIAMOND,
    "Dissolve": AnimationEffect.DISSOLVE,
    "Peek": AnimationEffect.PEEK,
    "Bounce": AnimationEffect.BOUNCE,
    "Flash": AnimationEffect.FLASH,
    "Grow & Turn": AnimationEffect.GROW_AND_TURN,
    "Spiral": AnimationEffect.SPIRAL,
    "Swivel": AnimationEffect.SWIVEL,
    "Unfold": AnimationEffect.UNFOLD,
    "Fade & Zoom": AnimationEffect.FADE_AND_ZOOM,
    "Float In": AnimationEffect.FLOAT_IN,
    "Float Out": AnimationEffect.FLOAT_OUT,
    "Pinwheel": AnimationEffect.PINWHEEL,
    "Rise Up": AnimationEffect.RISE_UP,
    "Swing": AnimationEffect.SWING,
    "Zoom & Fade": AnimationEffect.ZOOM_AND_FADE,
    "Zoom & Turn": AnimationEffect.ZOOM_AND_TURN,
}

# Reverse mapping from index to name
ANIMATION_INDEX_TO_NAME = {v.value: k for k, v in ANIMATION_NAME_TO_INDEX.items()}


def get_animation_index(name: str) -> int:
    """Get animation index from name"""
    return ANIMATION_NAME_TO_INDEX.get(name, AnimationEffect.NONE).value


def get_animation_name(index: int) -> str:
    """Get animation name from index"""
    return ANIMATION_INDEX_TO_NAME.get(index, "None")

