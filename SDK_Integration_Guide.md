# SDK Integration Guide for SLPlayer Project

## Executive Summary

This document provides a comprehensive guide for integrating the **Huidu Gen6 SDK V2.0.2** and **ViplexCore 3.6.3.0101.CTM21.11.1_x64** SDKs into the SLPlayer application. The current implementation uses placeholder network socket communication. This guide outlines how to replace those with actual SDK implementations.

---

## 1. Current Project Analysis

### 1.1 Project Overview

**SLPlayer** is a PyQt5-based LED display controller program management system that:
- Creates and edits programs with various content types (text, images, videos, clock, sensors, etc.)
- Manages multiple screens and programs
- Connects to LED display controllers (NovaStar and Huidu)
- Uploads/downloads programs to/from controllers
- Provides scheduling and playback control

### 1.2 Current Architecture

```
SLPlayer Architecture:
├── UI Layer (PyQt5)
│   ├── MainWindow
│   ├── ContentWidget (canvas for editing)
│   ├── PropertiesPanel
│   └── Toolbars
├── Core Layer
│   ├── ProgramManager (manages programs)
│   ├── ScreenManager (manages screens)
│   ├── ContentElement (content types)
│   └── FileManager (save/load .soo files)
├── Service Layer
│   ├── ControllerService (controller operations)
│   ├── ProgramActionService (send/export programs)
│   └── UIService (UI helpers)
└── Controller Layer (CURRENTLY STUB IMPLEMENTATIONS)
    ├── BaseController (abstract base)
    ├── HuiduController (placeholder)
    └── NovaStarController (placeholder)
```

### 1.3 Current Controller Implementation Status

**Current State:**
- `BaseController` - Abstract base class with well-defined interface
- `HuiduController` - Stub implementation using basic socket communication
- `NovaStarController` - Stub implementation using basic socket communication
- Both controllers have placeholder methods that don't actually communicate with real devices

**Key Methods in BaseController:**
- `connect()` - Establish connection
- `disconnect()` - Close connection
- `get_device_info()` - Get device information
- `upload_program()` - Send program to device
- `download_program()` - Retrieve program from device
- `get_program_list()` - List programs on device
- `test_connection()` - Test connectivity

### 1.4 Program Data Structure

The project uses a JSON-based program structure:
```python
Program {
    id: str
    name: str
    width: int
    height: int
    elements: List[Dict]  # ContentElement objects
    properties: Dict
    play_mode: Dict
    play_control: Dict
    duration: float
}
```

**ContentElement Types:**
- TEXT, SINGLELINE_TEXT
- VIDEO, PHOTO
- CLOCK, TIMING
- WEATHER, SENSOR
- HTML, HDMI
- ANIMATION

---

## 2. Integration Strategy

### 2.1 High-Level Approach

**Option 1: Python Ctypes Wrapper (Recommended)**
- Use Python's `ctypes` to call C DLL functions directly
- Pros: No compilation needed, works with existing Python codebase
- Cons: Manual type conversions, error handling complexity

**Option 2: Python C Extension**
- Create C extension modules using Python C API
- Pros: Better performance, cleaner interface
- Cons: Requires compilation, more complex build process

**Option 3: Separate C++ Service + Python IPC**
- Create separate C++ service using SDKs
- Communicate via sockets/HTTP/JSON-RPC
- Pros: Isolation, can use SDKs directly
- Cons: More complex architecture, IPC overhead

**Recommendation: Option 1 (ctypes)** - Best balance of simplicity and functionality for this project.

### 2.2 Integration Points

1. **Replace Controller Implementations**
   - Enhance `HuiduController` to use Huidu SDK
   - Enhance `NovaStarController` to use ViplexCore SDK

2. **Add SDK Wrapper Modules**
   - Create `sdk_wrappers/huidu_sdk.py` - Python wrapper for Huidu SDK
   - Create `sdk_wrappers/viplexcore_sdk.py` - Python wrapper for ViplexCore SDK

3. **Program Data Conversion**
   - Convert SLPlayer program format to SDK-specific formats
   - Handle content type mappings
   - Manage file paths and media assets

4. **Error Handling & Logging**
   - Map SDK error codes to application errors
   - Provide user-friendly error messages
   - Log SDK operations

---

## 3. Huidu SDK Integration

### 3.1 SDK Wrapper Implementation

Create `sdk_wrappers/huidu_sdk.py`:

