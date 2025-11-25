# How to Upload Programs to NovaStar and Huidu Controllers

## Overview

This guide explains how to upload/plant saved program files (`.soo` format) to NovaStar and Huidu LED display controllers via SDK.

## Prerequisites

1. **Controller Hardware Connected**: Ensure your NovaStar or Huidu controller is connected to the network and powered on
2. **Network Access**: PC must be on the same network as the controller
3. **Controller IP Address**: Know the IP address of your controller
4. **Program File Ready**: Have a saved `.soo` file or create a program in the application

## Step-by-Step Upload Process

### Method 1: Upload via UI (Recommended)

#### Step 1: Load Program File

1. **Open Application**: Launch SLPlayer application
2. **Load Screen File**:
   - Click `File` → `Open` (or press `Ctrl+O`)
   - Select your `.soo` file
   - The program will be loaded into the application

#### Step 2: Connect to Controller

1. **Discover Controllers** (Optional):
   - Go to `Control` menu → `Discover Controllers`
   - This will search for available controllers on the network

2. **Connect to Controller**:
   - Go to `Control` menu → `Connect`
   - Enter controller information:
     - **IP Address**: e.g., `192.168.1.100`
     - **Port**: 
       - NovaStar: `5200` (default)
       - Huidu: `5000` (default)
     - **Controller Type**: Select `NovaStar` or `Huidu`
   - Click `Connect`

3. **Verify Connection**:
   - Check connection status indicator
   - Connection status should show "Connected"

#### Step 3: Select Program

1. **Select Screen**: Select the screen containing your program
2. **Select Program**: Select the program you want to upload
   - Ensure the program has all desired elements (text, images, videos, animations, etc.)

#### Step 4: Upload Program

1. **Click Send Button**:
   - Click the `⬆️ Send` button in the Control toolbar, OR
   - Go to `Control` menu → `Send`

2. **Wait for Upload**:
   - Progress indicator will show upload status
   - The application will:
     - Save all current properties
     - Convert program structure using property adapter
     - Connect to controller (if not already connected)
     - Upload program to controller via SDK
     - Display success/error message

3. **Verify Upload**:
   - Success message: "Program sent successfully"
   - Check controller display to confirm program is running

---

### Method 2: Programmatic Upload (For Developers)

#### Using ControllerService

```python
from services.controller_service import ControllerService
from controllers.base_controller import ControllerType

# Initialize service
controller_service = ControllerService()

# Connect to NovaStar controller
success = controller_service.connect_to_controller(
    ip="192.168.1.100",
    port=5200,
    controller_type="novastar"
)

# Or connect to Huidu controller
success = controller_service.connect_to_controller(
    ip="192.168.1.100",
    port=5000,
    controller_type="huidu"
)

# Load program from file
from core.file_manager import FileManager
from core.screen_manager import ScreenManager

file_manager = FileManager()
screen_manager = ScreenManager()
file_manager.screen_manager = screen_manager

screen = file_manager.load_screen_from_file("path/to/program.soo")
if screen and screen.programs:
    program = screen.programs[0]
    
    # Upload program
    result = controller_service.send_program(program)
    if result:
        print("Program uploaded successfully!")
    else:
        print("Upload failed!")
```

#### Using Controllers Directly

```python
from controllers.novastar import NovaStarController
from controllers.huidu import HuiduController
from core.file_manager import FileManager

# Load program
file_manager = FileManager()
screen = file_manager.load_screen_from_file("path/to/program.soo")

if screen and screen.programs:
    program = screen.programs[0]
    program_dict = program.to_dict()
    
    # For NovaStar
    novastar = NovaStarController("192.168.1.100", 5200)
    if novastar.connect():
        result = novastar.upload_program(program_dict)
        if result:
            print("Uploaded to NovaStar successfully!")
        novastar.disconnect()
    
    # For Huidu
    huidu = HuiduController("192.168.1.100", 5000)
    if huidu.connect():
        result = huidu.upload_program(program_dict)
        if result:
            print("Uploaded to Huidu successfully!")
        huidu.disconnect()
```

---

## Technical Details

### Upload Process Flow

1. **Property Saving**: 
   - All current UI properties are saved to the program before upload
   - `PropertiesPanel.save_all_current_properties()` is called

