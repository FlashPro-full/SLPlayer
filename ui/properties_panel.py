"""
Bottom panel - Program properties and playback settings
"""
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QCheckBox, QComboBox, QSpinBox, QTimeEdit, QGroupBox,
                             QRadioButton, QPushButton, QLineEdit, QMenu, QFileDialog,
                             QCalendarWidget, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTime
from PyQt6.QtGui import QFont

from core.program_manager import Program


class PropertiesPanel(QWidget):
    """Program properties and playback settings panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program: Program = None
        self.selected_element: Dict = None
        # Set light gray background to match image
        # Apply pixel-perfect styling
        from ui.styles import Styles
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Styles.COLORS["background"]};
            }}
            {Styles.GROUPBOX}
            {Styles.INPUT}
        """)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Left section: Program Properties
        properties_group = QGroupBox("Program properties")
        properties_group.setStyleSheet("""
            QGroupBox {
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 0px;
                padding: 0px 0px 0px 0px;
            }
        """)
        properties_layout = QVBoxLayout(properties_group)
        properties_layout.setContentsMargins(5, 15, 5, 5)
        properties_layout.setSpacing(5)
        
        # Frame
        self.frame_checkbox = QCheckBox("Frame")
        self.frame_checkbox.stateChanged.connect(self.on_frame_changed)
        properties_layout.addWidget(self.frame_checkbox)
        
        self.frame_input = QLineEdit("--- --- --- 1")
        self.frame_input.setReadOnly(True)
        self.frame_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BDBDBD;
                border-radius: 2px;
                padding: 2px 4px;
                background-color: #FFFFFF;
            }
        """)
        # Add dropdown arrow indicator
        frame_layout = QHBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(self.frame_input)
        self.frame_dropdown_btn = QPushButton("▼")
        self.frame_dropdown_btn.setFixedWidth(20)
        self.frame_dropdown_btn.setFlat(True)
        self.frame_dropdown_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0px;
                font-size: 10px;
            }
        """)
        self.frame_menu = QMenu(self)
        # Load available frames from resources
        from core.resource_manager import resource_manager
        available_frames = resource_manager.list_available_frames()
        if available_frames:
            for frame_id in available_frames[:36]:  # Limit to 36 frames
                action = self.frame_menu.addAction(f"Frame {frame_id}")
                action.setData(frame_id)
        else:
            # Fallback to default frames
            self.frame_menu.addAction("--- --- --- 1")
            self.frame_menu.addAction("--- --- --- 2")
            self.frame_menu.addAction("--- --- --- 3")
        self.frame_menu.triggered.connect(self.on_frame_menu_selected)
        self.frame_dropdown_btn.setMenu(self.frame_menu)
        frame_layout.addWidget(self.frame_dropdown_btn)
        properties_layout.addLayout(frame_layout)
        
        # Background Music
        self.bgm_checkbox = QCheckBox("Background Music")
        self.bgm_checkbox.stateChanged.connect(self.on_bgm_changed)
        properties_layout.addWidget(self.bgm_checkbox)
        
        bgm_input_layout = QHBoxLayout()
        bgm_input_layout.setContentsMargins(0, 0, 0, 0)
        self.bgm_input = QLineEdit()
        self.bgm_input.setReadOnly(True)
        self.bgm_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BDBDBD;
                border-radius: 2px;
                padding: 2px 4px;
                background-color: #FFFFFF;
            }
        """)
        bgm_input_layout.addWidget(self.bgm_input)
        
        # Volume indicator (orange circle with 0)
        self.volume_indicator = QLabel("0")
        self.volume_indicator.setFixedSize(20, 20)
        self.volume_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volume_indicator.setStyleSheet("""
            QLabel {
                background-color: #FF9800;
                color: #FFFFFF;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        bgm_input_layout.addWidget(self.volume_indicator)
        
        self.bgm_dropdown_btn = QPushButton("▼")
        self.bgm_dropdown_btn.setFixedWidth(20)
        self.bgm_dropdown_btn.setFlat(True)
        self.bgm_dropdown_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0px;
                font-size: 10px;
            }
        """)
        self.bgm_menu = QMenu(self)
        self.bgm_menu.addAction("Select File...")
        self.bgm_menu.triggered.connect(self.on_bgm_menu_selected)
        self.bgm_dropdown_btn.setMenu(self.bgm_menu)
        bgm_input_layout.addWidget(self.bgm_dropdown_btn)
        properties_layout.addLayout(bgm_input_layout)
        
        properties_layout.addStretch()
        layout.addWidget(properties_group)
        
        # Middle section: Play Mode
        play_mode_group = QGroupBox("Play mode")
        play_mode_group.setStyleSheet("""
            QGroupBox {
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 0px;
                padding: 0px 0px 0px 0px;
            }
        """)
        play_mode_layout = QVBoxLayout(play_mode_group)
        play_mode_layout.setContentsMargins(5, 15, 5, 5)
        play_mode_layout.setSpacing(5)
        
        # Play times
        self.play_times_radio = QRadioButton("Play times")
        self.play_times_radio.setChecked(True)
        self.play_times_radio.toggled.connect(self.on_play_mode_changed)
        play_mode_layout.addWidget(self.play_times_radio)
        
        play_times_control_layout = QHBoxLayout()
        play_times_control_layout.setContentsMargins(0, 0, 0, 0)
        play_times_minus_btn = QPushButton("-")
        play_times_minus_btn.setFixedWidth(25)
        play_times_minus_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #BDBDBD;
                border-radius: 2px;
                background-color: #FFFFFF;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
        """)
        play_times_minus_btn.clicked.connect(lambda: self.play_times_spinbox.setValue(max(1, self.play_times_spinbox.value() - 1)))
        play_times_control_layout.addWidget(play_times_minus_btn)
        
        self.play_times_spinbox = QSpinBox()
        self.play_times_spinbox.setMinimum(1)
        self.play_times_spinbox.setMaximum(9999)
        self.play_times_spinbox.setValue(1)
        self.play_times_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.play_times_spinbox.valueChanged.connect(self.on_play_times_changed)
        self.play_times_spinbox.setStyleSheet("""
            QSpinBox {
                border: 1px solid #BDBDBD;
                border-radius: 2px;
                padding: 2px 4px;
                background-color: #FFFFFF;
            }
        """)
        play_times_control_layout.addWidget(self.play_times_spinbox)
        
        play_times_plus_btn = QPushButton("+")
        play_times_plus_btn.setFixedWidth(25)
        play_times_plus_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #BDBDBD;
                border-radius: 2px;
                background-color: #FFFFFF;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
        """)
        play_times_plus_btn.clicked.connect(lambda: self.play_times_spinbox.setValue(min(9999, self.play_times_spinbox.value() + 1)))
        play_times_control_layout.addWidget(play_times_plus_btn)
        play_mode_layout.addLayout(play_times_control_layout)
        
        # Fixed length
        self.fixed_length_radio = QRadioButton("Fixed length")
        self.fixed_length_radio.toggled.connect(self.on_play_mode_changed)
        play_mode_layout.addWidget(self.fixed_length_radio)
        
        self.fixed_length_time = QTimeEdit()
        self.fixed_length_time.setDisplayFormat("H:mm:ss")
        self.fixed_length_time.setTime(QTime(0, 0, 30))
        self.fixed_length_time.timeChanged.connect(self.on_fixed_length_changed)
        self.fixed_length_time.setStyleSheet("""
            QTimeEdit {
                border: 1px solid #BDBDBD;
                border-radius: 2px;
                padding: 2px 4px;
                background-color: #FFFFFF;
            }
        """)
        play_mode_layout.addWidget(self.fixed_length_time)
        
        play_mode_layout.addStretch()
        layout.addWidget(play_mode_group)
        
        # Duration display (between Play mode and Play control)
        duration_widget = QWidget()
        duration_widget.setFixedWidth(40)
        duration_layout = QVBoxLayout(duration_widget)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        self.duration_label = QLabel("0.0 S")
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.duration_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #424242;
                background-color: transparent;
            }
        """)
        duration_layout.addWidget(self.duration_label)
        duration_layout.addStretch()
        layout.addWidget(duration_widget)
        
        # Right section: Play Control
        play_control_group = QGroupBox("Play control")
        play_control_group.setStyleSheet("""
            QGroupBox {
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 0px;
                padding: 0px 0px 0px 0px;
            }
        """)
        play_control_layout = QVBoxLayout(play_control_group)
        play_control_layout.setContentsMargins(5, 15, 5, 5)
        play_control_layout.setSpacing(5)
        
        # Specified time
        self.specified_time_checkbox = QCheckBox("specified time")
        self.specified_time_checkbox.stateChanged.connect(self.on_specified_time_changed)
        play_control_layout.addWidget(self.specified_time_checkbox)
        
        specified_time_input_layout = QHBoxLayout()
        specified_time_input_layout.setContentsMargins(0, 0, 0, 0)
        self.specified_time_input = QLineEdit()
        self.specified_time_input.setReadOnly(True)
        self.specified_time_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BDBDBD;
                border-radius: 2px;
                padding: 2px 4px;
                background-color: #FFFFFF;
            }
        """)
        specified_time_input_layout.addWidget(self.specified_time_input)
        self.specified_time_dropdown_btn = QPushButton("▼")
        self.specified_time_dropdown_btn.setFixedWidth(20)
        self.specified_time_dropdown_btn.setFlat(True)
        self.specified_time_dropdown_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0px;
                font-size: 10px;
            }
        """)
        self.specified_time_menu = QMenu(self)
        # Add time options (example)
        for hour in range(24):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                self.specified_time_menu.addAction(time_str)
        self.specified_time_menu.triggered.connect(self.on_specified_time_menu_selected)
        self.specified_time_dropdown_btn.setMenu(self.specified_time_menu)
        specified_time_input_layout.addWidget(self.specified_time_dropdown_btn)
        play_control_layout.addLayout(specified_time_input_layout)
        
        # Specify week
        self.specify_week_checkbox = QCheckBox("Specify the week")
        self.specify_week_checkbox.stateChanged.connect(self.on_specify_week_changed)
        play_control_layout.addWidget(self.specify_week_checkbox)
        
        specify_week_input_layout = QHBoxLayout()
        specify_week_input_layout.setContentsMargins(0, 0, 0, 0)
        self.specify_week_input = QLineEdit()
        self.specify_week_input.setReadOnly(True)
        self.specify_week_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BDBDBD;
                border-radius: 2px;
                padding: 2px 4px;
                background-color: #FFFFFF;
            }
        """)
        specify_week_input_layout.addWidget(self.specify_week_input)
        self.specify_week_dropdown_btn = QPushButton("▼")
        self.specify_week_dropdown_btn.setFixedWidth(20)
        self.specify_week_dropdown_btn.setFlat(True)
        self.specify_week_dropdown_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0px;
                font-size: 10px;
            }
        """)
        self.specify_week_menu = QMenu(self)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            action = self.specify_week_menu.addAction(day)
            action.setCheckable(True)
        self.specify_week_menu.triggered.connect(self.on_specify_week_menu_selected)
        self.specify_week_dropdown_btn.setMenu(self.specify_week_menu)
        specify_week_input_layout.addWidget(self.specify_week_dropdown_btn)
        play_control_layout.addLayout(specify_week_input_layout)
        
        # Specify date
        self.specify_date_checkbox = QCheckBox("Specify the date")
        self.specify_date_checkbox.stateChanged.connect(self.on_specify_date_changed)
        play_control_layout.addWidget(self.specify_date_checkbox)
        
        specify_date_input_layout = QHBoxLayout()
        specify_date_input_layout.setContentsMargins(0, 0, 0, 0)
        self.specify_date_input = QLineEdit()
        self.specify_date_input.setReadOnly(True)
        self.specify_date_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BDBDBD;
                border-radius: 2px;
                padding: 2px 4px;
                background-color: #FFFFFF;
            }
        """)
        specify_date_input_layout.addWidget(self.specify_date_input)
        self.specify_date_dropdown_btn = QPushButton("▼")
        self.specify_date_dropdown_btn.setFixedWidth(20)
        self.specify_date_dropdown_btn.setFlat(True)
        self.specify_date_dropdown_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0px;
                font-size: 10px;
            }
        """)
        self.specify_date_menu = QMenu(self)
        date_action = self.specify_date_menu.addAction("Select Date...")
        date_action.triggered.connect(self.on_select_date)
        self.specify_date_menu.triggered.connect(self.on_specify_date_menu_selected)
        self.specify_date_dropdown_btn.setMenu(self.specify_date_menu)
        specify_date_input_layout.addWidget(self.specify_date_dropdown_btn)
        play_control_layout.addLayout(specify_date_input_layout)
        
        play_control_layout.addStretch()
        layout.addWidget(play_control_group)
        
        # Element Properties Section (shown when element is selected)
        self.element_properties_group = QGroupBox("Element Properties")
        self.element_properties_group.setStyleSheet("""
            QGroupBox {
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 0px;
                padding: 0px 0px 0px 0px;
            }
        """)
        self.element_properties_layout = QVBoxLayout(self.element_properties_group)
        self.element_properties_layout.setContentsMargins(5, 15, 5, 5)
        self.element_properties_layout.setSpacing(5)
        
        # Element property widgets (will be created dynamically)
        self.element_property_widgets = {}
        
        # Initially hide element properties
        self.element_properties_group.hide()
        layout.addWidget(self.element_properties_group)
    
    def set_program(self, program: Program):
        """Set the current program and update UI"""
        self.program = program
        self.selected_element = None
        if program:
            self.update_ui_from_program()
    
    def set_selected_element(self, element_data: Optional[Dict]):
        """Set the selected element and update UI"""
        self.selected_element = element_data
        if element_data:
            # If widgets already exist, just update their values instead of recreating
            if self.element_property_widgets:
                self.update_existing_widgets(element_data)
            else:
                self.update_ui_from_element(element_data)
            self.element_properties_group.show()
        else:
            # Clear element-specific UI
            self.element_properties_group.hide()
            self.clear_element_properties()
    
    def clear_element_properties(self):
        """Clear element property widgets"""
        for widget in self.element_property_widgets.values():
            widget.setParent(None)
            widget.deleteLater()
        self.element_property_widgets.clear()
    
    def update_existing_widgets(self, element_data: Dict):
        """Update existing property widgets with new element data"""
        # Update position and size widgets
        if "x" in self.element_property_widgets:
            self.element_property_widgets["x"].setValue(element_data.get("x", 0))
        if "y" in self.element_property_widgets:
            self.element_property_widgets["y"].setValue(element_data.get("y", 0))
        if "width" in self.element_property_widgets:
            self.element_property_widgets["width"].setValue(element_data.get("width", 200))
        if "height" in self.element_property_widgets:
            self.element_property_widgets["height"].setValue(element_data.get("height", 100))
        
        # Update type-specific properties
        element_props = element_data.get("properties", {})
        element_type = element_data.get("type", "")
        
        from config.constants import ContentType
        try:
            content_type = ContentType(element_type)
            
            if content_type == ContentType.TEXT or content_type == ContentType.SINGLE_LINE_TEXT:
                if "text" in self.element_property_widgets:
                    self.element_property_widgets["text"].setText(element_props.get("text", ""))
                if "font_size" in self.element_property_widgets:
                    self.element_property_widgets["font_size"].setValue(element_props.get("font_size", 24))
                if "color" in self.element_property_widgets:
                    self.element_property_widgets["color"].setText(element_props.get("color", "#000000"))
            
            elif content_type == ContentType.VIDEO or content_type == ContentType.PHOTO:
                if "file_path" in self.element_property_widgets:
                    self.element_property_widgets["file_path"].setText(element_props.get("file_path", ""))
            
            elif content_type == ContentType.CLOCK:
                if "format" in self.element_property_widgets:
                    self.element_property_widgets["format"].setText(element_props.get("format", "HH:mm:ss"))
                if "color" in self.element_property_widgets:
                    self.element_property_widgets["color"].setText(element_props.get("color", "#000000"))
            
            elif content_type == ContentType.NEON:
                if "neon_index" in self.element_property_widgets:
                    self.element_property_widgets["neon_index"].setValue(element_props.get("neon_index", 0))
        except ValueError:
            pass
    
    def update_ui_from_element(self, element_data: Dict):
        """Update UI from element data"""
        from config.constants import ContentType
        
        # Clear existing widgets
        self.clear_element_properties()
        
        element_type = element_data.get("type", "")
        element_props = element_data.get("properties", {})
        
        try:
            content_type = ContentType(element_type)
            
            # Position and Size
            pos_layout = QHBoxLayout()
            pos_layout.addWidget(QLabel("Position:"))
            x_spin = QSpinBox()
            x_spin.setMinimum(0)
            x_spin.setMaximum(9999)
            x_spin.setValue(element_data.get("x", 0))
            x_spin.valueChanged.connect(lambda v: self.update_element_property("x", v))
            pos_layout.addWidget(QLabel("X:"))
            pos_layout.addWidget(x_spin)
            
            y_spin = QSpinBox()
            y_spin.setMinimum(0)
            y_spin.setMaximum(9999)
            y_spin.setValue(element_data.get("y", 0))
            y_spin.valueChanged.connect(lambda v: self.update_element_property("y", v))
            pos_layout.addWidget(QLabel("Y:"))
            pos_layout.addWidget(y_spin)
            self.element_properties_layout.addLayout(pos_layout)
            
            size_layout = QHBoxLayout()
            size_layout.addWidget(QLabel("Size:"))
            w_spin = QSpinBox()
            w_spin.setMinimum(1)
            w_spin.setMaximum(9999)
            w_spin.setValue(element_data.get("width", 200))
            w_spin.valueChanged.connect(lambda v: self.update_element_property("width", v))
            size_layout.addWidget(QLabel("W:"))
            size_layout.addWidget(w_spin)
            
            h_spin = QSpinBox()
            h_spin.setMinimum(1)
            h_spin.setMaximum(9999)
            h_spin.setValue(element_data.get("height", 100))
            h_spin.valueChanged.connect(lambda v: self.update_element_property("height", v))
            size_layout.addWidget(QLabel("H:"))
            size_layout.addWidget(h_spin)
            self.element_properties_layout.addLayout(size_layout)
            
            self.element_property_widgets["x"] = x_spin
            self.element_property_widgets["y"] = y_spin
            self.element_property_widgets["width"] = w_spin
            self.element_property_widgets["height"] = h_spin
            
            # Layer controls (z-order)
            layer_layout = QHBoxLayout()
            layer_layout.addWidget(QLabel("Layer:"))
            move_up_btn = QPushButton("↑")
            move_up_btn.setToolTip("Move to front")
            move_up_btn.clicked.connect(lambda: self.move_element_layer(1))
            layer_layout.addWidget(move_up_btn)
            
            move_down_btn = QPushButton("↓")
            move_down_btn.setToolTip("Move to back")
            move_down_btn.clicked.connect(lambda: self.move_element_layer(-1))
            layer_layout.addWidget(move_down_btn)
            self.element_properties_layout.addLayout(layer_layout)
            
            # Type-specific properties
            if content_type == ContentType.TEXT:
                self.add_text_properties(element_props)
            elif content_type == ContentType.SINGLE_LINE_TEXT:
                self.add_single_line_text_properties(element_props)
            elif content_type == ContentType.VIDEO:
                self.add_video_properties(element_props)
            elif content_type == ContentType.PHOTO:
                self.add_photo_properties(element_props)
            elif content_type == ContentType.CLOCK:
                self.add_clock_properties(element_props)
            elif content_type == ContentType.CALENDAR:
                self.add_calendar_properties(element_props)
            elif content_type == ContentType.NEON:
                self.add_neon_properties(element_props)
            elif content_type == ContentType.TIMING:
                self.add_timer_properties(element_props)
            elif content_type == ContentType.WEATHER:
                self.add_weather_properties(element_props)
            elif content_type == ContentType.TEXT_3D:
                self.add_text3d_properties(element_props)
            
            self.element_properties_layout.addStretch()
            
        except ValueError:
            pass
    
    def add_text_properties(self, props: Dict):
        """Add text element properties"""
        # Text input with emoji picker button
        text_layout = QHBoxLayout()
        text_input = QLineEdit()
        text_input.setText(props.get("text", "New Text"))
        text_input.textChanged.connect(lambda v: self.update_element_property("text", v, "properties"))
        text_layout.addWidget(QLabel("Text:"))
        text_layout.addWidget(text_input)
        
        emoji_btn = QPushButton("😀")
        emoji_btn.setToolTip("Insert Emoji")
        emoji_btn.setFixedSize(30, 30)
        emoji_btn.clicked.connect(lambda: self.open_emoji_picker(text_input))
        text_layout.addWidget(emoji_btn)
        self.element_properties_layout.addLayout(text_layout)
        self.element_property_widgets["text"] = text_input
        
        font_size_spin = QSpinBox()
        font_size_spin.setMinimum(8)
        font_size_spin.setMaximum(200)
        font_size_spin.setValue(props.get("font_size", 24))
        font_size_spin.valueChanged.connect(lambda v: self.update_element_property("font_size", v, "properties"))
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        font_layout.addWidget(font_size_spin)
        self.element_properties_layout.addLayout(font_layout)
        self.element_property_widgets["font_size"] = font_size_spin
        
        color_input = QLineEdit()
        color_input.setText(props.get("color", "#000000"))
        color_input.textChanged.connect(lambda v: self.update_element_property("color", v, "properties"))
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        color_layout.addWidget(color_input)
        self.element_properties_layout.addLayout(color_layout)
        self.element_property_widgets["color"] = color_input
        
        # Animation controls
        anim_layout = QHBoxLayout()
        anim_layout.addWidget(QLabel("Animation:"))
        anim_combo = QComboBox()
        anim_combo.addItems(["None", "Scroll Left", "Scroll Right", "Scroll Up", "Scroll Down", 
                            "Marquee", "Fade In", "Fade Out", "Fade In/Out", "Typewriter", 
                            "Bounce", "Flash"])
        current_anim = props.get("animation", "None")
        anim_combo.setCurrentText(current_anim if current_anim in [anim_combo.itemText(i) for i in range(anim_combo.count())] else "None")
        anim_combo.currentTextChanged.connect(lambda v: self.update_element_property("animation", v, "properties"))
        anim_layout.addWidget(anim_combo)
        self.element_properties_layout.addLayout(anim_layout)
        self.element_property_widgets["animation"] = anim_combo
        
        # Text effects section
        effects_label = QLabel("Text Effects:")
        effects_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.element_properties_layout.addWidget(effects_label)
        
        # Shadow
        shadow_check = QCheckBox("Shadow")
        shadow_check.setChecked(props.get("text_shadow", False))
        shadow_check.stateChanged.connect(lambda s: self.update_element_property("text_shadow", s == Qt.CheckState.Checked.value, "properties"))
        self.element_properties_layout.addWidget(shadow_check)
        self.element_property_widgets["text_shadow"] = shadow_check
        
        shadow_color_input = QLineEdit()
        shadow_color_input.setText(props.get("shadow_color", "#000000"))
        shadow_color_input.textChanged.connect(lambda v: self.update_element_property("shadow_color", v, "properties"))
        shadow_layout = QHBoxLayout()
        shadow_layout.addWidget(QLabel("Shadow Color:"))
        shadow_layout.addWidget(shadow_color_input)
        self.element_properties_layout.addLayout(shadow_layout)
        self.element_property_widgets["shadow_color"] = shadow_color_input
        
        shadow_offset_x_spin = QSpinBox()
        shadow_offset_x_spin.setMinimum(-20)
        shadow_offset_x_spin.setMaximum(20)
        shadow_offset_x_spin.setValue(props.get("shadow_offset_x", 2))
        shadow_offset_x_spin.valueChanged.connect(lambda v: self.update_element_property("shadow_offset_x", v, "properties"))
        shadow_offset_y_spin = QSpinBox()
        shadow_offset_y_spin.setMinimum(-20)
        shadow_offset_y_spin.setMaximum(20)
        shadow_offset_y_spin.setValue(props.get("shadow_offset_y", 2))
        shadow_offset_y_spin.valueChanged.connect(lambda v: self.update_element_property("shadow_offset_y", v, "properties"))
        shadow_offset_layout = QHBoxLayout()
        shadow_offset_layout.addWidget(QLabel("Shadow Offset:"))
        shadow_offset_layout.addWidget(QLabel("X:"))
        shadow_offset_layout.addWidget(shadow_offset_x_spin)
        shadow_offset_layout.addWidget(QLabel("Y:"))
        shadow_offset_layout.addWidget(shadow_offset_y_spin)
        self.element_properties_layout.addLayout(shadow_offset_layout)
        self.element_property_widgets["shadow_offset_x"] = shadow_offset_x_spin
        self.element_property_widgets["shadow_offset_y"] = shadow_offset_y_spin
        
        # Outline
        outline_check = QCheckBox("Outline")
        outline_check.setChecked(props.get("text_outline", False))
        outline_check.stateChanged.connect(lambda s: self.update_element_property("text_outline", s == Qt.CheckState.Checked.value, "properties"))
        self.element_properties_layout.addWidget(outline_check)
        self.element_property_widgets["text_outline"] = outline_check
        
        outline_color_input = QLineEdit()
        outline_color_input.setText(props.get("outline_color", "#000000"))
        outline_color_input.textChanged.connect(lambda v: self.update_element_property("outline_color", v, "properties"))
        outline_layout = QHBoxLayout()
        outline_layout.addWidget(QLabel("Outline Color:"))
        outline_layout.addWidget(outline_color_input)
        self.element_properties_layout.addLayout(outline_layout)
        self.element_property_widgets["outline_color"] = outline_color_input
        
        outline_width_spin = QSpinBox()
        outline_width_spin.setMinimum(1)
        outline_width_spin.setMaximum(10)
        outline_width_spin.setValue(props.get("outline_width", 2))
        outline_width_spin.valueChanged.connect(lambda v: self.update_element_property("outline_width", v, "properties"))
        outline_width_layout = QHBoxLayout()
        outline_width_layout.addWidget(QLabel("Outline Width:"))
        outline_width_layout.addWidget(outline_width_spin)
        self.element_properties_layout.addLayout(outline_width_layout)
        self.element_property_widgets["outline_width"] = outline_width_spin
        
        # Gradient
        gradient_check = QCheckBox("Gradient")
        gradient_check.setChecked(props.get("text_gradient", False))
        gradient_check.stateChanged.connect(lambda s: self.update_element_property("text_gradient", s == Qt.CheckState.Checked.value, "properties"))
        self.element_properties_layout.addWidget(gradient_check)
        self.element_property_widgets["text_gradient"] = gradient_check
        
        gradient_color1_input = QLineEdit()
        gradient_color1_input.setText(props.get("gradient_color1", "#000000"))
        gradient_color1_input.textChanged.connect(lambda v: self.update_element_property("gradient_color1", v, "properties"))
        gradient_color2_input = QLineEdit()
        gradient_color2_input.setText(props.get("gradient_color2", "#FFFFFF"))
        gradient_color2_input.textChanged.connect(lambda v: self.update_element_property("gradient_color2", v, "properties"))
        gradient_layout = QHBoxLayout()
        gradient_layout.addWidget(QLabel("Gradient Colors:"))
        gradient_layout.addWidget(gradient_color1_input)
        gradient_layout.addWidget(gradient_color2_input)
        self.element_properties_layout.addLayout(gradient_layout)
        self.element_property_widgets["gradient_color1"] = gradient_color1_input
        self.element_property_widgets["gradient_color2"] = gradient_color2_input
        
        gradient_direction_combo = QComboBox()
        gradient_direction_combo.addItems(["Horizontal", "Vertical"])
        gradient_direction_combo.setCurrentText("Horizontal" if props.get("gradient_direction", "horizontal") == "horizontal" else "Vertical")
        gradient_direction_combo.currentTextChanged.connect(lambda v: self.update_element_property("gradient_direction", v.lower(), "properties"))
        gradient_direction_layout = QHBoxLayout()
        gradient_direction_layout.addWidget(QLabel("Gradient Direction:"))
        gradient_direction_layout.addWidget(gradient_direction_combo)
        self.element_properties_layout.addLayout(gradient_direction_layout)
        self.element_property_widgets["gradient_direction"] = gradient_direction_combo
        
        # Animation speed
        anim_speed_spin = QSpinBox()
        anim_speed_spin.setMinimum(1)
        anim_speed_spin.setMaximum(10)
        anim_speed_spin.setValue(props.get("animation_speed", 1))
        anim_speed_spin.valueChanged.connect(lambda v: self.update_element_property("animation_speed", v, "properties"))
        anim_speed_layout = QHBoxLayout()
        anim_speed_layout.addWidget(QLabel("Speed:"))
        anim_speed_layout.addWidget(anim_speed_spin)
        self.element_properties_layout.addLayout(anim_speed_layout)
        self.element_property_widgets["animation_speed"] = anim_speed_spin
    
    def add_single_line_text_properties(self, props: Dict):
        """Add single line text properties"""
        self.add_text_properties(props)
        
        speed_spin = QSpinBox()
        speed_spin.setMinimum(1)
        speed_spin.setMaximum(20)
        speed_spin.setValue(props.get("speed", 5))
        speed_spin.valueChanged.connect(lambda v: self.update_element_property("speed", v, "properties"))
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        speed_layout.addWidget(speed_spin)
        self.element_properties_layout.addLayout(speed_layout)
        self.element_property_widgets["speed"] = speed_spin
    
    def add_video_properties(self, props: Dict):
        """Add video element properties"""
        file_layout = QHBoxLayout()
        file_input = QLineEdit()
        file_input.setText(props.get("file_path", ""))
        file_input.setReadOnly(True)
        file_layout.addWidget(QLabel("File:"))
        file_layout.addWidget(file_input)
        
        file_btn = QPushButton("Browse...")
        file_btn.clicked.connect(lambda: self.select_video_file(file_input))
        file_layout.addWidget(file_btn)
        self.element_properties_layout.addLayout(file_layout)
        self.element_property_widgets["file_path"] = file_input
        
        loop_check = QCheckBox("Loop")
        loop_check.setChecked(props.get("loop", True))
        loop_check.stateChanged.connect(lambda s: self.update_element_property("loop", s == Qt.CheckState.Checked.value, "properties"))
        self.element_properties_layout.addWidget(loop_check)
        self.element_property_widgets["loop"] = loop_check
        
        # Element Timing Section (for video overlay timing)
        timing_label = QLabel("Element Timing:")
        timing_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.element_properties_layout.addWidget(timing_label)
        
        # Display Order
        display_order_spin = QSpinBox()
        display_order_spin.setMinimum(0)
        display_order_spin.setMaximum(999)
        display_order_spin.setValue(props.get("display_order", 0))
        display_order_spin.valueChanged.connect(lambda v: self.update_element_property("display_order", v, "properties"))
        display_order_layout = QHBoxLayout()
        display_order_layout.addWidget(QLabel("Display Order:"))
        display_order_layout.addWidget(display_order_spin)
        self.element_properties_layout.addLayout(display_order_layout)
        self.element_property_widgets["display_order"] = display_order_spin
    
    def add_photo_properties(self, props: Dict):
        """Add photo element properties"""
        file_layout = QHBoxLayout()
        file_input = QLineEdit()
        file_input.setText(props.get("file_path", ""))
        file_input.setReadOnly(True)
        file_layout.addWidget(QLabel("File:"))
        file_layout.addWidget(file_input)
        
        file_btn = QPushButton("Browse...")
        file_btn.clicked.connect(lambda: self.select_image_file(file_input))
        file_layout.addWidget(file_btn)
        self.element_properties_layout.addLayout(file_layout)
        self.element_property_widgets["file_path"] = file_input
        
        # Element Timing Section
        timing_label = QLabel("Element Timing:")
        timing_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.element_properties_layout.addWidget(timing_label)
        
        # Duration
        duration_spin = QDoubleSpinBox()
        duration_spin.setMinimum(0.1)
        duration_spin.setMaximum(3600.0)
        duration_spin.setSingleStep(0.5)
        duration_spin.setValue(props.get("duration", 5.0))
        duration_spin.setSuffix(" seconds")
        duration_spin.valueChanged.connect(lambda v: self.update_element_property("duration", v, "properties"))
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration:"))
        duration_layout.addWidget(duration_spin)
        self.element_properties_layout.addLayout(duration_layout)
        self.element_property_widgets["duration"] = duration_spin
        
        # Transition IN
        transition_in_combo = QComboBox()
        transition_in_combo.addItems(["None", "Fade", "Slide Left", "Slide Right", "Slide Up", "Slide Down", 
                                     "Zoom In", "Zoom Out", "Rotate", "Blur"])
        current_trans_in = props.get("transition_in", "none")
        transition_in_combo.setCurrentText(current_trans_in.replace("_", " ").title() if current_trans_in != "none" else "None")
        transition_in_combo.currentTextChanged.connect(lambda v: self.update_element_property("transition_in", v.lower().replace(" ", "_"), "properties"))
        transition_in_layout = QHBoxLayout()
        transition_in_layout.addWidget(QLabel("Transition IN:"))
        transition_in_layout.addWidget(transition_in_combo)
        self.element_properties_layout.addLayout(transition_in_layout)
        self.element_property_widgets["transition_in"] = transition_in_combo
        
        # Transition OUT
        transition_out_combo = QComboBox()
        transition_out_combo.addItems(["None", "Fade", "Slide Left", "Slide Right", "Slide Up", "Slide Down", 
                                      "Zoom In", "Zoom Out", "Rotate", "Blur"])
        current_trans_out = props.get("transition_out", "none")
        transition_out_combo.setCurrentText(current_trans_out.replace("_", " ").title() if current_trans_out != "none" else "None")
        transition_out_combo.currentTextChanged.connect(lambda v: self.update_element_property("transition_out", v.lower().replace(" ", "_"), "properties"))
        transition_out_layout = QHBoxLayout()
        transition_out_layout.addWidget(QLabel("Transition OUT:"))
        transition_out_layout.addWidget(transition_out_combo)
        self.element_properties_layout.addLayout(transition_out_layout)
        self.element_property_widgets["transition_out"] = transition_out_combo
        
        # Display Order
        display_order_spin = QSpinBox()
        display_order_spin.setMinimum(0)
        display_order_spin.setMaximum(999)
        display_order_spin.setValue(props.get("display_order", 0))
        display_order_spin.valueChanged.connect(lambda v: self.update_element_property("display_order", v, "properties"))
        display_order_layout = QHBoxLayout()
        display_order_layout.addWidget(QLabel("Display Order:"))
        display_order_layout.addWidget(display_order_spin)
        self.element_properties_layout.addLayout(display_order_layout)
        self.element_property_widgets["display_order"] = display_order_spin
        
        # Image effects section
        effects_label = QLabel("Image Effects:")
        effects_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.element_properties_layout.addWidget(effects_label)
        
        # Brightness
        brightness_spin = QSpinBox()
        brightness_spin.setMinimum(-100)
        brightness_spin.setMaximum(100)
        brightness_spin.setValue(props.get("brightness", 0))
        brightness_spin.valueChanged.connect(lambda v: self.update_element_property("brightness", v, "properties"))
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness:"))
        brightness_layout.addWidget(brightness_spin)
        self.element_properties_layout.addLayout(brightness_layout)
        self.element_property_widgets["brightness"] = brightness_spin
        
        # Contrast
        contrast_spin = QSpinBox()
        contrast_spin.setMinimum(-100)
        contrast_spin.setMaximum(100)
        contrast_spin.setValue(props.get("contrast", 0))
        contrast_spin.valueChanged.connect(lambda v: self.update_element_property("contrast", v, "properties"))
        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(QLabel("Contrast:"))
        contrast_layout.addWidget(contrast_spin)
        self.element_properties_layout.addLayout(contrast_layout)
        self.element_property_widgets["contrast"] = contrast_spin
        
        # Saturation
        saturation_spin = QSpinBox()
        saturation_spin.setMinimum(-100)
        saturation_spin.setMaximum(100)
        saturation_spin.setValue(props.get("saturation", 0))
        saturation_spin.valueChanged.connect(lambda v: self.update_element_property("saturation", v, "properties"))
        saturation_layout = QHBoxLayout()
        saturation_layout.addWidget(QLabel("Saturation:"))
        saturation_layout.addWidget(saturation_spin)
        self.element_properties_layout.addLayout(saturation_layout)
        self.element_property_widgets["saturation"] = saturation_spin
        
        # Filter
        filter_combo = QComboBox()
        filter_combo.addItems(["None", "Grayscale", "Sepia", "Invert"])
        current_filter = props.get("filter", "none")
        filter_combo.setCurrentText(current_filter.capitalize() if current_filter != "none" else "None")
        filter_combo.currentTextChanged.connect(lambda v: self.update_element_property("filter", v.lower(), "properties"))
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(filter_combo)
        self.element_properties_layout.addLayout(filter_layout)
        self.element_property_widgets["filter"] = filter_combo
    
    def add_clock_properties(self, props: Dict):
        """Add clock element properties"""
        format_input = QLineEdit()
        format_input.setText(props.get("format", "HH:mm:ss"))
        format_input.textChanged.connect(lambda v: self.update_element_property("format", v, "properties"))
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(format_input)
        self.element_properties_layout.addLayout(format_layout)
        self.element_property_widgets["format"] = format_input
        
        color_input = QLineEdit()
        color_input.setText(props.get("color", "#000000"))
        color_input.textChanged.connect(lambda v: self.update_element_property("color", v, "properties"))
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        color_layout.addWidget(color_input)
        self.element_properties_layout.addLayout(color_layout)
        self.element_property_widgets["color"] = color_input
    
    def add_calendar_properties(self, props: Dict):
        """Add calendar element properties"""
        highlight_check = QCheckBox("Highlight Today")
        highlight_check.setChecked(props.get("highlight_today", True))
        highlight_check.stateChanged.connect(lambda s: self.update_element_property("highlight_today", s == Qt.CheckState.Checked.value, "properties"))
        self.element_properties_layout.addWidget(highlight_check)
        self.element_property_widgets["highlight_today"] = highlight_check
    
    def add_neon_properties(self, props: Dict):
        """Add neon element properties"""
        neon_index_spin = QSpinBox()
        neon_index_spin.setMinimum(0)
        neon_index_spin.setMaximum(19)  # Based on available neon_gif files
        neon_index_spin.setValue(props.get("neon_index", 0))
        neon_index_spin.valueChanged.connect(lambda v: self.update_element_property("neon_index", v, "properties"))
        neon_layout = QHBoxLayout()
        neon_layout.addWidget(QLabel("Neon Effect:"))
        neon_layout.addWidget(neon_index_spin)
        self.element_properties_layout.addLayout(neon_layout)
        self.element_property_widgets["neon_index"] = neon_index_spin
    
    def add_timer_properties(self, props: Dict):
        """Add timer element properties"""
        # Mode selection
        mode_combo = QComboBox()
        mode_combo.addItems(["Countdown", "Timer"])
        current_mode = props.get("mode", "countdown")
        mode_combo.setCurrentText("Countdown" if current_mode == "countdown" else "Timer")
        mode_combo.currentTextChanged.connect(lambda v: self.update_element_property("mode", v.lower(), "properties"))
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        mode_layout.addWidget(mode_combo)
        self.element_properties_layout.addLayout(mode_layout)
        self.element_property_widgets["mode"] = mode_combo
        
        # Duration (for countdown)
        duration_spin = QSpinBox()
        duration_spin.setMinimum(1)
        duration_spin.setMaximum(86400)  # 24 hours
        duration_spin.setValue(props.get("duration", 60))
        duration_spin.setSuffix(" seconds")
        duration_spin.valueChanged.connect(lambda v: self.update_element_property("duration", v, "properties"))
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration:"))
        duration_layout.addWidget(duration_spin)
        self.element_properties_layout.addLayout(duration_layout)
        self.element_property_widgets["duration"] = duration_spin
        
        # Color
        color_input = QLineEdit()
        color_input.setText(props.get("color", "#000000"))
        color_input.textChanged.connect(lambda v: self.update_element_property("color", v, "properties"))
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        color_layout.addWidget(color_input)
        self.element_properties_layout.addLayout(color_layout)
        self.element_property_widgets["color"] = color_input
        
        # Font size
        font_size_spin = QSpinBox()
        font_size_spin.setMinimum(8)
        font_size_spin.setMaximum(200)
        font_size_spin.setValue(props.get("font_size", 48))
        font_size_spin.valueChanged.connect(lambda v: self.update_element_property("font_size", v, "properties"))
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Font Size:"))
        font_size_layout.addWidget(font_size_spin)
        self.element_properties_layout.addLayout(font_size_layout)
        self.element_property_widgets["font_size"] = font_size_spin
    
    def add_weather_properties(self, props: Dict):
        """Add weather element properties"""
        # API Key
        api_key_input = QLineEdit()
        api_key_input.setText(props.get("api_key", ""))
        api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_key_input.textChanged.connect(lambda v: self.update_element_property("api_key", v, "properties"))
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))
        api_key_layout.addWidget(api_key_input)
        self.element_properties_layout.addLayout(api_key_layout)
        self.element_property_widgets["api_key"] = api_key_input
        
        # City
        city_input = QLineEdit()
        city_input.setText(props.get("city", "London"))
        city_input.textChanged.connect(lambda v: self.update_element_property("city", v, "properties"))
        city_layout = QHBoxLayout()
        city_layout.addWidget(QLabel("City:"))
        city_layout.addWidget(city_input)
        self.element_properties_layout.addLayout(city_layout)
        self.element_property_widgets["city"] = city_input
        
        # Units
        units_combo = QComboBox()
        units_combo.addItems(["Metric", "Imperial"])
        units_combo.setCurrentText("Metric" if props.get("units", "metric") == "metric" else "Imperial")
        units_combo.currentTextChanged.connect(lambda v: self.update_element_property("units", v.lower(), "properties"))
        units_layout = QHBoxLayout()
        units_layout.addWidget(QLabel("Units:"))
        units_layout.addWidget(units_combo)
        self.element_properties_layout.addLayout(units_layout)
        self.element_property_widgets["units"] = units_combo
        
        # Format
        format_input = QLineEdit()
        format_input.setText(props.get("format", "{city}: {temperature}°C, {description}"))
        format_input.textChanged.connect(lambda v: self.update_element_property("format", v, "properties"))
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(format_input)
        self.element_properties_layout.addLayout(format_layout)
        self.element_property_widgets["format"] = format_input
        
        # Update interval
        interval_spin = QSpinBox()
        interval_spin.setMinimum(60)
        interval_spin.setMaximum(86400)
        interval_spin.setValue(props.get("update_interval", 3600))
        interval_spin.setSuffix(" seconds")
        interval_spin.valueChanged.connect(lambda v: self.update_element_property("update_interval", v, "properties"))
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Update Interval:"))
        interval_layout.addWidget(interval_spin)
        self.element_properties_layout.addLayout(interval_layout)
        self.element_property_widgets["update_interval"] = interval_spin
        
        # Font size
        font_size_spin = QSpinBox()
        font_size_spin.setMinimum(8)
        font_size_spin.setMaximum(200)
        font_size_spin.setValue(props.get("font_size", 24))
        font_size_spin.valueChanged.connect(lambda v: self.update_element_property("font_size", v, "properties"))
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Font Size:"))
        font_size_layout.addWidget(font_size_spin)
        self.element_properties_layout.addLayout(font_size_layout)
        self.element_property_widgets["font_size"] = font_size_spin
        
        # Color
        color_input = QLineEdit()
        color_input.setText(props.get("color", "#000000"))
        color_input.textChanged.connect(lambda v: self.update_element_property("color", v, "properties"))
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        color_layout.addWidget(color_input)
        self.element_properties_layout.addLayout(color_layout)
        self.element_property_widgets["color"] = color_input
    
    def add_text3d_properties(self, props: Dict):
        """Add 3D text element properties"""
        # Text content
        text_input = QLineEdit()
        text_input.setText(props.get("text", "3D Text"))
        text_input.textChanged.connect(lambda v: self.update_element_property("text", v, "properties"))
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text:"))
        text_layout.addWidget(text_input)
        self.element_properties_layout.addLayout(text_layout)
        self.element_property_widgets["text"] = text_input
        
        # Font size
        font_size_spin = QSpinBox()
        font_size_spin.setMinimum(8)
        font_size_spin.setMaximum(200)
        font_size_spin.setValue(props.get("font_size", 48))
        font_size_spin.valueChanged.connect(lambda v: self.update_element_property("font_size", v, "properties"))
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Font Size:"))
        font_size_layout.addWidget(font_size_spin)
        self.element_properties_layout.addLayout(font_size_layout)
        self.element_property_widgets["font_size"] = font_size_spin
        
        # Color
        color_input = QLineEdit()
        color_input.setText(props.get("color", "#000000"))
        color_input.textChanged.connect(lambda v: self.update_element_property("color", v, "properties"))
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        color_layout.addWidget(color_input)
        self.element_properties_layout.addLayout(color_layout)
        self.element_property_widgets["color"] = color_input
        
        # 3D Properties
        depth_spin = QDoubleSpinBox()
        depth_spin.setMinimum(0.0)
        depth_spin.setMaximum(100.0)
        depth_spin.setSingleStep(1.0)
        depth_spin.setValue(props.get("depth", 10.0))
        depth_spin.valueChanged.connect(lambda v: self.update_element_property("depth", v, "properties"))
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Depth:"))
        depth_layout.addWidget(depth_spin)
        self.element_properties_layout.addLayout(depth_layout)
        self.element_property_widgets["depth"] = depth_spin
        
        # Rotation
        rot_x_spin = QDoubleSpinBox()
        rot_x_spin.setMinimum(-180.0)
        rot_x_spin.setMaximum(180.0)
        rot_x_spin.setValue(props.get("rotation_x", 0.0))
        rot_x_spin.valueChanged.connect(lambda v: self.update_element_property("rotation_x", v, "properties"))
        rot_x_layout = QHBoxLayout()
        rot_x_layout.addWidget(QLabel("Rotation X:"))
        rot_x_layout.addWidget(rot_x_spin)
        self.element_properties_layout.addLayout(rot_x_layout)
        self.element_property_widgets["rotation_x"] = rot_x_spin
        
        rot_y_spin = QDoubleSpinBox()
        rot_y_spin.setMinimum(-180.0)
        rot_y_spin.setMaximum(180.0)
        rot_y_spin.setValue(props.get("rotation_y", 0.0))
        rot_y_spin.valueChanged.connect(lambda v: self.update_element_property("rotation_y", v, "properties"))
        rot_y_layout = QHBoxLayout()
        rot_y_layout.addWidget(QLabel("Rotation Y:"))
        rot_y_layout.addWidget(rot_y_spin)
        self.element_properties_layout.addLayout(rot_y_layout)
        self.element_property_widgets["rotation_y"] = rot_y_spin
        
        rot_z_spin = QDoubleSpinBox()
        rot_z_spin.setMinimum(-180.0)
        rot_z_spin.setMaximum(180.0)
        rot_z_spin.setValue(props.get("rotation_z", 0.0))
        rot_z_spin.valueChanged.connect(lambda v: self.update_element_property("rotation_z", v, "properties"))
        rot_z_layout = QHBoxLayout()
        rot_z_layout.addWidget(QLabel("Rotation Z:"))
        rot_z_layout.addWidget(rot_z_spin)
        self.element_properties_layout.addLayout(rot_z_layout)
        self.element_property_widgets["rotation_z"] = rot_z_spin
    
    def update_element_property(self, key: str, value: Any, parent_key: str = None):
        """Update element property"""
        if not self.selected_element or not self.program:
            return
        
        element_id = self.selected_element.get("id")
        if not element_id:
            return
        
        # Find and update element
        for element_data in self.program.elements:
            if element_data.get("id") == element_id:
                if parent_key:
                    if parent_key not in element_data:
                        element_data[parent_key] = {}
                    element_data[parent_key][key] = value
                else:
                    element_data[key] = value
                
                # Update selected element reference
                self.selected_element = element_data
                
                # Emit signal to update canvas
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self.parent().parent().canvas.canvas_widget.update() if hasattr(self.parent().parent(), 'canvas') else None)
                break
    
    def select_video_file(self, file_input: QLineEdit):
        """Select video file"""
        from PyQt6.QtWidgets import QFileDialog, QDialog, QDialogButtonBox
        from core.media_library import get_media_library
        
        # Show dialog with options: Library or Browse
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Video")
        layout = QVBoxLayout(dialog)
        
        from_media_library_btn = QPushButton("From Media Library")
        from_media_library_btn.clicked.connect(lambda: self.select_from_media_library("video", file_input, dialog))
        layout.addWidget(from_media_library_btn)
        
        browse_btn = QPushButton("Browse Files...")
        browse_btn.clicked.connect(lambda: self.browse_video_file(file_input, dialog))
        layout.addWidget(browse_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)
        
        dialog.exec()
    
    def browse_video_file(self, file_input: QLineEdit, dialog: QDialog):
        """Browse for video file"""
        from PyQt6.QtWidgets import QFileDialog
        from core.media_library import get_media_library
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*)"
        )
        if file_path:
            # Add to media library
            media_library = get_media_library()
            media_library.add_media_file(file_path)
            
            file_input.setText(file_path)
            self.update_element_property("file_path", file_path, "properties")
            # Setup video player in canvas
            if self.selected_element and hasattr(self.parent().parent(), 'canvas'):
                element_id = self.selected_element.get("id")
                element_x = self.selected_element.get("x", 0)
                element_y = self.selected_element.get("y", 0)
                element_width = self.selected_element.get("width", 640)
                element_height = self.selected_element.get("height", 360)
                element_props = self.selected_element.get("properties", {})
                self.parent().parent().canvas.canvas_widget.setup_video_player(
                    element_id, file_path, element_x, element_y, 
                    element_width, element_height, element_props
                )
                self.parent().parent().canvas.canvas_widget.update()
            dialog.accept()
    
    def select_from_media_library(self, media_type: str, file_input: QLineEdit, parent_dialog: QDialog):
        """Select file from media library"""
        from ui.media_library_panel import MediaLibraryPanel
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Media Library")
        dialog.setMinimumSize(800, 600)
        layout = QVBoxLayout(dialog)
        
        # Filter by type
        library_panel = MediaLibraryPanel()
        if media_type == "video":
            library_panel.type_filter.setCurrentText("Videos")
        elif media_type == "image":
            library_panel.type_filter.setCurrentText("Images")
        
        library_panel.media_selected.connect(lambda path: self.on_media_library_selected(
            path, media_type, file_input, dialog, parent_dialog
        ))
        layout.addWidget(library_panel)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.exec()
    
    def on_media_library_selected(self, file_path: str, media_type: str, 
                                 file_input: QLineEdit, library_dialog: QDialog,
                                 parent_dialog: QDialog):
        """Handle media selection from library"""
        file_input.setText(file_path)
        self.update_element_property("file_path", file_path, "properties")
        
        if media_type == "video" and self.selected_element and hasattr(self.parent().parent(), 'canvas'):
            element_id = self.selected_element.get("id")
            element_x = self.selected_element.get("x", 0)
            element_y = self.selected_element.get("y", 0)
            element_width = self.selected_element.get("width", 640)
            element_height = self.selected_element.get("height", 360)
            element_props = self.selected_element.get("properties", {})
            self.parent().parent().canvas.canvas_widget.setup_video_player(
                element_id, file_path, element_x, element_y, 
                element_width, element_height, element_props
            )
            self.parent().parent().canvas.canvas_widget.update()
        
        library_dialog.accept()
        parent_dialog.accept()
    
    def select_image_file(self, file_input: QLineEdit):
        """Select image file"""
        from PyQt6.QtWidgets import QFileDialog, QDialog
        from core.media_library import get_media_library
        
        # Show dialog with options: Library or Browse
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Image")
        layout = QVBoxLayout(dialog)
        
        from_media_library_btn = QPushButton("From Media Library")
        from_media_library_btn.clicked.connect(lambda: self.select_from_media_library("image", file_input, dialog))
        layout.addWidget(from_media_library_btn)
        
        browse_btn = QPushButton("Browse Files...")
        browse_btn.clicked.connect(lambda: self.browse_image_file(file_input, dialog))
        layout.addWidget(browse_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)
        
        dialog.exec()
    
    def browse_image_file(self, file_input: QLineEdit, dialog: QDialog):
        """Browse for image file"""
        from PyQt6.QtWidgets import QFileDialog
        from core.media_library import get_media_library
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        if file_path:
            # Add to media library
            media_library = get_media_library()
            media_library.add_media_file(file_path)
            
            file_input.setText(file_path)
            self.update_element_property("file_path", file_path, "properties")
            dialog.accept()
    
    def open_emoji_picker(self, text_input: QLineEdit):
        """Open emoji picker dialog"""
        from ui.widgets.emoji_picker import EmojiPickerDialog
        dialog = EmojiPickerDialog(self)
        if dialog.exec():
            emoji_char = dialog.get_selected_emoji()
            if emoji_char:
                current_text = text_input.text()
                text_input.setText(current_text + emoji_char)
                self.update_element_property("text", current_text + emoji_char, "properties")
    
    def move_element_layer(self, direction: int):
        """Move element up (1) or down (-1) in z-order"""
        if not self.selected_element or not self.program:
            return
        
        element_id = self.selected_element.get("id")
        if not element_id:
            return
        
        elements = self.program.elements
        # Find element index
        element_index = None
        for i, elem in enumerate(elements):
            if elem.get("id") == element_id:
                element_index = i
                break
        
        if element_index is None:
            return
        
        # Move element
        new_index = element_index + direction
        if 0 <= new_index < len(elements):
            # Swap elements
            elements[element_index], elements[new_index] = elements[new_index], elements[element_index]
            # Update canvas
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self.parent().parent().canvas.canvas_widget.update() if hasattr(self.parent().parent(), 'canvas') else None)
    
    def update_ui_from_program(self):
        """Update UI from program data"""
        if not self.program:
            return
        
        # Frame
        frame_enabled = self.program.properties.get("frame", {}).get("enabled", False)
        self.frame_checkbox.setChecked(frame_enabled)
        frame_style = self.program.properties.get("frame", {}).get("style", "--- --- --- 1")
        self.frame_input.setText(frame_style)
        
        # Background Music
        bgm_enabled = self.program.properties.get("background_music", {}).get("enabled", False)
        self.bgm_checkbox.setChecked(bgm_enabled)
        bgm_file = self.program.properties.get("background_music", {}).get("file", "")
        self.bgm_input.setText(bgm_file)
        bgm_volume = self.program.properties.get("background_music", {}).get("volume", 0)
        self.volume_indicator.setText(str(bgm_volume))
        
        # Play mode
        mode = self.program.play_mode.get("mode", "play_times")
        if mode == "play_times":
            self.play_times_radio.setChecked(True)
            self.play_times_spinbox.setValue(self.program.play_mode.get("play_times", 1))
        else:
            self.fixed_length_radio.setChecked(True)
            # Parse time string (H:mm:ss)
            time_str = self.program.play_mode.get("fixed_length", "0:00:30")
            parts = time_str.split(":")
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                self.fixed_length_time.setTime(QTime(hours, minutes, seconds))
        
        # Duration
        duration = self.program.duration
        self.duration_label.setText(f"{duration:.1f} S")
        
        # Play control
        specified_time_enabled = self.program.play_control.get("specified_time", {}).get("enabled", False)
        self.specified_time_checkbox.setChecked(specified_time_enabled)
        specified_time_value = self.program.play_control.get("specified_time", {}).get("time", "")
        self.specified_time_input.setText(specified_time_value)
        
        specify_week_enabled = self.program.play_control.get("specify_week", {}).get("enabled", False)
        self.specify_week_checkbox.setChecked(specify_week_enabled)
        specify_week_days = self.program.play_control.get("specify_week", {}).get("days", [])
        self.specify_week_input.setText(", ".join(specify_week_days) if specify_week_days else "")
        
        specify_date_enabled = self.program.play_control.get("specify_date", {}).get("enabled", False)
        self.specify_date_checkbox.setChecked(specify_date_enabled)
        specify_date_value = self.program.play_control.get("specify_date", {}).get("date", "")
        self.specify_date_input.setText(specify_date_value)
    
    def on_frame_changed(self, state):
        """Handle frame checkbox change"""
        if self.program:
            if "frame" not in self.program.properties:
                self.program.properties["frame"] = {}
            self.program.properties["frame"]["enabled"] = (state == Qt.CheckState.Checked.value)
    
    def on_frame_style_changed(self, text):
        """Handle frame style change"""
        if self.program:
            if "frame" not in self.program.properties:
                self.program.properties["frame"] = {}
            self.program.properties["frame"]["style"] = text
    
    def on_bgm_changed(self, state):
        """Handle background music checkbox change"""
        if self.program:
            if "background_music" not in self.program.properties:
                self.program.properties["background_music"] = {}
            self.program.properties["background_music"]["enabled"] = (state == Qt.CheckState.Checked.value)
    
    def on_play_mode_changed(self):
        """Handle play mode change"""
        if self.program:
            if self.play_times_radio.isChecked():
                self.program.play_mode["mode"] = "play_times"
            else:
                self.program.play_mode["mode"] = "fixed_length"
    
    def on_play_times_changed(self, value):
        """Handle play times change"""
        if self.program:
            self.program.play_mode["play_times"] = value
    
    def on_fixed_length_changed(self, time):
        """Handle fixed length change"""
        if self.program:
            time_str = f"{time.hour()}:{time.minute():02d}:{time.second():02d}"
            self.program.play_mode["fixed_length"] = time_str
    
    def on_specified_time_changed(self, state):
        """Handle specified time checkbox change"""
        if self.program:
            self.program.play_control["specified_time"]["enabled"] = (state == Qt.CheckState.Checked.value)
    
    def on_specify_week_changed(self, state):
        """Handle specify week checkbox change"""
        if self.program:
            self.program.play_control["specify_week"]["enabled"] = (state == Qt.CheckState.Checked.value)
    
    def on_specify_date_changed(self, state):
        """Handle specify date checkbox change"""
        if self.program:
            self.program.play_control["specify_date"]["enabled"] = (state == Qt.CheckState.Checked.value)
    
    def on_frame_menu_selected(self, action):
        """Handle frame menu selection"""
        frame_id = action.data()
        if frame_id is not None:
            frame_text = f"Frame {frame_id}"
            self.frame_input.setText(frame_text)
            if self.program:
                if "frame" not in self.program.properties:
                    self.program.properties["frame"] = {}
                self.program.properties["frame"]["style"] = frame_text
                self.program.properties["frame"]["id"] = frame_id
        else:
            frame_text = action.text()
            self.frame_input.setText(frame_text)
            if self.program:
                if "frame" not in self.program.properties:
                    self.program.properties["frame"] = {}
                self.program.properties["frame"]["style"] = frame_text
    
    def on_bgm_menu_selected(self, action):
        """Handle background music menu selection"""
        if action.text() == "Select File...":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Background Music File", "", 
                "Audio Files (*.mp3 *.wav *.ogg *.m4a);;All Files (*)"
            )
            if file_path and self.program:
                self.bgm_input.setText(file_path)
                if "background_music" not in self.program.properties:
                    self.program.properties["background_music"] = {}
                self.program.properties["background_music"]["file"] = file_path
    
    def on_specified_time_menu_selected(self, action):
        """Handle specified time menu selection"""
        if self.program:
            time_str = action.text()
            self.specified_time_input.setText(time_str)
            if "specified_time" not in self.program.play_control:
                self.program.play_control["specified_time"] = {}
            self.program.play_control["specified_time"]["time"] = time_str
    
    def on_specify_week_menu_selected(self, action):
        """Handle specify week menu selection"""
        if self.program:
            selected_days = []
            for act in self.specify_week_menu.actions():
                if act.isChecked():
                    selected_days.append(act.text())
            self.specify_week_input.setText(", ".join(selected_days) if selected_days else "")
            if "specify_week" not in self.program.play_control:
                self.program.play_control["specify_week"] = {}
            self.program.play_control["specify_week"]["days"] = selected_days
    
    def on_select_date(self):
        """Open date picker dialog"""
        from datetime import datetime
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date")
        layout = QVBoxLayout(dialog)
        
        calendar = QCalendarWidget()
        # Set to current date or previously selected date
        if self.program and self.program.play_control.get("specify_date", {}).get("date"):
            try:
                date_str = self.program.play_control["specify_date"]["date"]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                calendar.setSelectedDate(date_obj)
            except:
                pass
        
        layout.addWidget(calendar)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            selected_date = calendar.selectedDate().toPython()
            date_str = selected_date.strftime("%Y-%m-%d")
            self.specify_date_input.setText(date_str)
            if self.program:
                if "specify_date" not in self.program.play_control:
                    self.program.play_control["specify_date"] = {}
                self.program.play_control["specify_date"]["date"] = date_str
    
    def on_specify_date_menu_selected(self, action):
        """Handle specify date menu selection"""
        if action.text() == "Select Date...":
            self.on_select_date()
        elif self.program:
            date_text = action.text()
            self.specify_date_input.setText(date_text)
            if "specify_date" not in self.program.play_control:
                self.program.play_control["specify_date"] = {}
            self.program.play_control["specify_date"]["date"] = date_text