```python
import ctypes
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from ctypes import wintypes

class HuiduSDK:
    """Python wrapper for Huidu Gen6 SDK"""
    
    def __init__(self):
        self.dll = None
        self._load_dll()
    
    def _load_dll(self):
        """Load HDSDK.dll"""
        sdk_path = Path(__file__).parent.parent / "requirements" / "Huidu_Gen6SDK_V2.0.2"
        
        # Try x64 first, then x86
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
                except OSError as e:
                    print(f"Failed to load {dll_path}: {e}")
        
        raise RuntimeError("HDSDK.dll not found")
    
    def _setup_functions(self):
        """Configure function signatures"""
        # Hd_GetSDKLastError
        self.dll.Hd_GetSDKLastError.restype = ctypes.c_int
        
        # Hd_CreateScreen
        self.dll.Hd_CreateScreen.argtypes = [
            ctypes.c_int,  # nWidth
            ctypes.c_int,  # nHeight
            ctypes.c_int,  # nColor
            ctypes.c_int,  # nGray
            ctypes.c_int,  # nCardType
            ctypes.c_void_p,  # pExParamsBuf
            ctypes.c_int  # nBufSize
        ]
        self.dll.Hd_CreateScreen.restype = ctypes.c_int
        
        # Hd_AddProgram
        self.dll.Hd_AddProgram.argtypes = [
            ctypes.c_void_p,  # pBoderImgPath
            ctypes.c_int,  # nBorderEffect
            ctypes.c_int,  # nBorderSpeed
            ctypes.c_void_p,  # pExParamsBuf
            ctypes.c_int  # nBufSize
        ]
        self.dll.Hd_AddProgram.restype = ctypes.c_int
        
        # Hd_AddArea
        self.dll.Hd_AddArea.argtypes = [
            ctypes.c_int,  # nProgramID
            ctypes.c_int,  # nX
            ctypes.c_int,  # nY
            ctypes.c_int,  # nWidth
            ctypes.c_int,  # nHeight
            ctypes.c_void_p,  # pBoderImgPath
            ctypes.c_int,  # nBorderEffect
            ctypes.c_int,  # nBorderSpeed
            ctypes.c_void_p,  # pExParamsBuf
            ctypes.c_int  # nBufSize
        ]
        self.dll.Hd_AddArea.restype = ctypes.c_int
        
        # Hd_AddSimpleTextAreaItem
        self.dll.Hd_AddSimpleTextAreaItem.argtypes = [
            ctypes.c_int,  # nAreaID
            ctypes.c_void_p,  # pText (wchar_t*)
            ctypes.c_int,  # nTextColor
            ctypes.c_int,  # nBackGroupColor
            ctypes.c_int,  # nStyle
            ctypes.c_void_p,  # pFontName (wchar_t*)
            ctypes.c_int,  # nFontHeight
            ctypes.c_int,  # nShowEffect
            ctypes.c_int,  # nShowSpeed
            ctypes.c_int,  # nClearType
            ctypes.c_int,  # nStayTime
            ctypes.c_void_p,  # pExParamsBuf
            ctypes.c_int  # nBufSize
        ]
        self.dll.Hd_AddSimpleTextAreaItem.restype = ctypes.c_int
        
        # Hd_AddImageAreaItem
        self.dll.Hd_AddImageAreaItem.argtypes = [
            ctypes.c_int,  # nAreaID
            ctypes.c_void_p,  # pPaths (wchar_t*)
            ctypes.c_int,  # nShowEffect
            ctypes.c_int,  # nShowSpeed
            ctypes.c_int,  # nClearType
            ctypes.c_int,  # nStayTime
            ctypes.c_void_p,  # pExParamsBuf
            ctypes.c_int  # nBufSize
        ]
        self.dll.Hd_AddImageAreaItem.restype = ctypes.c_int
        
        # Hd_AddTimeAreaItem
        self.dll.Hd_AddTimeAreaItem.argtypes = [
            ctypes.c_int,  # nAreaID
            ctypes.c_int,  # nShowMode
            ctypes.c_int,  # bShowDate
            ctypes.c_int,  # nDateStyle
            ctypes.c_int,  # bShowWeek
            ctypes.c_int,  # nWeekStyle
            ctypes.c_int,  # bShowTime
            ctypes.c_int,  # nTimeStyle
            ctypes.c_int,  # nTextColor
            ctypes.c_void_p,  # pFontName
            ctypes.c_int,  # nFontHeight
            ctypes.c_int,  # nDiffHour
            ctypes.c_int,  # nDiffMin
            ctypes.c_void_p,  # pExParamsBuf
            ctypes.c_int  # nBufSize
        ]
        self.dll.Hd_AddTimeAreaItem.restype = ctypes.c_int
        
        # Hd_SendScreen
        self.dll.Hd_SendScreen.argtypes = [
            ctypes.c_int,  # nSendType (0=TCP, 1=Serial)
            ctypes.c_void_p,  # pStrParams (wchar_t*)
            ctypes.c_void_p,  # pDeviceGUID
            ctypes.c_void_p,  # pExParamsBuf
            ctypes.c_int  # nBufSize
        ]
        self.dll.Hd_SendScreen.restype = ctypes.c_int
        
        # Hd_GetColor
        self.dll.Hd_GetColor.argtypes = [
            ctypes.c_int,  # r
            ctypes.c_int,  # g
            ctypes.c_int  # b
        ]
        self.dll.Hd_GetColor.restype = ctypes.c_int
        
        # Cmd_IsCardOnline
        self.dll.Cmd_IsCardOnline.argtypes = [
            ctypes.c_int,  # nSendType
            ctypes.c_void_p,  # pStrParams
            ctypes.c_void_p  # pDeviceGUID
        ]
        self.dll.Cmd_IsCardOnline.restype = ctypes.c_int
        
        # Cmd_GetScreenParam
        self.dll.Cmd_GetScreenParam.argtypes = [
            ctypes.c_int,  # nSendType
            ctypes.c_void_p,  # pStrParams
            ctypes.POINTER(ctypes.c_int),  # pWidth
            ctypes.POINTER(ctypes.c_int),  # pHeight
            ctypes.POINTER(ctypes.c_int),  # pColor
            ctypes.POINTER(ctypes.c_int),  # pGray
            ctypes.POINTER(ctypes.c_int),  # pCardType
            ctypes.c_void_p  # pDeviceGUID
        ]
        self.dll.Cmd_GetScreenParam.restype = ctypes.c_int
    
    def get_last_error(self) -> int:
        """Get last SDK error code"""
        return self.dll.Hd_GetSDKLastError()
    
    def create_screen(self, width: int, height: int, color: int = 1, gray: int = 1, card_type: int = 0) -> bool:
        """Create screen configuration"""
        result = self.dll.Hd_CreateScreen(width, height, color, gray, card_type, None, 0)
        return result == 0
    
    def add_program(self, border_img_path: Optional[str] = None, border_effect: int = 0, border_speed: int = 5) -> Optional[int]:
        """Add program to screen. Returns program ID or None on error"""
        border_ptr = None
        if border_img_path:
            border_ptr = ctypes.c_wchar_p(border_img_path)
        
        program_id = self.dll.Hd_AddProgram(border_ptr, border_effect, border_speed, None, 0)
        return program_id if program_id != -1 else None
    
    def add_area(self, program_id: int, x: int, y: int, width: int, height: int,
                 border_img_path: Optional[str] = None, border_effect: int = 0, border_speed: int = 5) -> Optional[int]:
        """Add area to program. Returns area ID or None on error"""
        border_ptr = None
        if border_img_path:
            border_ptr = ctypes.c_wchar_p(border_img_path)
        
        area_id = self.dll.Hd_AddArea(program_id, x, y, width, height, border_ptr, border_effect, border_speed, None, 0)
        return area_id if area_id != -1 else None
    
    def add_text_item(self, area_id: int, text: str, font_name: str = "Arial", font_size: int = 24,
                     text_color: Tuple[int, int, int] = (255, 255, 255), bg_color: int = 0,
                     style: int = 4, show_effect: int = 0, show_speed: int = 25,
                     clear_type: int = 201, stay_time: int = 3) -> Optional[int]:
        """Add text area item"""
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
        """Add image area item"""
        path_w = ctypes.c_wchar_p(image_path)
        item_id = self.dll.Hd_AddImageAreaItem(area_id, path_w, show_effect, show_speed, clear_type, stay_time, None, 0)
        return item_id if item_id != -1 else None
    
    def add_time_item(self, area_id: int, show_date: bool = True, show_time: bool = True,
                     font_name: str = "Arial", font_size: int = 16,
                     text_color: Tuple[int, int, int] = (0, 255, 0),
                     date_style: int = 0, time_style: int = 0, diff_hour: int = 0, diff_min: int = 0) -> Optional[int]:
        """Add time/clock area item"""
        font_w = ctypes.c_wchar_p(font_name)
        color = self.get_color(text_color[0], text_color[1], text_color[2])
        
        item_id = self.dll.Hd_AddTimeAreaItem(
            area_id, 0, 1 if show_date else 0, date_style, 0, 0,
            1 if show_time else 0, time_style, color, font_w, font_size,
            diff_hour, diff_min, None, 0
        )
        return item_id if item_id != -1 else None
    
    def get_color(self, r: int, g: int, b: int) -> int:
        """Convert RGB to SDK color value"""
        return self.dll.Hd_GetColor(r, g, b)
    
    def send_screen(self, ip_address: str, send_type: int = 0) -> bool:
        """Send screen to device via TCP/IP"""
        ip_w = ctypes.c_wchar_p(ip_address)
        result = self.dll.Hd_SendScreen(send_type, ip_w, None, None, 0)
        return result == 0
    
    def is_card_online(self, ip_address: str, send_type: int = 0) -> bool:
        """Check if controller is online"""
        ip_w = ctypes.c_wchar_p(ip_address)
        result = self.dll.Cmd_IsCardOnline(send_type, ip_w, None)
        return result == 0
    
    def get_screen_params(self, ip_address: str, send_type: int = 0) -> Optional[Dict]:
        """Get screen parameters from device"""
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
```

