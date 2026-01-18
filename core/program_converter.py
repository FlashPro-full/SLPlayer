from typing import Dict, List, Optional, Any, Tuple
import uuid
from utils.logger import get_logger
from config.animation_effects import get_animation_index, get_animation_name

logger = get_logger(__name__)

def _generate_uuid() -> str:
    return uuid.uuid4().hex[:12].upper()

def program_to_sdk(program: Dict) -> Dict:
    program_name = program.get("name", "Program1")
    program_uuid = program.get("id", _generate_uuid())
    if program_uuid.startswith("program_"):
        program_uuid = _generate_uuid()
    
    elements = program.get("elements", [])
    areas = []
    
    for element in elements:
        area = _element_to_sdk_area(element)
        if area:
            areas.append(area)
    
    result = {
        "name": program_name,
        "type": "normal",
        "uuid": program_uuid,
        "area": areas
    }
    
    play_control = _convert_play_control_to_sdk(program.get("play_control", {}), program.get("play_mode", {}), program.get("duration", 0.0))
    if play_control:
        result["playControl"] = play_control
    
    properties = program.get("properties", {})
    if properties:
        result["_properties"] = properties
    
    return result

def _element_to_sdk_area(element: Dict) -> Optional[Dict]:
    element_type = element.get("type", "")
    x = element.get("x", 0)
    y = element.get("y", 0)
    width = element.get("width", 200)
    height = element.get("height", 100)
    properties = element.get("properties", {})
    
    item = None
    if element_type == "text":
        item = _text_element_to_sdk_item(properties, multi_line=True)
    elif element_type == "singleline_text":
        item = _text_element_to_sdk_item(properties, multi_line=False)
    elif element_type in ["photo", "image"]:
        item = _image_element_to_sdk_item(properties)
    elif element_type == "video":
        item = _video_element_to_sdk_item(properties)
    elif element_type == "clock":
        item = _clock_element_to_sdk_item(properties)
    else:
        return None
    
    if not item:
        return None
    
    area = {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "item": [item],
        "_metadata": {
            "id": element.get("id"),
            "type": element_type,
            "name": element.get("name", ""),
            "properties": properties.copy()
        }
    }
    
    border = properties.get("border", {})
    if border and border.get("enabled", False):
        border_effect = border.get("effect", "rotate")
        border_type = 0
        if border_effect == "rotate":
            border_type = 0
        area["border"] = {
            "type": border_type,
            "speed": border.get("speed", 5),
            "effect": border_effect
        }
    
    return area

def _text_element_to_sdk_item(properties: Dict, multi_line: bool = True) -> Optional[Dict]:
    text_props = properties.get("text", "")
    if isinstance(text_props, dict):
        text = text_props.get("content", "")
        format_props = text_props.get("format", {})
        font_family = format_props.get("font_family") or properties.get("font_family", "Arial")
        font_size = format_props.get("font_size") or properties.get("font_size", 14)
        color = format_props.get("font_color") or format_props.get("color") or properties.get("color", "#FFFFFF")
        bold = format_props.get("bold") if format_props.get("bold") is not None else properties.get("bold", False)
        italic = format_props.get("italic") if format_props.get("italic") is not None else properties.get("italic", False)
        underline = format_props.get("underline") if format_props.get("underline") is not None else properties.get("underline", False)
        multi_line = text_props.get("multiLine", multi_line) if multi_line else False
    else:
        text = str(text_props) if text_props else ""
        font_family = properties.get("font_family", "Arial")
        font_size = properties.get("font_size", 14)
        color = properties.get("color", "#FFFFFF")
        bold = properties.get("bold", False)
        italic = properties.get("italic", False)
        underline = properties.get("underline", False)
        multi_line = properties.get("multiLine", multi_line) if multi_line else False
    
    animation = properties.get("animation", {})
    if isinstance(animation, dict):
        animation_name = animation.get("entrance", "Direct display")
        animation_speed = animation.get("entrance_speed", "1 fast")
        hold_time = animation.get("hold_time", 5.0)
    else:
        animation_name = str(animation) if animation else "Direct display"
        animation_speed = properties.get("animation_speed", 1.0)
        hold_time = properties.get("duration", 5.0)
    
    effect_type = get_animation_index(animation_name)
    
    speed_value = 5
    if isinstance(animation_speed, str):
        if "fast" in animation_speed.lower():
            speed_value = 1
        elif "slow" in animation_speed.lower():
            speed_value = 10
        else:
            try:
                speed_value = int(animation_speed.split()[0])
            except:
                speed_value = 5
    elif isinstance(animation_speed, (int, float)):
        speed_value = int(animation_speed)
    
    hold_ms = int(hold_time * 1000) if isinstance(hold_time, float) else int(hold_time)
    
    background_color = format_props.get("text_bg_color") or properties.get("background_color", "")
    
    item = {
        "type": "text",
        "string": text,
        "multiLine": multi_line,
        "font": {
            "name": font_family,
            "size": font_size,
            "underline": underline,
            "bold": bold,
            "italic": italic,
            "color": color
        },
        "effect": {
            "type": effect_type,
            "speed": speed_value,
            "hold": hold_ms
        }
    }
    
    if background_color:
        item["background"] = background_color
    
    return item

