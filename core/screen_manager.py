import uuid
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime
from core.program_manager import Program
from config.constants import DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT
from utils.logger import get_logger

logger = get_logger(__name__)


class Screen:
    
    def __init__(self, name: str, width: int = DEFAULT_CANVAS_WIDTH, height: int = DEFAULT_CANVAS_HEIGHT):
        self.id = f"screen_{uuid.uuid4().hex[:12]}"
        self.name = name
        self.width = width
        self.height = height
        self.programs: List[Program] = []
        self._programs_by_id: Dict[str, Program] = {}  # O(1) lookup index
        self.created = datetime.now().isoformat()
        self.modified = datetime.now().isoformat()
        self.file_path: Optional[str] = None
    
    def add_program(self, program: Program):
        if program not in self.programs:
            self.programs.append(program)
            self._programs_by_id[program.id] = program  # Maintain index
            self._update_program_screen_properties(program)
            self.modified = datetime.now().isoformat()
    
    def remove_program(self, program: Program):
        if program in self.programs:
            self.programs.remove(program)
            self._programs_by_id.pop(program.id, None)  # Remove from index
            self.modified = datetime.now().isoformat()
    
    def _update_program_screen_properties(self, program: Program):
        if "screen" not in program.properties:
            program.properties["screen"] = {}
        if isinstance(program.properties["screen"], dict):
            program.properties["screen"]["screen_name"] = self.name
            program.properties["screen"]["width"] = self.width
            program.properties["screen"]["height"] = self.height
    
    def get_program_by_id(self, program_id: str) -> Optional[Program]:
        return self._programs_by_id.get(program_id)  # O(1) lookup
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "programs": [p.to_dict() for p in self.programs],
            "created": self.created,
            "modified": self.modified,
            "file_path": self.file_path
        }
    
    def from_dict(self, data: Dict):
        self.id = data.get("id", self.id)
        self.name = data.get("name", "Screen")
        self.width = data.get("width", DEFAULT_CANVAS_WIDTH)
        self.height = data.get("height", DEFAULT_CANVAS_HEIGHT)
        self.created = data.get("created", datetime.now().isoformat())
        self.modified = data.get("modified", datetime.now().isoformat())
        self.file_path = data.get("file_path")
        
        self.programs = []
        self._programs_by_id = {}  # Reset index
        for program_data in data.get("programs", []):
            program = Program()
            program.from_dict(program_data)
            self.add_program(program)


