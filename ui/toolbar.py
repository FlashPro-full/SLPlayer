"""
Toolbar components for the main window
"""
from PyQt5.QtWidgets import QToolBar, QToolButton, QAction
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QTimer
from config.constants import ContentType
from config.i18n import tr


class BaseToolbar(QToolBar):
    """Base class for all toolbars with common styling"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setMovable(True)
        self.setFloatable(True)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea | Qt.LeftToolBarArea | Qt.RightToolBarArea)
        self.setLayoutDirection(Qt.LeftToRight)
        self.toggleViewAction().setVisible(False)
        self.setWindowTitle("")
        self.apply_style()
        self.topLevelChanged.connect(self._on_top_level_changed)
        self.orientationChanged.connect(self._on_orientation_changed)

    def apply_style(self):
        """Apply styling to toolbar"""
        self.setStyleSheet("""
            QToolBar {
                background-color: #D6D6D6;
                border: 1px solid #B0B0B0;
                spacing: 3px;
                padding: 2px;
                font-size: 14px;
            }
            QToolBar::separator:vertical {
                width: 1px;
                background-color: #B0B0B0;
                margin: 2px 0px;
            }
            QToolBar::separator:horizontal {
                height: 1px;
                background-color: #B0B0B0;
                margin: 0px 2px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                margin: 1px;
                font-size: 14px;
                font-weight: normal;
            }
            QToolButton:hover {
                background-color: #E8F4F8;
                border: 1px solid #4A90E2;
            }
            QToolButton:pressed {
                background-color: #D0E8F2;
            }
        """)
        self.update_vertical_alignment()
    
    def update_vertical_alignment(self):
        """Update button alignment based on toolbar orientation"""
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        
        QTimer.singleShot(0, self._do_update_vertical_alignment)
    
    def _do_update_vertical_alignment(self):
        """Actually update button alignment - called after widgets are created"""
        orientation = self.orientation()
        if orientation == Qt.Vertical:
            self.setLayoutDirection(Qt.LeftToRight)
            layout = self.layout()
            if layout:
                layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            
            for action in self.actions():
                widget = self.widgetForAction(action)
                if widget and isinstance(widget, QToolButton):
                    widget.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                    widget.setLayoutDirection(Qt.LeftToRight)
                    from PyQt5.QtWidgets import QSizePolicy
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    widget.setStyleSheet("""
                        QToolButton {
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            padding: 6px 10px;
                            margin: 1px;
                            text-align: left;
                            font-size: 14px;
                            font-weight: normal;
                        }
                        QToolButton:hover {
                            background-color: #E8F4F8;
                            border: 1px solid #4A90E2;
                        }
                        QToolButton:pressed {
                            background-color: #D0E8F2;
                        }
                    """)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
            layout = self.layout()
            if layout:
                layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            for action in self.actions():
                widget = self.widgetForAction(action)
                if widget and isinstance(widget, QToolButton):
                    widget.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                    widget.setLayoutDirection(Qt.LeftToRight)
                    from PyQt5.QtWidgets import QSizePolicy
                    widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                    widget.setStyleSheet("")
    
    def _on_top_level_changed(self, top_level):
        """Handle toolbar becoming floating or docked"""
        QTimer.singleShot(10, self._do_update_vertical_alignment)
    
    def _on_orientation_changed(self, orientation):
        """Handle orientation change signal"""
        QTimer.singleShot(10, self._do_update_vertical_alignment)
    
    def event(self, event):
        """Handle events including orientation changes"""
        if event.type() == QEvent.OrientationChange:
            QTimer.singleShot(10, self._do_update_vertical_alignment)
        return super().event(event)


class ProgramToolbar(BaseToolbar):
    """Program toolbar with Program button"""
    
    def __init__(self, parent=None):
        super().__init__("Program", parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize toolbar UI"""
        program_action = QAction("💽 Program", self)
        program_action.setToolTip("Program")
        self.addAction(program_action)


class ContentTypesToolbar(BaseToolbar):
    """Toolbar for visible content types"""
    
    content_type_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Content Types", parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize toolbar UI with all content types"""
        content_types = [
            ("🎞 Video", ContentType.VIDEO),
            ("🌄 Photo", ContentType.PHOTO),
            ("🔠 Text", ContentType.TEXT),
            ("🔤 SingleLineText", ContentType.SINGLE_LINE_TEXT),
            ("🎇 Animation", ContentType.ANIMATION),
            ("🕓 Clock", ContentType.CLOCK),
            ("⌛️ Timing", ContentType.TIMING),
            ("🌦 Weather", ContentType.WEATHER),
            ("📎 Sensor", ContentType.SENSOR),
        ]
        
        for emoji_text, content_type in content_types:
            action = QAction(emoji_text, self)
            action.setToolTip(content_type.value.replace("_", " ").title())
            action.triggered.connect(lambda checked, ct=content_type.value: self.content_type_selected.emit(ct))
            self.addAction(action)


class PlaybackToolbar(BaseToolbar):
    """Playback control toolbar"""
    
    action_triggered = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Playback", parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize toolbar UI"""
        play_action = QAction("▶️ Play", self)
        play_action.setToolTip("Play")
        play_action.triggered.connect(lambda: self.action_triggered.emit("play"))
        self.addAction(play_action)
        
        pause_action = QAction("⏸ Pause", self)
        pause_action.setToolTip("Pause")
        pause_action.triggered.connect(lambda: self.action_triggered.emit("pause"))
        self.addAction(pause_action)
        
        stop_action = QAction("⏹ Stop", self)
        stop_action.setToolTip("Stop")
        stop_action.triggered.connect(lambda: self.action_triggered.emit("stop"))
        self.addAction(stop_action)


class ControlToolbar(BaseToolbar):
    """Controller toolbar with Download, Insert, Clear buttons"""
    
    action_triggered = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Control", parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize toolbar UI"""
        download_action = QAction("⬇️ Download", self)
        download_action.setToolTip(tr("toolbar.download"))
        download_action.triggered.connect(lambda: self.action_triggered.emit("download"))
        self.addAction(download_action)
        
        insert_action = QAction("📲 Insert", self)
        insert_action.setToolTip("Insert")
        insert_action.triggered.connect(lambda: self.action_triggered.emit("insert"))
        self.addAction(insert_action)
        
        clear_action = QAction("🧹 Clear", self)
        clear_action.setToolTip("Clear")
        clear_action.triggered.connect(lambda: self.action_triggered.emit("clear"))
        self.addAction(clear_action)


class ToolbarManager(QToolBar):
    """Manager for all toolbars - provides backward compatibility"""
    
    def __init__(self, parent=None):
        super().__init__("Toolbars", parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.toolbars = []
    
    def get_toolbars(self):
        """Get all managed toolbars"""
        return self.toolbars

