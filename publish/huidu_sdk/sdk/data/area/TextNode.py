from enum import Enum
from typing import Optional
from sdk.data.area.ContentNode import ContentNode  # Import base class
from sdk.data.other.Effect import Effect
from sdk.data.other.Font import Font

class TextNode(ContentNode):
    class Alignment(Enum):
        CENTER = "center"  # Center alignment
        LEFT = "left"  # Left alignment
        RIGHT = "right"  # Right alignment

        def get_value(self) -> str:
            return self.value

    class VAlignment(Enum):
        MIDDLE = "middle"  # Vertical center
        TOP = "top"  # Top alignment
        BOTTOM = "bottom"  # Bottom alignment

        def get_value(self) -> str:
            return self.value

    def __init__(self, *args):
        super().__init__()
        self.set_type("text")  # Set node type to "text"

        self.string: Optional[str] = None
        self.multiLine: bool = True
        self.alignment: Optional[TextNode.Alignment] = None
        self.valignment: Optional[TextNode.VAlignment] = None
        self.effect: Optional[Effect] = None
        self.font: Optional[Font] = None

        # Handle different argument patterns
        if len(args) == 1:
            if isinstance(args[0], str):
                # String constructor
                self.string = args[0]
            elif isinstance(args[0], TextNode):
                # Copy constructor
                self._copy_from(args[0])

    def _copy_from(self, other: 'TextNode'):
        super()._copy_from(other)  # Copy base class properties
        self.string = other.string
        self.multiLine = other.multiLine
        self.alignment = other.alignment
        self.valignment = other.valignment
        self.effect = other.effect
        self.font = other.font

    # Property accessors
    def get_string(self) -> Optional[str]:
        return self.string

    def set_string(self, text: str):
        self.string = text

    def get_multi_line(self) -> bool:
        return self.multiLine

    def set_multi_line(self, multi_line: bool):
        self.multiLine = multi_line

    def get_alignment(self) -> Optional[Alignment]:
        return self.alignment

    def set_alignment(self, alignment: Alignment):
        self.alignment = alignment

    def get_valignment(self) -> Optional[VAlignment]:
        return self.valignment

    def set_valignment(self, valignment: VAlignment):
        self.valignment = valignment

    def get_effect(self) -> Optional[Effect]:
        return self.effect

    def set_effect(self, effect: Effect):
        self.effect = effect

    def get_font(self) -> Optional[Font]:
        return self.font

    def set_font(self, font: Font):
        self.font = font

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "string": self.string,
            "multiLine": self.multiLine,
            "alignment": self.alignment.get_value() if self.alignment else None,
            "valignment": self.valignment.get_value() if self.valignment else None,
            "effect": self.effect.to_dict() if self.effect else None,
            "font": self.font.to_dict() if self.font else None
        })
        return data

    def __repr__(self) -> str:
        return (f"TextNode(uuid={self.id}, name='{self.name}', "
                f"string='{self.string}', multiLine={self.multiLine}, "
                f"alignment={self.alignment.name if self.alignment else None}, "
                f"valignment={self.valignment.name if self.valignment else None})")