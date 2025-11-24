import ctypes
from pathlib import Path
from typing import Optional, Dict, Tuple

class HuiduSDK:
    def __init__(self):
        self.dll = None
        self._load_dll()
    
    def _load_dll(self):
        sdk_path = Path(__file__).parent.parent / "requirements" / "Huidu_Gen6SDK_V2.0.2"
        dll_paths = [
            sdk_path / "x64" / "HDSDK.dll",
            sdk_path / "HDSDK.dll"
        ]
        for dll_path in dll_paths:
            if dll_path.exists():
                try:
                    self.dll = ctypes.CDLL(str(dll_path))
                    self._setup_functions()
                    return
                except OSError:
                    pass
        raise RuntimeError("HDSDK.dll not found")
    
    def _setup_functions(self):
        self.dll.Hd_GetSDKLastError.restype = ctypes.c_int
        self.dll.Hd_CreateScreen.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_void_p, ctypes.c_int
        ]
        self.dll.Hd_CreateScreen.restype = ctypes.c_int
        self.dll.Hd_AddProgram.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_void_p, ctypes.c_int
        ]
        self.dll.Hd_AddProgram.restype = ctypes.c_int
        self.dll.Hd_AddArea.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_void_p, ctypes.c_int
        ]
        self.dll.Hd_AddArea.restype = ctypes.c_int
        self.dll.Hd_AddSimpleTextAreaItem.argtypes = [
            ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p,
            ctypes.c_int
        ]
        self.dll.Hd_AddSimpleTextAreaItem.restype = ctypes.c_int
        self.dll.Hd_AddImageAreaItem.argtypes = [
            ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int
        ]
        self.dll.Hd_AddImageAreaItem.restype = ctypes.c_int
        self.dll.Hd_AddTimeAreaItem.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_void_p, ctypes.c_int
        ]
        self.dll.Hd_AddTimeAreaItem.restype = ctypes.c_int
        self.dll.Hd_AddTempAndHumiAreaItem.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int
        ]
        self.dll.Hd_AddTempAndHumiAreaItem.restype = ctypes.c_int
        self.dll.Hd_AddCountAreaItem.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_void_p, ctypes.c_int
        ]
        self.dll.Hd_AddCountAreaItem.restype = ctypes.c_int
        self.dll.Hd_SendScreen.argtypes = [
            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_int
        ]
        self.dll.Hd_SendScreen.restype = ctypes.c_int
        self.dll.Hd_GetColor.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        self.dll.Hd_GetColor.restype = ctypes.c_int
        self.dll.Cmd_IsCardOnline.argtypes = [
            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p
        ]
        self.dll.Cmd_IsCardOnline.restype = ctypes.c_int
        self.dll.Cmd_GetScreenParam.argtypes = [
            ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ctypes.c_void_p
        ]
        self.dll.Cmd_GetScreenParam.restype = ctypes.c_int
        self.dll.Hd_SetProgramParam.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_void_p, ctypes.c_int
        ]
        self.dll.Hd_SetProgramParam.restype = ctypes.c_int
        self.dll.Hd_SaveScreen.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int
        ]
        self.dll.Hd_SaveScreen.restype = ctypes.c_int
    
    def get_last_error(self) -> int:
        return self.dll.Hd_GetSDKLastError()
    
    def create_screen(self, width: int, height: int, color: int = 1, gray: int = 1, card_type: int = 0) -> bool:
        result = self.dll.Hd_CreateScreen(width, height, color, gray, card_type, None, 0)
        return result == 0
    
    def add_program(self, border_img_path: Optional[str] = None, border_effect: int = 0, border_speed: int = 5) -> Optional[int]:
        border_ptr = None
        if border_img_path:
            border_ptr = ctypes.c_wchar_p(border_img_path)
        program_id = self.dll.Hd_AddProgram(border_ptr, border_effect, border_speed, None, 0)
        return program_id if program_id != -1 else None
    
    def add_area(self, program_id: int, x: int, y: int, width: int, height: int,
                 border_img_path: Optional[str] = None, border_effect: int = 0, border_speed: int = 5) -> Optional[int]:
        border_ptr = None
        if border_img_path:
            border_ptr = ctypes.c_wchar_p(border_img_path)
        area_id = self.dll.Hd_AddArea(program_id, x, y, width, height, border_ptr, border_effect, border_speed, None, 0)
        return area_id if area_id != -1 else None
    
    def add_text_item(self, area_id: int, text: str, font_name: str = "Arial", font_size: int = 24,
                     text_color: Tuple[int, int, int] = (255, 255, 255), bg_color: int = 0,
                     style: int = 4, show_effect: int = 0, show_speed: int = 25,
                     clear_type: int = 201, stay_time: int = 3) -> Optional[int]:
        text_w = ctypes.c_wchar_p(text)
        font_w = ctypes.c_wchar_p(font_name)
        color = self.get_color(text_color[0], text_color[1], text_color[2])
        item_id = self.dll.Hd_AddSimpleTextAreaItem(
            area_id, text_w, color, bg_color, style, font_w, font_size,
            show_effect, show_speed, clear_type, stay_time, None, 0
        )
        return item_id if item_id != -1 else None
    
    def add_image_item(self, area_id: int, image_path: str, show_effect: int = 0,
                      show_speed: int = 30, clear_type: int = 201, stay_time: int = 3) -> Optional[int]:
        path_w = ctypes.c_wchar_p(image_path)
        item_id = self.dll.Hd_AddImageAreaItem(area_id, path_w, show_effect, show_speed, clear_type, stay_time, None, 0)
        return item_id if item_id != -1 else None
    
    def add_time_item(self, area_id: int, show_date: bool = True, show_time: bool = True,
                     font_name: str = "Arial", font_size: int = 16,
                     text_color: Tuple[int, int, int] = (0, 255, 0),
                     date_style: int = 0, time_style: int = 0, diff_hour: int = 0, diff_min: int = 0) -> Optional[int]:
        font_w = ctypes.c_wchar_p(font_name)
        color = self.get_color(text_color[0], text_color[1], text_color[2])
        item_id = self.dll.Hd_AddTimeAreaItem(
            area_id, 0, 1 if show_date else 0, date_style, 0, 0,
            1 if show_time else 0, time_style, color, font_w, font_size,
            diff_hour, diff_min, None, 0
        )
        return item_id if item_id != -1 else None
    
    def add_sensor_item(self, area_id: int, sensor_type: int = 0, text_color: Tuple[int, int, int] = (255, 255, 255),
                       font_name: str = "Arial", font_size: int = 16, show_effect: int = 0,
                       show_speed: int = 25, clear_type: int = 201, stay_time: int = 3) -> Optional[int]:
        font_w = ctypes.c_wchar_p(font_name)
        color = self.get_color(text_color[0], text_color[1], text_color[2])
        item_id = self.dll.Hd_AddTempAndHumiAreaItem(
            area_id, sensor_type, 0, 0, color, font_w, font_size,
            show_effect, show_speed, clear_type, stay_time, None, 0
        )
        return item_id if item_id != -1 else None
    
    def add_count_item(self, area_id: int, count_type: int = 0, count_value: int = 0,
                      text_color: Tuple[int, int, int] = (255, 255, 255),
                      font_name: str = "Arial", font_size: int = 16, show_effect: int = 0,
                      show_speed: int = 25, clear_type: int = 201, stay_time: int = 3) -> Optional[int]:
        font_w = ctypes.c_wchar_p(font_name)
        color = self.get_color(text_color[0], text_color[1], text_color[2])
        item_id = self.dll.Hd_AddCountAreaItem(
            area_id, count_type, count_value, 0, 0, 0, 0, color, font_w, font_size,
            show_effect, show_speed, clear_type, stay_time, None, 0
        )
        return item_id if item_id != -1 else None
    
    def get_color(self, r: int, g: int, b: int) -> int:
        return self.dll.Hd_GetColor(r, g, b)
    
    def send_screen(self, ip_address: str, send_type: int = 0) -> bool:
        ip_w = ctypes.c_wchar_p(ip_address)
        result = self.dll.Hd_SendScreen(send_type, ip_w, None, None, 0)
        return result == 0
    
    def is_card_online(self, ip_address: str, send_type: int = 0) -> bool:
        ip_w = ctypes.c_wchar_p(ip_address)
        result = self.dll.Cmd_IsCardOnline(send_type, ip_w, None)
        return result == 0
    
    def get_screen_params(self, ip_address: str, send_type: int = 0) -> Optional[Dict]:
        ip_w = ctypes.c_wchar_p(ip_address)
        width = ctypes.c_int()
        height = ctypes.c_int()
        color = ctypes.c_int()
        gray = ctypes.c_int()
        card_type = ctypes.c_int()
        result = self.dll.Cmd_GetScreenParam(
            send_type, ip_w,
            ctypes.byref(width), ctypes.byref(height),
            ctypes.byref(color), ctypes.byref(gray),
            ctypes.byref(card_type), None
        )
        if result == 0:
            return {
                "width": width.value,
                "height": height.value,
                "color": color.value,
                "gray": gray.value,
                "card_type": card_type.value
            }
        return None
    
    def set_program_param(self, program_id: int, play_mode: int = 0, play_length: int = 0,
                         week_flags: int = 0, start_date: int = 0, end_date: int = 0,
                         start_time: int = 0, end_time: int = 0) -> bool:
        result = self.dll.Hd_SetProgramParam(
            program_id, play_mode, play_length, week_flags,
            start_date, end_date, start_time, end_time, 0, None, 0
        )
        return result == 0
    
    def save_screen(self, file_path: str) -> bool:
        path_w = ctypes.c_wchar_p(file_path)
        result = self.dll.Hd_SaveScreen(path_w, None, 0)
        return result == 0