### 3.2 Enhanced HuiduController Implementation

Update `controllers/huidu.py`:

```python
import json
from typing import Optional, Dict, List
from pathlib import Path
from controllers.base_controller import BaseController, ControllerType, ConnectionStatus
from sdk_wrappers.huidu_sdk import HuiduSDK
from utils.logger import get_logger

logger = get_logger(__name__)


class HuiduController(BaseController):
    """Huidu controller using official SDK"""
    
    DEFAULT_PORT = 5000
    
    def __init__(self, ip_address: str, port: int = DEFAULT_PORT):
        super().__init__(ControllerType.HUIDU, ip_address, port)
        self.sdk = HuiduSDK()
        self._screen_created = False
        self._current_program_id = None
        self._current_area_id = None
    
    def connect(self) -> bool:
        """Connect to Huidu controller"""
        if self.status == ConnectionStatus.CONNECTED:
            return True
        
        self.set_status(ConnectionStatus.CONNECTING)
        
        try:
            # Check if device is online
            if not self.sdk.is_card_online(self.ip_address):
                logger.warning(f"Huidu controller at {self.ip_address} is not online")
                self.set_status(ConnectionStatus.ERROR)
                return False
            
            # Get device info
            info = self.get_device_info()
            if info:
                self.set_status(ConnectionStatus.CONNECTED)
                logger.info(f"Connected to Huidu controller at {self.ip_address}")
                return True
            else:
                self.set_status(ConnectionStatus.ERROR)
                return False
        except Exception as e:
            logger.error(f"Error connecting to Huidu controller: {e}", exc_info=True)
            self.set_status(ConnectionStatus.ERROR)
            return False
    
    def disconnect(self):
        """Disconnect from controller"""
        self._screen_created = False
        self._current_program_id = None
        self._current_area_id = None
        self.set_status(ConnectionStatus.DISCONNECTED)
        self.device_info = None
        logger.info(f"Disconnected from Huidu controller at {self.ip_address}")
    
    def get_device_info(self) -> Optional[Dict]:
        """Get device information using SDK"""
        try:
            params = self.sdk.get_screen_params(self.ip_address)
            if params:
                controller_id = f"HD-{self.ip_address.replace('.', '-')}"
                self.device_info = {
                    "name": "Huidu Controller",
                    "model": "Gen6",
                    "version": "2.0.2",
                    "ip": self.ip_address,
                    "controller_id": controller_id,
                    "controllerId": controller_id,
                    "serial_number": controller_id,
                    "width": params.get("width", 64),
                    "height": params.get("height", 32),
                    "color": params.get("color", 1),
                    "gray": params.get("gray", 1),
                    "card_type": params.get("card_type", 0)
                }
                return self.device_info
        except Exception as e:
            logger.error(f"Error getting device info: {e}", exc_info=True)
        
        # Fallback info
        controller_id = f"HD-{self.ip_address.replace('.', '-')}"
        self.device_info = {
            "name": "Huidu Controller",
            "model": "Gen6",
            "version": "2.0.2",
            "ip": self.ip_address,
            "controller_id": controller_id
        }
        return self.device_info
    
    def upload_program(self, program_data: Dict, file_path: str = None) -> bool:
        """Upload program to Huidu controller using SDK"""
        if self.status != ConnectionStatus.CONNECTED:
            if not self.connect():
                return False
        
        try:
            self.set_progress(0, "Preparing program...")
            
            # Get screen dimensions from program or device
            width = program_data.get("width", 64)
            height = program_data.get("height", 32)
            
            # Create screen
            if not self.sdk.create_screen(width, height):
                error = self.sdk.get_last_error()
                logger.error(f"Failed to create screen: error {error}")
                return False
            
            self._screen_created = True
            self.set_progress(10, "Screen created")
            
            # Add program
            program_id = self.sdk.add_program()
            if not program_id:
                error = self.sdk.get_last_error()
                logger.error(f"Failed to add program: error {error}")
                return False
            
            self._current_program_id = program_id
            self.set_progress(20, "Program added")
            
            # Process elements
            elements = program_data.get("elements", [])
            total_elements = len(elements)
            
            for idx, element in enumerate(elements):
                self.set_progress(20 + int((idx / total_elements) * 60), f"Processing element {idx + 1}/{total_elements}")
                
                if not self._add_element_to_sdk(element, program_id, width, height):
                    logger.warning(f"Failed to add element: {element.get('type', 'unknown')}")
            
            self.set_progress(90, "Sending to device...")
            
            # Send screen to device
            if not self.sdk.send_screen(self.ip_address):
                error = self.sdk.get_last_error()
                logger.error(f"Failed to send screen: error {error}")
                return False
            
            self.set_progress(100, "Upload complete")
            logger.info(f"Program '{program_data.get('name', 'Unknown')}' uploaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading program: {e}", exc_info=True)
            return False
    
    def _add_element_to_sdk(self, element: Dict, program_id: int, screen_width: int, screen_height: int) -> bool:
        """Convert SLPlayer element to SDK format and add to program"""
        element_type = element.get("type")
        properties = element.get("properties", {})
        
        # Calculate area dimensions (Huidu uses areas for content)
        x = element.get("x", 0)
        y = element.get("y", 0)
        width = element.get("width", 200)
        height = element.get("height", 100)
        
        # Add area for this element
        area_id = self.sdk.add_area(program_id, x, y, width, height)
        if not area_id:
            return False
        
        # Add content based on type
        if element_type == "text":
            text = properties.get("text", "")
            font_family = properties.get("font_family", "Arial")
            font_size = properties.get("font_size", 24)
            color_hex = properties.get("color", "#000000")
            color_rgb = self._hex_to_rgb(color_hex)
            
            item_id = self.sdk.add_text_item(
                area_id, text, font_family, font_size,
                color_rgb, 0, 4, 0, 25, 201, 3
            )
            return item_id is not None
        
        elif element_type == "photo":
            file_path = properties.get("file_path", "")
            if file_path and Path(file_path).exists():
                item_id = self.sdk.add_image_item(area_id, file_path, 0, 30, 201, 3)
                return item_id is not None
        
        elif element_type == "clock":
            show_date = properties.get("show_date", True)
            font_family = properties.get("font_family", "Arial")
            font_size = properties.get("font_size", 48)
            color_hex = properties.get("color", "#000000")
            color_rgb = self._hex_to_rgb(color_hex)
            
            item_id = self.sdk.add_time_item(
                area_id, show_date, True, font_family, font_size, color_rgb
            )
            return item_id is not None
        
        # Other types not directly supported by Huidu SDK
        logger.warning(f"Element type {element_type} not fully supported by Huidu SDK")
        return False
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (0, 0, 0)
    
    def download_program(self, program_id: str = None) -> Optional[Dict]:
        """Download program from controller (not fully supported by Huidu SDK)"""
        logger.warning("Program download not directly supported by Huidu SDK")
        return None
    
    def get_program_list(self) -> List[Dict]:
        """Get program list (not fully supported by Huidu SDK)"""
        logger.warning("Program list not directly supported by Huidu SDK")
        return []
    
    def test_connection(self) -> bool:
        """Test connection to controller"""
        try:
            return self.sdk.is_card_online(self.ip_address)
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return False
```

