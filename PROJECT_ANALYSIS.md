# SLPlayer Project Analysis

## Main Purpose

**SLPlayer** is a comprehensive LED display controller program management system designed for professional LED display content creation and management. It enables users to:

- Create and edit multimedia programs (text, images, videos, animations, widgets)
- Connect to and manage NovaStar and Huidu LED display controllers
- Upload/download programs between PC and controllers
- Schedule content playback with time-based and date-based rules
- Manage licenses for controller activation
- Preview content in real-time before deployment
- Synchronize data between local PC and remote controllers

The application serves as a complete solution for LED display content management, from creation to deployment and scheduling.

---

## Project Structure

```
SLPlayer(Python)/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
│
├── config/                    # Configuration management
│   ├── __init__.py
│   ├── constants.py          # Application constants and enums
│   ├── i18n.py               # Internationalization (i18n) support
│   └── settings.py           # Settings management (JSON-based)
│
├── core/                      # Core business logic
│   ├── __init__.py
│   ├── auto_save.py          # Automatic save system
│   ├── backup_restore.py     # Backup and restore functionality
│   ├── content_element.py    # Content element definitions
│   ├── controller_database.py # Controller database management
│   ├── controller_discovery.py # Network controller discovery
│   ├── export_handler.py     # Export functionality
│   ├── file_manager.py       # .soo file operations
│   ├── image_effects.py      # Image effect processing
│   ├── keyframe_system.py   # Keyframe animation system
│   ├── license_manager.py   # License activation/management
│   ├── license_verifier.py  # License verification (RSA)
│   ├── media_library.py     # Media library management
│   ├── media_processor.py   # Media processing utilities
│   ├── optimization.py     # Performance optimization
│   ├── program_manager.py   # Program CRUD operations
│   ├── resource_manager.py  # Resource management
│   ├── schedule_manager.py  # Scheduling system
│   ├── screen_manager.py    # Screen/program grouping
│   ├── startup_service.py   # Startup initialization
│   ├── sync_manager.py      # PC ↔ Controller synchronization
│   ├── templates.py         # Program templates
│   ├── text_3d_renderer.py # 3D text rendering
│   ├── timer_widget.py     # Timer widget functionality
│   ├── undo_redo.py        # Undo/redo system
│   └── weather_widget.py   # Weather widget functionality
│
├── controllers/              # Controller communication layer
│   ├── __init__.py
│   ├── base_controller.py   # Abstract base controller interface
│   ├── huidu.py            # Huidu controller protocol
│   ├── network_manager.py   # Network communication utilities
│   └── novastar.py         # NovaStar controller protocol
│
├── ui/                       # User interface components
│   ├── __init__.py
│   ├── alignment_tools.py  # Alignment tools for canvas
│   ├── login_dialog.py     # Login and license activation dialog
│   ├── main_window.py      # Main application window
│   ├── media_player_panel.py # Media preview/playback panel
│   ├── menu_bar.py         # Application menu bar
│   ├── program_list_panel.py # Program list sidebar
│   ├── properties_panel.py # Properties editor panel
│   ├── screen_settings_dialog.py # Screen configuration dialog
│   ├── status_bar.py       # Status bar component
│   ├── styles.py           # UI styling and themes
│   ├── toolbar.py          # Toolbar components
│   └── widgets/            # Custom UI widgets
│       ├── __init__.py
│       ├── loading_spinner.py # Loading spinner widget
│       └── toast.py        # Toast notification widget
│
├── media/                    # Media processing
│   ├── __init__.py
│   ├── animation_engine.py # Animation system
│   └── transition_engine.py # Transition effects engine
│
├── utils/                    # Utility modules
│   ├── __init__.py
│   ├── app_data.py         # Application data directory management
│   ├── device_id.py        # Device ID generation
│   ├── icon_manager.py     # Icon management
│   ├── logger.py           # Logging system
│   ├── ntp_sync.py         # NTP time synchronization
│   └── windows_icon.py     # Windows-specific icon handling
│
├── resources/                # Application resources
│   ├── app.ico             # Application icon
│   ├── controller_models_seed.json # Controller model data
│   └── Reference/          # Reference resources (images, effects, etc.)
│
└── requirements/            # Project requirements and specs
    ├── SLPlayer_-_Functional_Specifications_EN.pdf
    └── [various resource files]
```

