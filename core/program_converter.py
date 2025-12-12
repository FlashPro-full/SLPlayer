"""
Program format converter between *.soo format and SDK formats (NovaStar/Huidu)
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from utils.logger import get_logger

logger = get_logger(__name__)


class ProgramConverter:
    """Converts between *.soo program format and SDK formats"""
    
    @staticmethod
    def soo_to_sdk(program_dict: Dict, controller_type: str) -> Dict:
        """
        Convert *.soo program format to SDK format for upload
        
        Args:
            program_dict: Program data in *.soo format (from Program.to_dict())
            controller_type: "novastar" or "huidu"
            
        Returns:
            Program data in SDK format
        """
        if controller_type.lower() == "novastar":
            return ProgramConverter._soo_to_novastar(program_dict)
        elif controller_type.lower() == "huidu":
            return ProgramConverter._soo_to_huidu(program_dict)
        else:
            logger.warning(f"Unknown controller type: {controller_type}")
            return program_dict
    
    @staticmethod
    def sdk_to_soo(sdk_program_dict: Dict, controller_type: str) -> Dict:
        """
        Convert SDK program format to *.soo format for download/editing
        
        Args:
            sdk_program_dict: Program data in SDK format (from controller)
            controller_type: "novastar" or "huidu"
            
        Returns:
            Program data in *.soo format (ready for Program.from_dict())
        """
        if controller_type.lower() == "novastar":
            return ProgramConverter._novastar_to_soo(sdk_program_dict)
        elif controller_type.lower() == "huidu":
            return ProgramConverter._huidu_to_soo(sdk_program_dict)
        else:
            logger.warning(f"Unknown controller type: {controller_type}")
            return sdk_program_dict
    
    @staticmethod
    def _soo_to_novastar(program_dict: Dict) -> Dict:
        """Convert *.soo format to NovaStar SDK format"""
        from controllers.property_adapter import adapt_element_for_controller
        
        elements = program_dict.get("elements", [])
        adapted_elements = []
        
        for element in elements:
            adapted = adapt_element_for_controller(element, "novastar")
            adapted_elements.append(adapted)
        
        return {
            "name": program_dict.get("name", "Program"),
            "width": program_dict.get("width", 640),
            "height": program_dict.get("height", 480),
            "elements": adapted_elements,
            "properties": program_dict.get("properties", {}),
            "play_mode": program_dict.get("play_mode", {}),
            "play_control": program_dict.get("play_control", {})
        }
    
    @staticmethod
    def _soo_to_huidu(program_dict: Dict) -> Dict:
        """Convert *.soo format to Huidu SDK format"""
        from controllers.property_adapter import adapt_element_for_controller
        
        elements = program_dict.get("elements", [])
        adapted_elements = []
        
        for element in elements:
            adapted = adapt_element_for_controller(element, "huidu")
            adapted_elements.append(adapted)
        
        return {
            "name": program_dict.get("name", "Program"),
            "width": program_dict.get("width", 64),
            "height": program_dict.get("height", 32),
            "elements": adapted_elements,
            "properties": program_dict.get("properties", {}),
            "play_mode": program_dict.get("play_mode", {}),
            "play_control": program_dict.get("play_control", {})
        }
    
    @staticmethod
    def _novastar_to_soo(sdk_program_dict: Dict) -> Dict:
        """Convert NovaStar SDK format to *.soo format"""
        widgets = sdk_program_dict.get("widgets", []) or sdk_program_dict.get("elements", [])
        elements = []
        
        for widget in widgets:
            element = ProgramConverter._novastar_widget_to_soo_element(widget)
            if element:
                elements.append(element)
        
        return {
            "id": sdk_program_dict.get("id", f"program_{sdk_program_dict.get('name', 'Program').lower().replace(' ', '_')}"),
            "name": sdk_program_dict.get("name", "Program"),
            "width": sdk_program_dict.get("width", 640),
            "height": sdk_program_dict.get("height", 480),
            "elements": elements,
            "properties": {
                "checked": True,
                "frame": sdk_program_dict.get("frame", {"enabled": False, "style": "---"}),
                "background_music": sdk_program_dict.get("background_music", {"enabled": False, "file": "", "volume": 0})
            },
            "play_mode": sdk_program_dict.get("play_mode", {"mode": "play_times", "play_times": 1, "fixed_length": "0:00:30"}),
            "play_control": sdk_program_dict.get("play_control", {
                "specified_time": {"enabled": False, "time": ""},
                "specify_week": {"enabled": False, "days": []},
                "specify_date": {"enabled": False, "date": ""}
            }),
            "duration": sdk_program_dict.get("duration", 0.0)
        }
    
    @staticmethod
    def _huidu_to_soo(sdk_program_dict: Dict) -> Dict:
        """Convert Huidu SDK format to *.soo format"""
        soo_elements = []
        
        areas = sdk_program_dict.get("area", []) or sdk_program_dict.get("areas", []) or sdk_program_dict.get("elements", [])
        
        for area in areas:
            if isinstance(area, dict):
                items = area.get("item", [])
                area_x = area.get("x", 0)
                area_y = area.get("y", 0)
                area_width = area.get("width", 0)
                area_height = area.get("height", 0)
                
                for item in items:
                    if isinstance(item, dict):
                        soo_element = ProgramConverter._huidu_content_node_to_soo_element(item, area_x, area_y, area_width, area_height)
                        if soo_element:
                            soo_elements.append(soo_element)
            else:
                soo_element = ProgramConverter._huidu_element_to_soo_element(area)
                if soo_element:
                    soo_elements.append(soo_element)
        
        play_control = sdk_program_dict.get("playControl", {}) or sdk_program_dict.get("play_control", {})
        if isinstance(play_control, dict):
            play_control_converted = {
                "specified_time": play_control.get("specified_time", {"enabled": False, "time": ""}),
                "specify_week": play_control.get("specify_week", {"enabled": False, "days": []}),
                "specify_date": play_control.get("specify_date", {"enabled": False, "date": ""})
            }
        else:
            play_control_converted = {
                "specified_time": {"enabled": False, "time": ""},
                "specify_week": {"enabled": False, "days": []},
                "specify_date": {"enabled": False, "date": ""}
            }
        
        return {
            "id": sdk_program_dict.get("id") or sdk_program_dict.get("uuid") or f"program_{sdk_program_dict.get('name', 'Program').lower().replace(' ', '_')}",
            "name": sdk_program_dict.get("name", "Program"),
            "width": sdk_program_dict.get("width", 64),
            "height": sdk_program_dict.get("height", 32),
            "elements": soo_elements,
            "properties": {
                "checked": True,
                "frame": sdk_program_dict.get("frame", {"enabled": False, "style": "---"}),
                "background_music": sdk_program_dict.get("background_music", {"enabled": False, "file": "", "volume": 0})
            },
            "play_mode": sdk_program_dict.get("play_mode", {"mode": "play_times", "play_times": 1, "fixed_length": "0:00:30"}),
            "play_control": play_control_converted,
            "duration": sdk_program_dict.get("duration", 0.0)
        }
    
    @staticmethod
    def _novastar_widget_to_soo_element(widget: Dict) -> Optional[Dict]:
        """Convert NovaStar widget to *.soo element format"""
        widget_type = widget.get("type", "")
        layout = widget.get("layout", {})
        metadata = widget.get("metadata", {})
        
        element = {
            "type": "text",
            "x": int(layout.get("x", 0)) if isinstance(layout.get("x"), (int, str)) else 0,
            "y": int(layout.get("y", 0)) if isinstance(layout.get("y"), (int, str)) else 0,
            "width": int(layout.get("width", 200)) if isinstance(layout.get("width"), (int, str)) else 200,
            "height": int(layout.get("height", 100)) if isinstance(layout.get("height"), (int, str)) else 100,
            "properties": {}
        }
        
        if widget_type == "ARCH_TEXT":
            content = metadata.get("content", {})
            paragraphs = content.get("paragraphs", [])
            if paragraphs:
                lines = paragraphs[0].get("lines", [])
                if lines:
                    segs = lines[0].get("segs", [])
                    if segs:
                        element["properties"]["text"] = segs[0].get("content", "")
                
                text_attrs = paragraphs[0].get("textAttributes", [])
                if text_attrs:
                    attrs = text_attrs[0]
                    element["properties"]["color"] = attrs.get("textColor", "#000000")
                    font_info = attrs.get("attributes", {}).get("font", {})
                    if font_info:
                        element["properties"]["font_family"] = font_info.get("family", ["Arial"])[0] if isinstance(font_info.get("family"), list) else font_info.get("family", "Arial")
                        element["properties"]["font_size"] = font_info.get("size", 24)
            
            element["properties"]["duration"] = metadata.get("duration", 5000)
        elif widget_type in ["ARCH_IMAGE", "ARCH_PICTURE"]:
            element["type"] = "image"
            element["properties"]["file_path"] = widget.get("dataSource", "") or metadata.get("file_path", "")
            element["properties"]["duration"] = metadata.get("duration", 5000)
        elif widget_type == "ARCH_VIDEO":
            element["type"] = "video"
            element["properties"]["file_path"] = widget.get("dataSource", "") or metadata.get("file_path", "")
            element["properties"]["duration"] = metadata.get("duration", 10000)
        
        return element
    
    @staticmethod
    def _huidu_content_node_to_soo_element(item: Dict, area_x: int = 0, area_y: int = 0, area_width: int = 0, area_height: int = 0) -> Optional[Dict]:
        """Convert Huidu content node (from AreaNode.item) to *.soo element format"""
        element_type = item.get("type", "")
        
        soo_element = {
            "type": "",
            "x": area_x,
            "y": area_y,
            "width": area_width if area_width > 0 else 200,
            "height": area_height if area_height > 0 else 100,
            "properties": {}
        }
        
        if element_type == "text":
            soo_element["type"] = "text"
            soo_element["properties"]["text"] = item.get("string", "")
            if item.get("font"):
                font = item["font"]
                if isinstance(font, dict):
                    soo_element["properties"]["font_family"] = font.get("family", "Arial")
                    soo_element["properties"]["font_size"] = font.get("size", 24)
            soo_element["properties"]["color"] = item.get("color", "#000000")
        elif element_type == "image":
            soo_element["type"] = "photo"
            soo_element["properties"]["file_path"] = item.get("file_path", "") or item.get("filePath", "")
        elif element_type == "video":
            soo_element["type"] = "video"
            soo_element["properties"]["file_path"] = item.get("file_path", "") or item.get("filePath", "")
        elif element_type == "digitalClock":
            soo_element["type"] = "clock"
        elif element_type == "dialClock":
            soo_element["type"] = "dial_clock"
        elif element_type == "dynamic":
            soo_element["type"] = "animation"
        else:
            return None
        
        return soo_element
    
    @staticmethod
    def _huidu_element_to_soo_element(element: Dict) -> Optional[Dict]:
        """Convert Huidu element to *.soo element format (legacy format)"""
        element_type = element.get("type", "")
        
        soo_element = {
            "type": element_type,
            "x": element.get("x", 0),
            "y": element.get("y", 0),
            "width": element.get("width", 200),
            "height": element.get("height", 100),
            "properties": element.get("properties", {}).copy()
        }
        
        if element_type == "text":
            soo_element["properties"]["text"] = element.get("properties", {}).get("text", "")
            soo_element["properties"]["color"] = element.get("properties", {}).get("text_color", "#000000")
            soo_element["properties"]["font_family"] = element.get("properties", {}).get("font_name", "Arial")
            soo_element["properties"]["font_size"] = element.get("properties", {}).get("font_size", 24)
        elif element_type in ["photo", "image"]:
            soo_element["properties"]["file_path"] = element.get("properties", {}).get("file_path", "") or element.get("properties", {}).get("image_path", "")
        elif element_type == "video":
            soo_element["properties"]["file_path"] = element.get("properties", {}).get("file_path", "") or element.get("properties", {}).get("video_path", "")
        elif element_type == "clock":
            soo_element["properties"]["show_date"] = element.get("properties", {}).get("show_date", True)
            soo_element["properties"]["show_time"] = element.get("properties", {}).get("show_time", True)
        
        return soo_element

