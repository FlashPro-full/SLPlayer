from typing import Dict, Any


def ensure_element_defaults(element: Dict) -> Dict:
    element_type = element.get("type", "")
    if "properties" not in element:
        element["properties"] = {}
    
    properties = element["properties"]
    
    if element_type == "text" or element_type == "singleline_text":
        if "text" not in properties:
            properties["text"] = {}
        if "content" not in properties["text"]:
            properties["text"]["content"] = ""
        if "format" not in properties["text"]:
            properties["text"]["format"] = {}
        format_props = properties["text"]["format"]
        if "font_family" not in format_props:
            format_props["font_family"] = "Arial"
        if "font_size" not in format_props:
            format_props["font_size"] = 24
        if "font_color" not in format_props:
            format_props["font_color"] = "#000000"
        if "bold" not in format_props:
            format_props["bold"] = False
        if "italic" not in format_props:
            format_props["italic"] = False
        if "underline" not in format_props:
            format_props["underline"] = False
        if "alignment" not in format_props:
            format_props["alignment"] = "left"
        if "vertical_alignment" not in format_props:
            format_props["vertical_alignment"] = "top"
    
    elif element_type == "animation":
        if "text" not in properties:
            properties["text"] = {}
        if "content" not in properties["text"]:
            properties["text"]["content"] = ""
        if "format" not in properties["text"]:
            properties["text"]["format"] = {}
        format_props = properties["text"]["format"]
        if "font_family" not in format_props:
            format_props["font_family"] = "Arial"
        if "font_size" not in format_props:
            format_props["font_size"] = 24
        if "font_color" not in format_props:
            format_props["font_color"] = "#FFFFFF"
        if "animation_style" not in properties:
            properties["animation_style"] = {}
        style_props = properties["animation_style"]
        if "style_index" not in style_props:
            style_props["style_index"] = 0
        if "hold_time" not in style_props:
            style_props["hold_time"] = 6.0
        if "speed" not in style_props:
            style_props["speed"] = 5
    
    elif element_type == "photo":
        if "photo" not in properties:
            properties["photo"] = {}
        if "file_path" not in properties["photo"]:
            properties["photo"]["file_path"] = ""
    
    elif element_type == "video":
        if "video" not in properties:
            properties["video"] = {}
        if "file_path" not in properties["video"]:
            properties["video"]["file_path"] = ""
    
    elif element_type == "clock":
        if "clock" not in properties:
            properties["clock"] = {}
        clock_props = properties["clock"]
        if "show_date" not in clock_props:
            clock_props["show_date"] = True
        if "font_family" not in clock_props:
            clock_props["font_family"] = "Arial"
        if "font_size" not in clock_props:
            clock_props["font_size"] = 48
        if "color" not in clock_props:
            clock_props["color"] = "#000000"
    
    elif element_type == "timing":
        if "timing" not in properties:
            properties["timing"] = {}
        timing_props = properties["timing"]
        if "mode" not in timing_props:
            timing_props["mode"] = "suitable_time"
        if "top_text" not in timing_props:
            timing_props["top_text"] = "To **"
        if "top_text_color" not in timing_props:
            timing_props["top_text_color"] = "#cdcd00"
        if "multiline" not in timing_props:
            timing_props["multiline"] = True
        if "top_text_space" not in timing_props:
            timing_props["top_text_space"] = 5
        if "suitable_time" not in timing_props:
            timing_props["suitable_time"] = {}
        if "color" not in timing_props["suitable_time"]:
            timing_props["suitable_time"]["color"] = "#cdcd00"
        if "count_down" not in timing_props:
            timing_props["count_down"] = {}
        if "color" not in timing_props["count_down"]:
            timing_props["count_down"]["color"] = "#cdcd00"
        if "fixed_time" not in timing_props:
            timing_props["fixed_time"] = {}
        if "display_style" not in timing_props:
            timing_props["display_style"] = {}
        display_style = timing_props["display_style"]
        if "color" not in display_style:
            display_style["color"] = "#ff9900"
        if "year" not in display_style:
            display_style["year"] = True
        if "day" not in display_style:
            display_style["day"] = True
        if "hour" not in display_style:
            display_style["hour"] = True
        if "minute" not in display_style:
            display_style["minute"] = True
        if "second" not in display_style:
            display_style["second"] = True
        if "millisecond" not in display_style:
            display_style["millisecond"] = False
        if "position_align" not in display_style:
            display_style["position_align"] = "center"
    
    elif element_type == "weather":
        if "weather" not in properties:
            properties["weather"] = {}
        weather_props = properties["weather"]
        if "city" not in weather_props:
            weather_props["city"] = "Rome"
        if "temp_enabled" not in weather_props:
            weather_props["temp_enabled"] = True
        if "temp_color" not in weather_props:
            weather_props["temp_color"] = "#FFFFFF"
        if "temp_unit" not in weather_props:
            weather_props["temp_unit"] = "C"
    
    elif element_type == "sensor":
        if "sensor" not in properties:
            properties["sensor"] = {}
        sensor_props = properties["sensor"]
        if "sensor_type" not in sensor_props:
            sensor_props["sensor_type"] = "temp"
        if "fixed_text" not in sensor_props:
            sensor_props["fixed_text"] = "The Temperature"
        if "font_family" not in sensor_props:
            sensor_props["font_family"] = "Arial"
        if "font_color" not in sensor_props:
            sensor_props["font_color"] = "#FFFFFF"
        if "unit" not in sensor_props:
            sensor_props["unit"] = "°C"
    
    elif element_type == "html":
        if "html" not in properties:
            properties["html"] = {}
        html_props = properties["html"]
        if "url" not in html_props:
            html_props["url"] = "https://www.google.com/"
        if "time_refresh_enabled" not in html_props:
            html_props["time_refresh_enabled"] = False
        if "time_refresh_value" not in html_props:
            html_props["time_refresh_value"] = 15.0
    
    elif element_type == "hdmi":
        if "hdmi" not in properties:
            properties["hdmi"] = {}
        if "display_mode" not in properties["hdmi"]:
            properties["hdmi"]["display_mode"] = "Full Screen Zoom"
    
    return element


def ensure_program_defaults(program: Dict) -> Dict:
    elements = program.get("elements", [])
    for element in elements:
        ensure_element_defaults(element)
    return program

