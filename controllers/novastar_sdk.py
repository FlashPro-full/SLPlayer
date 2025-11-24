import ctypes
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict
from ctypes import wintypes

ExportViplexCallback = ctypes.WINFUNCTYPE(None, ctypes.c_uint16, ctypes.c_char_p)

class ViplexCoreSDK:
    def __init__(self):
        self.dll = None
        self._load_dll()
        self._callbacks = {}
        self._callback_results = {}
    
    def _load_dll(self):
        sdk_path = Path(__file__).parent.parent / "requirements" / "ViplexCore3.6.3.0101.CTM21.11.1_x64" / "bin"
        dll_path = sdk_path / "viplexcore.dll"
        if not dll_path.exists():
            raise RuntimeError(f"viplexcore.dll not found at {dll_path}")
        try:
            os.environ['PATH'] = str(sdk_path) + os.pathsep + os.environ.get('PATH', '')
            self.dll = ctypes.CDLL(str(dll_path))
            self._setup_functions()
        except OSError as e:
            raise RuntimeError(f"Failed to load viplexcore.dll: {e}")
    
    def _setup_functions(self):
        self.dll.nvInit.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.dll.nvInit.restype = ctypes.c_int
        self.dll.nvInitW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
        self.dll.nvInitW.restype = ctypes.c_int
        self.dll.nvSearchTerminalAsync.argtypes = [ExportViplexCallback]
        self.dll.nvSearchTerminalAsync.restype = None
        self.dll.nvSearchAppointIpAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvSearchAppointIpAsync.restype = None
        self.dll.nvSearchAppointIpAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvSearchAppointIpAsyncW.restype = None
        self.dll.nvLoginAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvLoginAsync.restype = None
        self.dll.nvLoginAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvLoginAsyncW.restype = None
        self.dll.nvCreateProgramAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvCreateProgramAsync.restype = None
        self.dll.nvCreateProgramAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvCreateProgramAsyncW.restype = None
        self.dll.nvSetPageProgramAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvSetPageProgramAsync.restype = None
        self.dll.nvSetPageProgramAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvSetPageProgramAsyncW.restype = None
        self.dll.nvMakeProgramAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvMakeProgramAsync.restype = None
        self.dll.nvMakeProgramAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvMakeProgramAsyncW.restype = None
        self.dll.nvStartTransferProgramAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvStartTransferProgramAsync.restype = None
        self.dll.nvStartTransferProgramAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvStartTransferProgramAsyncW.restype = None
        self.dll.nvGetProgramInfoAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvGetProgramInfoAsync.restype = None
        self.dll.nvGetProgramInfoAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvGetProgramInfoAsyncW.restype = None
        self.dll.nvGetTerminalInfoAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvGetTerminalInfoAsync.restype = None
        self.dll.nvGetTerminalInfoAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvGetTerminalInfoAsyncW.restype = None
        self.dll.nvStartPlayAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvStartPlayAsync.restype = None
        self.dll.nvStartPlayAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvStartPlayAsyncW.restype = None
        self.dll.nvStopPlayAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvStopPlayAsync.restype = None
        self.dll.nvStopPlayAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvStopPlayAsyncW.restype = None
    
    def init(self, sdk_root_dir: str, credentials: Dict) -> int:
        credentials_json = json.dumps(credentials)
        return self.dll.nvInitW(
            ctypes.c_wchar_p(sdk_root_dir),
            ctypes.c_wchar_p(credentials_json)
        )
    
    def _create_callback(self, callback_id: str) -> ExportViplexCallback:
        def callback(code: int, data: bytes):
            data_str = data.decode('utf-8') if data else ""
            self._callback_results[callback_id] = {
                "code": code,
                "data": data_str
            }
        cb = ExportViplexCallback(callback)
        self._callbacks[callback_id] = cb
        return cb
    
    def search_terminal_async(self, callback_id: str = "search") -> None:
        cb = self._create_callback(callback_id)
        self.dll.nvSearchTerminalAsync(cb)
    
    def search_appoint_ip_async(self, ip_address: str, callback_id: str = "search_ip") -> None:
        cb = self._create_callback(callback_id)
        self.dll.nvSearchAppointIpAsyncW(ctypes.c_wchar_p(ip_address), cb)
    
    def login_async(self, login_params: Dict, callback_id: str = "login") -> None:
        params_json = json.dumps(login_params)
        cb = self._create_callback(callback_id)
        self.dll.nvLoginAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def create_program_async(self, program_params: Dict, callback_id: str = "create_program") -> None:
        params_json = json.dumps(program_params)
        cb = self._create_callback(callback_id)
        self.dll.nvCreateProgramAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def set_page_program_async(self, page_params: Dict, callback_id: str = "set_page") -> None:
        params_json = json.dumps(page_params)
        cb = self._create_callback(callback_id)
        self.dll.nvSetPageProgramAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def make_program_async(self, make_params: Dict, callback_id: str = "make_program") -> None:
        params_json = json.dumps(make_params)
        cb = self._create_callback(callback_id)
        self.dll.nvMakeProgramAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def start_transfer_program_async(self, transfer_params: Dict, callback_id: str = "transfer") -> None:
        params_json = json.dumps(transfer_params)
        cb = self._create_callback(callback_id)
        self.dll.nvStartTransferProgramAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def get_program_info_async(self, info_params: Dict, callback_id: str = "get_info") -> None:
        params_json = json.dumps(info_params)
        cb = self._create_callback(callback_id)
        self.dll.nvGetProgramInfoAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def get_terminal_info_async(self, info_params: Dict, callback_id: str = "get_terminal_info") -> None:
        params_json = json.dumps(info_params)
        cb = self._create_callback(callback_id)
        self.dll.nvGetTerminalInfoAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def start_play_async(self, play_params: Dict, callback_id: str = "start_play") -> None:
        params_json = json.dumps(play_params)
        cb = self._create_callback(callback_id)
        self.dll.nvStartPlayAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def stop_play_async(self, stop_params: Dict, callback_id: str = "stop_play") -> None:
        params_json = json.dumps(stop_params)
        cb = self._create_callback(callback_id)
        self.dll.nvStopPlayAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def get_callback_result(self, callback_id: str, timeout: float = 5.0) -> Optional[Dict]:
        start_time = time.time()
        while callback_id not in self._callback_results:
            if time.time() - start_time > timeout:
                return None
            time.sleep(0.1)
        result = self._callback_results.pop(callback_id, None)
        return result
    
    def clear_callback_result(self, callback_id: str):
        self._callback_results.pop(callback_id, None)

