from enum import Enum


class Border:
    class Speed(Enum):
        Slow = "slow"
        Middle = "middle"
        Fast = "fast"

        def getValue(self):
            return self.value

    class Effect(Enum):
        Rotate = "rotate"
        Blink = "blink"
        Static = "null"

        def getValue(self):
            return self.value

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], Border):
            other = args[0]
            self.type = other.type
            self.speed = other.speed
            self.effect = other.effect
        else:
            self.type = args[0] if len(args) >= 1 else 0
            self.speed = args[1] if len(args) >= 2 else self.Speed.Middle
            self.effect = args[2] if len(args) >= 3 else self.Effect.Static

    def getType(self):
        return self.type

    def setType(self, type_val):
        self.type = type_val

    def getSpeed(self):
        return self.speed

    def setSpeed(self, speed):
        self.speed = speed

    def getEffect(self):
        return self.effect

    def setEffect(self, effect):
        self.effect = effect