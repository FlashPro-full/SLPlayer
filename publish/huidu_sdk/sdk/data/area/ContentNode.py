import json
from typing import List, Optional
from sdk.data.other.FileInfo import FileInfo  # Import FileInfo from its module


class ContentNode:
    def __init__(self, *args):
        self.uuid: Optional[str] = None
        self.name: Optional[str] = None
        self.type: Optional[str] = None
        self.bindType: Optional[str] = None  # Using Java-style field name

        if len(args) == 2:
            # ID and name constructor
            self.uuid = args[0]
            self.name = args[1]
        elif len(args) == 1 and isinstance(args[0], ContentNode):
            # Copy constructor
            self._copy_from(args[0])

    def _copy_from(self, other: 'ContentNode'):
        self.uuid = other.uuid
        self.name = other.name
        self.type = other.type
        self.bindType = other.bindType

    @property
    def id(self) -> Optional[str]:
        return self.uuid

    @id.setter
    def id(self, value: str):
        self.uuid = value

    def get_name(self) -> Optional[str]:
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_type(self) -> Optional[str]:
        return self.type

    def set_type(self, node_type: str):
        self.type = node_type

    def get_bind_type(self) -> Optional[str]:
        return self.bindType

    def set_bind_type(self, bind_type: str):
        self.bindType = bind_type

    def get_files_info(self) -> Optional[List[FileInfo]]:
        return None

    def update_files_info(self, files_info: List[FileInfo]):
        pass

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "type": self.type,
            "bindType": self.bindType
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __repr__(self) -> str:
        return (f"ContentNode(uuid={self.uuid}, name='{self.name}', "
                f"type='{self.type}', bindType='{self.bindType}')")