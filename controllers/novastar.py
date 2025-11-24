import json
import time
from typing import Optional, Dict, List
from pathlib import Path
from controllers.base_controller import BaseController, ControllerType, ConnectionStatus
from controllers.novastar_sdk import ViplexCoreSDK
from utils.logger import get_logger
from utils.app_data import get_app_data_dir

logger = get_logger(__name__)

class NovaStarController(BaseController):
    DEFAULT_PORT = 5200
    
    def __init__(self, ip_address: str, port: int = DEFAULT_PORT):
        super().__init__(ControllerType.NOVASTAR, ip_address, port)
        self.sdk = ViplexCoreSDK()
        self._initialized = False
        self._device_sn: Optional[str] = None
        self._session_token: Optional[str] = None
    
    def _ensure_initialized(self) -> bool:
        if self._initialized:
            return True
        try:
            sdk_root = get_app_data_dir() / "viplexcore"
            sdk_root.mkdir(parents=True, exist_ok=True)
            credentials = {
                "company": "SLPlayer",
                "phone": "",
                "email": ""
            }
            result = self.sdk.init(str(sdk_root), credentials)
            if result == 0:
                self._initialized = True
                logger.info("ViplexCore SDK initialized")
                return True
            else:
                logger.error(f"Failed to initialize ViplexCore SDK: error {result}")
                return False
        except Exception as e:
            logger.error(f"Error initializing SDK: {e}", exc_info=True)
            return False
    
    def connect(self) -> bool:
        if self.status == ConnectionStatus.CONNECTED:
            return True
        if not self._ensure_initialized():
            return False
        self.set_status(ConnectionStatus.CONNECTING)
        try:
            self.sdk.search_appoint_ip_async(self.ip_address, "search")
            time.sleep(2)
            login_params = {
                "sn": self.ip_address,
                "username": "admin",
                "password": "123456",
                "rememberPwd": 1,
                "loginType": 0
            }
            self.sdk.login_async(login_params, "login")
            result = self.sdk.get_callback_result("login", timeout=5.0)
            if result and result.get("code") == 0:
                self._device_sn = str(self.ip_address)
                info = self.get_device_info()
                if info:
                    self.set_status(ConnectionStatus.CONNECTED)
                    logger.info(f"Connected to NovaStar controller at {self.ip_address}")
                    return True
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
                "name": "NovaStar Controller",
                "model": "Unknown",
                "version": "3.6.3",
                "ip": self.ip_address,
                "controller_id": controller_id,
                "controllerId": controller_id,
                "serial_number": controller_id
            }
            return self.device_info
        try:
            info_params = {"sn": self._device_sn}
            self.sdk.get_terminal_info_async(info_params, "get_terminal_info")
            result = self.sdk.get_callback_result("get_terminal_info", timeout=3.0)
            if result and result.get("code") == 0:
                data = json.loads(result.get("data", "{}"))
                controller_id = f"NS-{self.ip_address.replace('.', '-')}"
                self.device_info = {
                    "name": "NovaStar Controller",
                    "model": data.get("model", "Unknown"),
                    "version": "3.6.3",
                    "ip": self.ip_address,
                    "controller_id": controller_id,
                    "controllerId": controller_id,
                    "serial_number": self._device_sn
                }
                return self.device_info
        except Exception as e:
            logger.warning(f"Could not get detailed device info: {e}")
        controller_id = f"NS-{self.ip_address.replace('.', '-')}"
        self.device_info = {
            "name": "NovaStar Controller",
            "model": "Unknown",
            "version": "3.6.3",
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
            self.sdk.create_program_async(create_params, "create")
            result = self.sdk.get_callback_result("create", timeout=5.0)
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
            self.sdk.set_page_program_async(page_params, "set_page")
            result = self.sdk.get_callback_result("set_page", timeout=5.0)
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
            self.sdk.make_program_async(make_params, "make")
            result = self.sdk.get_callback_result("make", timeout=10.0)
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
            self.sdk.start_transfer_program_async(transfer_params, "transfer")
            result = self.sdk.get_callback_result("transfer", timeout=30.0)
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
            element_type = element.get("type")
            properties = element.get("properties", {})
            widget = {
                "id": len(widgets) + 1,
                "enable": True,
                "layout": {
                    "x": f"{element.get('x', 0)}",
                    "y": f"{element.get('y', 0)}",
                    "width": f"{element.get('width', 200)}",
                    "height": f"{element.get('height', 100)}"
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
            self.sdk.get_program_info_async(info_params, "download")
            result = self.sdk.get_callback_result("download", timeout=5.0)
            if result and result.get("code") == 0:
                data = json.loads(result.get("data", "{}"))
                return self._convert_from_viplexcore_format(data)
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
        return []
    
    def test_connection(self) -> bool:
        try:
            if not self._ensure_initialized():
                return False
            self.sdk.search_appoint_ip_async(self.ip_address, "test")
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return False