---

## 4. ViplexCore SDK Integration

### 4.1 SDK Wrapper Implementation

Create `sdk_wrappers/viplexcore_sdk.py`:

```python
import ctypes
import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Callable
from ctypes import wintypes

# Callback type for async functions
ExportViplexCallback = ctypes.WINFUNCTYPE(None, ctypes.c_uint16, ctypes.c_char_p)

class ViplexCoreSDK:
    """Python wrapper for ViplexCore SDK"""
    
    def __init__(self):
        self.dll = None
        self._load_dll()
        self._callbacks = {}  # Store callbacks to prevent garbage collection
        self._callback_results = {}  # Store async results
    
    def _load_dll(self):
        """Load viplexcore.dll"""
        sdk_path = Path(__file__).parent.parent / "requirements" / "ViplexCore3.6.3.0101.CTM21.11.1_x64" / "bin"
        
        dll_path = sdk_path / "viplexcore.dll"
        if not dll_path.exists():
            raise RuntimeError(f"viplexcore.dll not found at {dll_path}")
        
        try:
            # Add bin directory to PATH for dependencies
            os.environ['PATH'] = str(sdk_path) + os.pathsep + os.environ.get('PATH', '')
            
            self.dll = ctypes.CDLL(str(dll_path))
            self._setup_functions()
        except OSError as e:
            raise RuntimeError(f"Failed to load viplexcore.dll: {e}")
    
    def _setup_functions(self):
        """Configure function signatures"""
        # nvInit
        self.dll.nvInit.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.dll.nvInit.restype = ctypes.c_int
        
        # nvInitW (Unicode version)
        self.dll.nvInitW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
        self.dll.nvInitW.restype = ctypes.c_int
        
        # nvSearchTerminalAsync
        self.dll.nvSearchTerminalAsync.argtypes = [ExportViplexCallback]
        self.dll.nvSearchTerminalAsync.restype = None
        
        # nvLoginAsync
        self.dll.nvLoginAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvLoginAsync.restype = None
        
        # nvLoginAsyncW (Unicode)
        self.dll.nvLoginAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvLoginAsyncW.restype = None
        
        # nvCreateProgramAsync
        self.dll.nvCreateProgramAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvCreateProgramAsync.restype = None
        
        # nvCreateProgramAsyncW
        self.dll.nvCreateProgramAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvCreateProgramAsyncW.restype = None
        
        # nvSetPageProgramAsync
        self.dll.nvSetPageProgramAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvSetPageProgramAsync.restype = None
        
        # nvSetPageProgramAsyncW
        self.dll.nvSetPageProgramAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvSetPageProgramAsyncW.restype = None
        
        # nvMakeProgramAsync
        self.dll.nvMakeProgramAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvMakeProgramAsync.restype = None
        
        # nvMakeProgramAsyncW
        self.dll.nvMakeProgramAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvMakeProgramAsyncW.restype = None
        
        # nvStartTransferProgramAsync
        self.dll.nvStartTransferProgramAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvStartTransferProgramAsync.restype = None
        
        # nvStartTransferProgramAsyncW
        self.dll.nvStartTransferProgramAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvStartTransferProgramAsyncW.restype = None
        
        # nvGetProgramInfoAsync
        self.dll.nvGetProgramInfoAsync.argtypes = [ctypes.c_char_p, ExportViplexCallback]
        self.dll.nvGetProgramInfoAsync.restype = None
        
        # nvGetProgramInfoAsyncW
        self.dll.nvGetProgramInfoAsyncW.argtypes = [ctypes.c_wchar_p, ExportViplexCallback]
        self.dll.nvGetProgramInfoAsyncW.restype = None
    
    def init(self, sdk_root_dir: str, credentials: Dict) -> int:
        """Initialize SDK"""
        credentials_json = json.dumps(credentials)
        return self.dll.nvInitW(
            ctypes.c_wchar_p(sdk_root_dir),
            ctypes.c_wchar_p(credentials_json)
        )
    
    def _create_callback(self, callback_id: str) -> ExportViplexCallback:
        """Create callback function for async operations"""
        def callback(code: int, data: bytes):
            data_str = data.decode('utf-8') if data else ""
            self._callback_results[callback_id] = {
                "code": code,
                "data": data_str
            }
        
        cb = ExportViplexCallback(callback)
        self._callbacks[callback_id] = cb  # Keep reference
        return cb
    
    def search_terminal_async(self, callback_id: str = "search") -> None:
        """Search for terminals asynchronously"""
        cb = self._create_callback(callback_id)
        self.dll.nvSearchTerminalAsync(cb)
    
    def login_async(self, login_params: Dict, callback_id: str = "login") -> None:
        """Login to device asynchronously"""
        params_json = json.dumps(login_params)
        cb = self._create_callback(callback_id)
        self.dll.nvLoginAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def create_program_async(self, program_params: Dict, callback_id: str = "create_program") -> None:
        """Create program asynchronously"""
        params_json = json.dumps(program_params)
        cb = self._create_callback(callback_id)
        self.dll.nvCreateProgramAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def set_page_program_async(self, page_params: Dict, callback_id: str = "set_page") -> None:
        """Set page program asynchronously"""
        params_json = json.dumps(page_params)
        cb = self._create_callback(callback_id)
        self.dll.nvSetPageProgramAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def make_program_async(self, make_params: Dict, callback_id: str = "make_program") -> None:
        """Make/generate program asynchronously"""
        params_json = json.dumps(make_params)
        cb = self._create_callback(callback_id)
        self.dll.nvMakeProgramAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def start_transfer_program_async(self, transfer_params: Dict, callback_id: str = "transfer") -> None:
        """Start program transfer asynchronously"""
        params_json = json.dumps(transfer_params)
        cb = self._create_callback(callback_id)
        self.dll.nvStartTransferProgramAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def get_program_info_async(self, info_params: Dict, callback_id: str = "get_info") -> None:
        """Get program info asynchronously"""
        params_json = json.dumps(info_params)
        cb = self._create_callback(callback_id)
        self.dll.nvGetProgramInfoAsyncW(ctypes.c_wchar_p(params_json), cb)
    
    def get_callback_result(self, callback_id: str, timeout: float = 5.0) -> Optional[Dict]:
        """Get callback result (wait for async operation)"""
        import time
        start_time = time.time()
        
        while callback_id not in self._callback_results:
            if time.time() - start_time > timeout:
                return None
            time.sleep(0.1)
        
        result = self._callback_results.pop(callback_id, None)
        return result
    
    def clear_callback_result(self, callback_id: str):
        """Clear callback result"""
        self._callback_results.pop(callback_id, None)
```