def _image_element_to_sdk_item(properties: Dict) -> Optional[Dict]:
    photo_props = properties.get("photo", {})
    photo_list = properties.get("photo_list", properties.get("image_list", []))
    active_photo_index = properties.get("active_photo_index", 0)
    
    if isinstance(photo_props, dict):
        file_path = photo_props.get("file_path", "") or properties.get("file_path", "")
        fit_mode = photo_props.get("fit_mode") or properties.get("fit_mode", "stretch")
        file_size = photo_props.get("fileSize") or properties.get("fileSize")
        file_md5 = photo_props.get("fileMd5") or properties.get("fileMd5")
        duration = photo_props.get("duration") or properties.get("duration", 5000)
    else:
        file_path = properties.get("file_path", "")
        fit_mode = properties.get("fit_mode", "stretch")
        file_size = properties.get("fileSize")
        file_md5 = properties.get("fileMd5")
        duration = properties.get("duration", 5000)
    
    if photo_list and isinstance(photo_list, list) and len(photo_list) > 0:
        if 0 <= active_photo_index < len(photo_list):
            active_photo = photo_list[active_photo_index]
            if isinstance(active_photo, dict):
                file_path = active_photo.get("path", file_path)
        elif len(photo_list) > 0:
            first_photo = photo_list[0]
            if isinstance(first_photo, dict):
                file_path = first_photo.get("path", file_path)
    
    animation = properties.get("animation", {})
    if isinstance(animation, dict):
        animation_name = animation.get("entrance", "Direct display")
        animation_speed = animation.get("entrance_speed", "1 fast")
        hold_time = animation.get("hold_time", duration / 1000.0 if duration > 100 else duration)
    else:
        animation_name = str(animation) if animation else "Direct display"
        animation_speed = properties.get("animation_speed", 1.0)
        hold_time = duration / 1000.0 if duration > 100 else duration
    
    effect_type = get_animation_index(animation_name)
    
    speed_value = 5
    if isinstance(animation_speed, str):
        if "fast" in animation_speed.lower():
            speed_value = 1
        elif "slow" in animation_speed.lower():
            speed_value = 10
        else:
            try:
                speed_value = int(animation_speed.split()[0])
            except:
                speed_value = 5
    elif isinstance(animation_speed, (int, float)):
        speed_value = int(animation_speed)
    
    hold_ms = int(hold_time * 1000) if isinstance(hold_time, float) else int(hold_time)
    
    fit_map = {
        "fill": "fill",
        "center": "center",
        "stretch": "stretch",
        "tile": "tile"
    }
    fit_value = fit_map.get(fit_mode.lower(), "stretch")
    
    item = {
        "type": "image",
        "file": file_path,
        "fit": fit_value,
        "effect": {
            "type": effect_type,
            "speed": speed_value,
            "hold": hold_ms
        }
    }
    
    if file_size is not None:
        item["fileSize"] = file_size
    if file_md5:
        item["fileMd5"] = file_md5
    
    return item

def _video_element_to_sdk_item(properties: Dict) -> Optional[Dict]:
    video_props = properties.get("video", {})
    video_list = properties.get("video_list", [])
    active_video_index = properties.get("active_video_index", 0)
    
    if isinstance(video_props, dict):
        file_path = video_props.get("file_path", "") or properties.get("file_path", "")
        file_size = video_props.get("fileSize") or properties.get("fileSize")
        file_md5 = video_props.get("fileMd5") or properties.get("fileMd5")
    else:
        file_path = properties.get("file_path", "")
        file_size = properties.get("fileSize")
        file_md5 = properties.get("fileMd5")
    
    if video_list and isinstance(video_list, list) and len(video_list) > 0:
        if 0 <= active_video_index < len(video_list):
            active_video = video_list[active_video_index]
            if isinstance(active_video, dict):
                file_path = active_video.get("path", file_path)
        elif len(video_list) > 0:
            first_video = video_list[0]
            if isinstance(first_video, dict):
                file_path = first_video.get("path", file_path)
    
    item = {
        "type": "video",
        "file": file_path
    }
    
    if file_size is not None:
        item["fileSize"] = file_size
    if file_md5:
        item["fileMd5"] = file_md5
    
    return item

def _clock_element_to_sdk_item(properties: Dict) -> Optional[Dict]:
    clock_props = properties.get("clock", {})
    if isinstance(clock_props, dict):
        font_family = clock_props.get("font_family") or properties.get("font_family", "Arial")
        font_size = clock_props.get("font_size") or properties.get("font_size", 8)
        color = clock_props.get("color") or properties.get("color", "#000000")
        show_date = clock_props.get("show_date", True)
        date_format = clock_props.get("date_format", "YYYY-MM-DD")
        time_format = clock_props.get("time_format", "HH:MM:SS")
        week_format = clock_props.get("week_format", "Full Name")
        timezone = clock_props.get("timezone", "")
        time_offset = clock_props.get("timeOffset", "")
        title_string = clock_props.get("title_string", "")
        clock_type = clock_props.get("clock_type") or properties.get("clock_type", "digitalClock")
    else:
        font_family = properties.get("font_family", "Arial")
        font_size = properties.get("font_size", 8)
        color = properties.get("color", "#FFFFFF")
        show_date = properties.get("show_date", True)
        date_format = properties.get("date_format", "YYYY-MM-DD")
        time_format = properties.get("time_format", "HH:MM:SS")
        week_format = properties.get("week_format", "Full Name")
        timezone = properties.get("timezone", "")
        time_offset = properties.get("timeOffset", "")
        title_string = properties.get("title_string", "")
        clock_type = properties.get("clock_type", "digitalClock")
    
    date_format_map = {
        "YYYY/MM/DD": "0",
        "MM/DD/YYYY": "1",
        "DD/MM/YYYY": "2",
        "Jan DD, YYYY": "3",
        "DD Jan, YYYY": "4",
        "YYYY-MM-DD-dd": "5",
        "MM-DD-dd": "6"
    }
    date_format_code = date_format_map.get(date_format, "0" if show_date else "0")
    
    week_format_map = {
        "Full Name": "0",
        "Monday": "1",
        "Mon": "2"
    }
    week_format_code = week_format_map.get(week_format, "0")
    
    time_format_map = {
        "HH:MM:SS": "0",
        "HH:MM": "1",
        "HH hour, MM minute, SS second": "2",
        "HH hour, MM minute": "3"
    }
    time_format_code = time_format_map.get(time_format, "0")
    
    item_type = "dialClock" if clock_type == "dial" else "digitalClock"
    
    item = {
        "type": item_type,
        "timezone": timezone,
        "timeOffset": time_offset,
        "font": {
            "name": font_family,
            "size": font_size,
            "underline": False,
            "bold": False,
            "italic": False,
            "color": color
        },
        "title": {
            "string": title_string,
            "color": color
        },
        "date": {
            "format": date_format_code,
            "color": color
        },
        "week": {
            "format": week_format_code,
            "color": color
        },
        "time": {
            "format": time_format_code,
            "color": color
        }
    }
    
    return item

