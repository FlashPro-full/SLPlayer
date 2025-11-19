from enum import Enum


class ContentType(Enum):
    PROGRAM = "program"
    VIDEO = "video"
    PHOTO = "photo"
    TEXT = "text"
    SINGLE_LINE_TEXT = "single_line_text"
    ANIMATION = "animation"
    CLOCK = "clock"
    TIMING = "timing"
    WEATHER = "weather"
    SENSOR = "sensor"
    HTML = "html"
    HDMI = "hdmi"


class PlayMode(Enum):
    PLAY_TIMES = "play_times"
    FIXED_LENGTH = "fixed_length"


class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


APP_NAME = "SLPlayer"
APP_VERSION = "1.0.0"
APP_AUTHOR = "SLPlayer Team"

DEFAULT_CANVAS_WIDTH = 1920
DEFAULT_CANVAS_HEIGHT = 1080
CANVAS_CHECKER_SIZE = 20

SUPPORTED_IMAGE_FORMATS = ["png", "jpg", "jpeg", "gif", "bmp"]

SUPPORTED_VIDEO_FORMATS = ["mp4", "avi", "mov", "mkv", "wmv"]

ANIMATION_FPS = 30
ANIMATION_TIMER_INTERVAL = 33

DEFAULT_EMOJI_SIZE = 64

TOOLBAR_FONT_SIZE_SMALL = 12
TOOLBAR_FONT_SIZE_MEDIUM = 14
TOOLBAR_FONT_SIZE_LARGE = 18

