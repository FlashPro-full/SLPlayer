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
            "checked": True
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
    
    def from_dict(self, data: Dict):
        self.id = data.get("id", self.id)
        self.name = data.get("name", "New Program")
        self.width = data.get("width", DEFAULT_CANVAS_WIDTH)
        self.height = data.get("height", DEFAULT_CANVAS_HEIGHT)
        self.created = data.get("created", datetime.now().isoformat())
        self.modified = data.get("modified", datetime.now().isoformat())
        self.elements = data.get("elements", [])
        self.properties = data.get("properties", self.properties)
        if "checked" not in self.properties:
            self.properties["checked"] = True
        self.play_mode = data.get("play_mode", self.play_mode)
        self.play_control = data.get("play_control", self.play_control)
        self.duration = data.get("duration", 0.0)


class ProgramManager:
    
    def __init__(self):
        self.programs: List[Program] = []
        self.current_program: Optional[Program] = None
    
    def create_program(self, name: str = None, width: int = DEFAULT_CANVAS_WIDTH,
                      height: int = DEFAULT_CANVAS_HEIGHT) -> Program:
        if not name:
            existing_names = [p.name for p in self.programs]
            n = 1
            while True:
                candidate = f"Program {n}"
                if candidate not in existing_names:
                    name = candidate
                    break
                n += 1
        program = Program(name, width, height)
        self.programs.append(program)
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
                if self.current_program == program:
                    self.current_program = self.programs[0] if self.programs else None
                return True
            return False
        except Exception as e:
            logger.exception(f"Error deleting program: {e}")
            return False
    
    def get_program_by_id(self, program_id: str) -> Optional[Program]:
        for program in self.programs:
            if program.id == program_id:
                return program
        return None

