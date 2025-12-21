from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScreenPropertiesConfig:
    screen_name: str = ""
    width: int = 640
    height: int = 480
    rotation: int = 0
    stretch: int = 0
    zoom_modulus: int = 0
    controller_type: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v or k in ["width", "height", "rotation", "stretch", "zoom_modulus", "controller_type"]}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScreenPropertiesConfig':
        return cls(**{k: data.get(k, getattr(cls(), k)) for k in cls.__dataclass_fields__.keys()})


@dataclass
class SOOFileConfig:
    version: str = "1.0"
    file_format: str = "soo"
    created: str = ""
    modified: str = ""
    screen_properties: ScreenPropertiesConfig = field(default_factory=ScreenPropertiesConfig)
    programs: List[Dict] = field(default_factory=list)
    schedule: Optional[Dict] = None
    
    def __post_init__(self):
        if not self.created:
            self.created = datetime.now().isoformat()
        if not self.modified:
            self.modified = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "version": self.version,
            "file_format": self.file_format,
            "created": self.created,
            "modified": self.modified,
            "screen_properties": self.screen_properties.to_dict(),
            "programs": self.programs
        }
        if self.schedule:
            result["schedule"] = self.schedule
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SOOFileConfig':
        screen_props = ScreenPropertiesConfig.from_dict(data.get("screen_properties", {}))
        
        return cls(
            version=data.get("version", "1.0"),
            file_format=data.get("file_format", "soo"),
            created=data.get("created", datetime.now().isoformat()),
            modified=data.get("modified", datetime.now().isoformat()),
            screen_properties=screen_props,
            programs=data.get("programs", []),
            schedule=data.get("schedule")
        )
