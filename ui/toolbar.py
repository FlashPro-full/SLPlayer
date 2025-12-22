from PyQt5.QtWidgets import QToolBar, QToolButton, QAction, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QTimer  # type: ignore
from config.constants import ContentType
from config.i18n import tr


class BaseToolbar(QToolBar):

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setMovable(True)
        self.setFloatable(True)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)  # type: ignore
        self.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea | Qt.LeftToolBarArea | Qt.RightToolBarArea)  # type: ignore
        self.setLayoutDirection(Qt.LeftToRight)  # type: ignore
        toggle_action = self.toggleViewAction()
        if toggle_action:
            toggle_action.setVisible(False)
        self.setWindowTitle("")
        self.apply_style()
        self.topLevelChanged.connect(self._on_top_level_changed)
        self.orientationChanged.connect(self._on_orientation_changed)

    def apply_style(self):
        self.setStyleSheet("""
            QToolBar {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                border-right: 2px solid #555555;
                spacing: 0px;
                padding: 0px;
                font-size: 14px;
                color: #FFFFFF;
            }
            QToolBar::separator:vertical {
                width: 1px;
                background-color: #555555;
                margin: 2px 0px;
            }
            QToolBar::separator:horizontal {
                height: 1px;
                background-color: #555555;
                margin: 0px 2px;
            }
            QToolBar::extension {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 0px;
                margin: 1px;
                color: #FFFFFF;
            }
            QToolBar::extension:hover {
                background-color: #3B3B3B;
                border: 1px solid #4A90E2;
                margin: 2px;
            }
            QToolBar::extension:pressed {
                background-color: #4B4B4B;
            }
        """)
        self.update_vertical_alignment()
    
    def update_vertical_alignment(self):
        QTimer.singleShot(0, self._do_update_vertical_alignment)
    
    def _do_update_vertical_alignment(self):
        orientation = self.orientation()
        if orientation == Qt.Vertical:
            self.setLayoutDirection(Qt.LeftToRight)
            layout = self.layout()
            if layout:
                layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                layout.setContentsMargins(2, 2, 2, 2)
            
            for action in self.actions():
                widget = self.widgetForAction(action)
                if widget and isinstance(widget, QToolButton):
                    widget.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                    widget.setLayoutDirection(Qt.LeftToRight)
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    widget.setMinimumWidth(0)
                    widget.setStyleSheet("""
                        QToolButton {
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            padding: 6px 0px;
                            margin: 1px;
                            text-align: left;
                            font-size: 14px;
                            font-weight: normal;
                            width: 120px;
                            color: #FFFFFF;
                        }
                        QToolButton:hover {
                            background-color: #3B3B3B;
                            border: 1px solid #4A90E2;
                        }
                        QToolButton:pressed {
                            background-color: #4B4B4B;
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
                    widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                    widget.setStyleSheet("""
                        QToolButton {
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            padding: 4px 8px;
                            margin: 1px;
                            font-size: 14px;
                            font-weight: normal;
                            color: #FFFFFF;
                        }
                        QToolButton:hover {
                            background-color: #3B3B3B;
                            border: 1px solid #4A90E2;
                        }
                        QToolButton:pressed {
                            background-color: #4B4B4B;
                        }
                    """)
    
    def _on_top_level_changed(self, top_level):
        QTimer.singleShot(10, self._do_update_vertical_alignment)
    
    def _on_orientation_changed(self, orientation):
        QTimer.singleShot(10, self._do_update_vertical_alignment)
    
    def event(self, event):
        if event.type() == QEvent.OrientationChange:
            QTimer.singleShot(10, self._do_update_vertical_alignment)
        return super().event(event)


class ProgramToolbar(BaseToolbar):
    
    new_program_requested = pyqtSignal()
    export_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Program", parent)
        self.init_ui()
    
    def init_ui(self):
        from config.i18n import tr
        program_action = QAction("💽 Program", self)
        program_action.setToolTip(tr("toolbar.program_tooltip"))
        program_action.triggered.connect(self.new_program_requested.emit)
        self.addAction(program_action)
        
        export_action = QAction("💾 Export", self)
        export_action.setToolTip(tr("toolbar.export_tooltip"))
        export_action.triggered.connect(self.export_requested.emit)
        self.addAction(export_action)


class ContentTypesToolbar(BaseToolbar):
    
    content_type_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Content Types", parent)
        self.init_ui()
    
    def init_ui(self):
        content_types = [
            ("🎞 Video", ContentType.VIDEO),
            ("🌄 Photo", ContentType.PHOTO),
            ("🔠 Text", ContentType.TEXT),
            ("🔤 SingleLineText", ContentType.SINGLELINE_TEXT),
            ("🎇 Animation", ContentType.ANIMATION),
            ("🕓 Clock", ContentType.CLOCK),
            ("⌛️ Timing", ContentType.TIMING),
            ("🌦 Weather", ContentType.WEATHER),
            ("📎 Sensor", ContentType.SENSOR),
            ("🔌 HDMI", ContentType.HDMI),
            ("🌐 HTML", ContentType.HTML)
        ]
        
        for emoji_text, content_type in content_types:
            action = QAction(emoji_text, self)
            action.setToolTip(content_type.value.replace("_", " ").title())
            action.triggered.connect(lambda checked, ct=content_type.value: self.content_type_selected.emit(ct))
            self.addAction(action)


class PlaybackToolbar(BaseToolbar):
    
    action_triggered = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Playback", parent)
        self.init_ui()
    
    def init_ui(self):
        from config.i18n import tr
        play_action = QAction("▶️ Play", self)
        play_action.setToolTip(tr("toolbar.play_tooltip"))
        play_action.triggered.connect(lambda: self.action_triggered.emit("play"))
        self.addAction(play_action)
        
        pause_action = QAction("⏸ Pause", self)
        pause_action.setToolTip(tr("toolbar.pause_tooltip"))
        pause_action.triggered.connect(lambda: self.action_triggered.emit("pause"))
        self.addAction(pause_action)
        
        stop_action = QAction("⏹ Stop", self)
        stop_action.setToolTip(tr("toolbar.stop_tooltip"))
        stop_action.triggered.connect(lambda: self.action_triggered.emit("stop"))
        self.addAction(stop_action)


class ControlToolbar(BaseToolbar):
    
    action_triggered = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Control", parent)
        self.init_ui()
        self.update_vertical_alignment()
    
    def init_ui(self):
        from config.i18n import tr
        send_action = QAction("⬆️ Send", self)
        send_action.setToolTip(tr("toolbar.send"))
        send_action.triggered.connect(lambda: self.action_triggered.emit("send"))
        self.addAction(send_action)
        
        self.addSeparator()
        
        insert_action = QAction("📲 Insert", self)
        insert_action.setToolTip(tr("toolbar.insert"))
        insert_action.triggered.connect(lambda: self.action_triggered.emit("insert"))
        self.addAction(insert_action)
        
        self.addSeparator()
        
        clear_action = QAction("🧹 Clear", self)
        clear_action.setToolTip(tr("toolbar.clear_tooltip"))
        clear_action.triggered.connect(lambda: self.action_triggered.emit("clear"))
        self.addAction(clear_action)


class DeviceToolbar(BaseToolbar):
    
    time_requested = pyqtSignal()
    brightness_requested = pyqtSignal()
    power_requested = pyqtSignal()
    schedule_requested = pyqtSignal()
    network_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Device", parent)
        self.init_ui()
    
    def init_ui(self):
        time_action = QAction("⏰ Time", self)
        time_action.setToolTip("Set time synchronization")
        time_action.triggered.connect(self.time_requested.emit)
        self.addAction(time_action)
        
        brightness_action = QAction("💡 Brightness", self)
        brightness_action.setToolTip("Set brightness settings")
        brightness_action.triggered.connect(self.brightness_requested.emit)
        self.addAction(brightness_action)
        
        power_action = QAction("⚡ Power", self)
        power_action.setToolTip("Set power schedule")
        power_action.triggered.connect(self.power_requested.emit)
        self.addAction(power_action)
        
        schedule_action = QAction("📅 Schedule", self)
        schedule_action.setToolTip("Schedule program playback")
        schedule_action.triggered.connect(self.schedule_requested.emit)
        self.addAction(schedule_action)
        
        network_action = QAction("🌐 Network", self)
        network_action.setToolTip("Configure network settings")
        network_action.triggered.connect(self.network_requested.emit)
        self.addAction(network_action)


class ToolbarManager(QToolBar):
    
    def __init__(self, parent=None):
        super().__init__("Toolbars", parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.toolbars = []
    
    def get_toolbars(self):
        return self.toolbars

