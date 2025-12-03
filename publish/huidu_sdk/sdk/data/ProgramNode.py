import json
from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass, field
from sdk.data.area.AreaNode import AreaNode
from sdk.data.area.ContentNode import ContentNode
from sdk.data.other.Border import Border
from sdk.data.other.PlayControl import PlayControl


@dataclass
class ProgramNode(ContentNode):
    area: List[AreaNode] = field(default_factory=list)
    border: Optional[Border] = None
    play_control: Optional[PlayControl] = None

    def __init__(self, *args):
        super().__init__()
        self.area = []
        self.border = None
        self.play_control = None

        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, AreaNode):
                # Single AreaNode
                self.area = [arg]
            elif isinstance(arg, list) and all(isinstance(x, AreaNode) for x in arg):
                # List of AreaNodes
                self.area = arg
            elif isinstance(arg, ContentNode):
                # Single ContentNode
                self.area = [AreaNode(arg)]
            elif isinstance(arg, list) and all(isinstance(x, ContentNode) for x in arg):
                # List of ContentNodes
                self.area = [AreaNode(arg)]
            elif isinstance(arg, str):
                # JSON string
                self._from_dict(json.loads(arg))
            elif isinstance(arg, dict):
                # Dictionary
                self._from_dict(arg)
            elif isinstance(arg, ProgramNode):
                # Copy constructor
                self._copy_from(arg)

    def _copy_from(self, other: 'ProgramNode'):
        super()._copy_from(other)
        self.area = [AreaNode(a) for a in other.area]
        self.border = Border(other.border) if other.border else None
        self.play_control = PlayControl(other.play_control) if other.play_control else None

    def _from_dict(self, data: Dict[str, Any]):
        # Set base ContentNode properties
        if 'uuid' in data:
            self.id = data['uuid']
        if 'name' in data:
            self.name = data['name']
        if 'type' in data:
            self.type = data['type']
        if 'bindType' in data:
            self.bindType = data['bindType']

        if 'area' in data:
            self.area = [AreaNode(a) for a in data['area']]
        if 'border' in data and data['border']:
            self.border = Border(**data['border'])
        if 'playControl' in data and data['playControl']:
            self.play_control = PlayControl.from_dict(data['playControl'])

    def get_area(self) -> List[AreaNode]:
        return self.area

    def set_area(self, areas: Union[AreaNode, List[AreaNode]]):
        if isinstance(areas, AreaNode):
            self.area = [areas]
        else:
            self.area = list(areas)

    def get_border(self) -> Optional[Border]:
        return self.border

    def set_border(self, border: Border):
        self.border = border

    def get_play_control(self) -> Optional[PlayControl]:
        return self.play_control

    def set_play_control(self, play_control: PlayControl):
        self.play_control = play_control

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'area': [a.to_dict() for a in self.area],
            'border': self.border.to_dict() if self.border else None,
            'playControl': self.play_control.to_dict() if self.play_control else None
        })
        return data

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __repr__(self) -> str:
        return (f"ProgramNode(uuid={self.id}, name='{self.name}', "
                f"areas={len(self.area)}, border={self.border is not None}, "
                f"play_control={self.play_control is not None})")