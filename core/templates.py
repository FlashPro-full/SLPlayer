"""
Program templates for common layouts
"""
from typing import Dict, List
from core.program_manager import Program
from core.content_element import create_element
from config.constants import ContentType, DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT


class TemplateManager:
    """Manages program templates"""
    
    @staticmethod
    def get_templates() -> List[Dict]:
        """Get list of available templates"""
        return [
            {
                "name": "Blank",
                "description": "Empty program with default resolution",
                "icon": "📄"
            },
            {
                "name": "Text Only",
                "description": "Program with a single text element",
                "icon": "🔠"
            },
            {
                "name": "Image + Text",
                "description": "Program with image and text elements",
                "icon": "🖼"
            },
            {
                "name": "Clock Display",
                "description": "Program with clock widget",
                "icon": "🕐"
            },
            {
                "name": "Video Player",
                "description": "Program with video element",
                "icon": "🎬"
            }
        ]
    
    @staticmethod
    def create_from_template(template_name: str, program_name: str = None) -> Program:
        """Create a program from a template"""
        if template_name == "Blank":
            return TemplateManager._create_blank(program_name)
        elif template_name == "Text Only":
            return TemplateManager._create_text_only(program_name)
        elif template_name == "Image + Text":
            return TemplateManager._create_image_text(program_name)
        elif template_name == "Clock Display":
            return TemplateManager._create_clock_display(program_name)
        elif template_name == "Video Player":
            return TemplateManager._create_video_player(program_name)
        else:
            return TemplateManager._create_blank(program_name)
    
    @staticmethod
    def _create_blank(name: str = None) -> Program:
        """Create blank program"""
        program = Program(
            name=name or "New Program",
            width=DEFAULT_CANVAS_WIDTH,
            height=DEFAULT_CANVAS_HEIGHT
        )
        return program
    
    @staticmethod
    def _create_text_only(name: str = None) -> Program:
        """Create program with text element"""
        program = TemplateManager._create_blank(name or "Text Program")
        
        # Add centered text element
        text_element = create_element(
            ContentType.TEXT,
            program.width // 2 - 100,
            program.height // 2 - 25
        )
        text_element.properties["text"] = "Welcome"
        text_element.properties["font_size"] = 48
        text_element.properties["color"] = "#000000"
        text_element.width = 200
        text_element.height = 50
        
        program.elements.append(text_element.to_dict())
        return program
    
    @staticmethod
    def _create_image_text(name: str = None) -> Program:
        """Create program with image and text"""
        program = TemplateManager._create_blank(name or "Image + Text Program")
        
        # Add image element (top)
        image_element = create_element(
            ContentType.PHOTO,
            program.width // 2 - 320,
            50
        )
        image_element.width = 640
        image_element.height = 360
        program.elements.append(image_element.to_dict())
        
        # Add text element (bottom)
        text_element = create_element(
            ContentType.TEXT,
            program.width // 2 - 200,
            program.height - 150
        )
        text_element.properties["text"] = "Caption Text"
        text_element.properties["font_size"] = 36
        text_element.properties["color"] = "#000000"
        text_element.width = 400
        text_element.height = 50
        program.elements.append(text_element.to_dict())
        
        return program
    
    @staticmethod
    def _create_clock_display(name: str = None) -> Program:
        """Create program with clock widget"""
        program = TemplateManager._create_blank(name or "Clock Display")
        
        # Add clock element (centered)
        clock_element = create_element(
            ContentType.CLOCK,
            program.width // 2 - 150,
            program.height // 2 - 50
        )
        clock_element.properties["format"] = "HH:mm:ss"
        clock_element.properties["color"] = "#000000"
        clock_element.width = 300
        clock_element.height = 100
        program.elements.append(clock_element.to_dict())
        
        return program
    
    @staticmethod
    def _create_video_player(name: str = None) -> Program:
        """Create program with video element"""
        program = TemplateManager._create_blank(name or "Video Player")
        
        # Add video element (centered)
        video_element = create_element(
            ContentType.VIDEO,
            program.width // 2 - 320,
            program.height // 2 - 180
        )
        video_element.width = 640
        video_element.height = 360
        video_element.properties["loop"] = True
        program.elements.append(video_element.to_dict())
        
        return program

