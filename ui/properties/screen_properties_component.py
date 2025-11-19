from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from pathlib import Path
from typing import Optional, Dict, List
from ui.properties.base_properties_component import BasePropertiesComponent


class ScreenPropertiesComponent(BasePropertiesComponent):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program_manager = None
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
            }
            QLabel {
                font-size: 13px;
            }
        """)
        
        display_props_group = QGroupBox("Display properties")
        display_props_group.setMinimumWidth(300)
        display_props_layout = QFormLayout(display_props_group)
        display_props_layout.setContentsMargins(8, 8, 8, 8)
        display_props_layout.setSpacing(8)
        display_props_layout.setLabelAlignment(Qt.AlignLeft)
        
        self.screen_controller_type_input = QLineEdit()
        self.screen_controller_type_input.setReadOnly(True)
        self.screen_controller_type_input.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 1px solid #CCCCCC;
                background-color: transparent;
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
        if not self.current_screen_programs or len(self.current_screen_programs) == 0:
            return
        
        first_program = self.current_screen_programs[0]
        if not first_program:
            return
        
        screen_props = first_program.properties.get("screen", {})
        
        controller_type = screen_props.get("controller_type", "")
        if not controller_type:
            brand = screen_props.get("brand", "")
            model = screen_props.get("model", "")
            if brand and model:
                controller_type = f"{brand} {model}"
            elif model:
                controller_type = model
        self.screen_controller_type_input.setText(controller_type if controller_type else "N/A")
        
        screen_props = first_program.properties.get("screen", {})
        width = screen_props.get("width")
        height = screen_props.get("height")
        if width and height:
            self.screen_size_input.setText(f"{width} x {height}")
        else:
            self.screen_size_input.setText("Not set")
        
        working_file_path = first_program.properties.get("working_file_path", "")
        if working_file_path:
            self.screen_path_input.setText(working_file_path)
        else:
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

