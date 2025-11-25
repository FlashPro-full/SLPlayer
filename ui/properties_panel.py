from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import pyqtSignal, Qt
from typing import Optional, Dict, List
from core.program_manager import ProgramManager, Program
from core.screen_manager import ScreenManager
from ui.properties import (
    ProgramPropertiesComponent,
    VideoPropertiesComponent,
    ImagePropertiesComponent,
    TextPropertiesComponent,
    ScreenPropertiesComponent,
    SingleLineTextPropertiesComponent,
    AnimationPropertiesComponent,
    ClockPropertiesComponent,
    TimingPropertiesComponent,
    WeatherPropertiesComponent,
    SensorPropertiesComponent,
    HdmiPropertiesComponent,
    HtmlPropertiesComponent
)


class PropertiesPanel(QWidget):
    
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_program: Optional[Program] = None
        self.current_element: Optional[Dict] = None
        self.current_screen_name: Optional[str] = None
        self.current_screen_programs: List[Program] = []
        self.main_window = parent
        self.program_manager: Optional[ProgramManager] = None
        self.screen_manager: Optional[ScreenManager] = None
        self.init_ui()
    
    def init_ui(self):
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
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content_layout.setSpacing(4)
        
        self.program_properties_widget = ProgramPropertiesComponent(self.content_widget)
        self.video_properties_widget = VideoPropertiesComponent(self.content_widget)
        self.image_properties_widget = ImagePropertiesComponent(self.content_widget)
        self.text_properties_widget = TextPropertiesComponent(self.content_widget)
        self.screen_properties_widget = ScreenPropertiesComponent(self.content_widget)
        self.singleline_text_properties_widget = SingleLineTextPropertiesComponent(self.content_widget)
        self.animation_properties_widget = AnimationPropertiesComponent(self.content_widget)
        self.clock_properties_widget = ClockPropertiesComponent(self.content_widget)
        self.timing_properties_widget = TimingPropertiesComponent(self.content_widget)
        self.weather_properties_widget = WeatherPropertiesComponent(self.content_widget)
        self.sensor_properties_widget = SensorPropertiesComponent(self.content_widget)
        self.hdmi_properties_widget = HdmiPropertiesComponent(self.content_widget)
        self.html_properties_widget = HtmlPropertiesComponent(self.content_widget)
        self.empty_widget = QWidget(self.content_widget)
        
        self.program_properties_widget.property_changed.connect(self.property_changed.emit)
        self.video_properties_widget.property_changed.connect(self.property_changed.emit)
        self.image_properties_widget.property_changed.connect(self.property_changed.emit)
        self.text_properties_widget.property_changed.connect(self.property_changed.emit)
        self.screen_properties_widget.property_changed.connect(self.property_changed.emit)
        self.singleline_text_properties_widget.property_changed.connect(self.property_changed.emit)
        self.animation_properties_widget.property_changed.connect(self.property_changed.emit)
        self.clock_properties_widget.property_changed.connect(self.property_changed.emit)
        self.timing_properties_widget.property_changed.connect(self.property_changed.emit)
        self.weather_properties_widget.property_changed.connect(self.property_changed.emit)
        self.sensor_properties_widget.property_changed.connect(self.property_changed.emit)
        self.hdmi_properties_widget.property_changed.connect(self.property_changed.emit)
        self.html_properties_widget.property_changed.connect(self.property_changed.emit)
        
        self.content_layout.addWidget(self.program_properties_widget)
        self.content_layout.addWidget(self.video_properties_widget)
        self.content_layout.addWidget(self.image_properties_widget)
        self.content_layout.addWidget(self.text_properties_widget)
        self.content_layout.addWidget(self.screen_properties_widget)
        self.content_layout.addWidget(self.singleline_text_properties_widget)
        self.content_layout.addWidget(self.animation_properties_widget)
        self.content_layout.addWidget(self.clock_properties_widget)
        self.content_layout.addWidget(self.timing_properties_widget)
        self.content_layout.addWidget(self.weather_properties_widget)
        self.content_layout.addWidget(self.sensor_properties_widget)
        self.content_layout.addWidget(self.hdmi_properties_widget)
        self.content_layout.addWidget(self.html_properties_widget)
        self.content_layout.addWidget(self.empty_widget)
        self.content_layout.addStretch()
        
        self.scroll_area.setWidget(self.content_widget)
        
        main_layout.addWidget(self.scroll_area)
        
        self.show_empty()
    
    def _hide_all(self):
        self.program_properties_widget.setVisible(False)
        self.video_properties_widget.setVisible(False)
        self.image_properties_widget.setVisible(False)
        self.text_properties_widget.setVisible(False)
        self.screen_properties_widget.setVisible(False)
        self.singleline_text_properties_widget.setVisible(False)
        self.animation_properties_widget.setVisible(False)
        self.clock_properties_widget.setVisible(False)
        self.timing_properties_widget.setVisible(False)
        self.weather_properties_widget.setVisible(False)
        self.sensor_properties_widget.setVisible(False)
        self.hdmi_properties_widget.setVisible(False)
        self.html_properties_widget.setVisible(False)
        self.empty_widget.setVisible(False)
    
    def _show_widget(self, widget):
        self._hide_all()
        widget.setVisible(True)
    
    def show_program_properties(self):
        self._show_widget(self.program_properties_widget)
    
    def show_video_properties(self):
        self._show_widget(self.video_properties_widget)
    
    def show_image_properties(self):
        self._show_widget(self.image_properties_widget)
    
    def show_text_properties(self):
        self._show_widget(self.text_properties_widget)
    
    def show_screen_properties(self):
        self._show_widget(self.screen_properties_widget)
    
    def show_singleline_text_properties(self):
        self._show_widget(self.singleline_text_properties_widget)
    
    def show_animation_properties(self):
        self._show_widget(self.animation_properties_widget)
    
    def show_clock_properties(self):
        self._show_widget(self.clock_properties_widget)
    
    def show_timing_properties(self):
        self._show_widget(self.timing_properties_widget)
    
    def show_weather_properties(self):
        self._show_widget(self.weather_properties_widget)
    
    def show_sensor_properties(self):
        self._show_widget(self.sensor_properties_widget)
    
    def show_hdmi_properties(self):
        self._show_widget(self.hdmi_properties_widget)
    
    def show_html_properties(self):
        self._show_widget(self.html_properties_widget)
    
    def show_empty(self):
        self._show_widget(self.empty_widget)
    
    def set_program(self, program: Optional[Program]):
        self.current_program = program
        self.current_element = None
        if program:
            self.show_program_properties()
            self.program_properties_widget.set_program_data(program)
        else:
            self.show_empty()
    
    def set_element(self, element: Optional[Dict], program: Optional[Program]):
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
            elif element_type == "singleline_text":
                self.show_singleline_text_properties()
                self.singleline_text_properties_widget.set_program_data(program, element)
            elif element_type == "animation":
                self.show_animation_properties()
                self.animation_properties_widget.set_program_data(program, element)
            elif element_type == "clock":
                self.show_clock_properties()
                self.clock_properties_widget.set_program_data(program, element)
            elif element_type == "timing":
                self.show_timing_properties()
                self.timing_properties_widget.set_program_data(program, element)
            elif element_type == "weather":
                self.show_weather_properties()
                self.weather_properties_widget.set_program_data(program, element)
            elif element_type == "sensor":
                self.show_sensor_properties()
                self.sensor_properties_widget.set_program_data(program, element)
            elif element_type == "hdmi":
                self.show_hdmi_properties()
                self.hdmi_properties_widget.set_program_data(program, element)
            elif element_type == "html":
                self.show_html_properties()
                self.html_properties_widget.set_program_data(program, element)
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
    
    def set_program_manager(self, program_manager: ProgramManager):
        self.program_manager = program_manager
    
    def set_screen_manager(self, screen_manager: ScreenManager):
        self.screen_manager = screen_manager
    
    def set_screen(self, screen_name: str, programs: List[Program], program_manager: Optional[ProgramManager] = None, 
                   screen_manager: Optional[ScreenManager] = None):
        try:
            self.current_screen_name = screen_name
            self.current_screen_programs = programs
            self.current_program = None
            self.current_element = None
            if program_manager:
                self.program_manager = program_manager
            if screen_manager:
                self.screen_manager = screen_manager
            if screen_name and programs:
                self.show_screen_properties()
                self.screen_properties_widget.set_program_manager(self.program_manager)
                self.screen_properties_widget.set_program_data(None, None, screen_name, programs)
            else:
                self.show_empty()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error in set_screen: {e}", exc_info=True)
            self.show_empty()

    def save_all_current_properties(self):
        if self.current_element and self.current_program:
            element_type = self.current_element.get("type", "").lower()
            if element_type == "animation":
                if hasattr(self.animation_properties_widget, 'save_all_animation_text_properties'):
                    self.animation_properties_widget.save_all_animation_text_properties()