def _html_element_to_sdk_item(properties: Dict) -> Optional[Dict]:
    html_props = properties.get("html", {})
    if isinstance(html_props, dict):
        file_path = html_props.get("url", "") or properties.get("file_path", "")
    else:
        file_path = properties.get("file_path", "")
    
    item = {
        "type": "html",
        "file": file_path
    }
    
    return item

def _hdmi_element_to_sdk_item(properties: Dict) -> Optional[Dict]:
    hdmi_props = properties.get("hdmi", {})
    if isinstance(hdmi_props, dict):
        source = hdmi_props.get("source") or properties.get("hdmi_source", 0)
    else:
        source = properties.get("hdmi_source", 0)
    
    item = {
        "type": "hdmi",
        "source": source
    }
    
    return item

def _sensor_element_to_sdk_item(properties: Dict) -> Optional[Dict]:
    sensor_props = properties.get("sensor", {})
    if isinstance(sensor_props, dict):
        sensor_type = sensor_props.get("sensor_type") or properties.get("sensor_type", 0)
        font_family = sensor_props.get("font_family") or properties.get("font_family", "Arial")
        font_size = sensor_props.get("font_size") or properties.get("font_size", 14)
        color = sensor_props.get("color") or properties.get("color", "#000000")
    else:
        sensor_type = properties.get("sensor_type", 0)
        font_family = properties.get("font_family", "Arial")
        font_size = properties.get("font_size", 14)
        color = properties.get("color", "#FFFFFF")
    
    item = {
        "type": "dynamic",
        "sensor_type": sensor_type,
        "font": {
            "name": font_family,
            "size": font_size,
            "underline": False,
            "bold": False,
            "italic": False,
            "color": color
        }
    }
    
    return item

def _weather_element_to_sdk_item(properties: Dict) -> Optional[Dict]:
    return _text_element_to_sdk_item(properties)

def _timing_element_to_sdk_item(properties: Dict) -> Optional[Dict]:
    return _text_element_to_sdk_item(properties)

def sdk_to_program(sdk_program: Dict) -> Dict:
    program_name = sdk_program.get("name", "Program1")
    program_uuid = sdk_program.get("uuid", _generate_uuid())
    program_id = f"program_{program_uuid.lower()}"
    
    areas = sdk_program.get("area", [])
    elements = []
    
    for area in areas:
        metadata = area.get("_metadata", {})
        area_items = area.get("item", [])
        for item in area_items:
            element = _sdk_item_to_element(item, area)
            if element:
                if metadata:
                    element_id = metadata.get("id")
                    if element_id:
                        element["id"] = element_id
                    element_name = metadata.get("name")
                    if element_name:
                        element["name"] = element_name
                elements.append(element)
    
    play_control_sdk = sdk_program.get("playControl", {})
    play_control, play_mode, duration = _convert_play_control_from_sdk(play_control_sdk)
    
    properties = sdk_program.get("_properties", {})
    if not properties:
        properties = {
            "checked": True,
            "frame": {"enabled": False, "style": "---"},
            "background_music": {"enabled": False, "file": "", "volume": 0}
        }
    else:
        if "checked" not in properties:
            properties["checked"] = True
        if "frame" not in properties:
            properties["frame"] = {"enabled": False, "style": "---"}
        if "background_music" not in properties:
            properties["background_music"] = {"enabled": False, "file": "", "volume": 0}
        if "content_upload_enabled" not in properties:
            properties["content_upload_enabled"] = True
    
    return {
        "id": program_id,
        "name": program_name,
        "width": 1920,
        "height": 1080,
        "elements": elements,
        "properties": properties,
        "play_mode": play_mode,
        "play_control": play_control,
        "duration": duration
    }

def _sdk_item_to_element(item: Dict, area: Dict) -> Optional[Dict]:
    item_type = item.get("type", "")
    
    if item_type == "text":
        multi_line = item.get("multiLine", True)
        if multi_line:
            return _sdk_text_item_to_element(item, area, "text")
        else:
            return _sdk_text_item_to_element(item, area, "singleline_text")
    elif item_type == "image":
        return _sdk_image_item_to_element(item, area)
    elif item_type == "video":
        return _sdk_video_item_to_element(item, area)
    elif item_type == "digitalClock":
        return _sdk_clock_item_to_element(item, area, "digitalClock")
    elif item_type == "dialClock":
        return _sdk_clock_item_to_element(item, area, "dialClock")
    
    return None

