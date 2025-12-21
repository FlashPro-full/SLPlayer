from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from pathlib import Path
from typing import Optional, Dict, List
from ui.properties.base_properties_component import BasePropertiesComponent
from utils.logger import get_logger

logger = get_logger(__name__)


class ScreenPropertiesComponent(BasePropertiesComponent):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program_manager = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)
        
        self.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                border: 1px solid #555555;
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QLabel {
                font-size: 13px;
                color: #FFFFFF;
            }
        """)
        
        display_props_group = QGroupBox("Display properties")
        display_props_layout = QFormLayout(display_props_group)
        display_props_layout.setContentsMargins(8, 8, 8, 8)
        display_props_layout.setSpacing(8)
        display_props_layout.setLabelAlignment(Qt.AlignLeft)
        
        self.screen_controller_type_input = QLineEdit()
        self.screen_controller_type_input.setReadOnly(True)
        self.screen_controller_type_input.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 1px solid #555555;
                background-color: #3B3B3B;
                color: #FFFFFF;
                padding: 4px 0px;
                font-size: 13px;
            }
        """)
        display_props_layout.addRow("Controller Type:", self.screen_controller_type_input)
        
        self.screen_size_input = QLineEdit()
        self.screen_size_input.setReadOnly(True)
        self.screen_size_input.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 1px solid #CCCCCC;
                background-color: transparent;
                padding: 4px 0px;
                font-size: 13px;
            }
        """)
        display_props_layout.addRow("Screen Size:", self.screen_size_input)
        
        self.screen_path_input = QLineEdit()
        self.screen_path_input.setReadOnly(True)
        self.screen_path_input.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 1px solid #CCCCCC;
                background-color: transparent;
                padding: 4px 0px;
                font-size: 13px;
            }
        """)
        display_props_layout.addRow("Path:", self.screen_path_input)
        
        layout.addWidget(display_props_group)
        layout.addStretch()
    
    def set_program_manager(self, program_manager):
        self.program_manager = program_manager
    
    def set_program_data(self, program, element, screen_name=None, programs=None):
        if screen_name and programs:
            self.current_screen_name = screen_name
            self.current_screen_programs = programs
            self.update_properties()
    
    def update_properties(self):
        from core.screen_config import get_screen_config
        
        screen_config = get_screen_config()
        
        controller_type = screen_config.get("controller_type", "") if screen_config else ""
        if self.main_window and hasattr(self.main_window, 'screen_manager') and self.main_window.screen_manager:
            current_screen = self.main_window.screen_manager.current_screen
            get_logger().info(f"{current_screen}")
            if current_screen and hasattr(current_screen, 'properties'):
                controller_type = current_screen.properties.get("controller_type", controller_type)
        
        self.screen_controller_type_input.setText(controller_type if controller_type else "N/A")
        
        width = screen_config.get("width")
        height = screen_config.get("height")
        if width and height:
            self.screen_size_input.setText(f"{width} x {height}")
        else:
            self.screen_size_input.setText("Not set")
        
        if self.program_manager:
            from utils.app_data import get_app_data_dir
            work_dir = get_app_data_dir() / "work"
            safe_name = self.current_screen_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
            soo_file = work_dir / f"{safe_name}.soo"
            if soo_file.exists():
                self.screen_path_input.setText(str(soo_file))
            else:
                self.screen_path_input.setText(str(soo_file))
        else:
            self.screen_path_input.setText("N/A")

