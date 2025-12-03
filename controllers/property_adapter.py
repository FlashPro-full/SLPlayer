from typing import Dict, Optional, Any


def get_default_properties(element_type: str) -> Dict[str, Any]:
    defaults = {
        "text": {
            "text": "",
            "font_family": "Arial",
            "font_size": 24,
            "color": "#000000"
        },
        "singleline_text": {
            "text": "",
            "font_family": "Arial",
            "font_size": 24,
            "color": "#000000"
        },
        "animation": {
            "text": "",
            "font_family": "Arial",
            "font_size": 24,
            "color": "#FFFFFF"
        },
        "photo": {
            "file_path": ""
        },
        "video": {
            "file_path": ""
        },
        "clock": {
            "show_date": True,
            "font_family": "Arial",
            "font_size": 48,
            "color": "#000000"
        },
        "timing": {
            "count_type": 0,
            "count_value": 0,
            "font_family": "Arial",
            "font_size": 24,
            "color": "#FFFFFF"
        },
        "sensor": {
            "sensor_type": 0,
            "font_family": "Arial",
            "font_size": 24,
            "color": "#FFFFFF"
        },
        "weather": {
            "text": "",
            "font_family": "Arial",
            "font_size": 24,
            "color": "#FFFFFF"
        },
        "html": {
            "file_path": ""
        },
        "hdmi": {
            "file_path": ""
        }
    }
    return defaults.get(element_type, {}).copy()


def extract_text_properties(properties: Dict) -> Dict[str, Any]:
    text_props = properties.get("text", {})
    if isinstance(text_props, str):
        return {
            "text": text_props,
            "font_family": properties.get("font_family", "Arial"),
            "font_size": properties.get("font_size", 24),
            "color": properties.get("color", "#000000")
        }
    
    content = text_props.get("content", "") if isinstance(text_props, dict) else ""
    format_props = text_props.get("format", {}) if isinstance(text_props, dict) else {}
    
    return {
        "text": content,
        "font_family": format_props.get("font_family") or properties.get("font_family") or "Arial",
        "font_size": format_props.get("font_size") or properties.get("font_size") or 24,
        "color": format_props.get("font_color") or format_props.get("color") or properties.get("color") or "#000000"
    }


def extract_file_path(properties: Dict, element_type: str) -> str:
    type_key = element_type
    if element_type == "html":
        html_props = properties.get("html", {})
        if isinstance(html_props, dict):
            url = html_props.get("url", "")
            return url if url else properties.get("file_path", "")
    elif element_type in ["photo", "video"]:
        type_props = properties.get(type_key, {})
        if isinstance(type_props, dict):
            return type_props.get("file_path", properties.get("file_path", ""))
    
    return properties.get("file_path", "")


def extract_clock_properties(properties: Dict) -> Dict[str, Any]:
    clock_props = properties.get("clock", {})
    if isinstance(clock_props, dict):
        return {
            "show_date": clock_props.get("show_date", True),
            "font_family": clock_props.get("font_family") or properties.get("font_family") or "Arial",
            "font_size": clock_props.get("font_size") or properties.get("font_size") or 48,
            "color": clock_props.get("color") or properties.get("color") or "#000000"
        }
    
    return {
        "show_date": properties.get("show_date", True),
        "font_family": properties.get("font_family", "Arial"),
        "font_size": properties.get("font_size", 48),
        "color": properties.get("color", "#000000")
    }


