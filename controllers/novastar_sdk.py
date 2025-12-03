import ctypes
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict
from ctypes import wintypes
from utils.logger import get_logger

logger = get_logger(__name__)

ExportViplexCallback = ctypes.WINFUNCTYPE(None, ctypes.c_uint16, ctypes.c_char_p)

def _get_base_path():
    """Get base path that works both as script and as executable"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent

def _get_novastar_sdk_path(base_path: Path) -> Path:
    novastar_sdk_path = base_path / "publish" / "novastar_sdk"
    return novastar_sdk_path

class ViplexCoreSDK:
    def __init__(self):
        self.dll = None
        try:
            self._load_dll()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.debug(f"NovaStar SDK DLL not available: {str(e).split(chr(10))[0] if chr(10) in str(e) else str(e)}")
            raise
        self._callbacks = {}
        self._callback_results = {}
    
    def _load_dll(self):
        base_path = _get_base_path()
        is_exe = getattr(sys, 'frozen', False)
        
        # Get path to publish/novastar_sdk/ where DLLs should be located
        novastar_sdk_path = _get_novastar_sdk_path(base_path)
        
        # DLL search paths - prioritize publish/novastar_sdk/
        dll_paths = [
            novastar_sdk_path / "viplexcore.dll",  # Primary location: publish/novastar_sdk/
            base_path / "_internal" / "publish" / "novastar_sdk" / "viplexcore.dll",  # _internal folder (PyInstaller onedir mode)
            base_path / "_internal" / "viplexcore.dll",  # _internal folder (fallback)
            base_path / "viplexcore.dll",  # Root directory (fallback)
        ]
        
        dll_path = None
        for path in dll_paths:
            if path.exists():
                dll_path = path
                break
        
        if not dll_path:
            error_msg = f"viplexcore.dll not found. Searched locations:\n"
            for p in dll_paths:
                error_msg += f"  - {p} ({'EXISTS' if p.exists() else 'NOT FOUND'})\n"
            error_msg += f"\nExpected location: {novastar_sdk_path / 'viplexcore.dll'}\n"
            if is_exe:
                error_msg += f"\nNOTE: When running as executable, DLLs should be in: {base_path}\n"
                error_msg += "Make sure build_exe.spec includes all required DLLs in the binaries section."
            raise RuntimeError(error_msg)
        
        try:
            # Use publish/novastar_sdk/ as the dependency directory (all DLLs are there)
            dependency_dir = str(novastar_sdk_path)
            dll_dir = dependency_dir
            
            # Add DLL directory to PATH
            try:
                current_path = os.environ.get('PATH', '')
                if not isinstance(current_path, str):
                    current_path = str(current_path) if current_path is not None else ''
                if dll_dir and dll_dir not in current_path:
                    os.environ['PATH'] = dll_dir + os.pathsep + current_path
                    logger.debug(f"Added DLL directory to PATH: {dll_dir}")
            except Exception as path_error:
                logger.debug(f"Could not modify PATH: {path_error}")
            
            # Add dependency directory to PATH (prepend for priority)
                try:
                    current_path = os.environ.get('PATH', '')
                    if not isinstance(current_path, str):
                        current_path = str(current_path) if current_path is not None else ''
                        if dependency_dir and dependency_dir not in current_path:
                            os.environ['PATH'] = dependency_dir + os.pathsep + current_path
                            logger.debug(f"Added dependency directory to PATH: {dependency_dir}")
                except Exception as path_error:
                    logger.debug(f"Could not modify PATH: {path_error}")
                
                # Also use os.add_dll_directory for Windows (Python 3.8+)
                if sys.platform == "win32":
                    try:
                        os.add_dll_directory(dependency_dir)
                        logger.debug(f"Added dependency directory to DLL search path: {dependency_dir}")
                    except (AttributeError, OSError) as e:
                        logger.debug(f"Could not add DLL directory: {e}")
            
            # Use LoadLibraryEx approach for better dependency resolution
            if sys.platform == "win32":
                try:
                    # Check if windll is available
                    if not hasattr(ctypes, 'windll') or ctypes.windll is None:
                        raise AttributeError("ctypes.windll is not available")
                    kernel32 = ctypes.windll.kernel32
                    if kernel32 is None:
                        raise AttributeError("kernel32 is not available")
                    kernel32.SetDllDirectoryW.argtypes = [ctypes.c_wchar_p]
                    kernel32.SetDllDirectoryW.restype = ctypes.c_bool
                    kernel32.LoadLibraryExW.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p, ctypes.c_uint32]
                    kernel32.LoadLibraryExW.restype = ctypes.c_void_p
                    kernel32.GetLastError.argtypes = []
                    kernel32.GetLastError.restype = ctypes.c_uint32
                    
                    # Set DLL directory to publish/novastar_sdk/ where all dependencies are
                    dll_search_dir = dependency_dir
                    dll_absolute = str(dll_path.resolve())
                    
                    # CRITICAL: Set DLL directory BEFORE any DLL operations
                    # This must remain active during the entire loading process
                    kernel32.SetDllDirectoryW(dll_search_dir)
                    
                    try:
                        LOAD_WITH_ALTERED_SEARCH_PATH = 0x00000008
                        
                        # Try LoadLibraryExW with altered search path
                        dll_handle = kernel32.LoadLibraryExW(
                            dll_absolute,
                            None,
                            LOAD_WITH_ALTERED_SEARCH_PATH
                        )
                        
                        if dll_handle and dll_handle != 0:
                            # Use WinDLL for Windows DLLs (stdcall calling convention)
                            self.dll = ctypes.WinDLL("", handle=dll_handle)
                            logger.debug(f"Loaded viplexcore.dll using LoadLibraryExW with handle: {dll_handle}")
                        else:
                            error_code = kernel32.GetLastError()
                            logger.warning(f"LoadLibraryExW failed with error code: {error_code}, trying standard WinDLL")
                            # SetDllDirectoryW is still active, so dependencies should be found
                            self.dll = ctypes.WinDLL(dll_absolute)
                            logger.debug(f"Loaded viplexcore.dll using standard WinDLL")
                    except Exception as load_error:
                        logger.error(f"DLL loading failed: {load_error}")
                        raise
                    finally:
                        # Keep DLL directory active for the lifetime of the DLL
                        # DO NOT reset it here - it's needed for DLL to function
                        pass
                except (OSError, AttributeError) as e:
                    logger.debug(f"LoadLibraryExW approach failed: {e}, trying standard WinDLL with PATH")
                    # Fallback: Ensure PATH is set and try standard loading
                    kernel32.SetDllDirectoryW(dependency_dir)
                    self.dll = ctypes.WinDLL(str(dll_path))
            else:
                self.dll = ctypes.WinDLL(str(dll_path))
            
            self._setup_functions()
            logger.info(f"NovaStar SDK: Loaded viplexcore.dll from {dll_path}")
        except OSError as e:
            error_msg = f"Failed to load viplexcore.dll from {dll_path}\n"
            error_msg += f"Error: {e}\n"
            error_msg += f"\nDependency DLLs should be in: {novastar_sdk_path}\n"
            error_msg += f"Make sure all DLLs are copied to: {novastar_sdk_path}"
            if is_exe:
                error_msg += f"\n\nNOTE: When running as executable, DLLs should be in: {base_path}\n"
                error_msg += "Make sure build_exe.spec includes all required DLLs in the binaries section."
            raise RuntimeError(error_msg)
    
    def _setup_functions(self):
        self.dll.nvInit.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.dll.nvInit.restype = ctypes.c_int
        self.dll.nvInitW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
        self.dll.nvInitW.restype = ctypes.c_int
        self.dll.nvSearchTerminalAsync.argtypes = [ExportViplexCallback]
        self.dll.nvSearchTerminalAsync.restype = None
        self.dll.nvSearchTerminalAsyncW.argtypes = [ExportViplexCallback]
        self.dll.nvSearchTerminalAsyncW.restype = None
        self.dll.nvSearchAppointIpAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvSearchAppointIpAsync.restype = None
        self.dll.nvSearchAppointIpAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvSearchAppointIpAsyncW.restype = None
        self.dll.nvSearchRangeIpAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvSearchRangeIpAsync.restype = None
        self.dll.nvSearchRangeIpAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvSearchRangeIpAsyncW.restype = None
        self.dll.nvFindAllTerminalsAsync.argtypes = [ExportViplexCallback]
        self.dll.nvFindAllTerminalsAsync.restype = None
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
    
    def search_range_ip_async(self, ip_start: str, ip_end: str, callback_id: str = "search_range") -> None:
        params = json.dumps({"ipStart": ip_start, "ipEnd": ip_end})
        cb = self._create_callback(callback_id)
        self.dll.nvSearchRangeIpAsyncW(ctypes.c_wchar_p(params), cb)
    
    def find_all_terminals_async(self, callback_id: str = "find_all") -> None:
        cb = self._create_callback(callback_id)
        self.dll.nvFindAllTerminalsAsync(cb)
    
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