---

## Detailed File Purposes

### Root Files

#### `main.py`
- **Purpose**: Application entry point
- **Key Functions**:
  - Initializes PyQt5 application
  - Handles command-line arguments (`--reset-first-launch`, `--skip-license`, `.soo` file loading)
  - Manages first-launch network setup dialog
  - Performs license verification at startup
  - Creates and displays main window
  - Loads autosaved `.soo` files on startup

#### `requirements.txt`
- **Purpose**: Python package dependencies
- **Key Dependencies**:
  - PyQt5 (GUI framework)
  - Pillow, opencv-python (media processing)
  - cryptography (license system)
  - requests, aiohttp (network communication)
  - PyOpenGL, moderngl (3D graphics)
  - numpy (numerical operations)

#### `README.md`
- **Purpose**: Project documentation with features, installation, usage instructions

---

### Configuration (`config/`)

#### `config/constants.py`
- **Purpose**: Application-wide constants and enumerations
- **Key Contents**:
  - `ContentType` enum (PROGRAM, VIDEO, TEXT, CLOCK, WEATHER, etc.)
  - `PlayMode` enum (PLAY_TIMES, FIXED_LENGTH)
  - `ConnectionStatus` enum
  - Default canvas dimensions (1920x1080)
  - Supported media formats
  - Animation settings (FPS, intervals)

#### `config/i18n.py`
- **Purpose**: Internationalization support
- **Functions**: Language switching, translation management

#### `config/settings.py`
- **Purpose**: Settings management with JSON persistence
- **Key Features**:
  - Dot-notation access (`settings.get("window.width")`)
  - Default settings with validation
  - Settings stored in `~/.slplayer/settings.json`
  - Window dimensions, canvas settings, controller defaults, license API URLs

---

### Core Modules (`core/`)

#### `core/program_manager.py`
- **Purpose**: Program (content) management
- **Key Classes**:
  - `Program`: Represents a program with elements, properties, play modes
  - `ProgramManager`: CRUD operations for programs
- **Features**: Create, delete, update programs; manage program list