def _sdk_text_item_to_element(item: Dict, area: Dict, element_type: str = "text") -> Dict:
    text_string = item.get("string", "")
    multi_line = item.get("multiLine", False)
    font = item.get("font", {})
    effect = item.get("effect", {})
    background_color = item.get("background", "")
    
    font_name = font.get("name", "Arial")
    font_size = font.get("size", 14)
    font_color = font.get("color", "#FFFFFF")
    bold = font.get("bold", False)
    italic = font.get("italic", False)
    underline = font.get("underline", False)
    
    effect_type = effect.get("type", 0)
    effect_speed = effect.get("speed", 5)
    effect_hold = effect.get("hold", 5000)
    
    animation_name = get_animation_name(effect_type)
    
    speed_str = f"{effect_speed} fast" if effect_speed <= 3 else f"{effect_speed} slow" if effect_speed >= 8 else f"{effect_speed} medium"
    hold_time = effect_hold / 1000.0 if effect_hold > 100 else effect_hold
    
    border = area.get("border", {})
    border_enabled = bool(border)
    
    metadata = area.get("_metadata", {})
    metadata_props = metadata.get("properties", {}) if metadata else {}
    
    if element_type == "singleline_text":
        multi_line = False
    
    if metadata_props:
        text_props_meta = metadata_props.get("text", {})
        if isinstance(text_props_meta, dict):
            text_string = text_props_meta.get("content", text_string)
            if element_type == "singleline_text":
                multi_line = False
            else:
                multi_line = text_props_meta.get("multiLine", multi_line)
            format_meta = text_props_meta.get("format", {})
            if format_meta:
                font_name = format_meta.get("font_family", font_name)
                font_size = format_meta.get("font_size", font_size)
                font_color = format_meta.get("font_color", format_meta.get("color", font_color))
                bold = format_meta.get("bold", bold)
                italic = format_meta.get("italic", italic)
                underline = format_meta.get("underline", underline)
        
        animation_meta = metadata_props.get("animation", {})
        if isinstance(animation_meta, dict) and animation_meta:
            animation_name = animation_meta.get("entrance", animation_name)
            speed_str = animation_meta.get("entrance_speed", speed_str)
            hold_time = animation_meta.get("hold_time", hold_time)
    
    element = {
        "id": _generate_uuid(),
        "type": element_type,
        "x": area.get("x", 0),
        "y": area.get("y", 0),
        "width": area.get("width", 200),
        "height": area.get("height", 100),
        "properties": {}
    }
    
    if metadata_props:
        element["properties"].update(metadata_props)
    
    element["properties"]["text"] = {
        "content": text_string,
        "multiLine": multi_line,
        "format": {
            "font_family": font_name,
            "font_size": font_size,
            "font_color": font_color,
            "bold": bold,
            "italic": italic,
            "underline": underline
        }
    }
    element["properties"]["font_family"] = font_name
    element["properties"]["font_size"] = font_size
    element["properties"]["color"] = font_color
    element["properties"]["bold"] = bold
    element["properties"]["italic"] = italic
    element["properties"]["underline"] = underline
    element["properties"]["multiLine"] = multi_line
    element["properties"]["animation"] = {
        "entrance": animation_name,
        "exit": animation_name,
        "entrance_speed": speed_str,
        "exit_speed": speed_str,
        "hold_time": hold_time
    }
    element["properties"]["animation_speed"] = effect_speed
    element["properties"]["duration"] = hold_time
    
    if background_color:
        element["properties"]["text"]["format"]["text_bg_color"] = background_color
        element["properties"]["background_color"] = background_color
    
    if border_enabled:
        element["properties"]["border"] = {
            "enabled": True,
            "type": border.get("type", 0),
            "speed": border.get("speed", 5),
            "effect": border.get("effect", "rotate")
        }
    
    return element