### 4.2 Enhanced NovaStarController Implementation

Update `controllers/novastar.py`:

```python
import json
from typing import Optional, Dict, List
from pathlib import Path
from controllers.base_controller import BaseController, ControllerType, ConnectionStatus
from sdk_wrappers.viplexcore_sdk import ViplexCoreSDK
from utils.logger import get_logger
from utils.app_data import get_app_data_dir
import time

logger = get_logger(__name__)


class NovaStarController(BaseController):
    """NovaStar controller using ViplexCore SDK"""
    
    DEFAULT_PORT = 5200
    
    def __init__(self, ip_address: str, port: int = DEFAULT_PORT):
        super().__init__(ControllerType.NOVASTAR, ip_address, port)
        self.sdk = ViplexCoreSDK()
        self._initialized = False
        self._device_sn = None
        self._session_token = None
    
    def _ensure_initialized(self) -> bool:
        """Ensure SDK is initialized"""
        if self._initialized:
            return True
        
        try:
            sdk_root = str(get_app_data_dir() / "viplexcore")
            sdk_root.mkdir(parents=True, exist_ok=True)
            
            credentials = {
                "company": "SLPlayer",
                "phone": "",
                "email": ""
            }
            
            result = self.sdk.init(sdk_root, credentials)
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
        """Connect to NovaStar controller"""
        if self.status == ConnectionStatus.CONNECTED:
            return True
        
        if not self._ensure_initialized():
            return False
        
        self.set_status(ConnectionStatus.CONNECTING)
        
        try:
            # Search for device
            self.sdk.search_terminal_async("search")
            time.sleep(2)  # Wait for search
            
            # Try to login
            login_params = {
                "sn": self.ip_address,  # Use IP as SN for now
                "username": "admin",
                "password": "123456",
                "rememberPwd": 1,
                "loginType": 0
            }
            
            self.sdk.login_async(login_params, "login")
            result = self.sdk.get_callback_result("login", timeout=5.0)
            
            if result and result.get("code") == 0:
                self._device_sn = self.ip_address
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
        """Disconnect from controller"""
        self._device_sn = None
        self._session_token = None
        self.set_status(ConnectionStatus.DISCONNECTED)
        self.device_info = None
        logger.info(f"Disconnected from NovaStar controller at {self.ip_address}")
    
    def get_device_info(self) -> Optional[Dict]:
        """Get device information"""
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
        
        # Try to get program info to verify connection
        try:
            info_params = {"sn": self._device_sn}
            self.sdk.get_program_info_async(info_params, "get_info")
            result = self.sdk.get_callback_result("get_info", timeout=3.0)
            
            if result and result.get("code") == 0:
                # Parse device info from response
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
        
        # Fallback
        controller_id = f"NS-{self.ip_address.replace('.', '-')}"
        self.device_info = {
            "name": "NovaStar Controller",
            "model": "Unknown",
            "version": "3.6.3",
            "ip": self.ip_address,
            "controller_id": controller_id
        }
        return self.device_info
    
    def upload_program(self, program_data: Dict, file_path: str = None) -> bool:
        """Upload program to NovaStar controller using ViplexCore SDK"""
        if self.status != ConnectionStatus.CONNECTED:
            if not self.connect():
                return False
        
        try:
            self.set_progress(0, "Creating program...")
            
            # Step 1: Create program
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
            
            # Step 2: Convert elements to ViplexCore format
            widgets = self._convert_elements_to_widgets(program_data.get("elements", []))
            
            # Step 3: Set page program
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
            
            # Step 4: Make program
            make_params = {
                "programID": 1,
                "outPutPath": str(Path(file_path).parent if file_path else get_app_data_dir() / "programs")
            }
            
            self.sdk.make_program_async(make_params, "make")
            result = self.sdk.get_callback_result("make", timeout=10.0)
            
            if not result or result.get("code") != 0:
                logger.error(f"Failed to make program: {result}")
                return False
            
            self.set_progress(80, "Transferring to device...")
            
            # Step 5: Transfer program
            transfer_params = {
                "sn": self._device_sn,
                "programName": program_data.get("name", "program1"),
                "deviceIdentifier": "Demo",
                "sendProgramFilePaths": {
                    "programPath": make_params["outPutPath"] + "/program1",
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
        """Convert SLPlayer elements to ViplexCore widget format"""
        widgets = []
        
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
            
            if element_type == "text":
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
            
            widgets.append(widget)
        
        return widgets
    
    def download_program(self, program_id: str = None) -> Optional[Dict]:
        """Download program from controller"""
        if not self._device_sn:
            return None
        
        try:
            info_params = {"sn": self._device_sn}
            self.sdk.get_program_info_async(info_params, "download")
            result = self.sdk.get_callback_result("download", timeout=5.0)
            
            if result and result.get("code") == 0:
                data = json.loads(result.get("data", "{}"))
                # Convert ViplexCore format to SLPlayer format
                return self._convert_from_viplexcore_format(data)
        except Exception as e:
            logger.error(f"Error downloading program: {e}", exc_info=True)
        
        return None
    
    def _convert_from_viplexcore_format(self, data: Dict) -> Dict:
        """Convert ViplexCore program format to SLPlayer format"""
        # Implementation depends on ViplexCore response format
        # This is a placeholder
        return {
            "name": data.get("name", "Program"),
            "width": data.get("width", 500),
            "height": data.get("height", 500),
            "elements": []
        }
    
    def get_program_list(self) -> List[Dict]:
        """Get program list from device"""
        # ViplexCore SDK doesn't have direct program list API
        # Would need to use get_program_info with different parameters
        return []
    
    def test_connection(self) -> bool:
        """Test connection to controller"""
        try:
            if not self._ensure_initialized():
                return False
            
            self.sdk.search_terminal_async("test")
            time.sleep(1)
            # Check if device is found in search results
            return True
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return False
```

