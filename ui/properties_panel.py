"""
Properties panel that shows different properties based on selection
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import pyqtSignal, Qt
from typing import Optional, Dict, List
from core.program_manager import ProgramManager, Program
from ui.properties import (
    ProgramPropertiesComponent,
    VideoPropertiesComponent,
    ImagePropertiesComponent,
    TextPropertiesComponent,
    ScreenPropertiesComponent
)


class PropertiesPanel(QWidget):
    """Properties panel showing properties based on selection"""
    
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_program: Optional[Program] = None
        self.current_element: Optional[Dict] = None
        self.current_screen_name: Optional[str] = None
        self.current_screen_programs: List[Program] = []
        self.main_window = parent
        self.program_manager: Optional[ProgramManager] = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-size: 12px;
            }
            QScrollArea {
                border: none;
                background-color: #FFFFFF;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                font-size: 12px;
            }
            QLabel {
                font-size: 12px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTimeEdit, QDateEdit {
                font-size: 12px;
                padding: 4px;
                min-height: 20px;
            }
            QPushButton {
                font-size: 12px;
                padding: 4px 8px;
                min-height: 20px;
            }
            QCheckBox, QRadioButton {
                font-size: 12px;
            }
        """)
        
        # Create scroll area for properties content
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Create container widget for all property components
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content_layout.setSpacing(4)
        
        # Create property components
        self.program_properties_widget = ProgramPropertiesComponent(self.content_widget)
        self.video_properties_widget = VideoPropertiesComponent(self.content_widget)
        self.image_properties_widget = ImagePropertiesComponent(self.content_widget)
        self.text_properties_widget = TextPropertiesComponent(self.content_widget)
        self.screen_properties_widget = ScreenPropertiesComponent(self.content_widget)
        self.empty_widget = QWidget(self.content_widget)
        
        # Connect component signals to panel signal
        self.program_properties_widget.property_changed.connect(self.property_changed.emit)
        self.video_properties_widget.property_changed.connect(self.property_changed.emit)
        self.image_properties_widget.property_changed.connect(self.property_changed.emit)
        self.text_properties_widget.property_changed.connect(self.property_changed.emit)
        self.screen_properties_widget.property_changed.connect(self.property_changed.emit)
        
        # Add all components to content layout
        self.content_layout.addWidget(self.program_properties_widget)
        self.content_layout.addWidget(self.video_properties_widget)
        self.content_layout.addWidget(self.image_properties_widget)
        self.content_layout.addWidget(self.text_properties_widget)
        self.content_layout.addWidget(self.screen_properties_widget)
        self.content_layout.addWidget(self.empty_widget)
        self.content_layout.addStretch()  # Add stretch at the end
        
        # Set content widget to scroll area
        self.scroll_area.setWidget(self.content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(self.scroll_area)
        
        self.show_empty()
    
    def show_program_properties(self):
        """Show program properties"""
        self.program_properties_widget.setVisible(True)
        self.video_properties_widget.setVisible(False)
        self.image_properties_widget.setVisible(False)
        self.text_properties_widget.setVisible(False)
        self.screen_properties_widget.setVisible(False)
        self.empty_widget.setVisible(False)
    
    def show_video_properties(self):
        """Show video properties"""
        self.program_properties_widget.setVisible(False)
        self.video_properties_widget.setVisible(True)
        self.image_properties_widget.setVisible(False)
        self.text_properties_widget.setVisible(False)
        self.screen_properties_widget.setVisible(False)
        self.empty_widget.setVisible(False)
    
    def show_image_properties(self):
        """Show image/photo properties"""
        self.program_properties_widget.setVisible(False)
        self.video_properties_widget.setVisible(False)
        self.image_properties_widget.setVisible(True)
        self.text_properties_widget.setVisible(False)
        self.screen_properties_widget.setVisible(False)
        self.empty_widget.setVisible(False)
    
    def show_text_properties(self):
        """Show text properties"""
        self.program_properties_widget.setVisible(False)
        self.video_properties_widget.setVisible(False)
        self.image_properties_widget.setVisible(False)
        self.text_properties_widget.setVisible(True)
        self.screen_properties_widget.setVisible(False)
        self.empty_widget.setVisible(False)
    
    def show_screen_properties(self):
        """Show screen properties"""
        self.program_properties_widget.setVisible(False)
        self.video_properties_widget.setVisible(False)
        self.image_properties_widget.setVisible(False)
        self.text_properties_widget.setVisible(False)
        self.screen_properties_widget.setVisible(True)
        self.empty_widget.setVisible(False)
    
    def show_empty(self):
        """Show empty state"""
        self.program_properties_widget.setVisible(False)
        self.video_properties_widget.setVisible(False)
        self.image_properties_widget.setVisible(False)
        self.text_properties_widget.setVisible(False)
        self.screen_properties_widget.setVisible(False)
        self.empty_widget.setVisible(True)
    
    def set_program(self, program: Optional[Program]):
        """Set the current program"""
        self.current_program = program
        self.current_element = None
        if program:
            self.show_program_properties()
            self.program_properties_widget.set_program_data(program)
        else:
            self.show_empty()
    
    def set_element(self, element: Optional[Dict], program: Optional[Program]):
        """Set the current element"""
        self.current_element = element
        self.current_program = program
        if element:
            element_type = element.get("type", "").lower()
            if element_type == "video":
                self.show_video_properties()
                self.video_properties_widget.set_program_data(program, element)
            elif element_type in ["image", "picture", "photo"]:
                self.show_image_properties()
                self.image_properties_widget.set_program_data(program, element)
            elif element_type == "text":
                self.show_text_properties()
                self.text_properties_widget.set_program_data(program, element)
            elif program:
                self.show_program_properties()
                self.program_properties_widget.set_program_data(program)
            else:
                self.show_empty()
        elif program:
            self.show_program_properties()
            self.program_properties_widget.set_program_data(program)
        else:
            self.show_empty()
    
    def set_screen(self, screen_name: str, programs: List[Program], program_manager: Optional[ProgramManager] = None):
        """Set the current screen"""
        try:
            self.current_screen_name = screen_name
            self.current_screen_programs = programs
            self.current_program = None
            self.current_element = None
            self.program_manager = program_manager
            if screen_name and programs:
                self.show_screen_properties()
                self.screen_properties_widget.set_program_manager(program_manager)
                self.screen_properties_widget.set_program_data(None, None, screen_name, programs)
            else:
                self.show_empty()
        except Exception as e:
            # Log error but don't crash - just show empty state
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error in set_screen: {e}", exc_info=True)
            self.show_empty()
