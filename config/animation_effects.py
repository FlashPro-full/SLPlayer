from enum import IntEnum

class AnimationEffect(IntEnum):
    DIRECT_DISPLAY = 0
    SHIFT_LEFT = 1
    SHIFT_RIGHT = 2
    SHIFT_UP = 3
    SHIFT_DOWN = 4
    OVERLAY_LEFT = 5
    OVERLAY_RIGHT = 6
    OVERLAY_UP = 7
    OVERLAY_DOWN = 8
    OVERLAY_TOP_LEFT = 9
    OVERLAY_BOTTOM_LEFT = 10
    OVERLAY_TOP_RIGHT = 11
    OVERLAY_BOTTOM_RIGHT = 12
    HORIZONTAL_OPENING = 13
    VERTICAL_OPENING = 14
    HORIZONTAL_CLOSING = 15
    VERTICAL_CLOSING = 16
    FADE_IN_OUT = 17
    VERTICAL_BLINDS = 18
    HORIZONTAL_BLINDS = 19
    DONT_CLEAR_SCREEN = 20
    RANDOM_SPECIAL = 25
    CONTINUOUS_LEFT = 26
    CONTINUOUS_RIGHT = 27
    CONTINUOUS_UP = 28
    CONTINUOUS_DOWN = 29
    FLASHING = 30

ANIMATION_NAME_TO_SDK_INDEX = {
    "Direct display": 0,
    "Immediate Show": 0,
    "Immediate Clear": 0,
    "Shift left": 1,
    "Move Left": 1,
    "Shift right": 2,
    "Move Right": 2,
    "Shift up": 3,
    "Move Up": 3,
    "Shift down": 4,
    "Move Down": 4,
    "Overlay left": 5,
    "Cover Left": 5,
    "Overlay right": 6,
    "Cover Right": 6,
    "Overlay up": 7,
    "Cover Up": 7,
    "Overlay down": 8,
    "Cover Down": 8,
    "Overlay top left": 9,
    "Top Left Cover": 9,
    "Overlay bottom left": 10,
    "Bottom Left Cover": 10,
    "Overlay top right": 11,
    "Top Right Cover": 11,
    "Overlay bottom right": 12,
    "Bottom Right Cover": 12,
    "Horizontal opening": 13,
    "Open From Middle": 13,
    "Vertical opening": 14,
    "Up Down Open": 14,
    "Horizontal closing": 15,
    "Close From Middle": 15,
    "Vertical closing": 16,
    "Up Down Close": 16,
    "Fade in and out": 17,
    "Gradual Change": 17,
    "Vertical blinds": 18,
    "Vertical Blinds": 18,
    "Horizontal blinds": 19,
    "Horizontal Blinds": 19,
    "Do not clear the screen": 20,
    "Don't Clear Screen": 20,
    "Random special effects": 25,
    "Random": 25,
    "Continuous left movement": 26,
    "Continuous Move Left": 26,
    "Continuous right movement": 27,
    "Continuous Move Right": 27,
    "Continuous up movement": 28,
    "Continuous Move Up": 28,
    "Continuous down movement": 29,
    "Continuous Move Down": 29,
    "Flashing": 30,
    "Twinkle": 30,
}

SDK_INDEX_TO_ANIMATION_NAME = {
    0: "Direct display",
    1: "Shift left",
    2: "Shift right",
    3: "Shift up",
    4: "Shift down",
    5: "Overlay left",
    6: "Overlay right",
    7: "Overlay up",
    8: "Overlay down",
    9: "Overlay top left",
    10: "Overlay bottom left",
    11: "Overlay top right",
    12: "Overlay bottom right",
    13: "Horizontal opening",
    14: "Vertical opening",
    15: "Horizontal closing",
    16: "Vertical closing",
    17: "Fade in and out",
    18: "Vertical blinds",
    19: "Horizontal blinds",
    20: "Do not clear the screen",
    25: "Random special effects",
    26: "Continuous left movement",
    27: "Continuous right movement",
    28: "Continuous up movement",
    29: "Continuous down movement",
    30: "Flashing",
}

def get_animation_index(name: str) -> int:
    return ANIMATION_NAME_TO_SDK_INDEX.get(name, 0)

def get_animation_name(index: int) -> str:
    return SDK_INDEX_TO_ANIMATION_NAME.get(index, "Direct display")