---

## 5. Implementation Steps

### 5.1 Step-by-Step Integration Plan

1. **Create SDK Wrapper Directory**
   ```bash
   mkdir sdk_wrappers
   touch sdk_wrappers/__init__.py
   ```

2. **Implement SDK Wrappers**
   - Create `sdk_wrappers/huidu_sdk.py` (as shown above)
   - Create `sdk_wrappers/viplexcore_sdk.py` (as shown above)

3. **Update Controller Classes**
   - Replace `controllers/huidu.py` with enhanced implementation
   - Replace `controllers/novastar.py` with enhanced implementation

4. **Add Error Handling**
   - Map SDK error codes to user-friendly messages
   - Add retry logic for network operations
   - Implement timeout handling

5. **Testing**
   - Test with actual devices
   - Verify all content types work
   - Test error scenarios

### 5.2 Content Type Mapping

| SLPlayer Type | Huidu SDK | ViplexCore SDK |
|---------------|-----------|----------------|
| TEXT | `Hd_AddSimpleTextAreaItem` | `ARCH_TEXT` widget |
| SINGLELINE_TEXT | `Hd_AddSimpleTextAreaItem` | `ARCH_TEXT` with scroll |
| PHOTO | `Hd_AddImageAreaItem` | `PICTURE` widget |
| VIDEO | Not directly supported | `VIDEO` widget |
| CLOCK | `Hd_AddTimeAreaItem` | `CLOCK` widget |
| TIMING | `Hd_AddCountAreaItem` | Custom widget |
| SENSOR | `Hd_AddTempAndHumiAreaItem` | Sensor widget |
| HTML | Not supported | `HTML` widget |
| HDMI | Not supported | `HDMI` widget |