def _sdk_image_item_to_element(item: Dict, area: Dict) -> Dict:
    file_path = item.get("file", "")
    fit_mode = item.get("fit", "stretch")
    file_size = item.get("fileSize")
    file_md5 = item.get("fileMd5")
    effect = item.get("effect", {})
    
    effect_type = effect.get("type", 0)
    effect_speed = effect.get("speed", 5)
    effect_hold = effect.get("hold", 5000)
    
    animation_name = get_animation_name(effect_type)
    
    speed_str = f"{effect_speed} fast" if effect_speed <= 3 else f"{effect_speed} slow" if effect_speed >= 8 else f"{effect_speed} medium"
    hold_time = effect_hold / 1000.0 if effect_hold > 100 else effect_hold
    
    metadata = area.get("_metadata", {})
    metadata_props = metadata.get("properties", {}) if metadata else {}
    
    photo_list = metadata_props.get("photo_list", metadata_props.get("image_list", []))
    active_photo_index = metadata_props.get("active_photo_index", 0)
    
    if not photo_list and file_path:
        photo_list = [{"path": file_path}]
    
    animation_from_metadata = metadata_props.get("animation", {})
    if isinstance(animation_from_metadata, dict) and animation_from_metadata:
        animation_name = animation_from_metadata.get("entrance", animation_name)
        speed_str = animation_from_metadata.get("entrance_speed", speed_str)
        hold_time = animation_from_metadata.get("hold_time", hold_time)
        exit_animation = animation_from_metadata.get("exit", animation_name)
        exit_speed = animation_from_metadata.get("exit_speed", speed_str)
    else:
        exit_animation = animation_name
        exit_speed = speed_str
    
    fit_mode_from_metadata = metadata_props.get("fit_mode", fit_mode)
    
    element = {
        "id": _generate_uuid(),
        "type": "photo",
        "x": area.get("x", 0),
        "y": area.get("y", 0),
        "width": area.get("width", 200),
        "height": area.get("height", 100),
        "properties": {}
    }
    
    element["properties"].update(metadata_props)
    
    element["properties"]["photo"] = metadata_props.get("photo", {})
    if not element["properties"]["photo"]:
        element["properties"]["photo"] = {}
    element["properties"]["photo"]["file_path"] = file_path
    element["properties"]["photo"]["fit_mode"] = fit_mode_from_metadata
    
    element["properties"]["file_path"] = file_path
    element["properties"]["fit_mode"] = fit_mode_from_metadata
    
    element["properties"]["animation"] = {
        "entrance": animation_name,
        "exit": exit_animation,
        "entrance_speed": speed_str,
        "exit_speed": exit_speed,
        "hold_time": hold_time
    }
    element["properties"]["animation_speed"] = effect_speed
    element["properties"]["duration"] = hold_time
    
    if photo_list:
        element["properties"]["photo_list"] = photo_list
        element["properties"]["image_list"] = photo_list
        if 0 <= active_photo_index < len(photo_list):
            element["properties"]["active_photo_index"] = active_photo_index
    
    if file_size is not None:
        element["properties"]["fileSize"] = file_size
        if "fileSize" not in element["properties"]["photo"]:
            element["properties"]["photo"]["fileSize"] = file_size
    if file_md5:
        element["properties"]["fileMd5"] = file_md5
        if "fileMd5" not in element["properties"]["photo"]:
            element["properties"]["photo"]["fileMd5"] = file_md5
    
    return element

def _sdk_video_item_to_element(item: Dict, area: Dict) -> Dict:
    file_path = item.get("file", "")
    file_size = item.get("fileSize")
    file_md5 = item.get("fileMd5")
    
    metadata = area.get("_metadata", {})
    metadata_props = metadata.get("properties", {}) if metadata else {}
    
    video_list = metadata_props.get("video_list", [])
    active_video_index = metadata_props.get("active_video_index", 0)
    
    if not video_list and file_path:
        video_list = [{"path": file_path}]
    
    element = {
        "id": _generate_uuid(),
        "type": "video",
        "x": area.get("x", 0),
        "y": area.get("y", 0),
        "width": area.get("width", 200),
        "height": area.get("height", 100),
        "properties": {}
    }
    
    element["properties"].update(metadata_props)
    
    element["properties"]["video"] = metadata_props.get("video", {})
    if not element["properties"]["video"]:
        element["properties"]["video"] = {}
    element["properties"]["video"]["file_path"] = file_path
    
    element["properties"]["file_path"] = file_path
    element["properties"]["video_list"] = video_list
    
    if video_list and 0 <= active_video_index < len(video_list):
        element["properties"]["active_video_index"] = active_video_index
    
    if file_size is not None:
        element["properties"]["fileSize"] = file_size
        element["properties"]["video"]["fileSize"] = file_size
    if file_md5:
        element["properties"]["fileMd5"] = file_md5
        element["properties"]["video"]["fileMd5"] = file_md5
    
    return element

def _sdk_clock_item_to_element(item: Dict, area: Dict, clock_type: str) -> Dict:
    font = item.get("font", {})
    title = item.get("title", {})
    date = item.get("date", {})
    week = item.get("week", {})
    time = item.get("time", {})
    
    font_name = font.get("name", "Arial")
    font_size = font.get("size", 8)
    font_color = font.get("color", "#FFFFFF")
    
    timezone = item.get("timezone", "")
    time_offset = item.get("timeOffset", "")
    title_string = title.get("string", "")
    
    date_format_code = str(date.get("format", "0"))
    week_format_code = str(week.get("format", "0"))
    time_format_code = str(time.get("format", "0"))
    
    date_format_map = {
        "0": "YYYY/MM/DD",
        "1": "MM/DD/YYYY",
        "2": "DD/MM/YYYY",
        "3": "Jan DD, YYYY",
        "4": "DD Jan, YYYY",
        "5": "YYYY-MM-DD-dd",
        "6": "MM-DD-dd"
    }
    date_format = date_format_map.get(date_format_code, "YYYY-MM-DD")
    show_date = date_format_code != "0"
    
    week_format_map = {
        "0": "Full Name",
        "1": "Monday",
        "2": "Mon"
    }
    week_format = week_format_map.get(week_format_code, "Full Name")
    
    time_format_map = {
        "0": "HH:MM:SS",
        "1": "HH:MM",
        "2": "HH hour, MM minute, SS second",
        "3": "HH hour, MM minute"
    }
    time_format = time_format_map.get(time_format_code, "HH:MM:SS")
    
    element = {
        "id": _generate_uuid(),
        "type": "clock",
        "x": area.get("x", 0),
        "y": area.get("y", 0),
        "width": area.get("width", 200),
        "height": area.get("height", 100),
        "properties": {
            "clock": {
                "show_date": show_date,
                "font_family": font_name,
                "font_size": font_size,
                "color": font_color,
                "date_format": date_format,
                "time_format": time_format,
                "week_format": week_format,
                "timezone": timezone,
                "timeOffset": time_offset,
                "title_string": title_string,
                "clock_type": "dial" if clock_type == "dialClock" else "digitalClock"
            },
            "font_family": font_name,
            "font_size": font_size,
            "color": font_color,
            "show_date": show_date,
            "date_format": date_format,
            "time_format": time_format,
            "week_format": week_format,
            "timezone": timezone,
            "timeOffset": time_offset,
            "title_string": title_string,
            "clock_type": "dial" if clock_type == "dialClock" else "digitalClock"
        }
    }
    
    return element

