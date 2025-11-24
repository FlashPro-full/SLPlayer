"""
Color conversion utilities based on InputLayout.fx shader code
"""
from PyQt5.QtGui import QColor
import math


def rgb_to_hsv(r: float, g: float, b: float) -> tuple:
    """
    Convert RGB to HSV (based on InputLayout.fx RGB2HSV)
    Returns: (h, s, v, a) where h is in degrees (0-360)
    """
    max_val = max(r, max(g, b))
    min_val = min(r, min(g, b))
    
    h = 0.0
    if max_val == r:
        h = (g - b) / (max_val - min_val) if (max_val - min_val) != 0 else 0
    elif max_val == g:
        h = 2.0 + (b - r) / (max_val - min_val) if (max_val - min_val) != 0 else 0
    elif max_val == b:
        h = 4.0 + (r - g) / (max_val - min_val) if (max_val - min_val) != 0 else 0
    
    h = h * 60.0
    if h < 0.0:
        h += 360.0
    
    v = max_val
    s = (max_val - min_val) / max_val if max_val != 0 else 0
    
    return (h, s, v)


def hsv_to_rgb(h: float, s: float, v: float) -> tuple:
    """
    Convert HSV to RGB (based on InputLayout.fx HSV2RGB)
    h: hue in degrees (0-360)
    s: saturation (0-1)
    v: value/brightness (0-1)
    Returns: (r, g, b) in range 0-1
    """
    if s == 0.0:
        return (v, v, v)
    
    h = h / 60.0
    i = int(h)
    f = h - float(i)
    
    a = v * (1.0 - s)
    b = v * (1.0 - s * f)
    c = v * (1.0 - s * (1.0 - f))
    
    if i == 0:
        return (v, c, a)
    elif i == 1:
        return (b, v, a)
    elif i == 2:
        return (a, v, c)
    elif i == 3:
        return (a, b, v)
    elif i == 4:
        return (c, a, v)
    else:
        return (v, a, b)


def get_gradient_color(angle: float, saturation: float = 1.0, value: float = 1.0) -> QColor:
    """
    Get a color from HSV gradient based on angle (0-360 degrees)
    Based on InputLayout.fx GetDazzleColor logic
    """
    # Normalize angle to 0-360
    angle = angle % 360.0
    if angle < 0:
        angle += 360.0
    
    r, g, b = hsv_to_rgb(angle, saturation, value)
    return QColor(int(r * 255), int(g * 255), int(b * 255))


def get_gradient_color_at_position(pos: float, style_index: int, num_colors: int = 7) -> QColor:
    """
    Get gradient color at position (0.0-1.0) for a given style
    Uses 7-color rainbow gradient by default
    """
    # Base rainbow colors in HSV
    base_hues = [0, 30, 60, 120, 240, 270, 300]  # Red, Orange, Yellow, Green, Blue, Indigo, Violet
    
    # Map position to hue based on style
    if style_index < 9:
        # Styles 0-8: Standard rainbow flow
        hue = pos * 360.0
    elif style_index < 18:
        # Styles 9-17: Reversed rainbow
        hue = (1.0 - pos) * 360.0
    else:
        # Styles 18-25: Multi-color segments
        segment = int(pos * num_colors)
        segment_pos = (pos * num_colors) % 1.0
        hue1 = base_hues[segment % len(base_hues)]
        hue2 = base_hues[(segment + 1) % len(base_hues)]
        hue = hue1 + (hue2 - hue1) * segment_pos
    
    return get_gradient_color(hue, 1.0, 1.0)

