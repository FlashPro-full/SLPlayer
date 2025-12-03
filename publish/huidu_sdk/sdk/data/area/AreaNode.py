from typing import List, Optional, Dict, Any, Type
from sdk.data.area.ContentNode import ContentNode
from sdk.data.other.Border import Border
from sdk.data.area import (
    TextNode, DynamicNode, ImageNode, VideoNode, DigitalClockNode, DialClockNode
)


class AreaNode(ContentNode):
    CONTENT_TYPE_MAP: Dict[str, Type[ContentNode]] = {
        "text": TextNode,
        "dynamic": DynamicNode,
        "image": ImageNode,
        "video": VideoNode,
        "digitalClock": DigitalClockNode,
        "dialClock": DialClockNode
    }

    def __init__(self, *args):
        super().__init__()
        self.x: int = 0
        self.y: int = 0
        self.width: int = 0
        self.height: int = 0
        self.item: List[ContentNode] = []
        self.border: Optional[Border] = None

        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, ContentNode):
                # Single content node constructor
                self.item = [arg]
            elif isinstance(arg, list) and all(isinstance(i, ContentNode) for i in arg):
                # List of content nodes
                self.item = arg
            elif isinstance(arg, AreaNode):
                # Copy constructor
                self._copy_from(arg)
            elif isinstance(arg, dict):
                # JSON dictionary constructor
                self._from_dict(arg)

    def _copy_from(self, other: 'AreaNode'):
        super()._copy_from(other)
        self.x = other.x
        self.y = other.y
        self.width = other.width
        self.height = other.height
        self.item = other.item.copy()  # Shallow copy
        self.border = Border(other.border) if other.border else None

    def _from_dict(self, data: Dict[str, Any]):
        if 'uuid' in data:
            self.id = data['uuid']
        if 'name' in data:
            self.name = data['name']
        if 'type' in data:
            self.type = data['type']
        if 'bindType' in data:
            self.bindType = data['bindType']

        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        self.width = data.get('width', 0)
        self.height = data.get('height', 0)

        if 'border' in data:
            self.border = Border(**data['border']) if data['border'] else None

        self.item = []
        for item_data in data.get('item', []):
            content_type = item_data.get('type')
            if content_type in self.CONTENT_TYPE_MAP:
                node_class = self.CONTENT_TYPE_MAP[content_type]
                self.item.append(node_class(item_data))

    def get_x(self) -> int:
        return self.x

    def set_x(self, x: int):
        self.x = x

    def get_y(self) -> int:
        return self.y

    def set_y(self, y: int):
        self.y = y

    def get_width(self) -> int:
        return self.width

    def set_width(self, width: int):
        self.width = width

    def get_height(self) -> int:
        return self.height

    def set_height(self, height: int):
        self.height = height

    def get_item(self) -> List[ContentNode]:
        return self.item

    def set_item(self, items: List[ContentNode]):
        self.item = items

    def get_border(self) -> Optional[Border]:
        return self.border

    def set_border(self, border: Border):
        self.border = border

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "item": [item.to_dict() for item in self.item],
            "border": self.border.to_dict() if self.border else None
        })
        return data

    def __repr__(self) -> str:
        return (f"AreaNode(uuid={self.id}, name='{self.name}', "
                f"x={self.x}, y={self.y}, width={self.width}, height={self.height}, "
                f"items={len(self.item)}, border={self.border is not None})")