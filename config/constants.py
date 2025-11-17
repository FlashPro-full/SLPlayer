"""
Application constants and enums
"""
from enum import Enum


class ContentType(Enum):
    """Content type enumeration"""
    PROGRAM = "program"
    CUSTOM_AREA = "custom_area"
    VIDEO = "video"
    PHOTO = "photo"
    TEXT = "text"
    SINGLE_LINE_TEXT = "single_line_text"
    ANIMATION = "animation"
    TEXT_3D = "text_3d"
    CLOCK = "clock"
    CALENDAR = "calendar"
    TIMING = "timing"
    WEATHER = "weather"
    SENSOR = "sensor"
    NEON = "neon"
    WPS = "wps"
    TABLE = "table"
    OFFICE = "office"
    DIGITAL_WATCH = "digital_watch"
    HTML = "html"
    LIVESTREAM = "livestream"
    QR_CODE = "qr_code"
    HDMI = "hdmi"


class PlayMode(Enum):
    """Play mode enumeration"""
    PLAY_TIMES = "play_times"
    FIXED_LENGTH = "fixed_length"


class ConnectionStatus(Enum):
    """Controller connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


# Application metadata
APP_NAME = "SLPlayer"
APP_VERSION = "1.0.0"
APP_AUTHOR = "SLPlayer Team"

# Default canvas settings
DEFAULT_CANVAS_WIDTH = 1920
DEFAULT_CANVAS_HEIGHT = 1080
CANVAS_CHECKER_SIZE = 20  # Size of checkered pattern squares

# Supported image formats
SUPPORTED_IMAGE_FORMATS = ["png", "jpg", "jpeg", "gif", "bmp"]

# Supported video formats
SUPPORTED_VIDEO_FORMATS = ["mp4", "avi", "mov", "mkv", "wmv"]

# Animation settings
ANIMATION_FPS = 30  # Frames per second for animations
ANIMATION_TIMER_INTERVAL = 33  # Milliseconds (1000/30 ≈ 33ms for 30 FPS)

# Emoji rendering settings
DEFAULT_EMOJI_SIZE = 64  # Default pixel size for emoji rendering

# Toolbar font sizes
TOOLBAR_FONT_SIZE_SMALL = 12  # Small font size for toolbar buttons
TOOLBAR_FONT_SIZE_MEDIUM = 14  # Medium font size for toolbar buttons and menu items
TOOLBAR_FONT_SIZE_LARGE = 18  # Large font size for emojis in menu items

