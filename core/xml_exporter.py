import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from core.program_manager import Program
from utils.logger import get_logger

logger = get_logger(__name__)


class XMLExporter:
    
    ELEMENT_TYPE_MAP = {
        "video": "HD_Video_Plugin",
        "image": "HD_Photo_Plugin",
        "text": "HD_Text_Plugin",
        "single_line_text": "HD_SingleLineText_Plugin",
        "animation": "HD_animationText_Plugin",
        "clock": "HD_Clock_Plugin",
        "timing": "HD_Time_Plugin",
        "weather": "HD_Weather_Plugin",
        "sensor": "HD_Sensor_Plugin"
    }
    
    @staticmethod
    def export_program(program: Program, file_path: str, screen_properties: Optional[Dict] = None) -> bool:
        try:
            if screen_properties is None:
                screen_properties = program.properties.get("screen", {})
            
            screen_width = screen_properties.get("width", program.width)
            screen_height = screen_properties.get("height", program.height)
            screen_name = screen_properties.get("screen_name", "Screen")
            rotation = screen_properties.get("rotation", 0)
            stretch = screen_properties.get("stretch", 0)
            zoom_modulus = screen_properties.get("zoom_modulus", 0)
            
            root = ET.Element("Node", Level="1", Type="HD_Controller_Plugin")
            
            XMLExporter._add_attribute(root, "AppVersion", "7.10.53.0")
            XMLExporter._add_attribute(root, "DeviceModel", "A4L")
            XMLExporter._add_attribute(root, "Height", str(screen_height))
            XMLExporter._add_attribute(root, "NewSpecialEffect", "close")
            XMLExporter._add_attribute(root, "Rotation", str(rotation))
            XMLExporter._add_attribute(root, "Stretch", str(stretch))
            XMLExporter._add_attribute(root, "SvnVersion", "13691")
            XMLExporter._add_attribute(root, "Width", str(screen_width))
            XMLExporter._add_attribute(root, "ZoomModulus", str(zoom_modulus))
            XMLExporter._add_attribute(root, "__NAME__", screen_name)
            XMLExporter._add_attribute(root, "mimiScreen", "0")
            
            ET.SubElement(root, "List", Name="communication", Index="-1")
            
            program_node = ET.SubElement(root, "Node", Level="2", Type="HD_OrdinaryScene_Plugin")
            
            XMLExporter._add_program_attributes(program_node, program)
            
            ET.SubElement(program_node, "List", Name="__FileList__", Index="-1")
            
            for element in program.elements:
                frame_node = XMLExporter._create_frame_node(element, screen_width, screen_height)
                if frame_node is not None:
                    program_node.append(frame_node)
            
            tree = ET.ElementTree(root)
            
            xml_str = minidom.parseString(ET.tostring(root, encoding='unicode')).toprettyxml(indent="    ")
            
            lines = xml_str.split('\n')
            if lines[0].startswith('<?xml'):
                lines = lines[1:]
            xml_str = '\n'.join(lines).strip()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
                f.write(xml_str)
            
            logger.info(f"Successfully exported program to XML: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting program to XML {file_path}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def _add_attribute(parent: ET.Element, name: str, value: str):
        attr_elem = ET.SubElement(parent, "Attribute", Name=name)
        attr_elem.text = str(value)
    
    @staticmethod
    def _add_program_attributes(program_node: ET.Element, program: Program):
        XMLExporter._add_attribute(program_node, "Alpha", "255")
        XMLExporter._add_attribute(program_node, "BgColor", "-16777216")
        XMLExporter._add_attribute(program_node, "BgMode", "BgImage")
        
        checked = program.properties.get("checked", True)
        XMLExporter._add_attribute(program_node, "Checked", "2" if checked else "0")
        
        play_mode = program.play_mode.get("mode", "play_times")
        if play_mode == "play_times":
            XMLExporter._add_attribute(program_node, "PlayMode", "LoopTime")
            XMLExporter._add_attribute(program_node, "PlayTimes", str(program.play_mode.get("play_times", 1)))
        else:
            XMLExporter._add_attribute(program_node, "PlayMode", "FixedDuration")
            fixed_length = program.play_mode.get("fixed_length", "0:00:30")
            parts = fixed_length.split(":")
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000
            else:
                total_ms = 30000
            XMLExporter._add_attribute(program_node, "FixedDuration", str(total_ms))
        
        play_control = program.play_control
        specified_time = play_control.get("specified_time", {})
        if specified_time.get("enabled", False):
            XMLExporter._add_attribute(program_node, "UseSpacifiled", "1")
            time_str = specified_time.get("time", "00:00:00-23:59:59")
            if "-" in time_str:
                start, stop = time_str.split("-", 1)
                XMLExporter._add_attribute(program_node, "SpaceStartTime", start)
                XMLExporter._add_attribute(program_node, "SpaceStopTime", stop)
            else:
                XMLExporter._add_attribute(program_node, "SpaceStartTime", "00:00:00")
                XMLExporter._add_attribute(program_node, "SpaceStopTime", "23:59:59")
        else:
            XMLExporter._add_attribute(program_node, "UseSpacifiled", "0")
            XMLExporter._add_attribute(program_node, "SpaceStartTime", "00:00:00")
            XMLExporter._add_attribute(program_node, "SpaceStopTime", "23:59:59")
        
        specify_week = play_control.get("specify_week", {})
        week_days = specify_week.get("days", [])
        day_map = {
            0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
            4: "Friday", 5: "Saturday", 6: "Sunday"
        }
        for day_index, day_name in day_map.items():
            XMLExporter._add_attribute(program_node, day_name, "1" if day_index in week_days else "0")
        
        XMLExporter._add_attribute(program_node, "FrameEffect", "0")
        XMLExporter._add_attribute(program_node, "FrameSpeed", "4")
        XMLExporter._add_attribute(program_node, "FrameType", "0")
        XMLExporter._add_attribute(program_node, "MotleyIndex", "0")
        XMLExporter._add_attribute(program_node, "PlayIndex", "0")
        XMLExporter._add_attribute(program_node, "PlayeTime", "30")
        XMLExporter._add_attribute(program_node, "PurityColor", "255")
        XMLExporter._add_attribute(program_node, "PurityIndex", "0")
        XMLExporter._add_attribute(program_node, "TricolorIndex", "0")
        XMLExporter._add_attribute(program_node, "Volume", "100")
        XMLExporter._add_attribute(program_node, "__GUID__", program.id)
        XMLExporter._add_attribute(program_node, "__NAME__", program.name)
    
    @staticmethod
    def _create_frame_node(element: Dict, screen_width: int, screen_height: int) -> Optional[ET.Element]:
        try:
            element_type = element.get("type", "")
            plugin_type = XMLExporter.ELEMENT_TYPE_MAP.get(element_type)
            
            if not plugin_type:
                logger.warning(f"Unknown element type: {element_type}")
                return None
            
            frame_node = ET.Element("Node", Level="3", Type="HD_Frame_Plugin")
            
            props = element.get("properties", {})
            area = props.get("area", {})
            frame = props.get("frame", {})
            
            XMLExporter._add_attribute(frame_node, "Alpha", "255")
            XMLExporter._add_attribute(frame_node, "ChildType", plugin_type)
            XMLExporter._add_attribute(frame_node, "FrameSpeed", str(frame.get("speed", 4)))
            XMLExporter._add_attribute(frame_node, "FrameType", "1" if frame.get("enabled", False) else "0")
            XMLExporter._add_attribute(frame_node, "Height", str(area.get("height", element.get("height", screen_height))))
            XMLExporter._add_attribute(frame_node, "LockArea", "0")
            XMLExporter._add_attribute(frame_node, "MotleyIndex", "0")
            XMLExporter._add_attribute(frame_node, "PurityColor", "255")
            XMLExporter._add_attribute(frame_node, "PurityIndex", "0")
            XMLExporter._add_attribute(frame_node, "TricolorIndex", "0")
            XMLExporter._add_attribute(frame_node, "Width", str(area.get("width", element.get("width", screen_width))))
            XMLExporter._add_attribute(frame_node, "X", str(area.get("x", element.get("x", 0))))
            XMLExporter._add_attribute(frame_node, "Y", str(area.get("y", element.get("y", 0))))
            XMLExporter._add_attribute(frame_node, "__GUID__", element.get("id", ""))
            XMLExporter._add_attribute(frame_node, "__NAME__", element.get("name", f"{element_type}1"))
            
            child_node = XMLExporter._create_child_plugin_node(element, element_type, plugin_type)
            if child_node is not None:
                frame_node.append(child_node)
            
            return frame_node
            
        except Exception as e:
            logger.error(f"Error creating frame node: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _create_child_plugin_node(element: Dict, element_type: str, plugin_type: str) -> Optional[ET.Element]:
        try:
            child_node = ET.Element("Node", Level="4", Type=plugin_type)
            props = element.get("properties", {})
            
            if element_type == "video":
                XMLExporter._add_video_attributes(child_node, props)
            elif element_type == "image":
                XMLExporter._add_image_attributes(child_node, props)
            elif element_type == "text":
                XMLExporter._add_text_attributes(child_node, props)
            elif element_type == "single_line_text":
                XMLExporter._add_single_line_text_attributes(child_node, props)
            elif element_type == "animation":
                XMLExporter._add_animation_attributes(child_node, props)
            elif element_type == "clock":
                XMLExporter._add_clock_attributes(child_node, props)
            elif element_type == "timing":
                XMLExporter._add_timing_attributes(child_node, props)
            elif element_type == "weather":
                XMLExporter._add_weather_attributes(child_node, props)
            elif element_type == "sensor":
                XMLExporter._add_sensor_attributes(child_node, props)
            
            XMLExporter._add_attribute(child_node, "__GUID__", element.get("id", ""))
            XMLExporter._add_attribute(child_node, "__NAME__", element.get("name", f"{element_type}1").lower())
            
            file_list = XMLExporter._create_file_list(element, element_type, props)
            if file_list is not None:
                child_node.append(file_list)
            
            return child_node
            
        except Exception as e:
            logger.error(f"Error creating child plugin node: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _add_video_attributes(child_node: ET.Element, props: Dict):
        pass
    
    @staticmethod
    def _add_image_attributes(child_node: ET.Element, props: Dict):
        animation = props.get("animation", {})
        
        entrance_animation = animation.get("entrance_animation", 0)
        if isinstance(entrance_animation, str):
            from config.animation_effects import get_animation_index
            entrance_animation = get_animation_index(entrance_animation)
        XMLExporter._add_attribute(child_node, "DispEffect", str(entrance_animation))
        
        entrance_speed_str = animation.get("entrance_speed", "1 fast")
        entrance_speed = XMLExporter._convert_speed_to_index(entrance_speed_str)
        XMLExporter._add_attribute(child_node, "DispTime", str(entrance_speed))
        
        exit_animation = animation.get("exit_animation", 0)
        if isinstance(exit_animation, str):
            from config.animation_effects import get_animation_index
            exit_animation = get_animation_index(exit_animation)
        XMLExporter._add_attribute(child_node, "ClearEffect", str(exit_animation))
        
        exit_speed_str = animation.get("exit_speed", "1 fast")
        exit_speed = XMLExporter._convert_speed_to_index(exit_speed_str)
        XMLExporter._add_attribute(child_node, "ClearTime", str(exit_speed))
        
        hold_time = animation.get("hold_time", 5.0)
        XMLExporter._add_attribute(child_node, "HoldTime", str(int(hold_time * 10)))
    
    @staticmethod
    def _convert_speed_to_index(speed_str: str) -> int:
        try:
            if "fast" in speed_str.lower():
                parts = speed_str.split()
                if len(parts) > 0:
                    return int(parts[0])
            return int(speed_str)
        except (ValueError, AttributeError):
            return 4
    
    @staticmethod
    def _add_text_attributes(child_node: ET.Element, props: Dict):
        text = props.get("text", {})
        XMLExporter._add_attribute(child_node, "Html", text.get("content", ""))
        XMLExporter._add_attribute(child_node, "TextFontName", text.get("font_name", "MS Shell Dlg 2"))
        XMLExporter._add_attribute(child_node, "TextFontSize", str(text.get("font_size", 16)))
        XMLExporter._add_attribute(child_node, "TextColor", text.get("text_color", "#ffffff"))
        XMLExporter._add_attribute(child_node, "StrokeColor", str(text.get("stroke_color", 65280)))
        XMLExporter._add_attribute(child_node, "UseStroke", "1" if text.get("use_stroke", False) else "0")
        XMLExporter._add_attribute(child_node, "UseHollow", "1" if text.get("use_hollow", False) else "0")
        XMLExporter._add_attribute(child_node, "ContentAlign", "132")
        XMLExporter._add_attribute(child_node, "ContentHAlign", "1")
        XMLExporter._add_attribute(child_node, "PageCount", "1")
        XMLExporter._add_attribute(child_node, "SingleMode", "0")
        XMLExporter._add_attribute(child_node, "SpeedTimeIndex", "4")
        XMLExporter._add_attribute(child_node, "TransBgColor", "1")
        XMLExporter._add_attribute(child_node, "HeadCloseToTail", "1")
        XMLExporter._add_attribute(child_node, "HoldTime", "50")
        XMLExporter._add_attribute(child_node, "DispEffect", "0")
        XMLExporter._add_attribute(child_node, "DispTime", "4")
        XMLExporter._add_attribute(child_node, "ClearEffect", "0")
        XMLExporter._add_attribute(child_node, "ClearTime", "4")
        XMLExporter._add_attribute(child_node, "EditBgColor", "0")
    
    @staticmethod
    def _add_single_line_text_attributes(child_node: ET.Element, props: Dict):
        slt = props.get("single_line_text", {})
        XMLExporter._add_attribute(child_node, "Html", slt.get("content", ""))
        XMLExporter._add_attribute(child_node, "TextFontName", slt.get("font_name", "MS Shell Dlg 2"))
        XMLExporter._add_attribute(child_node, "TextFontSize", str(slt.get("font_size", 16)))
        XMLExporter._add_attribute(child_node, "TextColor", slt.get("text_color", "#ffffff"))
        XMLExporter._add_attribute(child_node, "PlayType", slt.get("play_type", "ByCount"))
        XMLExporter._add_attribute(child_node, "ByCount", str(slt.get("by_count", 1)))
        XMLExporter._add_attribute(child_node, "ByTime", str(slt.get("by_time", 300)))
        XMLExporter._add_attribute(child_node, "Speed", str(slt.get("speed", 4)))
        XMLExporter._add_attribute(child_node, "SingleMode", "1")
        XMLExporter._add_attribute(child_node, "PageCount", "1")
        XMLExporter._add_attribute(child_node, "SpeedTimeIndex", "4")
        XMLExporter._add_attribute(child_node, "StrokeColor", "65280")
        XMLExporter._add_attribute(child_node, "UseHollow", "0")
        XMLExporter._add_attribute(child_node, "UseStroke", "0")
        XMLExporter._add_attribute(child_node, "TransBgColor", "1")
        XMLExporter._add_attribute(child_node, "HeadCloseToTail", "1")
        XMLExporter._add_attribute(child_node, "HoldTime", "50")
        XMLExporter._add_attribute(child_node, "DispEffect", str(slt.get("speed", 4)))
        XMLExporter._add_attribute(child_node, "DispTime", "4")
        XMLExporter._add_attribute(child_node, "ClearEffect", "25")
        XMLExporter._add_attribute(child_node, "ClearTime", "4")
        XMLExporter._add_attribute(child_node, "ContentAlign", "132")
        XMLExporter._add_attribute(child_node, "ContentHAlign", "1")
        XMLExporter._add_attribute(child_node, "EditBgColor", "0")
    
    @staticmethod
    def _add_animation_attributes(child_node: ET.Element, props: Dict):
        anim = props.get("animation_text", {})
        XMLExporter._add_attribute(child_node, "HtmlString", anim.get("html_string", ""))
        XMLExporter._add_attribute(child_node, "EffectType", str(anim.get("effect_type", 1)))
        XMLExporter._add_attribute(child_node, "AnimationSpeed", str(anim.get("animation_speed", 5)))
        XMLExporter._add_attribute(child_node, "ContinueSpeed", str(anim.get("continue_speed", 5)))
        XMLExporter._add_attribute(child_node, "ContinueStyle", str(anim.get("continue_style", 0)))
        hold_time = anim.get("hold_time", 5.0)
        XMLExporter._add_attribute(child_node, "HoldTime", str(int(hold_time * 10)))
        XMLExporter._add_attribute(child_node, "Id", "1254")
        XMLExporter._add_attribute(child_node, "PlayTimes", "1")
        XMLExporter._add_attribute(child_node, "CheckColorGradient", "1")
        XMLExporter._add_attribute(child_node, "CheckDazzle", "1")
        XMLExporter._add_attribute(child_node, "CheckNeonBg", "1")
        XMLExporter._add_attribute(child_node, "CheckPictureFills", "0")
        XMLExporter._add_attribute(child_node, "ColorGradient", "0")
        XMLExporter._add_attribute(child_node, "Hollow", "0")
        XMLExporter._add_attribute(child_node, "IntervalSpace", "0")
        XMLExporter._add_attribute(child_node, "NeonEffect", "6")
        XMLExporter._add_attribute(child_node, "NeonElePicPath", ":/images/24-3.bmp")
        XMLExporter._add_attribute(child_node, "NeonElement", "1")
        XMLExporter._add_attribute(child_node, "NeonMuliPicPath", ":/images/24-3.bmp")
        XMLExporter._add_attribute(child_node, "NeonSingleColor", "255")
        XMLExporter._add_attribute(child_node, "NeonSingleColorState", "1")
        XMLExporter._add_attribute(child_node, "NeonStayTime", "10")
        XMLExporter._add_attribute(child_node, "Stroke", "0")
        XMLExporter._add_attribute(child_node, "StrokeColor", "16711680")
        XMLExporter._add_attribute(child_node, "SystemFontName", "MS Shell Dlg 2")
        ET.SubElement(child_node, "List", Name="TextAttribute", Index="-1")
        ET.SubElement(child_node, "List", Name="TextWidth", Index="-1")
        ET.SubElement(child_node, "List", Name="TextHeight", Index="-1")
    
    @staticmethod
    def _add_clock_attributes(child_node: ET.Element, props: Dict):
        clock = props.get("clock", {})
        XMLExporter._add_attribute(child_node, "ClockType", str(clock.get("clock_type", 0)))
        XMLExporter._add_attribute(child_node, "TimeZone", clock.get("time_zone", "-08:00"))
        XMLExporter._add_attribute(child_node, "LcdTimeZone", clock.get("lcd_time_zone", "Asia/Shanghai"))
        XMLExporter._add_attribute(child_node, "UseDaylightSavingTime", "1" if clock.get("use_daylight_saving", False) else "0")
        XMLExporter._add_attribute(child_node, "Id", "1589")
        XMLExporter._add_attribute(child_node, "AdjustType", "0")
    
    @staticmethod
    def _add_timing_attributes(child_node: ET.Element, props: Dict):
        timing = props.get("timing", {})
        XMLExporter._add_attribute(child_node, "TimeMode", str(timing.get("time_mode", 0)))
        XMLExporter._add_attribute(child_node, "TargetTime", timing.get("target_time", ""))
        XMLExporter._add_attribute(child_node, "TimeZone", timing.get("time_zone", "-08:00"))
        XMLExporter._add_attribute(child_node, "TopText", timing.get("top_text", ""))
        XMLExporter._add_attribute(child_node, "ImageId", "1621")
        XMLExporter._add_attribute(child_node, "DisplayMode", "0")
        XMLExporter._add_attribute(child_node, "DispalyStyle", "0")
        XMLExporter._add_attribute(child_node, "TimeType", "0")
        XMLExporter._add_attribute(child_node, "TimeColor", "52685")
        XMLExporter._add_attribute(child_node, "TimeTextColor", "39423")
        XMLExporter._add_attribute(child_node, "TopTextColor", "52685")
        XMLExporter._add_attribute(child_node, "Time_f_name", "MS Shell Dlg 2")
        XMLExporter._add_attribute(child_node, "Time_f_size", "16")
        XMLExporter._add_attribute(child_node, "Time_f_bold", "0")
        XMLExporter._add_attribute(child_node, "Time_f_italic", "0")
        XMLExporter._add_attribute(child_node, "Time_f_undline", "0")
        XMLExporter._add_attribute(child_node, "TimeText_f_name", "MS Shell Dlg 2")
        XMLExporter._add_attribute(child_node, "TimeText_f_size", "16")
        XMLExporter._add_attribute(child_node, "TimeText_f_bold", "0")
        XMLExporter._add_attribute(child_node, "TimeText_f_italic", "0")
        XMLExporter._add_attribute(child_node, "TimeText_f_undline", "0")
        XMLExporter._add_attribute(child_node, "Toptext_f_name", "MS Shell Dlg 2")
        XMLExporter._add_attribute(child_node, "TopText_f_size", "16")
        XMLExporter._add_attribute(child_node, "TopText_f_bold", "0")
        XMLExporter._add_attribute(child_node, "TopText_f_italic", "0")
        XMLExporter._add_attribute(child_node, "TopText_f_undline", "0")
        XMLExporter._add_attribute(child_node, "Year", "1")
        XMLExporter._add_attribute(child_node, "Day", "1")
        XMLExporter._add_attribute(child_node, "Hour", "1")
        XMLExporter._add_attribute(child_node, "Minute", "1")
        XMLExporter._add_attribute(child_node, "SetSecond", "1")
        XMLExporter._add_attribute(child_node, "Millisecond", "0")
        XMLExporter._add_attribute(child_node, "Space", "0")
        XMLExporter._add_attribute(child_node, "AccumulateTime", "1")
        XMLExporter._add_attribute(child_node, "IfReset", "0")
        XMLExporter._add_attribute(child_node, "UnitInterval", "0")
    
    @staticmethod
    def _add_weather_attributes(child_node: ET.Element, props: Dict):
        weather = props.get("weather", {})
        XMLExporter._add_attribute(child_node, "AreaID", weather.get("area_id", "CH101010100"))
        XMLExporter._add_attribute(child_node, "AreaText", weather.get("area_text", "Beijing"))
        XMLExporter._add_attribute(child_node, "DisplayStyle", str(weather.get("display_style", 0)))
        XMLExporter._add_attribute(child_node, "Id", "1477")
    
    @staticmethod
    def _add_sensor_attributes(child_node: ET.Element, props: Dict):
        sensor = props.get("sensor", {})
        XMLExporter._add_attribute(child_node, "TopText", sensor.get("top_text", ""))
        XMLExporter._add_attribute(child_node, "ID", str(sensor.get("sensor_type", 1460)))
        XMLExporter._add_attribute(child_node, "TempUnit", str(sensor.get("temp_unit", 1)))
        XMLExporter._add_attribute(child_node, "HumidityUnit", str(sensor.get("humidity_unit", 0)))
        XMLExporter._add_attribute(child_node, "WindUnit", str(sensor.get("wind_unit", 1)))
        XMLExporter._add_attribute(child_node, "SensorColor", "255")
        XMLExporter._add_attribute(child_node, "SensorFontName", sensor.get("font_name", "MS Shell Dlg 2"))
        XMLExporter._add_attribute(child_node, "SensorFontSize", str(sensor.get("font_size", 16)))
        XMLExporter._add_attribute(child_node, "TopTextColor", "255")
        XMLExporter._add_attribute(child_node, "TopTextFontName", sensor.get("font_name", "MS Shell Dlg 2"))
        XMLExporter._add_attribute(child_node, "TopTextFontSize", str(sensor.get("font_size", 16)))
        XMLExporter._add_attribute(child_node, "AdjustValue", "0")
        XMLExporter._add_attribute(child_node, "GradeName", "0")
        XMLExporter._add_attribute(child_node, "HighPrecision", "0")
        XMLExporter._add_attribute(child_node, "LightIntensity", "0")
        XMLExporter._add_attribute(child_node, "MultiDisplay", "0")
        XMLExporter._add_attribute(child_node, "ShowLevel", "0")
        XMLExporter._add_attribute(child_node, "Space", "0")
        XMLExporter._add_attribute(child_node, "SwapPos", "0")
        XMLExporter._add_attribute(child_node, "WindGrade", "1")
        XMLExporter._add_attribute(child_node, "WindSpeed", "0")
    
    @staticmethod
    def _create_file_list(element: Dict, element_type: str, props: Dict) -> Optional[ET.Element]:
        file_list = ET.Element("List", Name="__FileList__", Index="0")
        
        if element_type == "video":
            video_list = props.get("video_list", [])
            for video_file in video_list:
                ET.SubElement(file_list, "ListItem", FileKey="Video", FileName=video_file)
        
        elif element_type == "image":
            photo_list = props.get("photo_list", props.get("image_list", []))
            for photo_file in photo_list:
                ET.SubElement(file_list, "ListItem", FileKey="Photo", FileName=photo_file)
        
        elif element_type == "text":
            ET.SubElement(file_list, "ListItem", FileKey="Text", FileName="")
        
        elif element_type == "single_line_text":
            ET.SubElement(file_list, "ListItem", FileKey="SingleLineText", FileName="")
        
        if len(file_list) > 0:
            return file_list
        return None

