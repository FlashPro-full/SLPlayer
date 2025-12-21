import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.logger import get_logger
from config.constants import ContentType

logger = get_logger(__name__)


class XMLConverter:
    
    @staticmethod
    def huidu_xml_to_soo_programs(xml_string: str, default_width: int = 1920, default_height: int = 1080) -> tuple[List[Dict], int, int]:
        from core.program_converter import program_to_sdk
        try:
            root = ET.fromstring(xml_string)
            
            width = default_width
            height = default_height
            
            # Handle API response structure: <sdk><out>...</out></sdk>
            out_elem = root.find(".//out") or root.find(".//Out")
            if out_elem is not None:
                root = out_elem
            
            # Find screen element to get dimensions
            screen_elem = root.find(".//screen") or root.find(".//Screen")
            if screen_elem is not None:
                screen_width = screen_elem.get("width", "0")
                screen_height = screen_elem.get("height", "0")
                try:
                    if screen_width and int(screen_width) > 0:
                        width = int(screen_width)
                    if screen_height and int(screen_height) > 0:
                        height = int(screen_height)
                except (ValueError, TypeError):
                    pass
            
            # Find all program elements (case-insensitive)
            programs_list = root.findall(".//program") or root.findall(".//Program")
            if not programs_list:
                programs_elem = root.find(".//program") or root.find(".//Program")
                if programs_elem is not None:
                    programs_list = [programs_elem]
            
            soo_programs = []
            for prog_elem in programs_list:
                program_guid = prog_elem.get("guid", "")
                program_name_elem = prog_elem.find("name")
                program_name = program_name_elem.text if program_name_elem is not None and program_name_elem.text else prog_elem.get("name", f"Program_{program_guid}" if program_guid else "Program")
                
                # Parse play control
                play_control = XMLConverter._parse_play_control(prog_elem)
                
                # Parse play mode
                play_mode = XMLConverter._parse_play_mode(prog_elem)
                
                # Parse elements from areas
                elements = []
                areas = prog_elem.findall("area")
                for area_elem in areas:
                    rectangle_elem = area_elem.find("rectangle")
                    if rectangle_elem is None:
                        continue
                    
                    try:
                        area_x = int(rectangle_elem.get("x", 0))
                        area_y = int(rectangle_elem.get("y", 0))
                        area_width = int(rectangle_elem.get("width", 0))
                        area_height = int(rectangle_elem.get("height", 0))
                    except (ValueError, TypeError):
                        continue
                    
                    resource_elem = area_elem.find("resource")
                    if resource_elem is not None:
                        for child in resource_elem:
                            element = XMLConverter._parse_resource_element(child, area_x, area_y, area_width, area_height)
                            if element:
                                elements.append(element)
                
                soo_program = {
                    "id": f"program_{program_guid.lower()}" if program_guid else f"program_{int(datetime.now().timestamp())}",
                    "name": program_name,
                    "width": width,
                    "height": height,
                    "created": datetime.now().isoformat(),
                    "modified": datetime.now().isoformat(),
                    "elements": elements,
                    "properties": {
                        "checked": True,
                        "frame": {"enabled": False, "style": "---"},
                        "background_music": {"enabled": False, "file": "", "volume": 0}
                    },
                    "play_mode": play_mode,
                    "play_control": play_control,
                    "duration": 0.0
                }
                from core.program_converter import program_to_sdk
                sdk_program = program_to_sdk(soo_program)
                soo_programs.append(sdk_program)
            
            return soo_programs, width, height
        except Exception as e:
            logger.error(f"Error converting XML to SOO: {e}", exc_info=True)
            return [], default_width, default_height
    
    @staticmethod
    def _parse_play_control(prog_elem: ET.Element) -> Dict:
        """Parse play control from program element"""
        play_control = {
            "specified_time": {"enabled": False, "time": ""},
            "specify_week": {"enabled": False, "days": []},
            "specify_date": {"enabled": False, "date": ""}
        }
        
        play_control_elem = prog_elem.find("playControl") or prog_elem.find("play_control")
        if play_control_elem is not None:
            specified_time_elem = play_control_elem.find("specifiedTime") or play_control_elem.find("specified_time")
            if specified_time_elem is not None:
                play_control["specified_time"] = {
                    "enabled": specified_time_elem.get("enabled", "false").lower() == "true",
                    "time": specified_time_elem.get("time", "")
                }
            
            specify_week_elem = play_control_elem.find("specifyWeek") or play_control_elem.find("specify_week")
            if specify_week_elem is not None:
                days_str = specify_week_elem.get("days", "")
                days = [int(d) for d in days_str.split(",") if d.strip().isdigit()] if days_str else []
                play_control["specify_week"] = {
                    "enabled": specify_week_elem.get("enabled", "false").lower() == "true",
                    "days": days
                }
            
            specify_date_elem = play_control_elem.find("specifyDate") or play_control_elem.find("specify_date")
            if specify_date_elem is not None:
                play_control["specify_date"] = {
                    "enabled": specify_date_elem.get("enabled", "false").lower() == "true",
                    "date": specify_date_elem.get("date", "")
                }
        
        return play_control
    
    @staticmethod
    def _parse_play_mode(prog_elem: ET.Element) -> Dict:
        """Parse play mode from program element"""
        play_mode = {
            "mode": "play_times",
            "play_times": 1,
            "fixed_length": "0:00:30"
        }
        
        play_mode_elem = prog_elem.find("playMode") or prog_elem.find("play_mode")
        if play_mode_elem is not None:
            mode = play_mode_elem.get("mode", "play_times")
            play_mode["mode"] = mode
            if mode == "play_times":
                try:
                    play_mode["play_times"] = int(play_mode_elem.get("play_times", 1))
                except (ValueError, TypeError):
                    pass
            elif mode == "fixed_length":
                play_mode["fixed_length"] = play_mode_elem.get("fixed_length", "0:00:30")
        
        return play_mode
    
    @staticmethod
    def _parse_resource_element(elem: ET.Element, x: int, y: int, width: int, height: int) -> Optional[Dict]:
        tag = elem.tag.lower()
        element_id = f"element_{datetime.now().timestamp()}_{id(elem)}"
        
        if tag == "text":
            return XMLConverter._parse_text_element(elem, element_id, x, y, width, height)
        elif tag in ["image", "photo"]:
            return XMLConverter._parse_photo_element(elem, element_id, x, y, width, height)
        elif tag == "video":
            return XMLConverter._parse_video_element(elem, element_id, x, y, width, height)
        elif tag in ["digitalclock", "dialclock"]:
            return XMLConverter._parse_clock_element(elem, element_id, x, y, width, height)
        elif tag == "dynamic":
            return XMLConverter._parse_sensor_element(elem, element_id, x, y, width, height)
        elif tag == "html":
            return XMLConverter._parse_html_element(elem, element_id, x, y, width, height)
        elif tag == "hdmi":
            return XMLConverter._parse_hdmi_element(elem, element_id, x, y, width, height)
        else:
            logger.warning(f"Unknown element type: {tag}")
            return None
    
    @staticmethod
    def _parse_text_element(elem: ET.Element, element_id: str, x: int, y: int, width: int, height: int) -> Dict:
        string_elem = elem.find("string")
        text_content = string_elem.text if string_elem is not None and string_elem.text else ""
        
        background_color = elem.get("background", "")
        text_color = elem.get("color", "")
        
        font_elem = elem.find("font")
        font_family = "Arial"
        font_size = 24
        color = "#FFFFFF"
        bold = False
        italic = False
        underline = False
        
        if font_elem is not None:
            font_family = font_elem.get("name", "Arial")
            if not text_color:
                color = font_elem.get("color", "#FFFFFF")
            else:
                color = text_color
            try:
                font_size = int(font_elem.get("size", 24))
            except (ValueError, TypeError):
                font_size = 24
            bold = font_elem.get("bold", "false").lower() == "true"
            italic = font_elem.get("italic", "false").lower() == "true"
            underline = font_elem.get("underline", "false").lower() == "true"
        elif text_color:
            color = text_color
        
        style_elem = elem.find("style")
        alignment = "left"
        vertical_alignment = "middle"
        if style_elem is not None:
            align_attr = style_elem.get("align", "left")
            alignment = align_attr.lower()
            vertical_align_attr = style_elem.get("verticalAlign", "middle")
            vertical_alignment = vertical_align_attr.lower()
        
        single_line = elem.get("singleLine", "false").lower() == "true"
        
        element_type = ContentType.SINGLELINE_TEXT.value if single_line else ContentType.TEXT.value
        
        effect_elem = elem.find("effect")
        animation_type = 0
        animation_speed = 5
        hold_time = 5000
        if effect_elem is not None:
            try:
                animation_type = int(effect_elem.get("type", "0"))
            except (ValueError, TypeError):
                animation_type = 0
            try:
                animation_speed = int(effect_elem.get("speed", "5"))
            except (ValueError, TypeError):
                animation_speed = 5
            try:
                hold_time = int(effect_elem.get("hold", "5000"))
            except (ValueError, TypeError):
                hold_time = 5000
        
        from config.animation_effects import get_animation_name
        animation_name = get_animation_name(animation_type)
        speed_str = f"{animation_speed} fast" if animation_speed <= 3 else f"{animation_speed} slow" if animation_speed >= 8 else f"{animation_speed} medium"
        hold_time_sec = hold_time / 1000.0 if hold_time > 100 else hold_time
        
        properties: Dict[str, Any]
        if element_type == ContentType.TEXT.value:
            properties = {
                "text": {
                    "content": text_content,
                    "multiLine": not single_line,
                    "format": {
                        "font_family": font_family,
                        "font_size": font_size,
                        "font_color": color,
                        "bold": bold,
                        "italic": italic,
                        "underline": underline,
                        "alignment": alignment,
                        "vertical_alignment": vertical_alignment
                    }
                },
                "font_family": font_family,
                "font_size": font_size,
                "color": color,
                "bold": bold,
                "italic": italic,
                "underline": underline,
                "multiLine": not single_line,
                "animation": {
                    "entrance": animation_name,
                    "exit": animation_name,
                    "entrance_speed": speed_str,
                    "exit_speed": speed_str,
                    "hold_time": hold_time_sec
                },
                "animation_speed": animation_speed,
                "duration": hold_time_sec
            }
            if background_color:
                properties["text"]["format"]["text_bg_color"] = background_color
                properties["background_color"] = background_color
        else:  # singleline_text
            properties = {
                "text": {
                    "content": text_content,
                    "multiLine": True,
                    "format": {
                        "font_family": font_family,
                        "font_size": font_size,
                        "font_color": color,
                        "bold": bold,
                        "italic": italic,
                        "underline": underline
                    }
                },
                "font_family": font_family,
                "font_size": font_size,
                "color": color,
                "bold": bold,
                "italic": italic,
                "underline": underline,
                "multiLine": True,
                "speed": 5,
                "direction": "left",
                "animation": {
                    "entrance": animation_name,
                    "exit": animation_name,
                    "entrance_speed": speed_str,
                    "exit_speed": speed_str,
                    "hold_time": hold_time_sec
                },
                "animation_speed": animation_speed,
                "duration": hold_time_sec
            }
        
        return {
            "id": element_id,
            "type": element_type,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "properties": properties
        }
    
    @staticmethod
    def _parse_photo_element(elem: ET.Element, element_id: str, x: int, y: int, width: int, height: int) -> Dict:
        file_elem = elem.find("file") or elem.find("url")
        file_path = ""
        if file_elem is not None and file_elem.text:
            file_path = file_elem.text
        else:
            file_path = elem.get("file") or elem.get("url") or ""
        
        # SOO format uses nested properties structure
        properties = {
            "photo": {
                "file_path": file_path
            }
        }
        
        return {
            "id": element_id,
            "type": ContentType.PHOTO.value,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "properties": properties
        }
    
    @staticmethod
    def _parse_video_element(elem: ET.Element, element_id: str, x: int, y: int, width: int, height: int) -> Dict:
        file_elem = elem.find("file") or elem.find("url")
        file_path = ""
        if file_elem is not None and file_elem.text:
            file_path = file_elem.text
        else:
            file_path = elem.get("file") or elem.get("url") or ""
        
        # SOO format uses nested properties structure
        properties = {
            "video": {
                "file_path": file_path
            },
            "video_shot": {
                "enabled": False
            }
        }
        
        return {
            "id": element_id,
            "type": ContentType.VIDEO.value,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "properties": properties
        }
    
    @staticmethod
    def _parse_clock_element(elem: ET.Element, element_id: str, x: int, y: int, width: int, height: int) -> Dict:
        font_elem = elem.find("font")
        font_family = "Arial"
        font_size = 48
        color = "#000000"
        
        if font_elem is not None:
            font_family = font_elem.get("name", "Arial")
            color = font_elem.get("color", "#000000")
            try:
                font_size = int(font_elem.get("size", 48))
            except (ValueError, TypeError):
                font_size = 48
        
        show_date = elem.get("showDate", "true").lower() == "true"
        show_time = elem.get("showTime", "true").lower() == "true"
        
        # SOO format uses nested properties structure
        properties = {
            "clock": {
                "show_date": show_date,
                "font_family": font_family,
                "font_size": font_size,
                "color": color
            }
        }
        
        return {
            "id": element_id,
            "type": ContentType.CLOCK.value,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "properties": properties
        }
    
    @staticmethod
    def _parse_sensor_element(elem: ET.Element, element_id: str, x: int, y: int, width: int, height: int) -> Dict:
        sensor_type_str = elem.get("type", "0")
        try:
            sensor_type_num = int(sensor_type_str)
        except (ValueError, TypeError):
            sensor_type_num = 0
        
        sensor_type_map = {
            0: "temp",
            1: "humidity",
            2: "pm25",
            3: "pm10",
            4: "wind_power",
            5: "wind_direction",
            6: "noise",
            7: "pressure",
            8: "light_intensity",
            9: "co2"
        }
        sensor_type = sensor_type_map.get(sensor_type_num, "temp")
        
        font_elem = elem.find("font")
        font_family = "Arial"
        font_size = 24
        color = "#FFFFFF"
        
        if font_elem is not None:
            font_family = font_elem.get("name", "Arial")
            color = font_elem.get("color", "#FFFFFF")
            try:
                font_size = int(font_elem.get("size", 24))
            except (ValueError, TypeError):
                font_size = 24
        
        # SOO format uses nested properties structure
        properties = {
            "sensor": {
                "sensor_type": sensor_type,
                "fixed_text": "The Temperature",
                "font_family": font_family,
                "font_color": color,
                "unit": "°C"
            }
        }
        
        return {
            "id": element_id,
            "type": ContentType.SENSOR.value,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "properties": properties
        }
    
    @staticmethod
    def _parse_html_element(elem: ET.Element, element_id: str, x: int, y: int, width: int, height: int) -> Dict:
        url_elem = elem.find("url") or elem.find("html")
        url = "https://www.google.com/"
        if url_elem is not None and url_elem.text:
            url = url_elem.text
        else:
            url = elem.get("url") or elem.get("html") or "https://www.google.com/"
        
        # SOO format uses nested properties structure
        properties = {
            "html": {
                "url": url,
                "time_refresh_enabled": False,
                "time_refresh_value": 15.0
            }
        }
        
        return {
            "id": element_id,
            "type": ContentType.HTML.value,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "properties": properties
        }
    
    @staticmethod
    def _parse_hdmi_element(elem: ET.Element, element_id: str, x: int, y: int, width: int, height: int) -> Dict:
        source = elem.get("source", "0")
        try:
            source_num = int(source)
        except (ValueError, TypeError):
            source_num = 0
        
        # SOO format uses nested properties structure
        properties = {
            "hdmi": {
                "display_mode": "Full Screen Zoom"
            }
        }
        
        return {
            "id": element_id,
            "type": ContentType.HDMI.value,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "properties": properties
        }


