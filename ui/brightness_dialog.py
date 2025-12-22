from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QCheckBox, QSpinBox, QSlider, QTableWidget, QTableWidgetItem, QHeaderView,
    QTimeEdit, QMessageBox, QFormLayout, QComboBox, QRadioButton, QButtonGroup,
    QWidget, QFrame
)
from PyQt5.QtCore import Qt, QTime, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from typing import Optional, Dict, Any
from controllers.huidu import HuiduController
from utils.logger import get_logger

logger = get_logger(__name__)

class RangeSlider(QWidget):
    valueChanged = pyqtSignal(int, int)
    
    def __init__(self, min_val=0, max_val=100, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.min_handle = min_val
        self.max_handle = max_val
        self.handle_size = 12
        self.dragging = None
        self.setMinimumHeight(30)
        self.setMinimumWidth(200)
    
    def setRange(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val
        self.min_handle = min(self.min_handle, max_val)
        self.max_handle = max(self.max_handle, min_val)
        self.update()
    
    def setValues(self, min_val, max_val):
        self.min_handle = max(self.min_val, min(self.max_val, min_val))
        self.max_handle = min(self.max_val, max(self.min_val, max_val))
        if self.min_handle > self.max_handle:
            self.min_handle, self.max_handle = self.max_handle, self.min_handle
        self.update()
        self.valueChanged.emit(self.min_handle, self.max_handle)
    
    def getValues(self):
        return (self.min_handle, self.max_handle)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        groove_height = 6
        groove_y = (height - groove_height) // 2
        
        groove_rect = QRect(0, groove_y, width, groove_height)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#555555")))
        painter.drawRoundedRect(groove_rect, 3, 3)
        
        if self.max_handle > self.min_handle:
            active_rect = QRect(
                int((self.min_handle - self.min_val) / (self.max_val - self.min_val) * width),
                groove_y,
                int((self.max_handle - self.min_handle) / (self.max_val - self.min_val) * width),
                groove_height
            )
            painter.setBrush(QBrush(QColor("#4A90E2")))
            painter.drawRoundedRect(active_rect, 3, 3)
        
        handle_radius = self.handle_size // 2
        min_x = int((self.min_handle - self.min_val) / (self.max_val - self.min_val) * width)
        max_x = int((self.max_handle - self.min_val) / (self.max_val - self.min_val) * width)
        
        painter.setBrush(QBrush(QColor("#4A90E2")))
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.drawEllipse(min_x - handle_radius, height // 2 - handle_radius, self.handle_size, self.handle_size)
        painter.drawEllipse(max_x - handle_radius, height // 2 - handle_radius, self.handle_size, self.handle_size)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            width = self.width()
            handle_radius = self.handle_size // 2
            min_x = int((self.min_handle - self.min_val) / (self.max_val - self.min_val) * width)
            max_x = int((self.max_handle - self.min_val) / (self.max_val - self.min_val) * width)
            
            min_dist = abs(event.x() - min_x)
            max_dist = abs(event.x() - max_x)
            
            if min_dist < max_dist and min_dist < handle_radius * 3:
                self.dragging = "min"
            elif max_dist < handle_radius * 3:
                self.dragging = "max"
            else:
                self.dragging = None
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            width = self.width()
            pos = max(0, min(width, event.x()))
            value = int(self.min_val + (pos / width) * (self.max_val - self.min_val))
            
            if self.dragging == "min":
                self.min_handle = max(self.min_val, min(value, self.max_handle))
            elif self.dragging == "max":
                self.max_handle = min(self.max_val, max(value, self.min_handle))
            
            self.update()
            self.valueChanged.emit(self.min_handle, self.max_handle)
    
    def mouseReleaseEvent(self, event):
        self.dragging = None

DIALOG_STYLE = """
    QDialog {
        background-color: #2B2B2B;
    }
    QLabel {
        color: #FFFFFF;
    }
    QPushButton {
        padding: 8px 20px;
        border: none;
        border-radius: 4px;
        font-size: 11pt;
        background-color: #4A90E2;
        color: #FFFFFF;
    }
    QPushButton:hover {
        background-color: #5AA0F2;
    }
    QPushButton:pressed {
        background-color: #3A80D2;
    }
    QPushButton:disabled {
        background-color: #555555;
        color: #888888;
    }
    QGroupBox {
        border: 1px solid #555555;
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
        color: #FFFFFF;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: #FFFFFF;
    }
    QComboBox {
        background-color: #3B3B3B;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
        color: #FFFFFF;
    }
    QComboBox:hover {
        border: 1px solid #4A90E2;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid #FFFFFF;
        margin-right: 5px;
    }
    QComboBox QAbstractItemView {
        background-color: #3B3B3B;
        border: 1px solid #555555;
        color: #FFFFFF;
        selection-background-color: #2A60B2;
    }
    QSlider::groove:horizontal {
        background-color: #555555;
        height: 6px;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background-color: #4A90E2;
        width: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }
    QSlider::handle:horizontal:hover {
        background-color: #5AA0F2;
    }
    QSpinBox {
        background-color: #3B3B3B;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
        color: #FFFFFF;
    }
    QSpinBox:hover {
        border: 1px solid #4A90E2;
    }
    QTimeEdit {
        background-color: #3B3B3B;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
        color: #FFFFFF;
    }
    QTimeEdit:hover {
        border: 1px solid #4A90E2;
    }
    QCheckBox {
        color: #FFFFFF;
    }
    QRadioButton {
        color: #FFFFFF;
    }
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #555555;
        border-radius: 9px;
        background-color: #3B3B3B;
    }
    QRadioButton::indicator:checked {
        background-color: #4A90E2;
        border: 2px solid #4A90E2;
    }
    QTableWidget {
        background-color: #2B2B2B;
        border: 1px solid #555555;
        color: #FFFFFF;
        gridline-color: #555555;
    }
    QTableWidget::item {
        color: #FFFFFF;
        border-bottom: 1px solid #555555;
    }
    QTableWidget::item:hover {
        background-color: #2A60B2;
        border: 1px solid #4A90E2;
        outline: none;
    }
    QTableWidget::item:selected {
        background-color: #2A60B2;
        border: 1px solid #4A90E2;
        outline: none;
    }
    QHeaderView {
        background-color: #3B3B3B;
    }
    QHeaderView::section {
        background-color: #3B3B3B;
        color: #FFFFFF;
        padding: 8px;
        border: 1px solid #555555;
    }
"""


class BrightnessDialog(QDialog):
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, controller=None, screen_name: Optional[str] = None):
        super().__init__(parent)
        self.controller = controller
        self.screen_name = screen_name
        self.controller_id = None
        if controller:
            try:
                self.controller_id = controller.get('controller_id') if isinstance(controller, dict) else (controller.get_controller_id() if hasattr(controller, 'get_controller_id') else None)
            except:
                pass
        
        self.setWindowTitle(f"Brightness setting" + (f" - {screen_name}" if screen_name else ""))
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        self.setStyleSheet(DIALOG_STYLE)
        
        self.brightness_settings: Dict[str, Any] = {}
        self.huidu_controller = HuiduController()
        self.schedule_items: list = []
        
        self.init_ui()
        self.load_from_device()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        brightness_group = QGroupBox("Brightness setting")
        brightness_layout = QVBoxLayout(brightness_group)
        
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Default mode", "Custom mode", "Automatic mode"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo, stretch=1)
        brightness_layout.addLayout(mode_layout)
        
        self.automatic_widget = QWidget()
        automatic_layout = QVBoxLayout(self.automatic_widget)
        automatic_layout.setContentsMargins(0, 0, 0, 0)
        
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Sensitivity:"))
        self.sensitivity_group = QButtonGroup(self)
        self.sensitivity_high = QRadioButton("high")
        self.sensitivity_medium = QRadioButton("in")
        self.sensitivity_low = QRadioButton("low")
        self.sensitivity_medium.setChecked(True)
        self.sensitivity_group.addButton(self.sensitivity_high, 0)
        self.sensitivity_group.addButton(self.sensitivity_medium, 1)
        self.sensitivity_group.addButton(self.sensitivity_low, 2)
        sensitivity_layout.addWidget(self.sensitivity_high)
        sensitivity_layout.addWidget(self.sensitivity_medium)
        sensitivity_layout.addWidget(self.sensitivity_low)
        sensitivity_layout.addStretch()
        automatic_layout.addLayout(sensitivity_layout)
        
        testing_cycle_layout = QHBoxLayout()
        testing_cycle_layout.addWidget(QLabel("Testing cycle:"))
        self.testing_cycle_spin = QSpinBox()
        self.testing_cycle_spin.setMinimum(1)
        self.testing_cycle_spin.setMaximum(3600)
        self.testing_cycle_spin.setValue(1)
        self.testing_cycle_spin.setSuffix("S")
        testing_cycle_layout.addWidget(self.testing_cycle_spin)
        testing_cycle_layout.addStretch()
        automatic_layout.addLayout(testing_cycle_layout)
        
        read_count_layout = QHBoxLayout()
        read_count_layout.addWidget(QLabel("Read Count:"))
        self.read_count_spin = QSpinBox()
        self.read_count_spin.setMinimum(1)
        self.read_count_spin.setMaximum(100)
        self.read_count_spin.setValue(1)
        read_count_layout.addWidget(self.read_count_spin)
        read_count_layout.addStretch()
        automatic_layout.addLayout(read_count_layout)
        
        brightness_range_layout = QHBoxLayout()
        brightness_range_layout.addWidget(QLabel("Brightness range:"))
        self.brightness_range_slider = RangeSlider(1, 100)
        self.brightness_range_slider.setValues(1, 100)
        self.brightness_range_slider.valueChanged.connect(self.on_brightness_range_changed)
        brightness_range_layout.addWidget(self.brightness_range_slider, stretch=1)
        self.brightness_range_label = QLabel("1% - 100%")
        self.brightness_range_label.setMinimumWidth(100)
        brightness_range_layout.addWidget(self.brightness_range_label)
        automatic_layout.addLayout(brightness_range_layout)
        
        monitoring_interval_layout = QHBoxLayout()
        monitoring_interval_layout.addWidget(QLabel("Brightness monitoring interval:"))
        self.monitoring_interval_slider = RangeSlider(1000, 20000)
        self.monitoring_interval_slider.setValues(3400, 14000)
        self.monitoring_interval_slider.valueChanged.connect(self.on_monitoring_interval_changed)
        monitoring_interval_layout.addWidget(self.monitoring_interval_slider, stretch=1)
        self.monitoring_interval_label = QLabel("3400 - 14000")
        self.monitoring_interval_label.setMinimumWidth(120)
        monitoring_interval_layout.addWidget(self.monitoring_interval_label)
        automatic_layout.addLayout(monitoring_interval_layout)
        
        brightness_layout.addWidget(self.automatic_widget)
        
        self.custom_widget = QWidget()
        custom_layout = QVBoxLayout(self.custom_widget)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        
        self.schedule_container = QWidget()
        schedule_layout = QVBoxLayout(self.schedule_container)
        schedule_layout.setContentsMargins(0, 0, 0, 0)
        schedule_layout.setSpacing(10)
        custom_layout.addWidget(self.schedule_container)
        
        add_btn_layout = QHBoxLayout()
        add_btn_layout.addStretch()
        add_schedule_btn = QPushButton("+")
        add_schedule_btn.setFixedSize(30, 30)
        add_schedule_btn.clicked.connect(self.add_schedule_item)
        add_btn_layout.addWidget(add_schedule_btn)
        custom_layout.addLayout(add_btn_layout)
        
        brightness_layout.addWidget(self.custom_widget)
        
        self.default_widget = QWidget()
        default_layout = QHBoxLayout(self.default_widget)
        default_layout.setContentsMargins(0, 0, 0, 0)
        default_layout.addWidget(QLabel("Brightness:"))
        self.default_brightness_slider = QSlider(Qt.Horizontal)
        self.default_brightness_slider.setMinimum(0)
        self.default_brightness_slider.setMaximum(100)
        self.default_brightness_slider.setValue(100)
        self.default_brightness_slider.valueChanged.connect(self.on_default_brightness_changed)
        default_layout.addWidget(self.default_brightness_slider)
        self.default_brightness_label = QLabel("100%")
        self.default_brightness_label.setMinimumWidth(50)
        default_layout.addWidget(self.default_brightness_label)
        
        brightness_layout.addWidget(self.default_widget)
        
        layout.addWidget(brightness_group)
        
        self.onset_time_group = QGroupBox("Onset time")
        onset_time_layout = QVBoxLayout(self.onset_time_group)
        self.onset_time_label = QLabel("")
        onset_time_layout.addWidget(self.onset_time_label)
        layout.addWidget(self.onset_time_group)
        
        self.on_mode_changed("Default mode")
        
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("OK")
        save_btn.clicked.connect(self.save_and_send)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def on_mode_changed(self, mode: str):
        self.automatic_widget.setVisible(mode == "Automatic mode")
        self.custom_widget.setVisible(mode == "Custom mode")
        self.default_widget.setVisible(mode == "Default mode")
        self.onset_time_group.setVisible(mode == "Custom mode")
        if mode == "Custom mode" and not self.schedule_items:
            self.add_schedule_item("08:00:00", 100)
    
    def on_brightness_range_changed(self, min_val, max_val):
        self.brightness_range_label.setText(f"{min_val}% - {max_val}%")
    
    def on_monitoring_interval_changed(self, min_val, max_val):
        self.monitoring_interval_label.setText(f"{min_val} - {max_val}")
    
    def on_default_brightness_changed(self, value: int):
        self.default_brightness_label.setText(f"{value}%")
    
    def add_schedule_item(self, time_str="08:00:00", brightness=100):
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        item_layout.addWidget(checkbox)
        
        time_edit = QTimeEdit()
        time_parts = time_str.split(":")
        if len(time_parts) == 3:
            time_edit.setTime(QTime(int(time_parts[0]), int(time_parts[1]), int(time_parts[2])))
        time_edit.setDisplayFormat("HH:mm:ss")
        item_layout.addWidget(time_edit)
        
        brightness_label = QLabel(f"{brightness}%")
        brightness_label.setMinimumWidth(50)
        
        brightness_slider = QSlider(Qt.Horizontal)
        brightness_slider.setMinimum(0)
        brightness_slider.setMaximum(100)
        brightness_slider.setValue(brightness)
        def on_brightness_changed(v):
            brightness_label.setText(f"{v}%")
            self.update_onset_time()
        brightness_slider.valueChanged.connect(on_brightness_changed)
        item_layout.addWidget(brightness_slider, stretch=1)
        item_layout.addWidget(brightness_label)
        
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(30, 30)
        delete_btn.clicked.connect(lambda: self.remove_schedule_item(item_widget))
        item_layout.addWidget(delete_btn)
        
        checkbox.toggled.connect(self.update_onset_time)
        time_edit.timeChanged.connect(self.update_onset_time)
        
        self.schedule_items.append({
            "widget": item_widget,
            "checkbox": checkbox,
            "time_edit": time_edit,
            "slider": brightness_slider,
            "label": brightness_label
        })
        
        schedule_layout = self.schedule_container.layout()
        schedule_layout.addWidget(item_widget)
        
        self.update_onset_time()
    
    def remove_schedule_item(self, item_widget):
        for item in self.schedule_items[:]:
            if item["widget"] == item_widget:
                schedule_layout = self.schedule_container.layout()
                schedule_layout.removeWidget(item_widget)
                item_widget.deleteLater()
                self.schedule_items.remove(item)
                break
        self.update_onset_time()
    
    def update_onset_time(self):
        if not self.schedule_items:
            self.onset_time_label.setText("")
            return
        
        sorted_items = sorted(
            [item for item in self.schedule_items if item["checkbox"].isChecked()],
            key=lambda x: x["time_edit"].time().msecsSinceStartOfDay()
        )
        
        if not sorted_items:
            self.onset_time_label.setText("")
            return
        
        lines = []
        for i, item in enumerate(sorted_items):
            time_str = item["time_edit"].time().toString("HH:mm:ss")
            brightness = item["slider"].value()
            
            next_item = sorted_items[(i + 1) % len(sorted_items)]
            next_time_str = next_item["time_edit"].time().toString("HH:mm:ss")
            
            lines.append(f"{i+1}. {time_str} ~ {next_time_str} : {brightness}%")
        
        self.onset_time_label.setText("\n".join(lines))
    
    def load_from_device(self):
        try:
            if not self.controller_id:
                return
            
            property_keys = ["luminance", "luminance.mode"]
            response = self.huidu_controller.get_device_property([self.controller_id], property_keys)
            
            if response.get("message") == "ok" and response.get("data"):
                device_data_list = response.get("data", [])
                if device_data_list and len(device_data_list) > 0:
                    device_data = device_data_list[0].get("data", {})
                    
                    mode = device_data.get("luminance.mode", "manual")
                    if mode == "automatic":
                        self.mode_combo.setCurrentText("Automatic mode")
                    elif mode == "time" or mode == "custom":
                        self.mode_combo.setCurrentText("Custom mode")
                    else:
                        self.mode_combo.setCurrentText("Default mode")
                    
                    luminance = device_data.get("luminance", "")
                    if luminance:
                        try:
                            brightness_val = int(luminance)
                            self.default_brightness_slider.setValue(brightness_val)
                            self.default_brightness_label.setText(f"{brightness_val}%")
                        except (ValueError, TypeError):
                            pass
                    
                    logger.info(f"Loaded brightness settings from device: {device_data}")
        except Exception as e:
            logger.error(f"Error loading brightness settings from device: {e}", exc_info=True)
    
    def save_and_send(self):
        try:
            if not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            properties = {}
            mode = self.mode_combo.currentText()
            
            if mode == "Default mode":
                properties["luminance"] = str(self.default_brightness_slider.value())
                properties["luminance.mode"] = "manual"
            elif mode == "Automatic mode":
                properties["luminance.mode"] = "automatic"
                sensitivity_map = {0: "high", 1: "in", 2: "low"}
                properties["luminance.sensitivity"] = sensitivity_map.get(self.sensitivity_group.checkedId(), "in")
                properties["luminance.testingCycle"] = str(self.testing_cycle_spin.value())
                properties["luminance.readCount"] = str(self.read_count_spin.value())
                min_bright, max_bright = self.brightness_range_slider.getValues()
                properties["luminance.brightnessRange"] = f"{min_bright}-{max_bright}"
                min_interval, max_interval = self.monitoring_interval_slider.getValues()
                properties["luminance.monitoringInterval"] = f"{min_interval}-{max_interval}"
            elif mode == "Custom mode":
                properties["luminance.mode"] = "time"
                schedule_data = []
                sorted_items = sorted(
                    [item for item in self.schedule_items if item["checkbox"].isChecked()],
                    key=lambda x: x["time_edit"].time().msecsSinceStartOfDay()
                )
                for item in sorted_items:
                    time_str = item["time_edit"].time().toString("HH:mm:ss")
                    brightness = item["slider"].value()
                    schedule_data.append({"time": time_str, "brightness": brightness})
                if schedule_data:
                    properties["luminance.schedule"] = str(schedule_data)
            
            response = self.huidu_controller.set_device_property(properties, [self.controller_id])
            
            if response.get("message") == "ok":
                QMessageBox.information(self, "Success", "Brightness settings saved and sent to controller.")
                self.settings_changed.emit(properties)
                self.accept()
            else:
                error_msg = response.get("data", "Unknown error")
                QMessageBox.warning(self, "Failed", f"Failed to save brightness settings: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")
