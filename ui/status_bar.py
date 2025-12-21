from PyQt5.QtWidgets import QStatusBar, QLabel, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

from services.controller_service import get_controller_service
from config.i18n import tr
from ui.widgets.loading_spinner import LoadingSpinner

class StatusBarWidget(QStatusBar):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QStatusBar {
                background-color: #2B2B2B;
                color: #FFFFFF;
                border-top: 2px solid #555555;
            }
        """)
        self.controller_service = get_controller_service()
        self.init_ui()
        self._update_status()
    
    def init_ui(self):
        self.connection_label = QLabel(tr("status.no_device"))
        self.connection_label.setStyleSheet("color: red;")
        self.addWidget(self.connection_label)
        
        self.scanning_widget = QWidget()
        scanning_layout = QHBoxLayout(self.scanning_widget)
        scanning_layout.setContentsMargins(0, 0, 0, 0)
        scanning_layout.setSpacing(6)
        
        self.scanning_spinner = LoadingSpinner(self.scanning_widget, size=16, color="#2196F3")
        self.scanning_label = QLabel("Scanning for controllers...")
        self.scanning_label.setStyleSheet("color: #CCCCCC; font-size: 11px;")
        
        scanning_layout.addWidget(self.scanning_spinner)
        scanning_layout.addWidget(self.scanning_label)
        
        self.scanning_widget.setVisible(False)
        self.addPermanentWidget(self.scanning_widget)
        
        self.program_label = QLabel("")
        self.addPermanentWidget(self.program_label)
        
        self.progress_label = QLabel("")
        self.addPermanentWidget(self.progress_label)
    
    def set_connection_status(self, status: bool, device_name: str = ""):
        if status:
            base_text = tr("status.connected")
            text = f"{base_text} ({device_name})" if device_name else base_text
            self.connection_label.setText(text)
            self.connection_label.setStyleSheet("color: green;")
        else:
            self.connection_label.setText(tr("status.no_device"))
            self.connection_label.setStyleSheet("color: red;")
    
    def set_program_name(self, name: str):
        program_label = tr("status.program")
        self.program_label.setText(f"{program_label}: {name}")
    
    def set_progress(self, message: str):
        self.progress_label.setText(message)
    
    def clear_progress(self):
        self.progress_label.setText("")
    
    def show_scanning(self, message: str = "Scanning for controllers..."):
        self.scanning_label.setText(message)
        self.scanning_spinner.start()
        self.scanning_widget.setVisible(True)
    
    def hide_scanning(self):
        self.scanning_spinner.stop()
        self.scanning_widget.setVisible(False)
    
    def _update_status(self):
        current_controller = self.controller_service.get_current_controller()
        if current_controller:
            is_online = self.controller_service.is_online()
            controller_id = current_controller.get("controller_id", "")
            self.set_connection_status(is_online, controller_id)
        else:
            self.set_connection_status(False, "")