class ScreenManager:
    
    def __init__(self):
        self.screens: List[Screen] = []
        self.current_screen: Optional[Screen] = None
        # O(1) lookup indexes
        self._screens_by_name: Dict[str, Screen] = {}
        self._screens_by_id: Dict[str, Screen] = {}
        self._programs_by_id: Dict[str, Program] = {}
    
    def create_screen(self, name: str, width: int = DEFAULT_CANVAS_WIDTH, 
                     height: int = DEFAULT_CANVAS_HEIGHT) -> Screen:
        if name in self._screens_by_name:
            counter = 1
            while f"{name}_{counter}" in self._screens_by_name:
                counter += 1
            name = f"{name}_{counter}"
        
        screen = Screen(name, width, height)
        self.screens.append(screen)
        self._screens_by_name[screen.name] = screen 
        self._screens_by_id[screen.id] = screen
        self.current_screen = screen
        return screen
    
    def get_screen_by_name(self, name: str) -> Optional[Screen]:
        return self._screens_by_name.get(name)  # O(1) lookup
    
    def get_screen_by_id(self, screen_id: str) -> Optional[Screen]:
        return self._screens_by_id.get(screen_id)  # O(1) lookup
    
    def delete_screen(self, screen: Screen) -> bool:
        try:
            if screen in self.screens:
                self.screens.remove(screen)
                self._screens_by_name.pop(screen.name, None)  # Remove from index
                self._screens_by_id.pop(screen.id, None)  # Remove from index
                # Remove programs from global index
                for program in screen.programs:
                    self._programs_by_id.pop(program.id, None)
                if self.current_screen == screen:
                    self.current_screen = self.screens[0] if self.screens else None
                return True
            return False
        except Exception as e:
            logger.exception(f"Error deleting screen: {e}")
            return False
    
    def add_program_to_screen(self, screen_name: str, program: Program) -> bool:
        screen = self.get_screen_by_name(screen_name)
        if screen:
            screen.add_program(program)
            self._programs_by_id[program.id] = program  # Maintain global index
            return True
        return False
    
    def remove_program_from_screen(self, screen_name: str, program: Program) -> bool:
        screen = self.get_screen_by_name(screen_name)
        if screen:
            screen.remove_program(program)
            self._programs_by_id.pop(program.id, None)  # Remove from global index
            return True
        return False
    
    def get_all_programs(self) -> List[Program]:
        all_programs = []
        for screen in self.screens:
            all_programs.extend(screen.programs)
        return all_programs
    
    def get_program_by_id(self, program_id: str) -> Optional[Program]:
        return self._programs_by_id.get(program_id)  # O(1) lookup
    
    @staticmethod
    def get_screen_name_from_program(program: Program) -> str:
        screen_props_raw = program.properties.get("screen", {})
        screen_props = screen_props_raw if isinstance(screen_props_raw, dict) else {}
        screen_name = screen_props.get("screen_name") if isinstance(screen_props, dict) else None
        
        if not screen_name:
            working_file = screen_props.get("working_file_path", "") if isinstance(screen_props, dict) else ""
            if working_file:
                try:
                    file_path = Path(working_file)
                    screen_name = file_path.stem
                except Exception:
                    screen_name = ScreenManager._generate_default_screen_name(program)
        else:
            if isinstance(screen_props, dict):
                screen_props["screen_name"] = screen_name
            
        if not screen_name:
            screen_name = ScreenManager._generate_default_screen_name(program)
            if "screen" not in program.properties:
                program.properties["screen"] = {}
            if isinstance(program.properties["screen"], dict):
                program.properties["screen"]["screen_name"] = screen_name
            
        return screen_name
    
    @staticmethod
    def _generate_default_screen_name(program: Program) -> str:
        return "Screen4" if hash(program.id) % 2 == 0 else "Screen5"
    
    @staticmethod
    def determine_screen_name(program: Program) -> str:
        if "screen" not in program.properties:
            program.properties["screen"] = {}
        
        screen_props_raw = program.properties["screen"]
        screen_props = screen_props_raw if isinstance(screen_props_raw, dict) else {}
        screen_name = screen_props.get("screen_name") if isinstance(screen_props, dict) else None
        if not screen_name:
            screen_name = ScreenManager._generate_default_screen_name(program)
            if isinstance(program.properties["screen"], dict):
                program.properties["screen"]["screen_name"] = screen_name
            
        return screen_name
    
    @staticmethod
    def generate_unique_program_name(programs: List[Program], screen_name: str) -> str:
        existing_numbers = set()
        for program in programs:
            program_screen_name = ScreenManager.get_screen_name_from_program(program)
            if program_screen_name == screen_name:
                program_name = program.name
                if program_name.startswith("Program"):
                    try:
                        num_str = program_name[7:]
                        if num_str.isdigit():
                            existing_numbers.add(int(num_str))
                    except Exception:
                        pass
        
        counter = 1
        while counter in existing_numbers:
            counter += 1
        
        return f"Program{counter}"
    
    @staticmethod
    def sanitize_screen_name(screen_name: str) -> str:
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        sanitized = screen_name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, "_")
        return sanitized
    
    @staticmethod
    def get_programs_for_screen(programs: List[Program], screen_name: str) -> List[Program]:
        screen_programs = []
        for program in programs:
            program_screen_name = ScreenManager.get_screen_name_from_program(program)
            if program_screen_name == screen_name:
                screen_programs.append(program)
        return screen_programs
    
    @staticmethod
    def get_all_screen_names(programs: List[Program]) -> set:
        screen_names = set()
        for program in programs:
            screen_name = ScreenManager.get_screen_name_from_program(program)
            if screen_name:
                screen_names.add(screen_name)
        return screen_names