def extract_timing_properties(properties: Dict) -> Dict[str, Any]:
    timing_props = properties.get("timing", {})
    if not isinstance(timing_props, dict):
        return {
            "count_type": properties.get("count_type", 0),
            "count_value": properties.get("count_value", 0),
            "font_family": properties.get("font_family", "Arial"),
            "font_size": properties.get("font_size", 24),
            "color": properties.get("color", "#FFFFFF")
        }
    
    mode = timing_props.get("mode", "suitable_time")
    count_type_map = {
        "suitable_time": 0,
        "count_down": 1,
        "fixed_time": 2
    }
    count_type = count_type_map.get(mode, 0)
    
    count_value = 0
    if mode == "suitable_time":
        suitable_time = timing_props.get("suitable_time", {})
        if isinstance(suitable_time, dict) and "datetime" in suitable_time:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(suitable_time["datetime"].replace('Z', '+00:00'))
                count_value = int(dt.timestamp())
            except:
                pass
    elif mode == "count_down":
        count_down = timing_props.get("count_down", {})
        if isinstance(count_down, dict) and "datetime" in count_down:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(count_down["datetime"].replace('Z', '+00:00'))
                count_value = int(dt.timestamp())
            except:
                pass
    elif mode == "fixed_time":
        fixed_time = timing_props.get("fixed_time", {})
        if isinstance(fixed_time, dict):
            day_period = fixed_time.get("day_period", 0)
            time_str = fixed_time.get("time", "00:00:00")
            count_value = day_period * 86400
            try:
                parts = time_str.split(":")
                if len(parts) >= 3:
                    count_value += int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            except:
                pass
    
    display_style = timing_props.get("display_style", {})
    color = "#FFFFFF"
    if isinstance(display_style, dict):
        color = display_style.get("color", "#FFFFFF")
    
    suitable_time = timing_props.get("suitable_time", {})
    if isinstance(suitable_time, dict) and "color" in suitable_time:
        color = suitable_time.get("color", color)
    
    count_down = timing_props.get("count_down", {})
    if isinstance(count_down, dict) and "color" in count_down:
        color = count_down.get("color", color)
    
    return {
        "count_type": count_type,
        "count_value": count_value,
        "font_family": properties.get("font_family", "Arial"),
        "font_size": properties.get("font_size", 24),
        "color": color
    }


SENSOR_TYPE_MAP = {
    "temp": 0,
    "Air Humidity": 1,
    "humidity": 1,
    "PM2.5": 2,
    "PM10": 3,
    "Wind power": 4,
    "Wind Direction": 5,
    "Noise": 6,
    "Pressure": 7,
    "Light Intensity": 8,
    "CO2": 9,
    "Co2": 9
}


def extract_sensor_properties(properties: Dict) -> Dict[str, Any]:
    sensor_props = properties.get("sensor", {})
    if not isinstance(sensor_props, dict):
        return {
            "sensor_type": properties.get("sensor_type", 0),
            "font_family": properties.get("font_family", "Arial"),
            "font_size": properties.get("font_size", 24),
            "color": properties.get("color", "#FFFFFF")
        }
    
    sensor_type_str = sensor_props.get("sensor_type", "temp")
    sensor_type = SENSOR_TYPE_MAP.get(sensor_type_str, 0)
    
    color = sensor_props.get("font_color") or sensor_props.get("color") or properties.get("color") or "#FFFFFF"
    
    return {
        "sensor_type": sensor_type,
        "font_family": sensor_props.get("font_family") or properties.get("font_family") or "Arial",
        "font_size": sensor_props.get("font_size") or properties.get("font_size") or 24,
        "color": color
    }


def adapt_element_for_controller(element: Dict, controller_type: str) -> Dict:
    adapted = {
        "type": element.get("type", ""),
        "x": element.get("x", 0),
        "y": element.get("y", 0),
        "width": element.get("width", 200),
        "height": element.get("height", 100),
        "properties": {}
    }
    
    element_type = element.get("type", "")
    properties = element.get("properties", {})
    defaults = get_default_properties(element_type)
    
    if element_type in ["text", "singleline_text"]:
        adapted["properties"] = extract_text_properties(properties)
        for key, value in defaults.items():
            if key not in adapted["properties"]:
                adapted["properties"][key] = value
    
    elif element_type == "animation":
        adapted["properties"] = extract_text_properties(properties)
        for key, value in defaults.items():
            if key not in adapted["properties"]:
                adapted["properties"][key] = value
    
    elif element_type == "photo":
        file_path = extract_file_path(properties, "photo")
        adapted["properties"] = {"file_path": file_path}
        if not file_path:
            adapted["properties"]["file_path"] = defaults.get("file_path", "")
    
    elif element_type == "video":
        file_path = extract_file_path(properties, "video")
        adapted["properties"] = {"file_path": file_path}
        if not file_path:
            adapted["properties"]["file_path"] = defaults.get("file_path", "")
    
    elif element_type == "clock":
        adapted["properties"] = extract_clock_properties(properties)
        for key, value in defaults.items():
            if key not in adapted["properties"]:
                adapted["properties"][key] = value
    
    elif element_type == "timing":
        adapted["properties"] = extract_timing_properties(properties)
        for key, value in defaults.items():
            if key not in adapted["properties"]:
                adapted["properties"][key] = value
    
    elif element_type == "sensor":
        adapted["properties"] = extract_sensor_properties(properties)
        for key, value in defaults.items():
            if key not in adapted["properties"]:
                adapted["properties"][key] = value
    
    elif element_type == "weather":
        weather_props = properties.get("weather", {})
        if isinstance(weather_props, dict):
            city = weather_props.get("city", "Rome")
            temp_enabled = weather_props.get("temp_enabled", False)
            text_parts = []
            if temp_enabled:
                text_parts.append(f"{city} Temperature")
            adapted["properties"] = extract_text_properties(properties)
            adapted["properties"]["text"] = " ".join(text_parts) if text_parts else city
        else:
            adapted["properties"] = extract_text_properties(properties)
        for key, value in defaults.items():
            if key not in adapted["properties"]:
                adapted["properties"][key] = value
    
    elif element_type == "html":
        file_path = extract_file_path(properties, "html")
        adapted["properties"] = {"file_path": file_path}
        if not file_path:
            adapted["properties"]["file_path"] = defaults.get("file_path", "")
    
    elif element_type == "hdmi":
        adapted["properties"] = {"file_path": ""}
    
    else:
        adapted["properties"] = defaults.copy()
    
    return adapted