### 5.3 Program Data Conversion

**Key Conversion Points:**

1. **Screen Dimensions**
   - SLPlayer: Uses canvas width/height
   - Huidu: Requires screen dimensions in `Hd_CreateScreen`
   - ViplexCore: Uses program width/height in JSON

2. **Element Positioning**
   - SLPlayer: Absolute pixel coordinates
   - Huidu: Area-based positioning (x, y, width, height)
   - ViplexCore: Relative positioning (0.0-1.0) or pixels

3. **Content Properties**
   - Fonts, colors, animations need mapping
   - File paths need to be absolute and accessible
   - Duration and timing need conversion

4. **Playback Control**
   - SLPlayer play_mode/play_control → SDK scheduling
   - Huidu: `Hd_SetProgramParam`
   - ViplexCore: Program constraints in JSON

---

## 6. Challenges and Solutions

### 6.1 Challenge: Async Operations (ViplexCore)

**Problem:** ViplexCore uses async callbacks, but Python code is synchronous.

**Solution:**
- Use callback storage with timeout waiting
- Consider using threading for true async operations
- Or use asyncio with callback wrappers

### 6.2 Challenge: String Encoding

**Problem:** SDKs use Unicode (wchar_t*), Python strings need conversion.

**Solution:**
- Use `ctypes.c_wchar_p` for Unicode strings
- Ensure proper encoding when converting
- Handle encoding errors gracefully

