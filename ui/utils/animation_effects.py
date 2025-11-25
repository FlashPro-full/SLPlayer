from PyQt5.QtGui import QColor, QTransform
from PyQt5.QtCore import QRectF
from ui.utils.color_utils import get_gradient_color_at_position
import math


def get_animation_transform(style_index, char_index, text_length, elapsed_sec, hold_time, speed, 
                           base_x, base_y, char_width, char_height, text_width, text_height, text_center_x=None, text_center_y=None):
    if style_index == 0:
        return _continuous_move_left(char_index, text_length, elapsed_sec, speed, base_x, base_y, char_width, text_width)
    elif style_index == 1:
        return _continuous_move_right(char_index, text_length, elapsed_sec, speed, base_x, base_y, char_width, text_width)
    elif style_index == 2:
        return _continuous_move_up(char_index, text_length, elapsed_sec, speed, base_x, base_y, char_height, text_height)
    elif style_index == 3:
        return _continuous_move_down(char_index, text_length, elapsed_sec, speed, base_x, base_y, char_height, text_height)
    elif style_index == 4:
        return _one_char_move_in_from_right(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, text_width)
    elif style_index == 5:
        return _one_char_move_in_from_left(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, text_width)
    elif style_index == 6:
        return _one_char_move_in_from_down(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height, text_height)
    elif style_index == 7:
        return _one_char_move_in_from_up(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height, text_height)
    elif style_index == 8:
        return _one_char_show_from_left(char_index, elapsed_sec, hold_time, speed, base_x, base_y)
    elif style_index == 9:
        return _one_char_jump_in_order(char_index, elapsed_sec, hold_time, speed, base_x, base_y)
    elif style_index == 10:
        return _screw_30_left_right(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width)
    elif style_index == 11:
        return _zoom_in_reverse(char_index, elapsed_sec, hold_time, speed, base_x, base_y)
    elif style_index == 12:
        return _one_char_brown_move(char_index, elapsed_sec, hold_time, speed, base_x, base_y)
    elif style_index == 13:
        return _one_char_zoom_in_left_bottom(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height)
    elif style_index == 14:
        return _one_char_zoom_out_right_top(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height)
    elif style_index == 15:
        return _one_char_rotate_top_center(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height)
    elif style_index == 16:
        return _rotate_per_char(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height)
    elif style_index == 17:
        return _one_char_rotate_bottom_center(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height)
    elif style_index == 18:
        return _smooth_mirror_bottom(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height)
    elif style_index == 19:
        return _one_char_stand_up_from_lie(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height)
    elif style_index == 20:
        return _smooth_one_char_move_in_from_up(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height)
    elif style_index == 21:
        return _smooth_move_in_from_up_lying_30(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height)
    elif style_index == 22:
        return _smooth_move_in_from_top_right_rotate_y_90(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height, text_width, text_height)
    elif style_index == 23:
        return _one_char_lie_down_stand_up(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height)
    elif style_index == 24:
        return _one_char_lie_down_stand_up_continuous(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height)
    elif style_index == 25:
        return _smooth_rotate_y_90(char_index, elapsed_sec, hold_time, speed, base_x, base_y)
    elif style_index == 26:
        return _smooth_move_in_from_top_right_dancing(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height, text_width, text_height)
    elif style_index == 27:
        return _continuous_move_in_from_bottom_center_diagonal(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height, text_width, text_height)
    elif style_index == 28:
        return _smooth_one_char_zoom_in_from_0_to_1(char_index, elapsed_sec, hold_time, speed, base_x, base_y)
    elif style_index == 29:
        if text_center_x is None:
            text_center_x = base_x + text_width / 2
        if text_center_y is None:
            text_center_y = base_y + text_height / 2
        return _spread_from_center_zoom_in(char_index, text_length, elapsed_sec, hold_time, speed, base_x, base_y, text_width, text_height, text_center_x, text_center_y)
    elif style_index == 30:
        return _splintered_chars_gather_rotate_y_90(char_index, text_length, elapsed_sec, hold_time, speed, base_x, base_y, text_width)
    elif style_index == 31:
        return _splintered_chars_gather_rotate_continuous(char_index, text_length, elapsed_sec, hold_time, speed, base_x, base_y, text_width)
    elif style_index == 32:
        return _continuous_zoom_in_out(char_index, elapsed_sec, hold_time, speed, base_x, base_y)
    elif style_index == 33:
        return _continuous_idle_30_left_right(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width)
    else:
        return {'x': base_x, 'y': base_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': 1.0}


def get_animation_color(style_index, char_index, text_length, elapsed_sec):
    pos = char_index / max(text_length - 1, 1) if text_length > 1 else 0.0
    time_offset = (elapsed_sec * 0.5) % 1.0
    pos = (pos + time_offset) % 1.0
    return get_gradient_color_at_position(pos, style_index)


def _continuous_move_left(char_index, text_length, elapsed_sec, speed, base_x, base_y, char_width, text_width):
    cycle_time = (text_length * char_width) / max(speed * 10, 1)
    cycle_pos = (elapsed_sec % cycle_time) / max(cycle_time, 0.001)
    offset = cycle_pos * text_width
    char_x = base_x + (char_index * char_width) - offset
    if char_x + char_width < base_x:
        char_x += text_width
    return {'x': char_x, 'y': base_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': 1.0}


def _continuous_move_right(char_index, text_length, elapsed_sec, speed, base_x, base_y, char_width, text_width):
    scroll_speed = speed * 10
    offset = (elapsed_sec * scroll_speed) % text_width
    char_x = base_x + (char_index * char_width) - offset
    return {'x': char_x, 'y': base_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': 1.0, 'scroll_offset': offset}


def _continuous_move_up(char_index, text_length, elapsed_sec, speed, base_x, base_y, char_height, text_height):
    cycle_time = (text_length * char_height) / max(speed * 10, 1)
    cycle_pos = (elapsed_sec % cycle_time) / max(cycle_time, 0.001)
    offset = cycle_pos * text_height
    char_y = base_y + (char_index * char_height) - offset
    if char_y + char_height < base_y:
        char_y += text_height
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': 1.0}


def _continuous_move_down(char_index, text_length, elapsed_sec, speed, base_x, base_y, char_height, text_height):
    cycle_time = (text_length * char_height) / max(speed * 10, 1)
    cycle_pos = (elapsed_sec % cycle_time) / max(cycle_time, 0.001)
    offset = cycle_pos * text_height
    char_y = base_y + (char_index * char_height) + offset
    if char_y > base_y + text_height:
        char_y -= text_height
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': 1.0}


def _one_char_move_in_from_right(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, text_width):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = (text_width / max(speed * 10, 1)) + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (1 - hold_time / cycle_time):
        move_progress = cycle_pos / (1 - hold_time / cycle_time)
        char_x = base_x + (1 - move_progress) * text_width
        opacity = 1.0
    else:
        char_x = base_x
        opacity = 1.0
    
    return {'x': char_x, 'y': base_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _one_char_move_in_from_left(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, text_width):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = (text_width / max(speed * 10, 1)) + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (1 - hold_time / cycle_time):
        move_progress = cycle_pos / (1 - hold_time / cycle_time)
        char_x = base_x - (1 - move_progress) * text_width
        opacity = 1.0
    else:
        char_x = base_x
        opacity = 1.0
    
    return {'x': char_x, 'y': base_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _one_char_move_in_from_down(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height, text_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = (text_height / max(speed * 10, 1)) + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (1 - hold_time / cycle_time):
        move_progress = cycle_pos / (1 - hold_time / cycle_time)
        char_y = base_y + (1 - move_progress) * text_height
        opacity = 1.0
    else:
        char_y = base_y
        opacity = 1.0
    
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _one_char_move_in_from_up(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height, text_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = (text_height / max(speed * 10, 1)) + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (1 - hold_time / cycle_time):
        move_progress = cycle_pos / (1 - hold_time / cycle_time)
        char_y = base_y - (1 - move_progress) * text_height
        opacity = 1.0
    else:
        char_y = base_y
        opacity = 1.0
    
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _one_char_show_from_left(char_index, elapsed_sec, hold_time, speed, base_x, base_y):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.5 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.5 / cycle_time):
        opacity = cycle_pos / (0.5 / cycle_time)
        char_x = base_x - 20 * (1 - opacity)
    else:
        opacity = 1.0
        char_x = base_x
    
    return {'x': char_x, 'y': base_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _one_char_jump_in_order(char_index, elapsed_sec, hold_time, speed, base_x, base_y):
    char_delay = char_index * 0.15
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.3 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.3 / cycle_time):
        jump_progress = cycle_pos / (0.3 / cycle_time)
        jump_height = math.sin(jump_progress * math.pi) * 20
        char_y = base_y - jump_height
        opacity = 1.0 if jump_progress > 0.1 else 0.0
    else:
        char_y = base_y
        opacity = 1.0
    
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _screw_30_left_right(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.5 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.5 / cycle_time):
        move_progress = cycle_pos / (0.5 / cycle_time)
        angle = math.sin(move_progress * math.pi) * 30
        rotation = math.radians(angle)
        offset_x = math.sin(rotation) * 10
        char_x = base_x + offset_x
        opacity = 1.0
    else:
        char_x = base_x
        rotation = 0.0
        opacity = 1.0
    
    return {'x': char_x, 'y': base_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': rotation, 'opacity': opacity}


def _zoom_in_reverse(char_index, elapsed_sec, hold_time, speed, base_x, base_y):
    char_delay = char_index * 0.05
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 1.0 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.5 / cycle_time):
        zoom_progress = cycle_pos / (0.5 / cycle_time)
        scale = 1.0 + zoom_progress
        opacity = 1.0
    elif cycle_pos < (1.0 / cycle_time):
        zoom_progress = (cycle_pos - 0.5 / cycle_time) / (0.5 / cycle_time)
        scale = 2.0 - zoom_progress
        opacity = 1.0
    else:
        scale = 1.0
        opacity = 1.0
    
    return {'x': base_x, 'y': base_y, 'scale_x': scale, 'scale_y': scale, 'rotation': 0.0, 'opacity': opacity}


def _one_char_brown_move(char_index, elapsed_sec, hold_time, speed, base_x, base_y):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.8 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.8 / cycle_time):
        move_progress = cycle_pos / (0.8 / cycle_time)
        offset_x = math.sin(move_progress * math.pi * 2) * 15
        offset_y = math.cos(move_progress * math.pi * 2) * 15
        char_x = base_x + offset_x
        char_y = base_y + offset_y
        opacity = 1.0
    else:
        char_x = base_x
        char_y = base_y
        opacity = 1.0
    
    return {'x': char_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _one_char_zoom_in_left_bottom(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.5 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.5 / cycle_time):
        zoom_progress = cycle_pos / (0.5 / cycle_time)
        scale = zoom_progress
        char_x = base_x - char_width * (1 - scale) / 2
        char_y = base_y + char_height * (1 - scale)
        opacity = 1.0
    else:
        scale = 1.0
        char_x = base_x
        char_y = base_y
        opacity = 1.0
    
    return {'x': char_x, 'y': char_y, 'scale_x': scale, 'scale_y': scale, 'rotation': 0.0, 'opacity': opacity}


def _one_char_zoom_out_right_top(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.5 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.5 / cycle_time):
        zoom_progress = cycle_pos / (0.5 / cycle_time)
        scale = 2.0 - zoom_progress
        char_x = base_x + char_width * (scale - 1.0) / 2
        char_y = base_y - char_height * (scale - 1.0)
        opacity = 1.0
    else:
        scale = 1.0
        char_x = base_x
        char_y = base_y
        opacity = 1.0
    
    return {'x': char_x, 'y': char_y, 'scale_x': scale, 'scale_y': scale, 'rotation': 0.0, 'opacity': opacity}


def _one_char_rotate_top_center(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 1.0 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    pivot_x = base_x + char_width / 2
    pivot_y = base_y
    
    if cycle_pos < (1.0 / cycle_time):
        rotation_progress = cycle_pos / (1.0 / cycle_time)
        rotation = rotation_progress * math.pi * 2
        offset_x = (char_width / 2) * (math.cos(rotation) - 1)
        offset_y = (char_height / 2) * math.sin(rotation)
        char_x = base_x + offset_x
        char_y = base_y + offset_y
    else:
        rotation = 0.0
        char_x = base_x
        char_y = base_y
    
    return {'x': char_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': rotation, 'opacity': 1.0, 'pivot_x': pivot_x, 'pivot_y': pivot_y}


def _rotate_per_char(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.5 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.5 / cycle_time):
        rotation_progress = cycle_pos / (0.5 / cycle_time)
        rotation = rotation_progress * math.pi * 2
        opacity = 1.0
    else:
        rotation = 0.0
        opacity = 1.0
    
    return {'x': base_x, 'y': base_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': rotation, 'opacity': opacity}


def _one_char_rotate_bottom_center(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 1.0 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    pivot_x = base_x + char_width / 2
    pivot_y = base_y + char_height
    
    if cycle_pos < (1.0 / cycle_time):
        rotation_progress = cycle_pos / (1.0 / cycle_time)
        rotation = rotation_progress * math.pi * 2
        offset_x = (char_width / 2) * (math.cos(rotation) - 1)
        offset_y = -(char_height / 2) * math.sin(rotation)
        char_x = base_x + offset_x
        char_y = base_y + offset_y
    else:
        rotation = 0.0
        char_x = base_x
        char_y = base_y
    
    return {'x': char_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': rotation, 'opacity': 1.0, 'pivot_x': pivot_x, 'pivot_y': pivot_y}


def _smooth_mirror_bottom(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height):
    char_delay = char_index * 0.05
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.6 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    pivot_y = base_y + char_height
    
    if cycle_pos < (0.6 / cycle_time):
        mirror_progress = cycle_pos / (0.6 / cycle_time)
        scale_y = 1.0 - (mirror_progress * 0.5)
        char_y = base_y + (char_height * (1 - scale_y))
        opacity = 1.0
    else:
        scale_y = 0.5
        char_y = base_y + (char_height * 0.5)
        opacity = 1.0
    
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': scale_y, 'rotation': 0.0, 'opacity': opacity, 'pivot_y': pivot_y}


def _one_char_stand_up_from_lie(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.5 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.5 / cycle_time):
        stand_progress = cycle_pos / (0.5 / cycle_time)
        rotation = -math.pi / 2 * (1 - stand_progress)
        char_y = base_y - math.sin(rotation) * char_height / 2
        opacity = 1.0
    else:
        rotation = 0.0
        char_y = base_y
        opacity = 1.0
    
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': rotation, 'opacity': opacity}


def _smooth_one_char_move_in_from_up(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height):
    char_delay = char_index * 0.08
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.6 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.6 / cycle_time):
        move_progress = cycle_pos / (0.6 / cycle_time)
        ease_progress = 1 - math.pow(1 - move_progress, 3)
        char_y = base_y - (1 - ease_progress) * char_height * 2
        opacity = ease_progress
    else:
        char_y = base_y
        opacity = 1.0
    
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _smooth_move_in_from_up_lying_30(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height):
    char_delay = char_index * 0.08
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.7 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.7 / cycle_time):
        move_progress = cycle_pos / (0.7 / cycle_time)
        ease_progress = 1 - math.pow(1 - move_progress, 3)
        rotation = math.radians(30) * (1 - ease_progress)
        char_y = base_y - (1 - ease_progress) * char_height * 2
        opacity = ease_progress
    else:
        rotation = 0.0
        char_y = base_y
        opacity = 1.0
    
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': rotation, 'opacity': opacity}


def _smooth_move_in_from_top_right_rotate_y_90(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height, text_width, text_height):
    char_delay = char_index * 0.08
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.8 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.8 / cycle_time):
        move_progress = cycle_pos / (0.8 / cycle_time)
        ease_progress = 1 - math.pow(1 - move_progress, 3)
        rotation_y = math.pi / 2 * (1 - ease_progress)
        char_x = base_x + (1 - ease_progress) * text_width / 2
        char_y = base_y - (1 - ease_progress) * text_height / 2
        opacity = ease_progress
        scale_x = math.cos(rotation_y)
    else:
        rotation_y = 0.0
        char_x = base_x
        char_y = base_y
        opacity = 1.0
        scale_x = 1.0
    
    return {'x': char_x, 'y': char_y, 'scale_x': scale_x, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _one_char_lie_down_stand_up(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 1.0 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.5 / cycle_time):
        progress = cycle_pos / (0.5 / cycle_time)
        rotation = -math.pi / 2 * progress
        char_y = base_y - math.sin(rotation) * char_height / 2
    elif cycle_pos < (1.0 / cycle_time):
        progress = (cycle_pos - 0.5 / cycle_time) / (0.5 / cycle_time)
        rotation = -math.pi / 2 * (1 - progress)
        char_y = base_y - math.sin(rotation) * char_height / 2
    else:
        rotation = 0.0
        char_y = base_y
    
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': rotation, 'opacity': 1.0}


def _one_char_lie_down_stand_up_continuous(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 1.0 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (1.0 / cycle_time):
        progress = cycle_pos / (1.0 / cycle_time)
        rotation = -math.pi / 2 * math.sin(progress * math.pi)
        char_y = base_y - math.sin(abs(rotation)) * char_height / 2
    else:
        rotation = 0.0
        char_y = base_y
    
    return {'x': base_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': rotation, 'opacity': 1.0}


def _smooth_rotate_y_90(char_index, elapsed_sec, hold_time, speed, base_x, base_y):
    char_delay = char_index * 0.08
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.6 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.6 / cycle_time):
        rotate_progress = cycle_pos / (0.6 / cycle_time)
        ease_progress = 1 - math.pow(1 - rotate_progress, 3)
        rotation_y = math.pi / 2 * ease_progress
        scale_x = math.cos(rotation_y)
        opacity = 1.0
    else:
        rotation_y = math.pi / 2
        scale_x = 0.0
        opacity = 1.0
    
    return {'x': base_x, 'y': base_y, 'scale_x': scale_x, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _smooth_move_in_from_top_right_dancing(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height, text_width, text_height):
    char_delay = char_index * 0.08
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 1.0 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (1.0 / cycle_time):
        move_progress = cycle_pos / (1.0 / cycle_time)
        ease_progress = 1 - math.pow(1 - move_progress, 3)
        dance_offset = math.sin(move_progress * math.pi * 4) * 10 * (1 - ease_progress)
        char_x = base_x + (1 - ease_progress) * text_width / 2 + dance_offset
        char_y = base_y - (1 - ease_progress) * text_height / 2
        opacity = ease_progress
    else:
        char_x = base_x
        char_y = base_y
        opacity = 1.0
    
    return {'x': char_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _continuous_move_in_from_bottom_center_diagonal(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width, char_height, text_width, text_height):
    char_delay = char_index * 0.1
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.8 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.8 / cycle_time):
        move_progress = cycle_pos / (0.8 / cycle_time)
        diagonal_dist = math.sqrt(text_width**2 + text_height**2) / 2
        char_x = base_x - (1 - move_progress) * diagonal_dist * 0.707
        char_y = base_y + (1 - move_progress) * diagonal_dist * 0.707
        opacity = 1.0
    else:
        char_x = base_x
        char_y = base_y
        opacity = 1.0
    
    return {'x': char_x, 'y': char_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _smooth_one_char_zoom_in_from_0_to_1(char_index, elapsed_sec, hold_time, speed, base_x, base_y):
    char_delay = char_index * 0.08
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.6 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.6 / cycle_time):
        zoom_progress = cycle_pos / (0.6 / cycle_time)
        ease_progress = 1 - math.pow(1 - zoom_progress, 3)
        scale = ease_progress
        opacity = ease_progress
    else:
        scale = 1.0
        opacity = 1.0
    
    return {'x': base_x, 'y': base_y, 'scale_x': scale, 'scale_y': scale, 'rotation': 0.0, 'opacity': opacity}


def _spread_from_center_zoom_in(char_index, text_length, elapsed_sec, hold_time, speed, base_x, base_y, text_width, text_height, text_center_x, text_center_y):
    char_delay = char_index * 0.05
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.7 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    final_char_x = base_x
    final_char_y = base_y
    
    if cycle_pos < (0.7 / cycle_time):
        zoom_progress = cycle_pos / (0.7 / cycle_time)
        scale = zoom_progress
        char_x = text_center_x + (final_char_x - text_center_x) * zoom_progress
        char_y = text_center_y + (final_char_y - text_center_y) * zoom_progress
        opacity = zoom_progress
    else:
        scale = 1.0
        char_x = final_char_x
        char_y = final_char_y
        opacity = 1.0
    
    return {'x': char_x, 'y': char_y, 'scale_x': scale, 'scale_y': scale, 'rotation': 0.0, 'opacity': opacity}


def _splintered_chars_gather_rotate_y_90(char_index, text_length, elapsed_sec, hold_time, speed, base_x, base_y, text_width):
    char_offset = char_index - text_length / 2
    char_delay = abs(char_offset) * 0.08
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.8 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.8 / cycle_time):
        gather_progress = cycle_pos / (0.8 / cycle_time)
        ease_progress = 1 - math.pow(1 - gather_progress, 3)
        rotation_y = math.pi / 2 * (1 - ease_progress)
        spread_dist = text_width / 2
        char_x = base_x - char_offset * spread_dist * (1 - ease_progress)
        scale_x = math.cos(rotation_y)
        opacity = ease_progress
    else:
        rotation_y = 0.0
        char_x = base_x
        scale_x = 1.0
        opacity = 1.0
    
    return {'x': char_x, 'y': base_y, 'scale_x': scale_x, 'scale_y': 1.0, 'rotation': 0.0, 'opacity': opacity}


def _splintered_chars_gather_rotate_continuous(char_index, text_length, elapsed_sec, hold_time, speed, base_x, base_y, text_width):
    char_offset = char_index - text_length / 2
    char_delay = abs(char_offset) * 0.08
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 0.8 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.8 / cycle_time):
        gather_progress = cycle_pos / (0.8 / cycle_time)
        ease_progress = 1 - math.pow(1 - gather_progress, 3)
        rotation = (1 - ease_progress) * math.pi * 2
        spread_dist = text_width / 2
        char_x = base_x - char_offset * spread_dist * (1 - ease_progress)
        opacity = ease_progress
    else:
        rotation = 0.0
        char_x = base_x
        opacity = 1.0
    
    return {'x': char_x, 'y': base_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': rotation, 'opacity': opacity}


def _continuous_zoom_in_out(char_index, elapsed_sec, hold_time, speed, base_x, base_y):
    char_delay = char_index * 0.05
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 1.0 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (0.5 / cycle_time):
        zoom_progress = cycle_pos / (0.5 / cycle_time)
        scale = zoom_progress
        opacity = 1.0
    elif cycle_pos < (1.0 / cycle_time):
        zoom_progress = (cycle_pos - 0.5 / cycle_time) / (0.5 / cycle_time)
        scale = 1.0 - zoom_progress
        opacity = 1.0
    else:
        scale = 0.0
        opacity = 1.0
    
    return {'x': base_x, 'y': base_y, 'scale_x': scale, 'scale_y': scale, 'rotation': 0.0, 'opacity': opacity}


def _continuous_idle_30_left_right(char_index, elapsed_sec, hold_time, speed, base_x, base_y, char_width):
    char_delay = char_index * 0.05
    char_elapsed = elapsed_sec - char_delay
    cycle_time = 1.0 + hold_time
    cycle_pos = (char_elapsed % cycle_time) / max(cycle_time, 0.001)
    
    if cycle_pos < (1.0 / cycle_time):
        idle_progress = cycle_pos / (1.0 / cycle_time)
        angle = math.sin(idle_progress * math.pi * 2) * 30
        rotation = math.radians(angle)
        offset_x = math.sin(rotation) * 10
        char_x = base_x + offset_x
        opacity = 1.0
    else:
        char_x = base_x
        rotation = 0.0
        opacity = 1.0
    
    return {'x': char_x, 'y': base_y, 'scale_x': 1.0, 'scale_y': 1.0, 'rotation': rotation, 'opacity': opacity}

