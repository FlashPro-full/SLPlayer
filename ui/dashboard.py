"""
Dashboard view integrating all management panels
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLabel, QPushButton)
from PyQt6.QtCore import Qt
from ui.time_power_lux_panel import TimePowerLuxPanel
from ui.network_config_panel import NetworkConfigPanel
from ui.diagnostics_panel import DiagnosticsPanel
from controllers.base_controller import BaseController


class Dashboard(QWidget):
    """Main dashboard integrating all management panels"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller: BaseController = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create tab widget for different management sections
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #CCC;
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                border-bottom: 2px solid #2196F3;
            }
        """)
        
        # Time/Power/Lux Tab
        self.time_power_lux_panel = TimePowerLuxPanel()
        tabs.addTab(self.time_power_lux_panel, "Time / Power / Lux")
        
        # Network Config Tab
        self.network_config_panel = NetworkConfigPanel()
        tabs.addTab(self.network_config_panel, "Network & Config")
        
        # Diagnostics Tab
        self.diagnostics_panel = DiagnosticsPanel()
        tabs.addTab(self.diagnostics_panel, "Diagnostics / Log")
        
        layout.addWidget(tabs)
    
    def set_controller(self, controller: BaseController):
        """Set current controller for all panels"""
        self.controller = controller
        self.time_power_lux_panel.set_controller(controller)
        self.network_config_panel.set_controller(controller)
        self.diagnostics_panel.set_controller(controller)