def _sdk_html_item_to_element(item: Dict, area: Dict) -> Dict:
    file_path = item.get("file", "")
    
    element = {
        "id": _generate_uuid(),
        "type": "html",
        "x": area.get("x", 0),
        "y": area.get("y", 0),
        "width": area.get("width", 200),
        "height": area.get("height", 100),
        "properties": {
            "html": {
                "url": file_path,
                "time_refresh_enabled": False,
                "time_refresh_value": 15.0
            },
            "file_path": file_path
        }
    }
    
    return element

def _sdk_hdmi_item_to_element(item: Dict, area: Dict) -> Dict:
    source = item.get("source", 0)
    
    element = {
        "id": _generate_uuid(),
        "type": "hdmi",
        "x": area.get("x", 0),
        "y": area.get("y", 0),
        "width": area.get("width", 200),
        "height": area.get("height", 100),
        "properties": {
            "hdmi": {
                "display_mode": "Full Screen Zoom"
            },
            "hdmi_source": source
        }
    }
    
    return element

def _sdk_sensor_item_to_element(item: Dict, area: Dict) -> Dict:
    sensor_type = item.get("sensor_type", 0)
    font = item.get("font", {})
    
    font_name = font.get("name", "Arial")
    font_size = font.get("size", 14)
    font_color = font.get("color", "#FFFFFF")
    
    element = {
        "id": _generate_uuid(),
        "type": "sensor",
        "x": area.get("x", 0),
        "y": area.get("y", 0),
        "width": area.get("width", 200),
        "height": area.get("height", 100),
        "properties": {
            "sensor": {
                "sensor_type": sensor_type,
                "font_family": font_name,
                "font_size": font_size,
                "color": font_color,
                "unit": "°C"
            },
            "font_family": font_name,
            "font_size": font_size,
            "color": font_color,
            "sensor_type": sensor_type
        }
    }
    
    return element

def _convert_play_control_to_sdk(play_control: Dict, play_mode: Dict, duration: float) -> Optional[Dict]:
    result = {}
    
    duration_str = play_mode.get("fixed_length", "0:00:30")
    if duration_str:
        result["duration"] = duration_str
    
    specified_time = play_control.get("specified_time", {})
    if specified_time.get("enabled", False):
        time_ranges = specified_time.get("ranges", [])
        if not time_ranges:
            start_time = specified_time.get("start_time", "00:00:00")
            end_time = specified_time.get("end_time", "23:59:59")
            if start_time and end_time:
                time_ranges = [{"start": start_time, "end": end_time}]
        
        if time_ranges:
            if len(time_ranges) == 1:
                result["time"] = time_ranges[0]
            else:
                result["time"] = time_ranges
    
    specify_week = play_control.get("specify_week", {})
    if specify_week.get("enabled", False):
        days = specify_week.get("days", [])
        if days:
            day_names = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]
            selected_days = [day_names[d] for d in sorted(days) if 0 <= d < 7]
            if selected_days:
                result["week"] = {"enable": ", ".join(selected_days)}
    
    specify_date = play_control.get("specify_date", {})
    if specify_date.get("enabled", False):
        date_ranges = specify_date.get("ranges", [])
        if not date_ranges:
            start_date = specify_date.get("start_date", "")
            end_date = specify_date.get("end_date", "")
            if start_date and end_date:
                date_ranges = [{"start": start_date, "end": end_date}]
        
        if date_ranges:
            result["date"] = date_ranges
    
    return result if result else None

def _convert_play_control_from_sdk(play_control_sdk: Dict) -> Tuple[Dict, Dict, float]:
    play_control = {
        "specified_time": {"enabled": False, "time": ""},
        "specify_week": {"enabled": False, "days": []},
        "specify_date": {"enabled": False, "date": ""}
    }
    
    play_mode = {
        "mode": "play_times",
        "play_times": 1,
        "fixed_length": "0:00:30"
    }
    
    duration = 0.0
    
    if play_control_sdk.get("duration"):
        duration_str = play_control_sdk["duration"]
        play_mode["fixed_length"] = duration_str
    
    if "time" in play_control_sdk:
        time_data = play_control_sdk["time"]
        if isinstance(time_data, dict):
            time_ranges = [time_data]
        elif isinstance(time_data, list):
            time_ranges = time_data
        else:
            time_ranges = []
        
        if time_ranges:
            play_control["specified_time"] = {
                "enabled": True,
                "ranges": time_ranges
            }
    
    if "week" in play_control_sdk:
        week_data = play_control_sdk["week"]
        if isinstance(week_data, dict):
            enable_str = week_data.get("enable", "")
            if enable_str:
                day_names = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]
                day_name_to_index = {name: i for i, name in enumerate(day_names)}
                days = []
                for day_name in enable_str.split(","):
                    day_name = day_name.strip()
                    if day_name in day_name_to_index:
                        days.append(day_name_to_index[day_name])
                
                if days:
                    play_control["specify_week"] = {
                        "enabled": True,
                        "days": sorted(days)
                    }
    
    if "date" in play_control_sdk:
        date_data = play_control_sdk["date"]
        if isinstance(date_data, list) and date_data:
            play_control["specify_date"] = {
                "enabled": True,
                "ranges": date_data
            }
    
    return play_control, play_mode, duration