### 6.3 Challenge: File Path Management

**Problem:** Media files need to be accessible to SDKs.

**Solution:**
- Use absolute paths
- Copy files to SDK-accessible locations if needed
- Manage file lifecycle (copy/cleanup)

### 6.4 Challenge: Error Handling

**Problem:** SDK errors are numeric codes, need user-friendly messages.

**Solution:**
- Create error code mapping dictionaries
- Log detailed errors, show user-friendly messages
- Provide error recovery options

---

## 7. Testing Recommendations

### 7.1 Unit Tests

- Test SDK wrapper initialization
- Test function parameter conversion
- Test error code mapping
- Test callback handling

### 7.2 Integration Tests

- Test controller connection
- Test program upload with various content types
- Test program download
- Test error scenarios

### 7.3 Manual Testing Checklist

- [ ] Connect to Huidu controller
- [ ] Connect to NovaStar controller
- [ ] Upload text program
- [ ] Upload image program
- [ ] Upload video program (NovaStar only)
- [ ] Upload clock program
- [ ] Test scheduling features
- [ ] Test error handling
- [ ] Test reconnection after disconnect

---

## 8. Future Enhancements

### 8.1 Additional Features

1. **Real-time Updates**
   - Use Huidu real-time area functions
   - Use ViplexCore real-time text/image updates

2. **Device Discovery**
   - Implement Huidu device search
   - Use ViplexCore `nvSearchTerminalAsync`

3. **Advanced Scheduling**
   - Implement complex scheduling rules
   - Support multiple programs per device

4. **Media Management**
   - Automatic media file handling
   - Media library management
   - Thumbnail generation

### 8.2 Performance Optimizations

1. **Async Operations**
   - Use threading for SDK operations
   - Non-blocking UI updates
   - Progress reporting

2. **Caching**
   - Cache device information
   - Cache program data
   - Reduce redundant SDK calls

---

## 9. Conclusion

This integration guide provides a comprehensive approach to integrating both SDKs into the SLPlayer project. The key points are:

1. **Use ctypes for Python-SDK communication** - Simplest approach for this project
2. **Create wrapper modules** - Isolate SDK complexity from application code
3. **Enhance existing controllers** - Replace stubs with real SDK implementations
4. **Handle async operations** - Use callbacks with timeout waiting
5. **Map content types** - Convert SLPlayer format to SDK-specific formats
6. **Implement error handling** - User-friendly error messages and recovery

The implementation should be done incrementally, starting with basic functionality (text, images) and gradually adding support for more content types and features.

---

*Integration Guide Version: 1.0*  
*Last Updated: 2024*