def convert_play_control_to_sdk(play_control: Dict, controller_type: str) -> Optional[Any]:
    """
    Convert Program.play_control to SDK PlayControl format.
    
    Args:
        play_control: Program play_control dict with specified_time, specify_week, specify_date
        controller_type: "huidu" or "novastar"
    
    Returns:
        SDK PlayControl object (for Huidu) or dict (for NovaStar)
    """
    if controller_type.lower() == "huidu":
        try:
            from controllers.huidu_sdk import SDK_AVAILABLE, PlayControl
            if not SDK_AVAILABLE:
                return None
            
            sdk_play_control = PlayControl()
            
            specified_time = play_control.get("specified_time", {})
            if specified_time.get("enabled", False):
                time_ranges = specified_time.get("ranges", [])
                for time_range in time_ranges:
                    start_str = time_range.get("start", "00:00:00")
                    end_str = time_range.get("end", "23:59:59")
                    try:
                        from datetime import time
                        start_time = time.fromisoformat(start_str) if ":" in start_str else None
                        end_time = time.fromisoformat(end_str) if ":" in end_str else None
                        if start_time and end_time:
                            sdk_play_control.time.append(PlayControl.Time(start_time, end_time))
                    except:
                        pass
            
            specify_week = play_control.get("specify_week", {})
            if specify_week.get("enabled", False):
                days = specify_week.get("days", [])
                weekday_map = {
                    0: PlayControl.Weekday.Mon,
                    1: PlayControl.Weekday.Tue,
                    2: PlayControl.Weekday.Wed,
                    3: PlayControl.Weekday.Thur,
                    4: PlayControl.Weekday.Fri,
                    5: PlayControl.Weekday.Sat,
                    6: PlayControl.Weekday.Sun
                }
                enabled_weekdays = [weekday_map[day] for day in days if day in weekday_map]
                sdk_play_control.week.enable_weekdays = enabled_weekdays
            
            specify_date = play_control.get("specify_date", {})
            if specify_date.get("enabled", False):
                date_ranges = specify_date.get("ranges", [])
                for date_range in date_ranges:
                    start_str = date_range.get("start", "")
                    end_str = date_range.get("end", "")
                    try:
                        from datetime import date
                        start_date = date.fromisoformat(start_str) if start_str else None
                        end_date = date.fromisoformat(end_str) if end_str else None
                        if start_date and end_date:
                            sdk_play_control.date.append(PlayControl.Date(start_date, end_date))
                    except:
                        pass
            
            if sdk_play_control.time or sdk_play_control.date or (sdk_play_control.week.enable_weekdays and len(sdk_play_control.week.enable_weekdays) > 0):
                return sdk_play_control
            
            return None
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error converting play_control to SDK format: {e}")
            return None
    
    elif controller_type.lower() == "novastar":
        schedule_data = {
            "time_ranges": [],
            "weekdays": [],
            "date_ranges": []
        }
        
        specified_time = play_control.get("specified_time", {})
        if specified_time.get("enabled", False):
            time_ranges = specified_time.get("ranges", [])
            schedule_data["time_ranges"] = time_ranges
        
        specify_week = play_control.get("specify_week", {})
        if specify_week.get("enabled", False):
            schedule_data["weekdays"] = specify_week.get("days", [])
        
        specify_date = play_control.get("specify_date", {})
        if specify_date.get("enabled", False):
            date_ranges = specify_date.get("ranges", [])
            schedule_data["date_ranges"] = date_ranges
        
        if schedule_data["time_ranges"] or schedule_data["weekdays"] or schedule_data["date_ranges"]:
            return schedule_data
        
        return None
    
    return None
