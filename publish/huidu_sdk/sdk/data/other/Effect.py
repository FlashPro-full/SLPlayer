from enum import IntEnum
import json

class Effect:
    class EffectType(IntEnum):
        IMMEDIATE_SHOW = 0         # Direct display
        LEFT_PARALLEL_MOVE = 1     # Left parallel move
        RIGHT_PARALLEL_MOVE = 2    # Right parallel move
        UP_PARALLEL_MOVE = 3       # Up parallel move
        DOWN_PARALLEL_MOVE = 4     # Down parallel move
        LEFT_COVER = 5             # Left cover
        RIGHT_COVER = 6            # Right cover
        UP_COVER = 7               # Up cover
        DOWN_COVER = 8             # Down cover
        LEFT_TOP_COVER = 9         # Top-left cover
        LEFT_BOTTOM_COVER = 10     # Bottom-left cover
        RIGHT_TOP_COVER = 11       # Top-right cover
        RIGHT_BOTTOM_COVER = 12    # Bottom-right cover
        HORIZONTAL_DIVIDE = 13     # Horizontal split
        VERTICAL_DIVIDE = 14       # Vertical split
        HORIZONTAL_CLOSE = 15      # Horizontal close
        VERTICAL_CLOSE = 16        # Vertical close
        FADE = 17                  # Fade in/out
        HORIZONTAL_SHUTTER = 18    # Horizontal blinds
        VERTICAL_SHUTTER = 19      # Vertical blinds
        NOT_CLEAR_AREA = 20        # Don't clear area
        LEFT_SERIES_MOVE = 21      # Continuous left move
        RIGHT_SERIES_MOVE = 22     # Continuous right move
        UP_SERIES_MOVE = 23        # Continuous up move
        DOWN_SERIES_MOVE = 24      # Continuous down move
        RANDOM = 25                # Random effect
        HT_LEFT_SERIES_MOVE = 26   # Head-to-tail continuous left
        HT_RIGHT_SERIES_MOVE = 27  # Head-to-tail continuous right
        HT_UP_SERIES_MOVE = 28     # Head-to-tail continuous up
        HT_DOWN_SERIES_MOVE = 29   # Head-to-tail continuous down
        FLICKEREFFECT = 30         # Flicker effect

        @classmethod
        def from_int(cls, value: int):
            for effect_type in cls:
                if effect_type.value == value:
                    return effect_type
            return cls.IMMEDIATE_SHOW  # Default for unknown values

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], Effect):
            # Copy constructor
            other = args[0]
            self._type = other._type
            self.speed = other.speed
            self.hold = other.hold
        else:
            # Handle different argument counts
            self._type = args[0] if len(args) >= 1 else self.EffectType.IMMEDIATE_SHOW
            self.speed = args[1] if len(args) >= 2 else 5
            self.hold = args[2] if len(args) >= 3 else 5000

    @property
    def type(self) -> EffectType:
        return self._type

    @type.setter
    def type(self, value: EffectType):
        self._type = value

    @property
    def type_value(self) -> int:
        return self._type.value

    @type_value.setter
    def type_value(self, value: int):
        self._type = self.EffectType.from_int(value)

    def get_speed(self) -> int:
        return self.speed

    def set_speed(self, speed: int):
        self.speed = speed

    def get_hold(self) -> int:
        return self.hold

    def set_hold(self, hold: int):
        self.hold = hold

    def to_dict(self) -> dict:
        return {
            "type": self.type_value,
            "speed": self.speed,
            "hold": self.hold
        }

    @classmethod
    def from_dict(cls, data: dict):
        effect = cls()
        if "type" in data:
            effect.type_value = data["type"]
        if "speed" in data:
            effect.speed = data["speed"]
        if "hold" in data:
            effect.hold = data["hold"]
        return effect

    def __repr__(self):
        return f"Effect(type={self._type.name}, speed={self.speed}, hold={self.hold})"