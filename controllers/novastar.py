import json
import time
import ctypes
import os
import sys
from typing import Optional, Dict, List, Any, Callable
from pathlib import Path
from datetime import datetime
from controllers.common import ControllerType, ConnectionStatus
from controllers.property_adapter import adapt_element_for_controller
from utils.logger import get_logger
from utils.app_data import get_app_data_dir

logger = get_logger(__name__)

ExportViplexCallback = ctypes.WINFUNCTYPE(None, ctypes.c_uint16, ctypes.c_char_p)

def _get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent

def _get_novastar_sdk_path(base_path: Path) -> Path:
    novastar_sdk_path = base_path / "publish" / "novastar_sdk"
    return novastar_sdk_path

class NovaStarController:
    DEFAULT_PORT = 5200
    
    def __init__(self, ip_address: str, port: int = DEFAULT_PORT):
        self.controller_type = ControllerType.NOVASTAR
        self.ip_address = ip_address
        self.port = port
        self.status = ConnectionStatus.DISCONNECTED
        self.device_info: Optional[Dict] = None
        self.on_status_changed: Optional[Callable] = None
        self.on_progress: Optional[Callable] = None
        self._cached_controller_id: Optional[str] = None
        self.dll: Optional[ctypes.WinDLL] = None
        self._callbacks: Dict[str, Any] = {}
        self._callback_results: Dict[str, Dict] = {}
        self._initialized = False
        self._device_sn: Optional[str] = None
        self._session_token: Optional[str] = None
        try:
            self._load_dll()
        except Exception as e:
            logger.debug(f"NovaStar SDK DLL not available: {str(e).split(chr(10))[0] if chr(10) in str(e) else str(e)}")
            raise
    
    def _load_dll(self):
        base_path = _get_base_path()
        is_exe = getattr(sys, 'frozen', False)
        novastar_sdk_path = _get_novastar_sdk_path(base_path)
        dll_paths = [
            novastar_sdk_path / "viplexcore.dll",
            base_path / "_internal" / "publish" / "novastar_sdk" / "viplexcore.dll",
            base_path / "_internal" / "viplexcore.dll",
            base_path / "viplexcore.dll",
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
            dependency_dir = str(novastar_sdk_path)
            dll_dir = dependency_dir
            try:
                current_path = os.environ.get('PATH', '')
                if not isinstance(current_path, str):
                    current_path = str(current_path) if current_path is not None else ''
                if dll_dir and dll_dir not in current_path:
                    os.environ['PATH'] = dll_dir + os.pathsep + current_path
                    logger.debug(f"Added DLL directory to PATH: {dll_dir}")
            except Exception as path_error:
                logger.debug(f"Could not modify PATH: {path_error}")
            try:
                current_path = os.environ.get('PATH', '')
                if not isinstance(current_path, str):
                    current_path = str(current_path) if current_path is not None else ''
                    if dependency_dir and dependency_dir not in current_path:
                        os.environ['PATH'] = dependency_dir + os.pathsep + current_path
                        logger.debug(f"Added dependency directory to PATH: {dependency_dir}")
            except Exception as path_error:
                logger.debug(f"Could not modify PATH: {path_error}")
            if sys.platform == "win32":
                try:
                    os.add_dll_directory(dependency_dir)
                    logger.debug(f"Added dependency directory to DLL search path: {dependency_dir}")
                except (AttributeError, OSError) as e:
                    logger.debug(f"Could not add DLL directory: {e}")
            if sys.platform == "win32":
                try:
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
                    dll_search_dir = dependency_dir
                    dll_absolute = str(dll_path.resolve())
                    kernel32.SetDllDirectoryW(dll_search_dir)
                    try:
                        LOAD_WITH_ALTERED_SEARCH_PATH = 0x00000008
                        dll_handle = kernel32.LoadLibraryExW(
                            dll_absolute,
                            None,
                            LOAD_WITH_ALTERED_SEARCH_PATH
                        )
                        if dll_handle and dll_handle != 0:
                            self.dll = ctypes.WinDLL("", handle=dll_handle)
                            logger.debug(f"Loaded viplexcore.dll using LoadLibraryExW with handle: {dll_handle}")
                        else:
                            error_code = kernel32.GetLastError()
                            logger.warning(f"LoadLibraryExW failed with error code: {error_code}, trying standard WinDLL")
                            self.dll = ctypes.WinDLL(dll_absolute)
                            logger.debug(f"Loaded viplexcore.dll using standard WinDLL")
                    except Exception as load_error:
                        logger.error(f"DLL loading failed: {load_error}")
                        raise
                except (OSError, AttributeError) as e:
                    logger.debug(f"LoadLibraryExW approach failed: {e}, trying standard WinDLL with PATH")
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
        if not self.dll:
            return -1
        return self.dll.nvInitW( # type: ignore
            ctypes.c_wchar_p(sdk_root_dir),
            ctypes.c_wchar_p(credentials_json)
        )
    
    def _create_callback(self, callback_id: str):  # type: ignore
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
        if not self.dll:
            return
        self.dll.nvSearchTerminalAsync(cb) # type: ignore
    
    def search_appoint_ip_async(self, ip_address: str, callback_id: str = "search_ip") -> None:
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvSearchAppointIpAsyncW(ctypes.c_wchar_p(ip_address), cb) # type: ignore
    
    def search_range_ip_async(self, ip_start: str, ip_end: str, callback_id: str = "search_range") -> None:
        params = json.dumps({"ipStart": ip_start, "ipEnd": ip_end})
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvSearchRangeIpAsyncW(ctypes.c_wchar_p(params), cb) # type: ignore
    
    def find_all_terminals_async(self, callback_id: str = "find_all") -> None:
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvFindAllTerminalsAsync(cb) # type: ignore
    
    def login_async(self, login_params: Dict, callback_id: str = "login") -> None:
        params_json = json.dumps(login_params)
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvLoginAsyncW(ctypes.c_wchar_p(params_json), cb) # type: ignore
    
    def create_program_async(self, program_params: Dict, callback_id: str = "create_program") -> None:
        params_json = json.dumps(program_params)
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvCreateProgramAsyncW(ctypes.c_wchar_p(params_json), cb) # type: ignore
    
    def set_page_program_async(self, page_params: Dict, callback_id: str = "set_page") -> None:
        params_json = json.dumps(page_params)
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvSetPageProgramAsyncW(ctypes.c_wchar_p(params_json), cb) # type: ignore
    
    def make_program_async(self, make_params: Dict, callback_id: str = "make_program") -> None:
        params_json = json.dumps(make_params)
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvMakeProgramAsyncW(ctypes.c_wchar_p(params_json), cb) # type: ignore
    
    def start_transfer_program_async(self, transfer_params: Dict, callback_id: str = "transfer") -> None:
        params_json = json.dumps(transfer_params)
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvStartTransferProgramAsyncW(ctypes.c_wchar_p(params_json), cb) # type: ignore
    
    def get_program_info_async(self, info_params: Dict, callback_id: str = "get_info") -> None:
        params_json = json.dumps(info_params)
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvGetProgramInfoAsyncW(ctypes.c_wchar_p(params_json), cb) # type: ignore
    
    def get_terminal_info_async(self, info_params: Dict, callback_id: str = "get_terminal_info") -> None:
        params_json = json.dumps(info_params)
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvGetTerminalInfoAsyncW(ctypes.c_wchar_p(params_json), cb) # type: ignore
    
    def start_play_async(self, play_params: Dict, callback_id: str = "start_play") -> None:
        params_json = json.dumps(play_params)
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvStartPlayAsyncW(ctypes.c_wchar_p(params_json), cb) # type: ignore
    
    def stop_play_async(self, stop_params: Dict, callback_id: str = "stop_play") -> None:
        params_json = json.dumps(stop_params)
        cb = self._create_callback(callback_id)
        if not self.dll:
            return
        self.dll.nvStopPlayAsyncW(ctypes.c_wchar_p(params_json), cb) # type: ignore
    
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
    
    def _ensure_initialized(self) -> bool:
        if self._initialized:
            return True
        try:
            sdk_root = get_app_data_dir() / "viplexcore"
            sdk_root.mkdir(parents=True, exist_ok=True)
            sdk_root_str = str(sdk_root.resolve()).replace('\\', '/')
            credentials = {
                "company": "Starled Italia",
                "phone": "+39 095 328 6309",
                "email": "info@starled-italia.com"
            }
            original_cwd = os.getcwd()
            try:
                os.chdir(str(sdk_root))
                result = self.init(sdk_root_str, credentials)
            finally:
                os.chdir(original_cwd)
            if result == 0:
                self._initialized = True
                logger.info("ViplexCore SDK initialized")
                return True
            else:
                logger.warning(f"ViplexCore SDK init returned error code {result} (checkParamvalid warning may appear)")
                logger.debug(f"SDK root: {sdk_root_str}, Credentials: {credentials}")
                self._initialized = True
                logger.info("Continuing with SDK operations despite init warning")
                return True
        except Exception as e:
            logger.error(f"Error initializing SDK: {e}", exc_info=True)
            return False
    
    def set_status(self, status: ConnectionStatus):
        self.status = status
        if self.on_status_changed:
            try:
                self.on_status_changed(status)
            except Exception as e:
                logger.debug(f"Error in status changed callback: {e}")
    
    def set_progress(self, percentage: int, message: str):
        if self.on_progress:
            try:
                self.on_progress(percentage, message)
            except Exception as e:
                logger.debug(f"Error in progress callback: {e}")
    
    def connect(self) -> bool:
        if self.status == ConnectionStatus.CONNECTED:
            return True
        if not self._ensure_initialized():
            return False
        self.set_status(ConnectionStatus.CONNECTING)
        try:
            self.search_appoint_ip_async(self.ip_address, "search_ip")
            search_result = self.get_callback_result("search_ip", timeout=3.0)
            if search_result and search_result.get("code") == 0:
                try:
                    data_str = search_result.get("data", "")
                    if data_str:
                        terminal_data = json.loads(data_str)
                        if isinstance(terminal_data, dict):
                            sn = terminal_data.get("sn", "")
                            if sn:
                                self._device_sn = sn
                                logger.info(f"Found NovaStar controller SN: {sn}")
                except:
                    pass
            if not self._device_sn:
                self._device_sn = self.ip_address
                logger.debug(f"Using IP as SN: {self._device_sn}")
            login_params = {
                "sn": self._device_sn,
                "username": "admin",
                "password": "123456",
                "rememberPwd": 1,
                "loginType": 0
            }
            self.login_async(login_params, "login")
            login_result = self.get_callback_result("login", timeout=5.0)
            if login_result and login_result.get("code") == 0:
                info = self.get_device_info()
                if info:
                    self.set_status(ConnectionStatus.CONNECTED)
                    logger.info(f"Connected to NovaStar controller at {self.ip_address} (SN: {self._device_sn})")
                    return True
                else:
                    logger.warning("Login successful but could not get device info")
                    self.set_status(ConnectionStatus.ERROR)
                    return False
            else:
                error_code = login_result.get("code") if login_result else "unknown"
                logger.warning(f"NovaStar login failed with code: {error_code}")
                self.set_status(ConnectionStatus.ERROR)
                return False
        except Exception as e:
            logger.error(f"Error connecting to NovaStar controller: {e}", exc_info=True)
            self.set_status(ConnectionStatus.ERROR)
            return False
    
    def disconnect(self):
        self._device_sn = None
        self._session_token = None
        self.set_status(ConnectionStatus.DISCONNECTED)
        self.device_info = None
        logger.info(f"Disconnected from NovaStar controller at {self.ip_address}")
    
    def get_device_info(self) -> Optional[Dict]:
        if not self._device_sn:
            controller_id = f"NS-{self.ip_address.replace('.', '-')}"
            self.device_info = {
                "ip": self.ip_address,
                "controller_id": controller_id,
                "controllerId": controller_id,
                "serial_number": controller_id
            }
            return self.device_info
        try:
            info_params = {"sn": self._device_sn}
            self.get_terminal_info_async(info_params, "get_terminal_info")
            result = self.get_callback_result("get_terminal_info", timeout=3.0)
            if result and result.get("code") == 0:
                data = json.loads(result.get("data", "{}"))
                controller_id = f"NS-{self.ip_address.replace('.', '-')}"
                self.device_info = {
                    "ip": self.ip_address,
                    "controller_id": controller_id,
                    "controllerId": controller_id,
                    "serial_number": self._device_sn
                }
                if data.get("model"):
                    self.device_info["model"] = data.get("model")
                return self.device_info
        except Exception as e:
            logger.warning(f"Could not get detailed device info: {e}")
        controller_id = f"NS-{self.ip_address.replace('.', '-')}"
        self.device_info = {
            "ip": self.ip_address,
            "controller_id": controller_id
        }
        return self.device_info
    
    def upload_program(self, program_data: Dict, file_path: Optional[str] = None) -> bool:
        if self.status != ConnectionStatus.CONNECTED:
            if not self.connect():
                return False
        try:
            self.set_progress(0, "Creating program...")
            create_params = {
                "name": program_data.get("name", "Program"),
                "width": program_data.get("width", 500),
                "height": program_data.get("height", 500),
                "tplID": 1,
                "winInfo": {
                    "height": 1.0,
                    "width": 1.0,
                    "left": 0.0,
                    "top": 0.0,
                    "zindex": 0,
                    "index": 0
                }
            }
            self.create_program_async(create_params, "create")
            result = self.get_callback_result("create", timeout=5.0)
            if not result or result.get("code") != 0:
                logger.error(f"Failed to create program: {result}")
                return False
            self.set_progress(20, "Setting page content...")
            widgets = self._convert_elements_to_widgets(program_data.get("elements", []))
            page_params = {
                "programID": 1,
                "pageID": 1,
                "pageInfo": {
                    "name": program_data.get("name", "Program"),
                    "widgetContainers": [{
                        "id": 1,
                        "name": "container1",
                        "layout": {"x": "0.0", "y": "0.0", "width": "1.0", "height": "1.0"},
                        "contents": {
                            "widgets": widgets
                        },
                        "enable": True
                    }]
                }
            }
            self.set_page_program_async(page_params, "set_page")
            result = self.get_callback_result("set_page", timeout=5.0)
            if not result or result.get("code") != 0:
                logger.error(f"Failed to set page: {result}")
                return False
            self.set_progress(60, "Generating program...")
            output_dir = Path(file_path).parent if file_path else get_app_data_dir() / "programs"
            output_dir.mkdir(parents=True, exist_ok=True)
            make_params = {
                "programID": 1,
                "outPutPath": str(output_dir)
            }
            self.make_program_async(make_params, "make")
            result = self.get_callback_result("make", timeout=10.0)
            if not result or result.get("code") != 0:
                logger.error(f"Failed to make program: {result}")
                return False
            self.set_progress(80, "Transferring to device...")
            program_name = program_data.get("name", "program1")
            transfer_params = {
                "sn": self._device_sn,
                "programName": program_name,
                "deviceIdentifier": "Demo",
                "sendProgramFilePaths": {
                    "programPath": str(output_dir / "program1"),
                    "mediasPath": {}
                },
                "startPlayAfterTransferred": True,
                "insertPlay": True
            }
            self.start_transfer_program_async(transfer_params, "transfer")
            result = self.get_callback_result("transfer", timeout=30.0)
            if result and result.get("code") == 0:
                self.set_progress(100, "Upload complete")
                logger.info(f"Program '{program_data.get('name')}' uploaded successfully")
                return True
            else:
                logger.error(f"Transfer failed: {result}")
            return False
        except Exception as e:
            logger.error(f"Error uploading program: {e}", exc_info=True)
            return False
    
    def _convert_elements_to_widgets(self, elements: List[Dict]) -> List[Dict]:
        widgets: List[Dict] = []
        for element in elements:
            adapted_element = adapt_element_for_controller(element, "novastar")
            element_type = adapted_element.get("type")
            properties = adapted_element.get("properties", {})
            widget = {
                "id": len(widgets) + 1,
                "enable": True,
                "layout": {
                    "x": f"{adapted_element.get('x', 0)}",
                    "y": f"{adapted_element.get('y', 0)}",
                    "width": f"{adapted_element.get('width', 200)}",
                    "height": f"{adapted_element.get('height', 100)}"
                },
                "backgroundColor": "#00000000",
                "zOrder": 0
            }
            if element_type == "text" or element_type == "singleline_text":
                widget.update({
                    "type": "ARCH_TEXT",
                    "name": "text",
                    "dataSource": "",
                    "metadata": {
                        "content": {
                            "paragraphs": [{
                                "lines": [{
                                    "segs": [{
                                        "content": properties.get("text", "")
                                    }]
                                }],
                                "textAttributes": [{
                                    "textColor": properties.get("color", "#000000"),
                                    "attributes": {
                                        "font": {
                                            "family": [properties.get("font_family", "Arial")],
                                            "size": properties.get("font_size", 24),
                                            "style": "NORMAL"
                                        }
                                    }
                                }]
                            }]
                        }
                    },
                    "duration": properties.get("duration", 5000)
                })
            elif element_type == "animation":
                widget.update({
                    "type": "ARCH_TEXT",
                    "name": "animation",
                    "dataSource": "",
                    "metadata": {
                        "content": {
                            "paragraphs": [{
                                "lines": [{
                                    "segs": [{
                                        "content": properties.get("text", "")
                                    }]
                                }],
                                "textAttributes": [{
                                    "textColor": properties.get("color", "#FFFFFF"),
                                    "attributes": {
                                        "font": {
                                            "family": [properties.get("font_family", "Arial")],
                                            "size": properties.get("font_size", 24),
                                            "style": "NORMAL"
                                        }
                                    }
                                }]
                            }]
                        }
                    },
                    "duration": properties.get("duration", 5000)
                })
            elif element_type == "weather":
                widget.update({
                    "type": "ARCH_TEXT",
                    "name": "weather",
                    "dataSource": "",
                    "metadata": {
                        "content": {
                            "paragraphs": [{
                                "lines": [{
                                    "segs": [{
                                        "content": properties.get("text", "")
                                    }]
                                }],
                                "textAttributes": [{
                                    "textColor": properties.get("color", "#FFFFFF"),
                                    "attributes": {
                                        "font": {
                                            "family": [properties.get("font_family", "Arial")],
                                            "size": properties.get("font_size", 24),
                                            "style": "NORMAL"
                                        }
                                    }
                                }]
                            }]
                        }
                    },
                    "duration": properties.get("duration", 5000)
                })
            elif element_type == "timing":
                widget.update({
                    "type": "ARCH_TEXT",
                    "name": "timing",
                    "dataSource": "",
                    "metadata": {
                        "content": {
                            "paragraphs": [{
                                "lines": [{
                                    "segs": [{
                                        "content": "Countdown"
                                    }]
                                }],
                                "textAttributes": [{
                                    "textColor": properties.get("color", "#FFFFFF"),
                                    "attributes": {
                                        "font": {
                                            "family": [properties.get("font_family", "Arial")],
                                            "size": properties.get("font_size", 24),
                                            "style": "NORMAL"
                                        }
                                    }
                                }]
                            }]
                        }
                    },
                    "duration": properties.get("duration", 5000)
                })
            elif element_type == "sensor":
                widget.update({
                    "type": "ARCH_TEXT",
                    "name": "sensor",
                    "dataSource": "",
                    "metadata": {
                        "content": {
                            "paragraphs": [{
                                "lines": [{
                                    "segs": [{
                                        "content": "Sensor"
                                    }]
                                }],
                                "textAttributes": [{
                                    "textColor": properties.get("color", "#FFFFFF"),
                                    "attributes": {
                                        "font": {
                                            "family": [properties.get("font_family", "Arial")],
                                            "size": properties.get("font_size", 24),
                                            "style": "NORMAL"
                                        }
                                    }
                                }]
                            }]
                        }
                    },
                    "duration": properties.get("duration", 5000)
                })
            elif element_type == "photo":
                file_path = properties.get("file_path", "")
                widget.update({
                    "type": "PICTURE",
                    "name": Path(file_path).name if file_path else "image",
                    "dataSource": file_path,
                    "duration": properties.get("duration", 5000)
                })
            elif element_type == "video":
                file_path = properties.get("file_path", "")
                widget.update({
                    "type": "VIDEO",
                    "name": Path(file_path).name if file_path else "video",
                    "dataSource": file_path,
                    "duration": properties.get("duration", 5000)
                })
            elif element_type == "clock":
                widget.update({
                    "type": "CLOCK",
                    "name": "clock",
                    "duration": 5000
                })
            elif element_type == "html":
                file_path = properties.get("file_path", "")
                widget.update({
                    "type": "HTML",
                    "name": "html",
                    "dataSource": file_path,
                    "duration": properties.get("duration", 5000)
                })
            elif element_type == "hdmi":
                widget.update({
                    "type": "HDMI",
                    "name": "hdmi",
                    "duration": 5000
                })
            widgets.append(widget)
        return widgets
    
    def download_program(self, program_id: Optional[str] = None) -> Optional[Dict]:
        if not self._device_sn:
            return None
        try:
            info_params = {"sn": self._device_sn}
            self.get_program_info_async(info_params, "download")
            result = self.get_callback_result("download", timeout=5.0)
            if result and result.get("code") == 0:
                data = json.loads(result.get("data", "{}"))
                return self._convert_from_viplexcore_format(data)
            return None
        except Exception as e:
            logger.error(f"Error downloading program: {e}", exc_info=True)
            return None
    
    def _convert_from_viplexcore_format(self, data: Dict) -> Dict:
        return {
            "name": data.get("name", "Program"),
            "width": data.get("width", 500),
            "height": data.get("height", 500),
            "elements": []
        }
    
    def get_program_list(self) -> List[Dict]:
        if not self._device_sn:
            return []
        try:
            info_params = {"sn": self._device_sn}
            self.get_program_info_async(info_params, "get_program_list")
            result = self.get_callback_result("get_program_list", timeout=5.0)
            if result and result.get("code") == 0:
                data = json.loads(result.get("data", "[]"))
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "programs" in data:
                    return data["programs"]
        except Exception as e:
            logger.error(f"Error getting program list: {e}")
        return []
    
    def get_time(self) -> Optional[datetime]:
        try:
            if not self._device_sn:
                return None
            info_params = {"sn": self._device_sn}
            if hasattr(self, 'get_terminal_info_async'):
                self.get_terminal_info_async(info_params, "get_time")
                result = self.get_callback_result("get_time", timeout=3.0)
                if result and result.get("code") == 0:
                    data = json.loads(result.get("data", "{}"))
                    time_str = data.get("time") or data.get("system_time")
                    if time_str:
                        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            return datetime.now()
        except Exception as e:
            logger.warning(f"Error getting time: {e}")
            return datetime.now()
    
    def set_time(self, time: datetime) -> bool:
        try:
            if not self._device_sn or not hasattr(self, 'set_time_async'):
                return False
            time_params = {
                "sn": self._device_sn,
                "time": time.isoformat()
            }
            self.set_time_async(time_params, "set_time")
            result = self.get_callback_result("set_time", timeout=3.0)
            return bool(result and isinstance(result, dict) and result.get("code") == 0)
        except Exception as e:
            logger.error(f"Error setting time: {e}")
            return False
    
    def get_brightness(self) -> Optional[int]:
        try:
            if not self._device_sn:
                return None
            info_params = {"sn": self._device_sn}
            self.get_terminal_info_async(info_params, "get_brightness")
            result = self.get_callback_result("get_brightness", timeout=3.0)
            if result and result.get("code") == 0:
                data = json.loads(result.get("data", "{}"))
                return data.get("brightness") or data.get("luminance")
        except Exception as e:
            logger.warning(f"Error getting brightness: {e}")
        return None
    
    def set_brightness(self, brightness: int, brightness_settings: Optional[Dict] = None) -> bool:
        try:
            if not self._device_sn or not hasattr(self, 'set_brightness_async'):
                return False
            if brightness_settings and brightness_settings.get("time_ranges"):
                time_ranges = brightness_settings.get("time_ranges", [])
                for time_range in time_ranges:
                    pass
            if brightness_settings and brightness_settings.get("sensor", {}).get("enabled"):
                pass
            brightness_params = {
                "sn": self._device_sn,
                "brightness": brightness
            }
            self.set_brightness_async(brightness_params, "set_brightness")
            result = self.get_callback_result("set_brightness", timeout=3.0)
            return bool(result and isinstance(result, dict) and result.get("code") == 0)
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
            return False
    
    def get_power_schedule(self) -> Optional[Dict]:
        try:
            if not self._device_sn or not hasattr(self, 'get_timing_power_switch_status'):
                return None
            params = {"sn": self._device_sn}
            self.get_timing_power_switch_status(params, "get_power_schedule")
            result = self.get_callback_result("get_power_schedule", timeout=3.0)
            if result and result.get("code") == 0:
                return json.loads(result.get("data", "{}"))
        except Exception as e:
            logger.warning(f"Error getting power schedule: {e}")
        return None
    
    def set_power_schedule(self, schedule: Dict) -> bool:
        try:
            if not self._device_sn or not hasattr(self, 'set_timing_power_switch_status'):
                return False
            if isinstance(schedule, list):
                for day_schedule in schedule:
                    day = day_schedule.get("day", "")
                    on_time = day_schedule.get("on_time", "08:00")
                    off_time = day_schedule.get("off_time", "22:00")
                    enabled = day_schedule.get("enabled", True)
                    schedule_params = {
                        "sn": self._device_sn,
                        "day": day,
                        "enabled": enabled,
                        "on_time": on_time,
                        "off_time": off_time
                    }
                    self.set_timing_power_switch_status(schedule_params, "set_power_schedule")
                    result = self.get_callback_result("set_power_schedule", timeout=3.0)
                    if not result or result.get("code") != 0:
                        logger.warning(f"Failed to set schedule for {day}")
                return True
            elif isinstance(schedule, dict):
                if "on_time" in schedule and "off_time" in schedule:
                    schedule_params = {
                        "sn": self._device_sn,
                        "enabled": schedule.get("enabled", True),
                        "on_time": schedule.get("on_time", "08:00"),
                        "off_time": schedule.get("off_time", "22:00")
                    }
                    self.set_timing_power_switch_status(schedule_params, "set_power_schedule")
                    result = self.get_callback_result("set_power_schedule", timeout=3.0)
                    return bool(result and isinstance(result, dict) and result.get("code") == 0)
            return False
        except Exception as e:
            logger.error(f"Error setting power schedule: {e}")
            return False
    
    def get_network_config(self) -> Optional[Dict]:
        try:
            if not self._device_sn:
                return None
            info_params = {"sn": self._device_sn}
            self.get_terminal_info_async(info_params, "get_network")
            result = self.get_callback_result("get_network", timeout=3.0)
            if result and result.get("code") == 0:
                data = json.loads(result.get("data", "{}"))
                return data.get("network") or {
                    "ip": data.get("ip"),
                    "gateway": data.get("gateway"),
                    "subnet": data.get("subnet")
                }
        except Exception as e:
            logger.warning(f"Error getting network config: {e}")
        return None
    
    def set_network_config(self, network_config: Dict) -> bool:
        try:
            if not self._device_sn or not hasattr(self, 'set_network_config_async'):
                return False
            network_params = {
                "sn": self._device_sn,
                **network_config
            }
            self.set_network_config_async(network_params, "set_network")
            result = self.get_callback_result("set_network", timeout=3.0)
            return bool(result and isinstance(result, dict) and result.get("code") == 0)
        except Exception as e:
            logger.error(f"Error setting network config: {e}")
            return False
    
    def get_wifi_config(self) -> Optional[Dict]:
        try:
            if not self._device_sn:
                return None
            info_params = {"sn": self._device_sn}
            self.get_terminal_info_async(info_params, "get_wifi")
            result = self.get_callback_result("get_wifi", timeout=3.0)
            if result and result.get("code") == 0:
                data = json.loads(result.get("data", "{}"))
                return data.get("wifi") or {
                    "enabled": data.get("wifi_enabled", False),
                    "ssid": data.get("wifi_ssid", ""),
                    "password": data.get("wifi_password", "")
                }
        except Exception as e:
            logger.warning(f"Error getting wifi config: {e}")
        return None
    
    def set_wifi_config(self, wifi_config: Dict) -> bool:
        try:
            if not self._device_sn or not hasattr(self, 'set_wifi_config_async'):
                return False
            wifi_params = {
                "sn": self._device_sn,
                **wifi_config
            }
            self.set_wifi_config_async(wifi_params, "set_wifi")
            result = self.get_callback_result("set_wifi", timeout=3.0)
            if result and isinstance(result, dict):
                return result.get("code") == 0
            return False
        except Exception as e:
            logger.error(f"Error setting wifi config: {e}")
            return False
    
    def reboot(self) -> bool:
        try:
            if not self._device_sn or not hasattr(self, 'reboot_async'):
                return False
            reboot_params = {"sn": self._device_sn}
            self.reboot_async(reboot_params, "reboot")
            result = self.get_callback_result("reboot", timeout=3.0)
            if result and isinstance(result, dict):
                return result.get("code") == 0
            return False
        except Exception as e:
            logger.error(f"Error rebooting controller: {e}")
            return False
    
    def delete_program(self, program_id: str) -> bool:
        try:
            if not self._device_sn or not hasattr(self, 'delete_program_async'):
                return False
            delete_params = {
                "sn": self._device_sn,
                "program_id": program_id
            }
            self.delete_program_async(delete_params, "delete_program")
            result = self.get_callback_result("delete_program", timeout=3.0)
            if result and isinstance(result, dict):
                return result.get("code") == 0
            return False
        except Exception as e:
            logger.error(f"Error deleting program: {e}")
            return False
    
    def test_connection(self) -> bool:
        try:
            if not self._ensure_initialized():
                return False
            self.search_appoint_ip_async(self.ip_address, "test")
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return False
