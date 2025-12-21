from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QCheckBox, QSpinBox, QSlider, QTableWidget, QTableWidgetItem, QHeaderView,
    QTimeEdit, QMessageBox, QFormLayout
)
from PyQt5.QtCore import Qt, QTime, pyqtSignal
from typing import Optional, Dict, Any
from controllers.huidu import HuiduController
from utils.logger import get_logger

logger = get_logger(__name__)

TABLE_STYLE = """
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
    QTableWidget::item:selected:hover {
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
    QTableWidget QHeaderView::section:horizontal {
        background-color: #3B3B3B;
        color: #FFFFFF;
        padding: 8px;
        border: 1px solid #555555;
        border-top: none;
    }
    QTableCornerButton::section {
        background-color: #3B3B3B;
        border: 1px solid #555555;
    }
"""

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
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #555555;
        background-color: #3B3B3B;
        border-radius: 3px;
    }
    QCheckBox::indicator:checked {
        background-color: #4A90E2;
        border: 1px solid #4A90E2;
    }
""" + TABLE_STYLE


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
        
        self.setWindowTitle(f"💡 Brightness Settings" + (f" - {screen_name}" if screen_name else ""))
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        self.setStyleSheet(DIALOG_STYLE)
        
        self.brightness_settings: Dict[str, Any] = {}
        self.huidu_controller = HuiduController()
        
        self.init_ui()
        self.load_from_device()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        current_group = QGroupBox("Current Brightness")
        current_layout = QFormLayout(current_group)
        
        self.current_brightness_label = QLabel("--")
        current_layout.addRow("Brightness Level:", self.current_brightness_label)
        
        layout.addWidget(current_group)
        
        control_group = QGroupBox("Brightness Control")
        control_layout = QVBoxLayout(control_group)
        
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness:"))
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        brightness_layout.addWidget(self.brightness_slider)
        
        self.brightness_value_label = QLabel("100%")
        self.brightness_value_label.setMinimumWidth(50)
        brightness_layout.addWidget(self.brightness_value_label)
        
        control_layout.addLayout(brightness_layout)
        
        time_range_group = QGroupBox("Brightness by Time Range")
        time_range_layout = QVBoxLayout(time_range_group)
        
        self.enable_time_brightness_check = QCheckBox("Enable Time-Based Brightness")
        time_range_layout.addWidget(self.enable_time_brightness_check)
        
        self.brightness_table = QTableWidget()
        self.brightness_table.setColumnCount(4)
        self.brightness_table.setHorizontalHeaderLabels(["From Time", "To Time", "Brightness %", "Enabled"])
        self.brightness_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.brightness_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.brightness_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.brightness_table.verticalHeader().setVisible(False)
        
        self.brightness_table.setRowCount(1)
        self.add_brightness_row(0, QTime(0, 0), QTime(23, 59), 100)
        
        time_range_layout.addWidget(self.brightness_table)
        
        brightness_btn_layout = QHBoxLayout()
        add_brightness_btn = QPushButton("➕ Add Time Range")
        add_brightness_btn.clicked.connect(self.add_brightness_range)
        brightness_btn_layout.addWidget(add_brightness_btn)
        
        remove_brightness_btn = QPushButton("➖ Remove Time Range")
        remove_brightness_btn.clicked.connect(self.remove_brightness_range)
        brightness_btn_layout.addWidget(remove_brightness_btn)
        brightness_btn_layout.addStretch()
        time_range_layout.addLayout(brightness_btn_layout)
        
        control_layout.addWidget(time_range_group)
        
        sensor_group = QGroupBox("Brightness by Sensor")
        sensor_layout = QVBoxLayout(sensor_group)
        
        self.enable_sensor_brightness_check = QCheckBox("Enable Sensor-Based Brightness")
        sensor_layout.addWidget(self.enable_sensor_brightness_check)
        
        sensor_info_layout = QHBoxLayout()
        sensor_info_layout.addWidget(QLabel("Sensor Value:"))
        self.sensor_value_label = QLabel("--")
        sensor_info_layout.addWidget(self.sensor_value_label)
        
        read_sensor_btn = QPushButton("📥 Read Sensor")
        read_sensor_btn.clicked.connect(self.read_sensor_value)
        sensor_info_layout.addWidget(read_sensor_btn)
        sensor_info_layout.addStretch()
        sensor_layout.addLayout(sensor_info_layout)
        
        sensor_config_layout = QFormLayout()
        self.sensor_min_brightness = QSpinBox()
        self.sensor_min_brightness.setMinimum(0)
        self.sensor_min_brightness.setMaximum(100)
        self.sensor_min_brightness.setValue(20)
        self.sensor_min_brightness.setSuffix("%")
        sensor_config_layout.addRow("Min Brightness:", self.sensor_min_brightness)
        
        self.sensor_max_brightness = QSpinBox()
        self.sensor_max_brightness.setMinimum(0)
        self.sensor_max_brightness.setMaximum(100)
        self.sensor_max_brightness.setValue(100)
        self.sensor_max_brightness.setSuffix("%")
        sensor_config_layout.addRow("Max Brightness:", self.sensor_max_brightness)
        
        sensor_layout.addLayout(sensor_config_layout)
        control_layout.addWidget(sensor_group)
        
        layout.addWidget(control_group)
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save & Send")
        save_btn.clicked.connect(self.save_and_send)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def add_brightness_row(self, row: int, from_time: QTime, to_time: QTime, brightness: int):
        from_time_edit = QTimeEdit()
        from_time_edit.setTime(from_time)
        from_time_edit.setDisplayFormat("HH:mm")
        self.brightness_table.setCellWidget(row, 0, from_time_edit)
        
        to_time_edit = QTimeEdit()
        to_time_edit.setTime(to_time)
        to_time_edit.setDisplayFormat("HH:mm")
        self.brightness_table.setCellWidget(row, 1, to_time_edit)
        
        brightness_spin = QSpinBox()
        brightness_spin.setMinimum(0)
        brightness_spin.setMaximum(100)
        brightness_spin.setValue(brightness)
        brightness_spin.setSuffix("%")
        self.brightness_table.setCellWidget(row, 2, brightness_spin)
        
        enabled_check = QCheckBox()
        enabled_check.setChecked(True)
        self.brightness_table.setCellWidget(row, 3, enabled_check)
    
    def add_brightness_range(self):
        row = self.brightness_table.rowCount()
        self.brightness_table.insertRow(row)
        self.add_brightness_row(row, QTime(0, 0), QTime(23, 59), 100)
    
    def remove_brightness_range(self):
        current_row = self.brightness_table.currentRow()
        if current_row >= 0 and self.brightness_table.rowCount() > 1:
            self.brightness_table.removeRow(current_row)
        elif current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a row to remove.")
    
    def on_brightness_changed(self, value: int):
        self.brightness_value_label.setText(f"{value}%")
    
    def read_sensor_value(self):
        try:
            if not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            property_keys = ["luminance", "luminance.mode"]
            response = self.huidu_controller.get_device_property([self.controller_id])
            
            if response.get("message") == "ok" and response.get("data"):
                device_data_list = response.get("data", [])
                if device_data_list and len(device_data_list) > 0:
                    device_data = device_data_list[0].get("data", {})
                    sensor_value = device_data.get("luminance", "")
                    if sensor_value:
                        self.sensor_value_label.setText(str(sensor_value))
                        QMessageBox.information(self, "Success", f"Sensor value read: {sensor_value}")
                    else:
                        QMessageBox.warning(self, "No Sensor", "No sensor value available from controller.")
        except Exception as e:
            logger.error(f"Error reading sensor value: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error reading sensor value: {str(e)}")
    
    def load_from_device(self):
        try:
            if not self.controller_id:
                return
            
            property_keys = ["luminance", "luminance.mode"]
            response = self.huidu_controller.get_device_property([self.controller_id])
            
            if response.get("message") == "ok" and response.get("data"):
                device_data_list = response.get("data", [])
                if device_data_list and len(device_data_list) > 0:
                    device_data = device_data_list[0].get("data", {})
                    
                    luminance = device_data.get("luminance", "")
                    if luminance:
                        try:
                            brightness_val = int(luminance)
                            self.brightness_slider.setValue(brightness_val)
                            self.brightness_value_label.setText(f"{brightness_val}%")
                            self.current_brightness_label.setText(f"{brightness_val}%")
                        except (ValueError, TypeError):
                            pass
                    
                    logger.info(f"Loaded brightness settings from device: {device_data}")
        except Exception as e:
            logger.error(f"Error loading brightness settings from device: {e}", exc_info=True)
    
    def get_brightness_settings(self) -> Dict:
        settings = {
            "current": self.brightness_slider.value(),
            "time_ranges": [],
            "sensor": {
                "enabled": self.enable_sensor_brightness_check.isChecked(),
                "min_brightness": self.sensor_min_brightness.value(),
                "max_brightness": self.sensor_max_brightness.value()
            }
        }
        
        if self.enable_time_brightness_check.isChecked():
            for i in range(self.brightness_table.rowCount()):
                from_widget = self.brightness_table.cellWidget(i, 0)
                to_widget = self.brightness_table.cellWidget(i, 1)
                brightness_widget = self.brightness_table.cellWidget(i, 2)
                enabled_widget = self.brightness_table.cellWidget(i, 3)
                
                if from_widget and to_widget and brightness_widget and enabled_widget:
                    if enabled_widget.isChecked():
                        time_ranges = settings.get("time_ranges", [])
                        if not isinstance(time_ranges, list):
                            time_ranges = []
                        time_ranges.append({
                            "from": from_widget.time().toString("HH:mm"),
                            "to": to_widget.time().toString("HH:mm"),
                            "brightness": brightness_widget.value()
                        })
                        settings["time_ranges"] = time_ranges
        
        return settings
    
    def save_and_send(self):
        try:
            if not self.controller_id:
                QMessageBox.warning(self, "No Controller", "No controller connected.")
                return
            
            brightness = self.brightness_slider.value()
            
            properties = {
                "luminance": str(brightness)
            }
            
            if self.enable_time_brightness_check.isChecked():
                properties["luminance.mode"] = "time"
            elif self.enable_sensor_brightness_check.isChecked():
                properties["luminance.mode"] = "sensor"
            else:
                properties["luminance.mode"] = "manual"
            
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

