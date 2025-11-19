import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import uuid

from core.program_manager import Program
from utils.logger import get_logger

logger = get_logger(__name__)


class XMLImporter:
    
    PLUGIN_TYPE_MAP = {
        "HD_Video_Plugin": "video",
        "HD_Photo_Plugin": "image",
        "HD_Text_Plugin": "text",
        "HD_SingleLineText_Plugin": "single_line_text",
        "HD_animationText_Plugin": "animation",
        "HD_Clock_Plugin": "clock",
        "HD_Time_Plugin": "timing",
        "HD_Weather_Plugin": "weather",
        "HD_Sensor_Plugin": "sensor"
    }
    
    @staticmethod
    def import_xml_file(file_path: str) -> Optional[Program]:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            screen_node = root.find(".//Node[@Type='HD_Controller_Plugin']")
            if screen_node is None:
                logger.error("No HD_Controller_Plugin node found in XML")
                return None
            
            screen_props = {}
            for attr in screen_node.findall("Attribute"):
                name = attr.get("Name")
                value = attr.text if attr.text is not None else attr.get("Value", "")
                if name:
                    screen_props[name] = value
            
            screen_width = int(screen_props.get("Width", 640))
            screen_height = int(screen_props.get("Height", 480))
            screen_name = screen_props.get("__NAME__", "Screen")
            
            program_node = screen_node.find(".//Node[@Type='HD_OrdinaryScene_Plugin']")
            if program_node is None:
                logger.error("No HD_OrdinaryScene_Plugin node found in XML")
                return None
            
            program_attrs = {}
            for attr in program_node.findall("Attribute"):
                name = attr.get("Name")
                value = attr.text if attr.text is not None else attr.get("Value", "")
                if name:
                    program_attrs[name] = value
            
            program_name = program_attrs.get("__NAME__", "Program1")
            
            program = Program(name=program_name, width=screen_width, height=screen_height)
            
            XMLImporter._apply_program_attributes(program, program_attrs, screen_props, screen_width, screen_height, screen_name)
            
            frame_nodes = program_node.findall(".//Node[@Type='HD_Frame_Plugin']")
            for frame_node in frame_nodes:
                element = XMLImporter._parse_frame_node(frame_node, screen_width, screen_height)
                if element:
                    program.elements.append(element)
            
            logger.info(f"Successfully imported XML file: {file_path}")
            return program
            
        except Exception as e:
            logger.error(f"Error importing XML file {file_path}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _parse_program_node(program_node: ET.Element, screen_properties: Dict) -> Optional[Program]:
        try:
            program_attrs = {}
            for attr in program_node.findall("Attribute"):
                name = attr.get("Name")
                value = attr.text if attr.text is not None else attr.get("Value", "")
                if name:
                    program_attrs[name] = value
            
            program_name = program_attrs.get("__NAME__", "Program1")
            screen_width = screen_properties.get("width", 640)
            screen_height = screen_properties.get("height", 480)
            screen_name = screen_properties.get("screen_name", "Screen")
            
            program = Program(name=program_name, width=screen_width, height=screen_height)
            
            screen_props = {
                "Rotation": screen_properties.get("rotation", 0),
                "Stretch": screen_properties.get("stretch", 0),
                "ZoomModulus": screen_properties.get("zoom_modulus", 0)
            }
            
            XMLImporter._apply_program_attributes(program, program_attrs, screen_props, screen_width, screen_height, screen_name)
            
            frame_nodes = program_node.findall(".//Node[@Type='HD_Frame_Plugin']")
            for frame_node in frame_nodes:
                element = XMLImporter._parse_frame_node(frame_node, screen_width, screen_height)
                if element:
                    program.elements.append(element)
            
            return program
        except Exception as e:
            logger.error(f"Error parsing program node: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _apply_program_attributes(program: Program, program_attrs: Dict, screen_props: Dict, screen_width: int, screen_height: int, screen_name: str):
        if "screen" not in program.properties:
            program.properties["screen"] = {}
        if isinstance(program.properties["screen"], dict):
            program.properties["screen"].update({
                "screen_name": screen_name,
                "width": screen_width,
                "height": screen_height,
                "rotation": int(screen_props.get("Rotation", 0)),
                "stretch": int(screen_props.get("Stretch", 0)),
                "zoom_modulus": int(screen_props.get("ZoomModulus", 0))
            })
        
        play_mode_str = program_attrs.get("PlayMode", "LoopTime")
        if play_mode_str == "LoopTime":
            program.play_mode["mode"] = "play_times"
            program.play_mode["play_times"] = int(program_attrs.get("PlayTimes", 1))
        else:
            program.play_mode["mode"] = "fixed_length"
            fixed_duration = int(program_attrs.get("FixedDuration", 30000))
            seconds = fixed_duration // 1000
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            program.play_mode["fixed_length"] = f"{hours}:{minutes:02d}:{secs:02d}"
        
        use_specified = int(program_attrs.get("UseSpacifiled", 0))
        if use_specified:
            program.play_control["specified_time"]["enabled"] = True
            start_time = program_attrs.get("SpaceStartTime", "00:00:00")
            stop_time = program_attrs.get("SpaceStopTime", "23:59:59")
            program.play_control["specified_time"]["time"] = f"{start_time}-{stop_time}"
        
        week_days = []
        day_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        for day_name, day_index in day_map.items():
            if int(program_attrs.get(day_name, 0)) == 1:
                week_days.append(day_index)
        if week_days:
            program.play_control["specify_week"]["enabled"] = True
            program.play_control["specify_week"]["days"] = week_days
    
    @staticmethod
    def _parse_frame_node(frame_node: ET.Element, screen_width: int, screen_height: int) -> Optional[Dict]:
        try:
            frame_attrs = {}
            for attr in frame_node.findall("Attribute"):
                name = attr.get("Name")
                value = attr.text if attr.text is not None else attr.get("Value", "")
                if name:
                    frame_attrs[name] = value
            
            child_type = frame_attrs.get("ChildType", "")
            element_type = XMLImporter.PLUGIN_TYPE_MAP.get(child_type)
            
            if not element_type:
                logger.warning(f"Unknown child type: {child_type}")
                return None
            
            element = {
                "id": f"element_{uuid.uuid4().hex[:12]}",
                "type": element_type,
                "name": frame_attrs.get("__NAME__", f"{element_type}1"),
                "x": int(frame_attrs.get("X", 0)),
                "y": int(frame_attrs.get("Y", 0)),
                "width": int(frame_attrs.get("Width", screen_width)),
                "height": int(frame_attrs.get("Height", screen_height)),
                "properties": {}
            }
            
            if "properties" not in element:
                element["properties"] = {}
            if isinstance(element["properties"], dict):
                element["properties"]["area"] = {
                    "x": element["x"],
                    "y": element["y"],
                    "width": element["width"],
                    "height": element["height"]
                }
                
                frame_enabled = int(frame_attrs.get("FrameType", 0)) != 0
                if frame_enabled:
                    element["properties"]["frame"] = {
                        "enabled": True,
                        "type": int(frame_attrs.get("FrameType", 0)),
                        "speed": int(frame_attrs.get("FrameSpeed", 4)),
                        "effect": int(frame_attrs.get("FrameEffect", 0))
                    }
                else:
                    element["properties"]["frame"] = {
                        "enabled": False,
                        "type": 0,
                        "speed": 4,
                        "effect": 0
                    }
            
            child_node = frame_node.find(f".//Node[@Type='{child_type}']")
            if child_node:
                XMLImporter._parse_child_plugin(child_node, element, element_type)
            
            return element
            
        except Exception as e:
            logger.error(f"Error parsing frame node: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _parse_child_plugin(child_node: ET.Element, element: Dict, element_type: str):
        child_attrs = {}
        for attr in child_node.findall("Attribute"):
            name = attr.get("Name")
            value = attr.text if attr.text is not None else attr.get("Value", "")
            if name:
                child_attrs[name] = value
        
        props = element["properties"]
        
        if element_type == "video":
            file_list = child_node.find("List[@Name='__FileList__']")
            if file_list is not None:
                video_files = []
                for item in file_list.findall("ListItem"):
                    file_key = item.get("FileKey", "")
                    file_name = item.get("FileName", "")
                    if file_key == "Video" and file_name:
                        video_files.append(file_name)
                if video_files:
                    props["video_list"] = video_files
        
        elif element_type == "image":
            file_list = child_node.find("List[@Name='__FileList__']")
            if file_list is not None:
                photo_files = []
                for item in file_list.findall("ListItem"):
                    file_key = item.get("FileKey", "")
                    file_name = item.get("FileName", "")
                    if file_key in ["Photo", "Image"] and file_name:
                        photo_files.append(file_name)
                if photo_files:
                    props["photo_list"] = photo_files
                    props["image_list"] = photo_files
            
            disp_effect = int(child_attrs.get("DispEffect", 0))
            disp_time = int(child_attrs.get("DispTime", 4))
            clear_effect = int(child_attrs.get("ClearEffect", 0))
            clear_time = int(child_attrs.get("ClearTime", 4))
            hold_time = float(child_attrs.get("HoldTime", 50))
            
            from config.animation_effects import get_animation_name
            entrance_name = get_animation_name(disp_effect)
            exit_name = get_animation_name(clear_effect)
            
            entrance_speed_str = f"{disp_time} fast" if disp_time > 1 else "1 fast"
            exit_speed_str = f"{clear_time} fast" if clear_time > 1 else "1 fast"
            
            props["animation"] = {
                "entrance": entrance_name,
                "entrance_animation": disp_effect,
                "entrance_speed": entrance_speed_str,
                "exit": exit_name,
                "exit_animation": clear_effect,
                "exit_speed": exit_speed_str,
                "hold_time": hold_time / 10.0
            }
        
        elif element_type == "text":
            props["text"] = {
                "content": child_attrs.get("Html", ""),
                "font_name": child_attrs.get("TextFontName", "MS Shell Dlg 2"),
                "font_size": int(child_attrs.get("TextFontSize", 16)),
                "text_color": child_attrs.get("TextColor", "#ffffff"),
                "stroke_color": int(child_attrs.get("StrokeColor", 65280)),
                "use_stroke": int(child_attrs.get("UseStroke", 0)) == 1,
                "use_hollow": int(child_attrs.get("UseHollow", 0)) == 1
            }
        
        elif element_type == "single_line_text":
            props["single_line_text"] = {
                "content": child_attrs.get("Html", ""),
                "font_name": child_attrs.get("TextFontName", "MS Shell Dlg 2"),
                "font_size": int(child_attrs.get("TextFontSize", 16)),
                "text_color": child_attrs.get("TextColor", "#ffffff"),
                "play_type": child_attrs.get("PlayType", "ByCount"),
                "by_count": int(child_attrs.get("ByCount", 1)),
                "by_time": int(child_attrs.get("ByTime", 300)),
                "speed": int(child_attrs.get("Speed", 4))
            }
        
        elif element_type == "animation":
            props["animation_text"] = {
                "html_string": child_attrs.get("HtmlString", ""),
                "effect_type": int(child_attrs.get("EffectType", 1)),
                "animation_speed": int(child_attrs.get("AnimationSpeed", 5)),
                "continue_speed": int(child_attrs.get("ContinueSpeed", 5)),
                "continue_style": int(child_attrs.get("ContinueStyle", 0)),
                "hold_time": float(child_attrs.get("HoldTime", 50)) / 10.0
            }
        
        elif element_type == "clock":
            props["clock"] = {
                "clock_type": int(child_attrs.get("ClockType", 0)),
                "time_zone": child_attrs.get("TimeZone", "-08:00"),
                "lcd_time_zone": child_attrs.get("LcdTimeZone", "Asia/Shanghai"),
                "use_daylight_saving": int(child_attrs.get("UseDaylightSavingTime", 0)) == 1
            }
        
        elif element_type == "timing":
            props["timing"] = {
                "time_mode": int(child_attrs.get("TimeMode", 0)),
                "target_time": child_attrs.get("TargetTime", ""),
                "time_zone": child_attrs.get("TimeZone", "-08:00"),
                "top_text": child_attrs.get("TopText", "")
            }
        
        elif element_type == "weather":
            props["weather"] = {
                "area_id": child_attrs.get("AreaID", "CH101010100"),
                "area_text": child_attrs.get("AreaText", "Beijing"),
                "display_style": int(child_attrs.get("DisplayStyle", 0))
            }
        
        elif element_type == "sensor":
            props["sensor"] = {
                "top_text": child_attrs.get("TopText", ""),
                "sensor_type": int(child_attrs.get("ID", 1460)),
                "temp_unit": int(child_attrs.get("TempUnit", 1)),
                "humidity_unit": int(child_attrs.get("HumidityUnit", 0)),
                "wind_unit": int(child_attrs.get("WindUnit", 1))
            }

