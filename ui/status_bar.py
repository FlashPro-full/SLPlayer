"""
Status bar component
"""
from PyQt5.QtWidgets import QStatusBar, QLabel
from PyQt5.QtCore import Qt

from controllers.base_controller import ConnectionStatus


class StatusBarWidget(QStatusBar):
    """Application status bar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.set_connection_status(ConnectionStatus.DISCONNECTED)
    
    def init_ui(self):
        """Initialize the status bar"""
        # Connection status label
        self.connection_label = QLabel("No Device Detected")
        self.connection_label.setStyleSheet("color: red;")
        self.addWidget(self.connection_label)
        
        # Program name label
        self.program_label = QLabel("")
        self.addPermanentWidget(self.program_label)
        
        # Progress label (for upload/download)
        self.progress_label = QLabel("")
        self.addPermanentWidget(self.progress_label)
    
    def set_connection_status(self, status: ConnectionStatus, device_name: str = ""):
        """Set connection status"""
        # Get the enum value for comparison
        try:
            status_value = status.value
        except AttributeError:
            # Fallback if status is not an enum member
            status_value = str(status).lower()
        
        if status_value == "disconnected":
            self.connection_label.setText("No Device Detected")
            self.connection_label.setStyleSheet("color: red;")
        elif status_value == "connecting":
            self.connection_label.setText("Connecting...")
            self.connection_label.setStyleSheet("color: orange;")
        elif status_value == "connected":
            text = f"Device Connected ({device_name})" if device_name else "Device Connected"
            self.connection_label.setText(text)
            self.connection_label.setStyleSheet("color: green;")
        elif status_value == "error":
            self.connection_label.setText("Connection Error")
            self.connection_label.setStyleSheet("color: red;")
    
    def set_program_name(self, name: str):
        """Set current program name"""
        self.program_label.setText(f"Program: {name}")
    
    def set_progress(self, message: str):
        """Set progress message"""
        self.progress_label.setText(message)
    
    def clear_progress(self):
        """Clear progress message"""
        self.progress_label.setText("")
