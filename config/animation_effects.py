"""
Animation effects configuration and mapping
Maps animation names to numeric indices used in XML export
"""
from enum import IntEnum


class AnimationEffect(IntEnum):
    RANDOM = -1
    IMMEDIATE_SHOW = 0
    IMMEDIATE_CLEAR = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    MOVE_UP = 3
    MOVE_DOWN = 4
    COVER_LEFT = 5
    COVER_RIGHT = 6
    COVER_UP = 7
    COVER_DOWN = 8
    TOP_LEFT_COVER = 9
    TOP_RIGHT_COVER = 10
    BOTTOM_LEFT_COVER = 11
    BOTTOM_RIGHT_COVER = 12
    OPEN_FROM_MIDDLE = 13
    UP_DOWN_OPEN = 14
    CLOSE_FROM_MIDDLE = 15
    UP_DOWN_CLOSE = 16
    GRADUAL_CHANGE = 17
    VERTICAL_BLINDS = 18
    HORIZONTAL_BLINDS = 19
    TWINKLE = 20
    CONTINUOUS_MOVE_LEFT = 21
    CONTINUOUS_MOVE_RIGHT = 22
    DONT_CLEAR_SCREEN = 23


ANIMATION_NAME_TO_INDEX = {
    "Random": AnimationEffect.RANDOM,
    "Immediate Show": AnimationEffect.IMMEDIATE_SHOW,
    "Immediate Clear": AnimationEffect.IMMEDIATE_CLEAR,
    "Move Left": AnimationEffect.MOVE_LEFT,
    "Move Right": AnimationEffect.MOVE_RIGHT,
    "Move Up": AnimationEffect.MOVE_UP,
    "Move Down": AnimationEffect.MOVE_DOWN,
    "Cover Left": AnimationEffect.COVER_LEFT,
    "Cover Right": AnimationEffect.COVER_RIGHT,
    "Cover Up": AnimationEffect.COVER_UP,
    "Cover Down": AnimationEffect.COVER_DOWN,
    "Top Left Cover": AnimationEffect.TOP_LEFT_COVER,
    "Top Right Cover": AnimationEffect.TOP_RIGHT_COVER,
    "Bottom Left Cover": AnimationEffect.BOTTOM_LEFT_COVER,
    "Bottom Right Cover": AnimationEffect.BOTTOM_RIGHT_COVER,
    "Open From Middle": AnimationEffect.OPEN_FROM_MIDDLE,
    "Up Down Open": AnimationEffect.UP_DOWN_OPEN,
    "Close From Middle": AnimationEffect.CLOSE_FROM_MIDDLE,
    "Up Down Close": AnimationEffect.UP_DOWN_CLOSE,
    "Gradual Change": AnimationEffect.GRADUAL_CHANGE,
    "Vertical Blinds": AnimationEffect.VERTICAL_BLINDS,
    "Horizontal Blinds": AnimationEffect.HORIZONTAL_BLINDS,
    "Twinkle": AnimationEffect.TWINKLE,
    "Continuous Move Left": AnimationEffect.CONTINUOUS_MOVE_LEFT,
    "Continuous Move Right": AnimationEffect.CONTINUOUS_MOVE_RIGHT,
    "Don't Clear Screen": AnimationEffect.DONT_CLEAR_SCREEN,
}

# Reverse mapping from index to name
ANIMATION_INDEX_TO_NAME = {v.value: k for k, v in ANIMATION_NAME_TO_INDEX.items()}


def get_animation_index(name: str) -> int:
    """Get animation index from name"""
    return ANIMATION_NAME_TO_INDEX.get(name, AnimationEffect.IMMEDIATE_SHOW).value


def get_animation_name(index: int) -> str:
    """Get animation name from index"""
    return ANIMATION_INDEX_TO_NAME.get(index, "Immediate Show")

