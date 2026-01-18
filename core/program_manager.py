import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config.constants import DEFAULT_CANVAS_HEIGHT, DEFAULT_CANVAS_WIDTH
from utils.logger import get_logger

logger = get_logger(__name__)


class Program:
    
    def __init__(self, name: str = "New Program", width: int = DEFAULT_CANVAS_WIDTH, 
                 height: int = DEFAULT_CANVAS_HEIGHT):
        self.id = f"program_{uuid.uuid4().hex[:12]}"
        self.name = name
        self.width = width
        self.height = height
        self.created = datetime.now().isoformat()
        self.modified = datetime.now().isoformat()
        self.elements: List[Dict] = []
        self.properties = {
            "frame": {"enabled": False, "style": "---"},
            "background_music": {"enabled": False, "file": "", "volume": 0},
            "checked": True,
            "content_upload_enabled": True
        }
        self.play_mode = {
            "mode": "play_times",
            "play_times": 1,
            "fixed_length": "0:00:30"
        }
        self.play_control = {
            "specified_time": {"enabled": False, "time": ""},
            "specify_week": {"enabled": False, "days": []},
            "specify_date": {"enabled": False, "date": ""}
        }
        self.duration = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "created": self.created,
            "modified": self.modified,
            "elements": self.elements,
            "properties": self.properties,
            "play_mode": self.play_mode,
            "play_control": self.play_control,
            "duration": self.duration
        }
    
    def from_dict(self, data: Dict) -> None:
        self.id = data.get("id", self.id)
        self.name = data.get("name", "New Program")
        self.width = data.get("width", DEFAULT_CANVAS_WIDTH)
        self.height = data.get("height", DEFAULT_CANVAS_HEIGHT)
        self.created = data.get("created", datetime.now().isoformat())
        self.modified = data.get("modified", datetime.now().isoformat())
        self.elements = data.get("elements", [])
        from controllers.element_defaults import ensure_element_defaults
        for element in self.elements:
            ensure_element_defaults(element)
            element_props = element.get("properties", {})
            if element.get("type") == "video":
                video_list = element_props.get("video_list", [])
                if video_list:
                    video_list = [v for v in video_list if isinstance(v, dict) and Path(v.get("path", "")).exists()]
                    element_props["video_list"] = video_list
                    active_video_index = element_props.get("active_video_index", 0)
                    if active_video_index >= len(video_list):
                        element_props["active_video_index"] = max(0, len(video_list) - 1) if video_list else 0
            elif element.get("type") == "photo":
                photo_list = element_props.get("photo_list", element_props.get("image_list", []))
                if photo_list:
                    photo_list = [p for p in photo_list if isinstance(p, dict) and Path(p.get("path", "")).exists()]
                    element_props["photo_list"] = photo_list
                    element_props["image_list"] = photo_list
                    active_photo_index = element_props.get("active_photo_index", 0)
                    if active_photo_index >= len(photo_list):
                        element_props["active_photo_index"] = max(0, len(photo_list) - 1) if photo_list else 0
        self.properties = data.get("properties", self.properties)
        if "checked" not in self.properties:
            self.properties["checked"] = True
        if "content_upload_enabled" not in self.properties:
            self.properties["content_upload_enabled"] = True
        self.play_mode = data.get("play_mode", self.play_mode)
        self.play_control = data.get("play_control", self.play_control)
        self.duration = data.get("duration", 0.0)


class ProgramManager:
    
    def __init__(self) -> None:
        self.programs: List[Program] = []
        self.current_program: Optional[Program] = None
        self._programs_by_id: Dict[str, Program] = {}  # O(1) lookup index
    
    def create_program(self, name: Optional[str] = None, width: int = DEFAULT_CANVAS_WIDTH,
                      height: int = DEFAULT_CANVAS_HEIGHT) -> Program:
        if not name:
            existing_names = [p.name for p in self.programs]
            n = 1
            while True:
                candidate = f"Program{n}"
                if candidate not in existing_names:
                    name = candidate
                    break
                n += 1
        program = Program(name, width, height)
        self.programs.append(program)
        self._programs_by_id[program.id] = program
        self.current_program = program
        return program
    
    def load_program(self, file_path: str) -> Optional[Program]:
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            program = Program()
            program.from_dict(data)
            
            existing = self.get_program_by_id(program.id)
            if existing:
                existing.from_dict(data)
                self.current_program = existing
                return existing
            else:
                self.programs.append(program)
                self._programs_by_id[program.id] = program  # Maintain index
                self.current_program = program
                return program
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in program file '{file_path}': {e}")
            return None
        except FileNotFoundError:
            logger.warning(f"Program file not found: {file_path}")
            return None
        except PermissionError as e:
            logger.error(f"Permission denied reading program file '{file_path}': {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error loading program from '{file_path}': {e}")
            return None
    
    def save_program(self, program: Program, file_path: str) -> bool:
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            program.modified = datetime.now().isoformat()
            data = program.to_dict()
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except PermissionError as e:
            logger.error(f"Permission denied saving program to '{file_path}': {e}")
            return False
        except OSError as e:
            logger.error(f"OS error saving program to '{file_path}': {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error saving program to '{file_path}': {e}")
            return False
    
    def delete_program(self, program: Program) -> bool:
        try:
            if program in self.programs:
                self.programs.remove(program)
                self._programs_by_id.pop(program.id, None)  # Remove from index
                if self.current_program == program:
                    self.current_program = self.programs[0] if self.programs else None
                return True
            return False
        except Exception as e:
            logger.exception(f"Error deleting program: {e}")
            return False
    
    def get_program_by_id(self, program_id: str) -> Optional[Program]:
        return self._programs_by_id.get(program_id)  # O(1) lookup