class ProgramConverter:
    
    @staticmethod
    def soo_to_sdk(program_dict: Dict, controller_type: str) -> Dict:
        if controller_type.lower() == "novastar":
            return ProgramConverter._soo_to_novastar(program_dict)
        elif controller_type.lower() == "huidu":
            return ProgramConverter._soo_to_huidu(program_dict)
        else:
            logger.warning(f"Unknown controller type: {controller_type}")
            return program_dict
    
    @staticmethod
    def sdk_to_soo(sdk_program_dict: Dict, controller_type: str) -> Dict:
        if controller_type.lower() == "novastar":
            return ProgramConverter._novastar_to_soo(sdk_program_dict)
        elif controller_type.lower() == "huidu":
            return ProgramConverter._huidu_to_soo(sdk_program_dict)
        else:
            logger.warning(f"Unknown controller type: {controller_type}")
            return sdk_program_dict
    
    @staticmethod
    def _soo_to_novastar(program_dict: Dict) -> Dict:
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
        if "area" in program_dict:
            return program_dict
        
        return program_to_sdk(program_dict)
    
    @staticmethod
    def _soo_element_to_huidu_area(element: Dict) -> Optional[Dict]:
        element_type = element.get("type", "")
        x = element.get("x", 0)
        y = element.get("y", 0)
        width = element.get("width", 200)
        height = element.get("height", 100)
        properties = element.get("properties", {})
        
        item = ProgramConverter._soo_element_to_huidu_item(element_type, properties, x, y, width, height)
        if not item:
            return None
        
        area = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "item": [item]
        }
        
        border = properties.get("border", {})
        if border and border.get("enabled", False):
            area["border"] = {
                "type": border.get("type", 0),
                "speed": border.get("speed", 5),
                "effect": border.get("effect", "rotate")
            }
        
        return area
    
    @staticmethod
    def _soo_element_to_huidu_item(element_type: str, properties: Dict, x: int, y: int, width: int, height: int) -> Optional[Dict]:
        if element_type == "text":
            text_props = properties.get("text", {})
            if isinstance(text_props, dict):
                multi_line = text_props.get("multiLine", True)
            else:
                multi_line = properties.get("multiLine", True)
            if multi_line:
                return ProgramConverter._soo_text_to_huidu_item(properties, multi_line=True)
            else:
                return ProgramConverter._soo_text_to_huidu_item(properties, multi_line=False)
        elif element_type == "singleline_text":
            return ProgramConverter._soo_text_to_huidu_item(properties, multi_line=False)
        elif element_type in ["photo", "image"]:
            return ProgramConverter._soo_image_to_huidu_item(properties)
        elif element_type == "video":
            return ProgramConverter._soo_video_to_huidu_item(properties)
        elif element_type == "clock":
            return ProgramConverter._soo_clock_to_huidu_item(properties)
        return None
    
    @staticmethod
    def _soo_text_to_huidu_item(properties: Dict, multi_line: bool = True) -> Dict:
        item = _text_element_to_sdk_item(properties, multi_line=multi_line)
        if not item:
            text_props = properties.get("text", "")
            if isinstance(text_props, dict):
                text = text_props.get("content", "")
            else:
                text = str(text_props) if text_props else ""
            font_family = properties.get("font_family", "Arial")
            font_size = properties.get("font_size", 14)
            color = properties.get("color", "#FFFFFF")
            duration = properties.get("duration", 5000)
            item = {
                "type": "text",
                "string": text,
                "multiLine": multi_line,
                "font": {
                    "name": font_family,
                    "size": font_size,
                    "underline": False,
                    "bold": False,
                    "italic": False,
                    "color": color
                },
                "effect": {
                    "type": 0,
                    "speed": 5,
                    "hold": duration
                }
            }
        return item
    
    @staticmethod
    def _soo_image_to_huidu_item(properties: Dict) -> Dict:
        file_path = properties.get("file_path", "")
        duration = properties.get("duration", 5000)
        
        item = {
            "type": "image",
            "file": file_path,
            "fit": "stretch",
            "effect": {
                "type": 0,
                "speed": 5,
                "hold": duration
            }
        }
        
        if "fileSize" in properties:
            item["fileSize"] = properties["fileSize"]
        if "fileMd5" in properties:
            item["fileMd5"] = properties["fileMd5"]
        
        return item
    
    @staticmethod
    def _soo_video_to_huidu_item(properties: Dict) -> Dict:
        file_path = properties.get("file_path", "")
        
        item = {
            "type": "video",
            "file": file_path,
            "aspectRatio": False
        }
        
        if "fileSize" in properties:
            item["fileSize"] = properties["fileSize"]
        if "fileMd5" in properties:
            item["fileMd5"] = properties["fileMd5"]
        
        return item
    
    @staticmethod
    def _soo_clock_to_huidu_item(properties: Dict) -> Dict:
        font_family = properties.get("font_family", "Arial")
        font_size = properties.get("font_size", 8)
        color = properties.get("color", "#FFFFFF")
        show_date = properties.get("show_date", True)
        
        clock_type = properties.get("clock_type", "digitalClock")
        if clock_type == "dial":
            item_type = "dialClock"
        else:
            item_type = "digitalClock"
        
        item = {
            "type": item_type,
            "timezone": "",
            "timeOffset": "",
            "font": {
                "name": font_family,
                "size": font_size,
                "underline": False,
                "bold": False,
                "italic": False,
                "color": color
            },
            "title": {
                "string": "0",
                "color": color
            },
            "date": {
                "format": "6" if show_date else "0",
                "color": color
            },
            "week": {
                "format": "0",
                "color": color
            },
            "time": {
                "format": "0",
                "color": color
            }
        }
        return item
    
    @staticmethod
    def _soo_timing_to_huidu_item(properties: Dict) -> Dict:
        font_family = properties.get("font_family", "Arial")
        font_size = properties.get("font_size", 14)
        color = properties.get("color", "#FFFFFF")
        count_type = properties.get("count_type", 0)
        count_value = properties.get("count_value", 0)
        
        item = {
            "type": "text",
            "string": f"Count: {count_value}",
            "multiLine": False,
            "font": {
                "name": font_family,
                "size": font_size,
                "underline": False,
                "bold": False,
                "italic": False,
                "color": color
            },
            "effect": {
                "type": 0,
                "speed": 5,
                "hold": 5000
            }
        }
        return item
    
    @staticmethod
    def _soo_sensor_to_huidu_item(properties: Dict) -> Dict:
        font_family = properties.get("font_family", "Arial")
        font_size = properties.get("font_size", 14)
        color = properties.get("color", "#FFFFFF")
        sensor_type = properties.get("sensor_type", 0)
        
        item = {
            "type": "dynamic",
            "sensor_type": sensor_type,
            "font": {
                "name": font_family,
                "size": font_size,
                "underline": False,
                "bold": False,
                "italic": False,
                "color": color
            }
        }
        return item
    
    @staticmethod
    def _soo_weather_to_huidu_item(properties: Dict) -> Dict:
        return ProgramConverter._soo_text_to_huidu_item(properties)
    
    @staticmethod
    def _soo_html_to_huidu_item(properties: Dict) -> Dict:
        file_path = properties.get("file_path", "")
        
        item = {
            "type": "html",
            "file": file_path
        }
        return item
    
    @staticmethod
    def _soo_hdmi_to_huidu_item(properties: Dict) -> Dict:
        item = {
            "type": "hdmi",
            "source": properties.get("hdmi_source", 0)
        }
        return item
    
    @staticmethod
    def _novastar_to_soo(sdk_program_dict: Dict) -> Dict:
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
        return sdk_to_program(sdk_program_dict)
    
    @staticmethod
    def _huidu_item_to_soo_element(item: Dict, area: Dict) -> Optional[Dict]:
        element = _sdk_text_item_to_element(item, area)
        if element:
            return element
        
        item_type = item.get("type", "")
        
        element_type = item_type
        if item_type == "text":
            multi_line = item.get("multiLine", False)
            element_type = "singleline_text" if not multi_line else "text"
        
        soo_element = {
            "type": element_type,
            "x": area.get("x", 0),
            "y": area.get("y", 0),
            "width": area.get("width", 200),
            "height": area.get("height", 100),
            "properties": {}
        }
        
        if item_type == "text":
            soo_element["properties"]["text"] = item.get("string", "")
            font = item.get("font", {})
            if font:
                soo_element["properties"]["font_family"] = font.get("name", "Arial")
                soo_element["properties"]["font_size"] = font.get("size", 24)
                soo_element["properties"]["color"] = font.get("color", "#000000")
            effect = item.get("effect", {})
            if effect:
                soo_element["properties"]["duration"] = effect.get("hold", 5000)
        elif item_type in ["photo", "image"]:
            soo_element["properties"]["file_path"] = item.get("file", "") or item.get("url", "")
            effect = item.get("effect", {})
            if effect:
                soo_element["properties"]["duration"] = effect.get("hold", 5000)
        elif item_type == "video":
            soo_element["properties"]["file_path"] = item.get("file", "") or item.get("url", "")
        elif item_type == "digitalClock":
            soo_element["type"] = "clock"
            soo_element["properties"]["show_date"] = item.get("showDate", True)
            soo_element["properties"]["show_time"] = item.get("showTime", True)
            font = item.get("font", {})
            if font:
                soo_element["properties"]["font_family"] = font.get("name", "Arial")
                soo_element["properties"]["font_size"] = font.get("size", 24)
                soo_element["properties"]["color"] = font.get("color", "#000000")
        elif item_type == "dialClock":
            soo_element["type"] = "clock"
            soo_element["properties"]["show_date"] = item.get("showDate", True)
            soo_element["properties"]["show_time"] = item.get("showTime", True)
        elif item_type == "dynamic":
            soo_element["type"] = "sensor"
            soo_element["properties"]["sensor_type"] = item.get("type", 0)
        elif item_type == "html":
            soo_element["properties"]["html_content"] = item.get("html", "")
        elif item_type == "hdmi":
            soo_element["properties"]["hdmi_source"] = item.get("source", 0)
        
        return soo_element
    
    @staticmethod
    def _novastar_widget_to_soo_element(widget: Dict) -> Optional[Dict]:
        widget_type = widget.get("type", "")
        layout = widget.get("layout", {})
        metadata = widget.get("metadata", {})
        
        element: Dict[str, Any] = {
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
    def _huidu_element_to_soo_element(element: Dict) -> Optional[Dict]:
        """Convert Huidu element to *.soo element format"""
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