#### `core/file_manager.py`
- **Purpose**: `.soo` file operations (SLPlayer's native format)
- **Key Functions**:
  - `load_soo_file()`: Load program from `.soo` file
  - `save_soo_file_for_screen()`: Save screen with all programs to `.soo`
  - `load_latest_soo_files()`: Auto-load all `.soo` files from work directory
- **File Format**: JSON-based with screen properties and programs array

#### `core/screen_manager.py`
- **Purpose**: Screen management (screens group multiple programs)
- **Functions**: Screen name resolution, program grouping, screen operations

#### `core/schedule_manager.py`
- **Purpose**: Scheduling system for time-based content playback
- **Features**: Time ranges, day-of-week, date ranges, playlist scheduling

#### `core/sync_manager.py`
- **Purpose**: Synchronization between PC and controllers
- **Features**: Hash-based diff comparison, intelligent sync, upload/download

#### `core/license_manager.py`
- **Purpose**: License activation and management
- **Key Functions**:
  - `activate_license()`: Activate license via server API
  - `get_license_file_path()`: Get local license file path
  - `request_transfer()`: Request license transfer to new device
- **API**: Communicates with Starled Italia license server

#### `core/license_verifier.py`
- **Purpose**: License verification using RSA signatures
- **Features**: RSA+SHA256 signature verification, offline validation

#### `core/auto_save.py`
- **Purpose**: Automatic save system
- **Features**: Periodic auto-save, configurable interval, background saving

#### `core/backup_restore.py`
- **Purpose**: Backup and restore functionality
- **Features**: Full backup of user data, restore from backup

#### `core/content_element.py`
- **Purpose**: Content element type definitions and properties
- **Features**: Element structure, property validation

#### `core/controller_database.py`
- **Purpose**: Controller database management
- **Features**: Store controller information, model data

#### `core/controller_discovery.py`
- **Purpose**: Network-based controller discovery
- **Features**: Scan network for controllers, auto-detect IP addresses

#### `core/export_handler.py`
- **Purpose**: Export functionality
- **Features**: Export programs to various formats

#### `core/image_effects.py`
- **Purpose**: Image effect processing
- **Features**: Apply effects to images (filters, transformations)

#### `core/keyframe_system.py`
- **Purpose**: Keyframe animation system
- **Features**: Keyframe-based animations, interpolation

#### `core/media_library.py`
- **Purpose**: Media library management
- **Features**: Organize media files, metadata management

#### `core/media_processor.py`
- **Purpose**: Media processing utilities
- **Features**: Image/video processing, format conversion

#### `core/optimization.py`
- **Purpose**: Performance optimization
- **Features**: Code optimization, caching strategies

#### `core/resource_manager.py`
- **Purpose**: Resource management
- **Features**: Manage application resources (images, fonts, etc.)

#### `core/templates.py`
- **Purpose**: Program templates
- **Features**: Pre-defined program templates, template system

#### `core/text_3d_renderer.py`
- **Purpose**: 3D text rendering
- **Features**: Render 3D text effects using OpenGL

#### `core/timer_widget.py`
- **Purpose**: Timer widget functionality
- **Features**: Countdown timer, time display widget

#### `core/undo_redo.py`
- **Purpose**: Undo/redo system
- **Features**: Command pattern for undo/redo operations

#### `core/weather_widget.py`
- **Purpose**: Weather widget functionality
- **Features**: Weather data display, API integration

#### `core/startup_service.py`
- **Purpose**: Startup initialization service
- **Features**: License verification at startup, initialization sequence

---

### Controllers (`controllers/`)

#### `controllers/base_controller.py`
- **Purpose**: Abstract base class for all controller implementations
- **Key Classes**:
  - `BaseController`: Abstract interface
  - `ConnectionStatus`: Connection state enum
  - `ControllerType`: Controller type enum (NOVASTAR, HUIDU)
- **Key Methods**:
  - `connect()`, `disconnect()`: Connection management
  - `get_device_info()`: Get controller information
  - `get_controller_id()`: Get unique controller ID for licensing
- **Features**: Status callbacks, progress reporting

#### `controllers/novastar.py`
- **Purpose**: NovaStar controller protocol implementation
- **Features**: NovaStar-specific commands, protocol handling

#### `controllers/huidu.py`
- **Purpose**: Huidu controller protocol implementation
- **Features**: Huidu-specific commands, protocol handling

#### `controllers/network_manager.py`
- **Purpose**: Network communication utilities
- **Features**: TCP/UDP communication, connection management, error handling

---

### User Interface (`ui/`)

#### `ui/main_window.py`
- **Purpose**: Main application window
- **Key Components**:
  - Program list panel (left sidebar)
  - Media player panel (center canvas)
  - Properties panel (bottom)
  - Multiple toolbars
- **Key Functions**:
  - Program creation, deletion, renaming
  - Screen management
  - Content type selection
  - File operations (load/save `.soo` files)
  - UI updates and refresh

#### `ui/menu_bar.py`
- **Purpose**: Application menu bar
- **Features**: File menu, Edit menu, View menu, Control menu, Help menu

#### `ui/program_list_panel.py`
- **Purpose**: Program list sidebar
- **Features**: 
  - Display programs grouped by screen
  - Program selection, renaming, deletion
  - Context menus for programs and screens
  - Drag-and-drop support

#### `ui/media_player_panel.py`
- **Purpose**: Media preview and playback panel
- **Features**: 
  - Canvas for content display
  - Playback controls (play, pause, stop)
  - Real-time preview
  - Element positioning and editing

#### `ui/properties_panel.py`
- **Purpose**: Properties editor panel
- **Features**: 
  - Edit element properties
  - Edit program properties
  - Edit screen properties
  - Property validation

#### `ui/login_dialog.py`
- **Purpose**: Login and license activation dialog
- **Features**: 
  - Username/password authentication
  - License key entry
  - License activation flow
  - Email-based activation

#### `ui/screen_settings_dialog.py`
- **Purpose**: Screen configuration dialog
- **Features**: 
  - Screen dimensions (width, height)
  - Rotation settings
  - Controller brand/model selection
  - Controller ID selection

#### `ui/toolbar.py`
- **Purpose**: Toolbar components
- **Key Toolbars**:
  - `ProgramToolbar`: Program operations (new, save, etc.)
  - `ContentTypesToolbar`: Content type selection buttons
  - `PlaybackToolbar`: Playback controls
  - `ControlToolbar`: Controller operations

#### `ui/status_bar.py`
- **Purpose**: Status bar component
- **Features**: Connection status, progress indicators, messages

#### `ui/styles.py`
- **Purpose**: UI styling and themes
- **Features**: CSS-like styling, theme management

#### `ui/alignment_tools.py`
- **Purpose**: Alignment tools for canvas
- **Features**: Align elements, distribute spacing, snap to grid

#### `ui/widgets/loading_spinner.py`
- **Purpose**: Loading spinner widget
- **Features**: Animated loading indicator

#### `ui/widgets/toast.py`
- **Purpose**: Toast notification widget
- **Features**: Temporary notification messages

---

### Media Processing (`media/`)

#### `media/animation_engine.py`
- **Purpose**: Animation system
- **Key Classes**:
  - `AnimationType`: Animation type enum (scroll, marquee, fade, etc.)
  - `AnimationEngine`: Animation processing engine
- **Features**: Text animations, element animations, timing control

#### `media/transition_engine.py`
- **Purpose**: Transition effects engine
- **Key Classes**:
  - `TransitionType`: Transition type enum (fade, slide, zoom, etc.)
  - `TransitionEngine`: Transition processing engine
- **Features**: IN/OUT transitions, timing, easing functions

---

### Utilities (`utils/`)

#### `utils/logger.py`
- **Purpose**: Centralized logging system
- **Key Features**:
  - File logging with rotation (10MB max, 5 backups)
  - Console logging
  - Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Logs stored in `~/.slplayer/logs/`

#### `utils/app_data.py`
- **Purpose**: Application data directory management
- **Features**: 
  - Get application data directory (`~/.slplayer/`)
  - Get settings file path
  - Get licenses directory
  - Cross-platform support

#### `utils/device_id.py`
- **Purpose**: Device ID generation
- **Features**: Generate unique device ID for license activation, persistence

#### `utils/icon_manager.py`
- **Purpose**: Icon management
- **Features**: Load application icons, set taskbar icons (Windows)

#### `utils/ntp_sync.py`
- **Purpose**: NTP time synchronization
- **Features**: Sync time with NTP server (it.pool.ntp.org)

#### `utils/windows_icon.py`
- **Purpose**: Windows-specific icon handling
- **Features**: Set Windows taskbar icon using Windows API

---

### Resources (`resources/`)

#### `resources/app.ico`
- **Purpose**: Application icon file

#### `resources/controller_models_seed.json`
- **Purpose**: Seed data for controller models (brands, models, specifications)

#### `resources/Reference/`
- **Purpose**: Reference resources
  - `config/`: Reference configuration files
  - `Effects/`: Shader effects files
  - `images/`: Reference images (backgrounds, borders, effects)
  - `neon_gif_background/`: Neon GIF backgrounds
  - `NeonPic/`: Neon picture resources
  - `samples/`: Sample files

---

## Architecture Overview

### Design Patterns

1. **MVC-like Architecture**:
   - **Model**: `core/` modules (business logic)
   - **View**: `ui/` modules (presentation)
   - **Controller**: `controllers/` modules (communication)

2. **Abstract Base Classes**:
   - `BaseController` provides interface for controller implementations
   - Protocol-specific implementations (`NovaStar`, `Huidu`) inherit from base

3. **Singleton Pattern**:
   - `Settings` class (global settings instance)
   - `Logger` class (centralized logging)

4. **Manager Pattern**:
   - `ProgramManager`, `ScheduleManager`, `SyncManager`, `LicenseManager`
   - Centralized management of related operations

### Data Flow

1. **Program Creation**:
   - User creates program → `ProgramManager.create_program()`
   - Program saved → `FileManager.save_soo_file_for_screen()`
   - Auto-save → `AutoSaveManager` periodically saves

2. **Controller Communication**:
   - User connects → `BaseController.connect()`
   - Protocol-specific handler (`NovaStar`/`Huidu`) handles communication
   - `NetworkManager` manages network layer

3. **License Activation**:
   - Startup → `StartupService.verify_license_at_startup()`
   - Activation → `LicenseManager.activate_license()`
   - Verification → `LicenseVerifier.verify_license()`

4. **Synchronization**:
   - User triggers sync → `SyncManager.sync()`
   - Hash comparison → Determine changes
   - Upload/Download → Controller communication

### File Format

**`.soo` File Structure** (JSON):
```json
{
  "screen_name": "Screen1",
  "screen_properties": {
    "width": 1920,
    "height": 1080,
    "rotate": 0,
    "brand": "NovaStar",
    "model": "M30",
    "controller_id": "..."
  },
  "programs": [
    {
      "id": "program_...",
      "name": "Program 1",
      "elements": [...],
      "properties": {...},
      "play_mode": {...},
      "play_control": {...}
    }
  ]
}
```

---

## Key Features

### 1. Program Management
- Create, edit, delete programs
- Multiple programs per screen
- Auto-save functionality
- Undo/redo support

### 2. Content Types
- **Text**: Rich text with fonts, colors, effects
- **Images**: PNG, JPG, GIF, BMP support
- **Videos**: MP4, AVI, MOV support
- **Animations**: Scroll, marquee, fade, typewriter, bounce, flash
- **Widgets**: Clock, Calendar, Weather, Timer, 3D Text, Neon effects
- **Transitions**: 10+ transition types with IN/OUT support

### 3. Controller Support
- **NovaStar**: Full protocol support
- **Huidu**: Full protocol support
- **Auto-Discovery**: Network scanning
- **Connection Management**: Real-time status monitoring

### 4. Scheduling
- Time-based scheduling (from/to times)
- Day-of-week scheduling
- Date range scheduling
- Playlist scheduling
- Priority-based content switching

### 5. Synchronization
- **Import**: Download all controller data
- **Export**: Upload changes to controller
- **Hash-based Diff**: Intelligent change detection
- **Offline Editing**: Work offline, sync when ready

### 6. License System
- Server-based activation
- RSA signature verification
- Offline validation
- Multi-controller support
- License transfer requests

### 7. Preview System
- Real-time preview window
- Playback controls
- Resolution scaling
- Fullscreen preview

---

## Technology Stack

- **GUI Framework**: PyQt5
- **Media Processing**: Pillow, OpenCV, pygame
- **3D Graphics**: PyOpenGL, ModernGL
- **Network**: requests, aiohttp
- **Cryptography**: cryptography (RSA)
- **Data**: JSON for file format, SQLite (implied for controller database)
- **Logging**: Python logging with rotation
- **Platform**: Cross-platform (Windows, Linux, macOS)

---

## Development Status

**Completion**: ~95%

### Fully Implemented ✅
- Startup and Authentication
- Time, Power and Brightness Management
- Content & Programming (all features)
- Scheduling System
- Diagnostics & Safety
- Import/Export Synchronization
- Controller Drivers (structure complete)
- License System (client with remote API support)
- Preview System
- Enhanced Controller ID
- Email Transfer Requests
- First Launch Network Setup

### Protocol-Dependent ⚠️
- Full controller data reading (requires protocol docs)
- Protocol-specific functions (NTP sync, brightness, power schedule)
- Network config apply and reboot

### Optional Enhancements 📝
- Comprehensive test suite expansion
- User manual documentation
- Advanced video editing features
- Additional widget types

---

## Configuration

### Settings Location
- **Settings**: `~/.slplayer/settings.json`
- **Licenses**: `~/.slplayer/licenses/<controller_id>.slp`
- **Logs**: `~/.slplayer/logs/slplayer.log`
- **Work Files**: `~/.slplayer/work/*.soo`

### Key Settings
- Window dimensions and position
- Auto-save interval
- License API URL
- SMTP settings (for license transfer)
- Language preference

---

## Summary

SLPlayer is a professional-grade LED display content management system with comprehensive features for content creation, controller management, scheduling, and synchronization. The architecture is modular and extensible, with clear separation between UI, business logic, and controller communication layers. The application supports multiple controller types, extensive content types, and includes a robust license management system.