2. **Property Adaptation**:
   - `PropertyAdapter.adapt_element_for_controller()` converts nested structure to controller-expected format
   - Default values are applied for missing properties
   - Element types are mapped appropriately:
     - Animation → Text (for controllers that don't support animation)
     - Weather → Text (for controllers that don't support weather)
     - Sensor → Sensor item with mapped sensor type

3. **Controller Upload**:
   - **NovaStar**: Uses `ViplexCoreSDK` to create program, add widgets, generate and transfer
   - **Huidu**: Uses `HuiduSDK` to create screen, add areas, add items, and send to device

### Element Type Support

#### NovaStar Controller
- ✅ Text / Singleline Text → ARCH_TEXT widget
- ✅ Photo → PICTURE widget
- ✅ Video → VIDEO widget
- ✅ Clock → CLOCK widget
- ✅ HTML → HTML widget
- ✅ HDMI → HDMI widget
- ✅ Animation → ARCH_TEXT widget (text content)
- ✅ Weather → ARCH_TEXT widget (text content)
- ✅ Timing → ARCH_TEXT widget (text content)
- ✅ Sensor → ARCH_TEXT widget (text content)

#### Huidu Controller
- ✅ Text / Singleline Text → Text item
- ✅ Photo → Image item
- ✅ Clock → Time item
- ✅ Sensor → Sensor item
- ✅ Timing → Count item
- ✅ Animation → Text item (text content)
- ✅ Weather → Text item (text content)
- ❌ Video (not supported)
- ❌ HTML (not supported)
- ❌ HDMI (not supported)

### Property Mapping

The property adapter automatically converts nested properties to flat structure:

**Saved Structure:**
```json
{
  "properties": {
    "text": {
      "content": "Hello",
      "format": {
        "font_family": "Arial",
        "font_size": 24,
        "font_color": "#FF0000"
      }
    }
  }
}
```

**Controller-Expected Structure:**
```json
{
  "properties": {
    "text": "Hello",
    "font_family": "Arial",
    "font_size": 24,
    "color": "#FF0000"
  }
}
```

---

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to controller
- **Solution**: 
  - Verify controller IP address is correct
  - Check network connectivity (ping controller IP)
  - Ensure controller is powered on
  - Check firewall settings
  - Verify port numbers (NovaStar: 5200, Huidu: 5000)

### Upload Failures

**Problem**: Upload fails with error message
- **Solution**:
  - Check controller connection status
  - Verify program has valid elements
  - Check SDK DLL files are present:
    - NovaStar: `viplexcore.dll`
    - Huidu: `HDSDK.dll`
  - Check log files for detailed error messages

### Missing Properties

**Problem**: Some element properties don't appear on controller
- **Solution**:
  - Default values are automatically applied
  - Check if element type is supported by controller
  - Some properties may be converted (e.g., animation → text)

### Element Not Displaying

**Problem**: Element uploaded but not visible
- **Solution**:
  - Check element coordinates are within screen bounds
  - Verify element has valid content (text, file path, etc.)
  - Check element is enabled
  - For images/videos, verify file paths are accessible

---

## API Reference

### ControllerService Methods

```python
# Connect to controller
connect_to_controller(ip: str, port: int, controller_type: str) -> bool

# Disconnect from controller
disconnect() -> bool

# Send program to controller
send_program(program: Program) -> bool

# Get connection status
is_connected() -> bool

# Get device information
get_device_info() -> Dict[str, Any]
```

### Controller Methods

```python
# Connect to controller
connect() -> bool

# Disconnect from controller
disconnect()

# Upload program
upload_program(program_data: Dict, file_path: str = None) -> bool

# Get device info
get_device_info() -> Optional[Dict]

# Test connection
test_connection() -> bool
```

---

## Examples

### Example 1: Upload Current Program

```python
from services.program_action_service import ProgramActionService
from services.controller_service import ControllerService
from core.program_manager import ProgramManager

# Initialize services
controller_service = ControllerService()
program_manager = ProgramManager()
action_service = ProgramActionService(program_manager, controller_service)

# Connect first
controller_service.connect_to_controller("192.168.1.100", 5200, "novastar")

# Upload current program
action_service.send_program()
```

### Example 2: Upload from File

```python
from core.file_manager import FileManager
from services.controller_service import ControllerService

file_manager = FileManager()
controller_service = ControllerService()

# Load file
screen = file_manager.load_screen_from_file("program.soo")

# Connect
controller_service.connect_to_controller("192.168.1.100", 5000, "huidu")

# Upload first program
if screen and screen.programs:
    controller_service.send_program(screen.programs[0])
```

---

## Notes

1. **Auto-Save**: Properties are automatically saved before upload
2. **Property Adapter**: Automatically converts structure for controller compatibility
3. **Default Values**: Missing properties are filled with defaults during upload
4. **Progress Tracking**: Upload progress is displayed during the process
5. **Error Handling**: Detailed error messages are logged for troubleshooting

---

## Support

For issues or questions:
1. Check log files in application data directory
2. Review error messages in UI
3. Verify SDK files are properly installed
4. Check controller documentation for specific requirements

