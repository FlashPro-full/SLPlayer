import socket
import threading
import time
import json
import ctypes
from typing import List, Dict, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal
from utils.logger import get_logger
from utils.app_data import get_app_data_dir

logger = get_logger(__name__)

class ControllerInfo:

    def __init__(self, ip: str, port: int, controller_type: str = "unknown", name: str = ""):
        self.ip = ip
        self.port = port
        self.controller_type = controller_type
        self.name = name or f"{controller_type}_{ip}"
        self.mac_address = ""
        self.firmware_version = ""
        self.display_resolution = ""
        self.model = ""
        self.display_name = ""
        self.last_seen = time.time()
        self.program_count = 0
        self.media_count = 0
        self.programs: List[Dict] = []
        self.media_files: List[str] = []
    
    def to_dict(self) -> Dict:
        return {
            "ip": self.ip,
            "port": self.port,
            "controller_type": self.controller_type,
            "name": self.name,
            "mac_address": self.mac_address,
            "firmware_version": self.firmware_version,
            "display_resolution": self.display_resolution,
            "model": self.model,
            "display_name": self.display_name,
            "program_count": self.program_count,
            "media_count": self.media_count,
            "programs": self.programs,
            "media_files": self.media_files
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ControllerInfo':
        info = cls(data.get("ip", ""), data.get("port", 5200), 
                  data.get("controller_type", "unknown"), data.get("name", ""))
        info.mac_address = data.get("mac_address", "")
        info.firmware_version = data.get("firmware_version", "")
        info.display_resolution = data.get("display_resolution", "")
        info.model = data.get("model", "")
        info.display_name = data.get("display_name", "")
        info.program_count = data.get("program_count", 0)
        info.media_count = data.get("media_count", 0)
        info.programs = data.get("programs", [])
        info.media_files = data.get("media_files", [])
        return info


class ControllerDiscovery(QObject):
    controller_found = pyqtSignal(object)
    discovery_finished = pyqtSignal()
    
    NOVASTAR_PORTS = [5200]
    HUIDU_PORTS = [30080]
    COMMON_PORTS = NOVASTAR_PORTS + HUIDU_PORTS
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.discovered_controllers: List[ControllerInfo] = []
        self.is_scanning = False
        self.scan_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self._novastar_sdk = None
        self._huidu_sdk = None
        self._novastar_initialized = False
        self._callback_refs = []
    
    def _init_novastar_sdk(self) -> bool:
        if self._novastar_initialized:
            return True
        try:
            from controllers.novastar_sdk import ViplexCoreSDK
            if self._novastar_sdk is None:
                try:
                    self._novastar_sdk = ViplexCoreSDK()
                except RuntimeError as e:
                    logger.error(f"NovaStar SDK DLL load failed: {e}")
                    return False
                except Exception as e:
                    logger.error(f"NovaStar SDK creation failed: {e}", exc_info=True)
                    return False
            
            import os
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
                result = self._novastar_sdk.init(sdk_root_str, credentials)
            finally:
                os.chdir(original_cwd)
            if result == 0:
                self._novastar_initialized = True
                logger.info("NovaStar SDK initialized successfully for discovery")
                return True
            else:
                logger.warning(f"NovaStar SDK init returned error code {result} (checkParamvalid warning may appear - this is often non-fatal)")
                logger.info(f"SDK root: {sdk_root_str}")
                logger.debug(f"Credentials: {credentials}")
                self._novastar_initialized = True
                logger.info("Attempting NovaStar discovery (search may work despite init warning)")
                return True
        except Exception as e:
            error_msg = str(e).split(chr(10))[0] if chr(10) in str(e) else str(e)
            logger.error(f"NovaStar SDK initialization exception: {error_msg}", exc_info=True)
            return False
    
    def _init_huidu_sdk(self) -> bool:
        try:
            from controllers.huidu_sdk import HuiduSDK, DEFAULT_HOST
            if self._huidu_sdk is None:
                self._huidu_sdk = HuiduSDK(DEFAULT_HOST)
                if not self._huidu_sdk._initialized:
                    self._huidu_sdk.initialize(DEFAULT_HOST)
            return True
        except Exception as e:
            logger.warning(f"Could not initialize Huidu SDK: {e}. Huidu discovery will be skipped.")
            return False
    
    def _discover_novastar_controllers(self) -> List[ControllerInfo]:
        discovered: List[ControllerInfo] = []
        if not self._init_novastar_sdk():
            logger.warning("NovaStar SDK initialization failed - skipping NovaStar discovery")
            return discovered
        
        if not self._novastar_sdk or not self._novastar_sdk.dll:
            logger.error("NovaStar: SDK object or DLL is None - cannot perform search")
            return discovered
        
        try:
            all_terminals = []
            seen_terminals = set()
            callback_lock = threading.Lock()
            callback_received = threading.Event()
            
            def search_callback(code: int, data: bytes):
                logger.debug(f"NovaStar callback received: code={code}, data_length={len(data) if data else 0}")
                if code == 0 and data:
                    try:
                        data_str = data.decode('utf-8', errors='ignore')
                        if not data_str or data_str.strip() == '':
                            logger.debug("NovaStar callback: Empty data string")
                            return
                        
                        try:
                            terminal_data = json.loads(data_str)
                        except json.JSONDecodeError:
                            for line in data_str.split('\n'):
                                line = line.strip()
                                if line:
                                    try:
                                        terminal_data = json.loads(line)
                                        with callback_lock:
                                            if isinstance(terminal_data, list):
                                                all_terminals.extend(terminal_data)
                                            elif isinstance(terminal_data, dict):
                                                all_terminals.append(terminal_data)
                                    except:
                                        pass
                            return
                        
                        with callback_lock:
                            if isinstance(terminal_data, list):
                                all_terminals.extend(terminal_data)
                            elif isinstance(terminal_data, dict):
                                all_terminals.append(terminal_data)
                            callback_received.set()
                    except Exception as e:
                        logger.debug(f"Error parsing NovaStar callback data: {e}")
                elif code == 65535:
                    logger.info("NovaStar search timeout - no controllers found on network")
                    callback_received.set()
                else:
                    logger.warning(f"NovaStar search error code: {code}")
                    callback_received.set()
            
            import ctypes
            from ctypes import WINFUNCTYPE
            ExportViplexCallback = WINFUNCTYPE(None, ctypes.c_uint16, ctypes.c_char_p)
            cb = ExportViplexCallback(search_callback)
            self._callback_refs.append(cb)
            
            logger.info("NovaStar: Starting UDP broadcast search (nvSearchTerminalAsync)")
            callback_received.clear()
            all_terminals.clear()
            
            if not self._novastar_sdk or not self._novastar_sdk.dll:
                logger.error("NovaStar: SDK not properly initialized")
                return discovered
            
            try:
                logger.debug(f"NovaStar: Calling nvSearchTerminalAsyncW with callback {cb}")
                self._novastar_sdk.dll.nvSearchTerminalAsyncW(cb)
                logger.debug("NovaStar: Search command sent successfully, waiting for callbacks...")
            except Exception as e:
                logger.error(f"NovaStar: Failed to call search function: {e}", exc_info=True)
                return discovered
            
            if not callback_received.wait(timeout=1.5):
                logger.warning("NovaStar: Search timeout - no callback received within 1.5 seconds")
            
            time.sleep(0.5)
            
            logger.info(f"NovaStar: Search completed. Found {len(all_terminals)} terminal(s) in callback data")
            
            for terminal in all_terminals:
                try:
                    sn = terminal.get("sn", "")
                    if not sn:
                        continue
                    
                    ip = terminal.get("ip", "")
                    if not ip:
                        continue
                    
                    terminal_key = f"{sn}_{ip}"
                    if terminal_key in seen_terminals:
                        continue
                    seen_terminals.add(terminal_key)
                    
                    port = terminal.get("tcpPort", 5200)
                    if isinstance(port, str):
                        try:
                            port = int(port)
                        except:
                            port = 5200
                    if not port or port <= 0:
                        port = 5200
                    
                    name = terminal.get("aliasName") or terminal.get("productName", "NovaStar")
                    controller_info = ControllerInfo(ip, port, "novastar", name)
                    controller_info.mac_address = sn
                    controller_info.firmware_version = terminal.get("version", "") or terminal.get("firmware", "")
                    controller_info.model = terminal.get("productName", "") or terminal.get("model", "")
                    controller_info.display_name = terminal.get("aliasName", "")
                    
                    width = terminal.get("width", 0)
                    height = terminal.get("height", 0)
                    if width and height:
                        controller_info.display_resolution = f"{width}x{height}"
                    
                    discovered.append(controller_info)
                    logger.info(f"Found NovaStar controller: {ip}:{port} ({name}) - SN: {sn}")
                    
                    threading.Thread(target=self._read_controller_data, args=(controller_info,), daemon=True).start()
                except Exception as e:
                    logger.debug(f"Error processing NovaStar terminal: {e}")
            
            if discovered:
                logger.info(f"NovaStar discovery complete: Found {len(discovered)} controller(s)")
            else:
                logger.info("NovaStar discovery complete: No controllers found")
                
        except Exception as e:
            logger.error(f"Error discovering NovaStar controllers: {e}", exc_info=True)
        return discovered
    
    def _discover_novastar_mobile_ranges(self, ranges: List[Dict[str, str]]) -> List[ControllerInfo]:
        discovered: List[ControllerInfo] = []
        if not self._init_novastar_sdk():
            return discovered
        
        for ip_range in ranges:
            if self.stop_event.is_set():
                break
            try:
                ip_start = ip_range.get("ipStart", "")
                ip_end = ip_range.get("ipEnd", "")
                if not ip_start or not ip_end:
                    continue
                
                all_terminals = []
                callback_lock = threading.Lock()
                
                def custom_callback(code: int, data: bytes):
                    if code == 0 and data:
                        try:
                            data_str = data.decode('utf-8')
                            terminal_data = json.loads(data_str)
                            with callback_lock:
                                if isinstance(terminal_data, list):
                                    all_terminals.extend(terminal_data)
                                elif isinstance(terminal_data, dict):
                                    all_terminals.append(terminal_data)
                        except Exception:
                            pass
                
                from ctypes import WINFUNCTYPE
                ExportViplexCallback = WINFUNCTYPE(None, ctypes.c_uint16, ctypes.c_char_p)
                cb = ExportViplexCallback(custom_callback)
                
                range_params = json.dumps({"ipStart": ip_start, "ipEnd": ip_end})
                self._novastar_sdk.dll.nvSearchRangeIpAsyncW(ctypes.c_wchar_p(range_params), cb)
                
                time.sleep(4)
                
                for terminal in all_terminals:
                    try:
                        sn = terminal.get("sn", "")
                        if not sn:
                            continue
                        
                        ip = terminal.get("ip", "")
                        if not ip:
                            continue
                        
                        port = terminal.get("tcpPort", 5200)
                        if isinstance(port, str):
                            try:
                                port = int(port)
                            except:
                                port = 5200
                        if not port or port <= 0:
                            port = 5200
                        
                        name = terminal.get("aliasName") or terminal.get("productName", "NovaStar")
                        controller_info = ControllerInfo(ip, port, "novastar", name)
                        controller_info.mac_address = sn
                        width = terminal.get("width", 0)
                        height = terminal.get("height", 0)
                        if width and height:
                            controller_info.display_resolution = f"{width}x{height}"
                        discovered.append(controller_info)
                        logger.info(f"Found NovaStar controller (Mobile): {ip}:{port} ({name})")
                    except Exception:
                        pass
            except Exception as e:
                logger.warning(f"Error scanning mobile network range: {e}")
        
        return discovered
    
    def _discover_novastar_specific_ips(self, ip_list: List[str]) -> List[ControllerInfo]:
        discovered: List[ControllerInfo] = []
        if not self._init_novastar_sdk():
            return discovered
        
        for ip in ip_list:
            if self.stop_event.is_set():
                break
            try:
                all_terminals = []
                callback_lock = threading.Lock()
                
                def custom_callback(code: int, data: bytes):
                    if code == 0 and data:
                        try:
                            data_str = data.decode('utf-8')
                            terminal_data = json.loads(data_str)
                            with callback_lock:
                                if isinstance(terminal_data, list):
                                    all_terminals.extend(terminal_data)
                                elif isinstance(terminal_data, dict):
                                    all_terminals.append(terminal_data)
                        except Exception:
                            pass
                
                from ctypes import WINFUNCTYPE
                ExportViplexCallback = WINFUNCTYPE(None, ctypes.c_uint16, ctypes.c_char_p)
                cb = ExportViplexCallback(custom_callback)
                
                self._novastar_sdk.dll.nvSearchAppointIpAsyncW(ctypes.c_wchar_p(ip), cb)
                
                time.sleep(4)
                
                for terminal in all_terminals:
                    try:
                        sn = terminal.get("sn", "")
                        if not sn:
                            continue
                        
                        terminal_ip = terminal.get("ip", ip)
                        port = terminal.get("tcpPort", 5200)
                        if isinstance(port, str):
                            try:
                                port = int(port)
                            except:
                                port = 5200
                        if not port or port <= 0:
                            port = 5200
                        
                        name = terminal.get("aliasName") or terminal.get("productName", "NovaStar")
                        controller_info = ControllerInfo(terminal_ip, port, "novastar", name)
                        controller_info.mac_address = sn
                        width = terminal.get("width", 0)
                        height = terminal.get("height", 0)
                        if width and height:
                            controller_info.display_resolution = f"{width}x{height}"
                        discovered.append(controller_info)
                        logger.info(f"Found NovaStar controller: {terminal_ip}:{port} ({name})")
                    except Exception:
                        pass
            except Exception:
                pass
        
        return discovered
    
    def _discover_huidu_controllers(self) -> List[ControllerInfo]:
        discovered: List[ControllerInfo] = []
        
        network_discovered = self._discover_huidu_network()
        discovered.extend(network_discovered)
        return discovered
    
    def _discover_huidu_network(self) -> List[ControllerInfo]:
        discovered: List[ControllerInfo] = []
        
        try:
            from controllers.huidu_sdk import HuiduSDK, SDK_AVAILABLE, DEFAULT_HOST, _is_port_open
            from core.controller_database import get_controller_database
            
            if not SDK_AVAILABLE:
                logger.debug("Huidu SDK not available - skipping network discovery")
                return discovered
            
            default_port = 30080
            logger.info(f"Huidu network discovery: Checking 127.0.0.1:{default_port}")
            
            if not self._huidu_sdk:
                if not self._init_huidu_sdk():
                    return discovered
            
            if not self._huidu_sdk:
                return discovered
            
            sdk = self._huidu_sdk
            
            if "127.0.0.1" in str(DEFAULT_HOST):
                max_wait = 10.0
                waited = 0.0
                while not _is_port_open("127.0.0.1", 30080, timeout=0.5) and waited < max_wait and not self.stop_event.is_set():
                    time.sleep(0.5)
                    waited += 0.5
                if waited >= max_wait:
                    logger.warning("API server not ready after waiting, continuing anyway")
            
            if self.stop_event.is_set():
                return discovered
            
            if not sdk._initialized:
                try:
                    sdk.initialize(sdk.host, sdk.sdk_key, sdk.sdk_secret)
                except Exception as e:
                    logger.error(f"Failed to initialize SDK: {e}")
                    return discovered
            
            if not sdk.device:
                logger.error("SDK device not available")
                return discovered
            
            db = get_controller_database()
            
            db_controllers = db.get_all_controllers(active_only=False)
            db_device_ids = {ctrl.get("controller_id"): ctrl for ctrl in db_controllers if ctrl.get("controller_type") == "Huidu"}
            logger.debug(f"Loaded {len(db_device_ids)} Huidu devices from local database")
            
            if self.stop_event.is_set():
                return discovered
            
            try:
                result = sdk.device.get_online_devices()
                if result.get("message") != "ok":
                    logger.debug("No online devices found")
                    return discovered
                
                online_devices = result.get("data", [])
                if not online_devices or not isinstance(online_devices, list):
                    logger.debug("No online devices found")
                    return discovered
                
                logger.info(f"Found {len(online_devices)} online device(s)")
                
                online_device_ids = set()

                from controllers.huidu_sdk import validate_device_id
                
                for device_id in online_devices:
                    if self.stop_event.is_set():
                        break
                    
                    if not isinstance(device_id, str):
                        continue
                    
                    if not validate_device_id(device_id):
                        logger.debug(f"Skipping device {device_id}: Not an engineering card (must contain 'D' in ID)")
                        continue
                    
                    online_device_ids.add(device_id)
                    
                    try:
                        existing_controller = db_device_ids.get(device_id)
                        
                        if existing_controller:
                            device_ip = existing_controller.get("ip_address", "127.0.0.1")
                            device_name = existing_controller.get("device_name", f"Huidu_{device_id}")
                            display_resolution = existing_controller.get("display_resolution", "64x32")
                            firmware_version = existing_controller.get("firmware_version", "")
                            model = existing_controller.get("model", "Huidu")
                            
                            device_info = {
                                "name": device_name,
                                "controller_id": device_id,
                                "ip": device_ip,
                                "port": default_port,
                                "model": model,
                                "version": firmware_version,
                                "version.app": firmware_version,
                                "display_resolution": display_resolution,
                                "mac_address": device_id,
                                "serial_number": device_id
                            }
                            
                            db.add_or_update_controller(
                                device_id,
                                device_ip,
                                default_port,
                                "Huidu",
                                device_info
                            )
                            
                            controller_info = ControllerInfo(device_ip, default_port, "huidu", device_name)
                            controller_info.name = device_name
                            controller_info.mac_address = device_id
                            controller_info.firmware_version = firmware_version
                            controller_info.model = model
                            controller_info.display_resolution = display_resolution
                            
                            discovered.append(controller_info)
                            logger.debug(f"Updated existing device {device_id} as connected")
                        else:
                            property_result = sdk.get_device_property([device_id], None)
                            if property_result.get("message") != "ok":
                                logger.debug(f"Failed to get properties for device {device_id}: {property_result.get('data')}")
                                continue
                            
                            data_array = property_result.get("data", [])
                            if not data_array or len(data_array) == 0:
                                logger.debug(f"No property data for device {device_id}")
                                continue
                            
                            first_item = data_array[0]
                            if not isinstance(first_item, dict) or first_item.get("message") != "ok":
                                logger.debug(f"Invalid response item for device {device_id}")
                                continue
                            
                            item_id = first_item.get("id", "")
                            if item_id != device_id:
                                logger.debug(f"Device ID mismatch: expected {device_id}, got {item_id}")
                                for item in data_array:
                                    if isinstance(item, dict) and item.get("id") == device_id and item.get("message") == "ok":
                                        first_item = item
                                        break
                            
                            device_data = first_item.get("data", {})
                            if not device_data or not isinstance(device_data, dict):
                                logger.debug(f"Empty property data for device {device_id}")
                                continue
                            
                            import re
                            ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
                            
                            device_ip = None
                            
                            if ip_pattern.match(device_id):
                                device_ip = device_id
                                logger.debug(f"Device ID is already an IP address: {device_ip}")
                            
                            if not device_ip or device_ip == "127.0.0.1":
                                device_ip = device_data.get("eth.ip")
                                if device_ip and ip_pattern.match(device_ip) and device_ip != "127.0.0.1":
                                    logger.debug(f"Found IP from eth.ip: {device_ip}")
                            
                            if not device_ip or device_ip == "127.0.0.1":
                                logger.warning(f"Could not determine real IP from device properties for device {device_id}, defaulting to 127.0.0.1")
                                device_ip = "127.0.0.1"
                            else:
                                logger.info(f"Found device IP from eth.ip: {device_ip} for device {device_id}")
                            
                            device_name = device_data.get("name", f"Huidu_{device_id}")
                            
                            device_info = device_data.copy()
                            device_info["controller_id"] = device_id
                            device_info["ip"] = device_ip
                            device_info["port"] = default_port
                            device_info["mac_address"] = device_id
                            device_info["serial_number"] = device_id
                            
                            screen_width = device_data.get("screen.width", "64")
                            screen_height = device_data.get("screen.height", "32")
                            controller_info = ControllerInfo(device_ip, default_port, "huidu", device_name)
                            controller_info.name = device_name
                            controller_info.mac_address = device_id
                            controller_info.firmware_version = device_data.get("version.app", "")
                            controller_info.model = device_data.get("version.hardware") or device_data.get("model", "Huidu")
                            controller_info.display_resolution = f"{screen_width}x{screen_height}"
                            
                            db.add_or_update_controller(
                                device_id,
                                device_ip,
                                default_port,
                                "Huidu",
                                device_info
                            )
                            
                            discovered.append(controller_info)
                            logger.info(f"Found new Huidu controller: {device_id} at {device_ip}:{default_port}")
                    except Exception as e:
                        logger.debug(f"Error processing device {device_id}: {e}")
                
                for device_id, controller_data in db_device_ids.items():
                    if device_id not in online_device_ids:
                        db.mark_controller_disconnected(device_id)
                        logger.debug(f"Marked device {device_id} as disconnected")
                
                if discovered:
                    logger.info(f"Huidu network discovery complete: Found {len(discovered)} controller(s)")
                else:
                    logger.info("Huidu network discovery complete: No controllers found")
            
            except Exception as e:
                logger.debug(f"Error checking 127.0.0.1 for Huidu controllers: {e}")
            
        except Exception as e:
            logger.error(f"Error discovering Huidu network controllers: {e}", exc_info=True)
        
        return discovered
    
    def _get_all_network_ranges(self) -> List[List[str]]:
        try:
            import platform
            all_ranges = []
            seen_networks = set()
            
            if platform.system().lower() == "windows":
                import subprocess
                result = subprocess.run(
                    ["ipconfig"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                ip_mask_pairs = []
                current_ip = None
                current_mask = None
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if 'IPv4' in line or 'IP Address' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            ip_str = parts[-1].strip()
                            if ip_str and not ip_str.startswith('(') and not ip_str.startswith('::'):
                                try:
                                    ip_parts = ip_str.split('.')
                                    if len(ip_parts) == 4 and all(0 <= int(p) <= 255 for p in ip_parts):
                                        if current_ip and current_mask:
                                            ip_mask_pairs.append((current_ip, current_mask))
                                        current_ip = ip_str
                                        current_mask = None
                                except:
                                    pass
                    elif ('Subnet Mask' in line or 'Subnet' in line) and current_ip:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            mask_str = parts[-1].strip()
                            try:
                                mask_parts = mask_str.split('.')
                                if len(mask_parts) == 4 and all(0 <= int(p) <= 255 for p in mask_parts):
                                    current_mask = mask_str
                            except:
                                pass
                
                if current_ip and current_mask:
                    ip_mask_pairs.append((current_ip, current_mask))
                
                for ip_str, mask_str in ip_mask_pairs:
                    try:
                        ip_parts = ip_str.split('.')
                        mask_parts = mask_str.split('.')
                        if len(ip_parts) == 4 and len(mask_parts) == 4:
                            network_prefix_parts = []
                            for i in range(4):
                                network_prefix_parts.append(str(int(ip_parts[i]) & int(mask_parts[i])))
                            network_prefix = '.'.join(network_prefix_parts)
                            
                            if network_prefix not in seen_networks:
                                seen_networks.add(network_prefix)
                                network_base = '.'.join(network_prefix_parts[:3])
                                gateway_ip = f"{network_base}.1"
                                ip_range = [gateway_ip]
                                all_ranges.append(ip_range)
                                logger.info(f"Detected network: {network_prefix} (gateway: {gateway_ip})")
                    except:
                        pass
            
            if not all_ranges:
                try:
                    import netifaces
                    seen_networks_netifaces = set()
                    for interface in netifaces.interfaces():
                        addrs = netifaces.ifaddresses(interface)
                        if netifaces.AF_INET in addrs:
                            for addr_info in addrs[netifaces.AF_INET]:
                                ip = addr_info.get('addr')
                                netmask = addr_info.get('netmask')
                                if ip and netmask and not ip.startswith('127.'):
                                    try:
                                        ip_parts = ip.split('.')
                                        mask_parts = netmask.split('.')
                                        if len(ip_parts) == 4 and len(mask_parts) == 4:
                                            network_prefix_parts = []
                                            for i in range(4):
                                                network_prefix_parts.append(str(int(ip_parts[i]) & int(mask_parts[i])))
                                            network_prefix = '.'.join(network_prefix_parts)
                                            
                                            if network_prefix not in seen_networks_netifaces:
                                                seen_networks_netifaces.add(network_prefix)
                                                network_base = '.'.join(network_prefix_parts[:3])
                                                gateway_ip = f"{network_base}.1"
                                                ip_range = [gateway_ip]
                                                all_ranges.append(ip_range)
                                                logger.info(f"Detected network: {network_prefix} (gateway: {gateway_ip})")
                                    except:
                                        pass
                except ImportError:
                    pass
            
            if not all_ranges:
                all_ranges.append(["192.168.1.1"])
            
            return all_ranges
            
        except Exception as e:
            logger.exception(f"Error getting network ranges: {e}")
            return [["192.168.1.1"]]
    
    def _discover_huidu_mobile_ranges(self, ranges: List[Dict[str, str]]) -> List[ControllerInfo]:
        discovered: List[ControllerInfo] = []
        return discovered
    
    def get_local_network_range(self) -> List[str]:
        try:
            import platform
            all_ranges = []
            
            if platform.system().lower() == "windows":
                import subprocess
                result = subprocess.run(
                    ["ipconfig"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                current_ip = None
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if 'IPv4' in line or 'IP Address' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            ip_str = parts[-1].strip()
                            if ip_str and not ip_str.startswith('('):
                                try:
                                    ip_parts = ip_str.split('.')
                                    if len(ip_parts) == 4 and all(0 <= int(p) <= 255 for p in ip_parts):
                                        current_ip = ip_str
                                        network_prefix = '.'.join(ip_parts[:3])
                                        ip_range = [f"{network_prefix}.{i}" for i in range(1, 255)]
                                        if ip_range not in all_ranges:
                                            all_ranges.append(ip_range)
                                except (ValueError, IndexError):
                                    pass
            else:
                import netifaces
                interfaces = netifaces.interfaces()
                for interface in interfaces:
                    try:
                        addrs = netifaces.ifaddresses(interface)
                        if netifaces.AF_INET in addrs:
                            for addr_info in addrs[netifaces.AF_INET]:
                                ip = addr_info.get('addr')
                                if ip and not ip.startswith('127.'):
                                    ip_parts = ip.split('.')
                                    if len(ip_parts) == 4:
                                        network_prefix = '.'.join(ip_parts[:3])
                                        ip_range = [f"{network_prefix}.{i}" for i in range(1, 255)]
                                        if ip_range not in all_ranges:
                                            all_ranges.append(ip_range)
                    except Exception:
                        continue
            
            if not all_ranges:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                ip_parts = local_ip.split('.')
                if len(ip_parts) == 4:
                    network_prefix = '.'.join(ip_parts[:3])
                    all_ranges.append([f"{network_prefix}.{i}" for i in range(1, 255)])
            
            if all_ranges:
                combined_range = []
                for ip_range in all_ranges:
                    combined_range.extend(ip_range)
                logger.info(f"Found {len(all_ranges)} network interface(s), total {len(combined_range)} IPs to scan")
                return combined_range
            
            return []
        except Exception as e:
            logger.exception(f"Error getting local network range: {e}")
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                ip_parts = local_ip.split('.')
                if len(ip_parts) == 4:
                    network_prefix = '.'.join(ip_parts[:3])
                    return [f"{network_prefix}.{i}" for i in range(1, 255)]
            except Exception:
                pass
            return []
    
    def is_mobile_network_ip(self, ip: str) -> bool:
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            
            first_octet = int(parts[0])
            second_octet = int(parts[1])
            
            if first_octet == 10:
                return False
            elif first_octet == 172 and 16 <= second_octet <= 31:
                return False
            elif first_octet == 192 and second_octet == 168:
                return False
            else:
                return True
        except (ValueError, IndexError):
            return False
    
    def scan_port(self, ip: str, port: int, timeout: float = 0.5) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def identify_controller_type(self, ip: str, port: int) -> str:
        if port in self.NOVASTAR_PORTS:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                sock.connect((ip, port))
                sock.close()
                return "novastar"
            except (OSError, ConnectionError, TimeoutError):
                pass
        
        if port in self.HUIDU_PORTS:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                sock.connect((ip, port))
                sock.close()
                return "huidu"
            except (OSError, ConnectionError, TimeoutError):
                pass
        
        return "unknown"
    
    def scan_ip(self, ip: str):
        if self.stop_event.is_set():
            return
        
        for port in self.COMMON_PORTS:
            if self.stop_event.is_set():
                return
            
            if self.scan_port(ip, port, timeout=0.3):
                controller_type = self.identify_controller_type(ip, port)
                controller_info = ControllerInfo(ip, port, controller_type)
                
                existing = next((c for c in self.discovered_controllers 
                               if c.ip == ip and c.port == port), None)
                if not existing:
                    self.discovered_controllers.append(controller_info)
                    logger.info(f"Found controller: {ip}:{port} ({controller_type})")
                    self.controller_found.emit(controller_info)
    
    def start_scan(self, ip_range: Optional[List[str]] = None, 
                   mobile_network_ranges: Optional[List[Dict[str, str]]] = None):
        if self.is_scanning:
            logger.warning("Discovery scan already in progress")
            return
        
        self.is_scanning = True
        self.stop_event.clear()
        self.discovered_controllers.clear()
        
        def scan_thread():
            try:
                logger.info("=" * 60)
                logger.info("Starting comprehensive controller discovery")
                logger.info("Connection types: Wi-Fi, Ethernet, Huidu Network, 3G/4G/5G")
                logger.info("=" * 60)
                
                try:
                    logger.info("Step 1: Scanning NovaStar controllers (Wi-Fi/Ethernet)")
                    novastar_controllers = self._discover_novastar_controllers()
                except Exception as e:
                    logger.debug(f"NovaStar discovery skipped: {e}")
                    novastar_controllers = []
                for controller in novastar_controllers:
                    if self.stop_event.is_set():
                        break
                    existing = next((c for c in self.discovered_controllers 
                                   if c.ip == controller.ip and c.port == controller.port), None)
                    if not existing:
                        self.discovered_controllers.append(controller)
                        self.controller_found.emit(controller)
                        try:
                            self._read_controller_data(controller)
                        except Exception as e:
                            logger.debug(f"Error reading data from NovaStar controller {controller.ip}: {e}")
                
                if not self.stop_event.is_set():
                    logger.info("Step 2: Scanning Huidu controllers (via API server)")
                    try:
                        huidu_controllers = self._discover_huidu_controllers()
                        for controller in huidu_controllers:
                            if self.stop_event.is_set():
                                break
                            existing = next((c for c in self.discovered_controllers 
                                           if c.ip == controller.ip and c.port == controller.port), None)
                            if not existing:
                                self.discovered_controllers.append(controller)
                                self.controller_found.emit(controller)
                    except Exception as e:
                        logger.warning(f"Error during Huidu discovery: {e}. Continuing with other discovery methods...")
                
                if not self.stop_event.is_set() and mobile_network_ranges:
                    logger.info(f"Step 3: Scanning mobile network ranges (3G/4G/5G) - {len(mobile_network_ranges)} ranges")
                    try:
                        novastar_mobile = self._discover_novastar_mobile_ranges(mobile_network_ranges)
                        for controller in novastar_mobile:
                            if self.stop_event.is_set():
                                break
                            existing = next((c for c in self.discovered_controllers 
                                           if c.ip == controller.ip and c.port == controller.port), None)
                            if not existing:
                                self.discovered_controllers.append(controller)
                                self.controller_found.emit(controller)
                                try:
                                    self._read_controller_data(controller)
                                except Exception as e:
                                    logger.debug(f"Error reading data from NovaStar mobile controller {controller.ip}: {e}")
                    except Exception as e:
                        logger.warning(f"Error during NovaStar mobile network discovery: {e}")
                    
                
                if not self.stop_event.is_set() and ip_range:
                    logger.info(f"Step 4: Scanning specific IP addresses ({len(ip_range)} IPs)")
                    try:
                        for ip in ip_range:
                            if self.stop_event.is_set():
                                break
                            self.scan_ip(ip)
                        
                        specific_controllers = self._discover_novastar_specific_ips(ip_range)
                        for controller in specific_controllers:
                            if self.stop_event.is_set():
                                break
                            existing = next((c for c in self.discovered_controllers 
                                           if c.ip == controller.ip and c.port == controller.port), None)
                            if not existing:
                                self.discovered_controllers.append(controller)
                                self.controller_found.emit(controller)
                                try:
                                    self._read_controller_data(controller)
                                except Exception as e:
                                    logger.debug(f"Error reading data from specific IP controller {controller.ip}: {e}")
                    except Exception as e:
                        logger.warning(f"Error during specific IP discovery: {e}")
                
                logger.info(f"Discovery scan finished. Found {len(self.discovered_controllers)} controllers")
            except Exception as e:
                logger.exception(f"Error during discovery scan: {e}")
            finally:
                self.is_scanning = False
                self.discovery_finished.emit()
        
        self.scan_thread = threading.Thread(target=scan_thread, daemon=True)
        self.scan_thread.start()
    
    def stop_scan(self):
        if self.is_scanning:
            self.stop_event.set()
            logger.info("Stopping controller discovery scan")
    
    def get_discovered_controllers(self) -> List[ControllerInfo]:
        return self.discovered_controllers.copy()
    
    def scan_single_ip(self, ip: str, callback: Optional[Callable] = None):
        def scan():
            self.scan_ip(ip)
            if callback:
                callback()
        
        thread = threading.Thread(target=scan, daemon=True)
        thread.start()
    
    def _read_controller_data(self, controller_info: ControllerInfo):
        try:
            from controllers.novastar import NovaStarController
            from controllers.huidu import HuiduController
            from controllers.base_controller import BaseController
            from core.controller_database import get_controller_database
            from core.sync_manager import SyncManager
            
            controller: Optional[BaseController] = None
            try:
                if controller_info.controller_type == "novastar":
                    controller = NovaStarController(controller_info.ip, controller_info.port)  # type: ignore
                    if controller_info.mac_address and hasattr(controller, '_device_sn'):
                        controller._device_sn = controller_info.mac_address  # type: ignore
                elif controller_info.controller_type == "huidu":
                    controller = HuiduController(controller_info.ip, controller_info.port)  # type: ignore
                else:
                    return
                
                if not controller.connect():
                    logger.debug(f"Could not connect to {controller_info.ip}:{controller_info.port} for data reading")
                    return
                
                device_info = controller.get_device_info()
                if not device_info:
                    device_info = {}
                
                device_info.update({
                    "name": controller_info.name,
                    "display_name": controller_info.display_name,
                    "mac_address": controller_info.mac_address,
                    "firmware_version": controller_info.firmware_version,
                    "display_resolution": controller_info.display_resolution,
                    "model": controller_info.model
                })
                
                programs: List[Dict] = []
                media_files: List[str] = []
                
                if hasattr(controller, 'get_program_list'):
                    try:
                        program_list = controller.get_program_list()  # type: ignore
                        controller_info.program_count = len(program_list) if program_list else 0
                        programs = program_list or []
                        
                        for program_info in programs:
                            program_id = program_info.get("id") or program_info.get("name") or program_info.get("program_id")
                            if program_id and hasattr(controller, 'download_program'):
                                try:
                                    program_data = controller.download_program(program_id)  # type: ignore
                                    if program_data:
                                        sync_manager = SyncManager()
                                        media_from_program = sync_manager._extract_media_from_program(program_data)
                                        media_files.extend(media_from_program)
                                except Exception as e:
                                    logger.debug(f"Error downloading program {program_id}: {e}")
                    except Exception as e:
                        logger.debug(f"Error reading programs from {controller_info.ip}: {e}")
                
                media_files = list(set(media_files))
                controller_info.media_count = len(media_files)
                controller_info.programs = programs
                controller_info.media_files = media_files
                
                if controller:
                    controller_id = controller.get_controller_id()  # type: ignore
                    if controller_id:
                        db = get_controller_database()
                        db.add_or_update_controller(
                            controller_id,
                            controller_info.ip,
                            controller_info.port,
                            controller_info.controller_type.capitalize(),
                            device_info
                        )
                        logger.info(f"Updated database for controller {controller_id}: {controller_info.program_count} programs, {controller_info.media_count} media files")
                    
                    controller.disconnect()  # type: ignore
                
            except Exception as e:
                logger.debug(f"Error reading data from controller {controller_info.ip}:{controller_info.port}: {e}")
                if controller:
                    try:
                        controller.disconnect()
                    except:
                        pass
        except Exception as e:
            logger.debug(f"Error in _read_controller_data: {e}")

