"""
Reusable form field component
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from typing import Optional


class FormField(QWidget):
    """Reusable form field with label and input"""
    
    def __init__(self, label: str, widget: QWidget, parent=None):
        super().__init__(parent)
        self.label_text = label
        self.input_widget = widget
        self.init_ui()
    
    def init_ui(self):
        """Initialize form field UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        label = QLabel(self.label_text)
        label.setMinimumWidth(100)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(label)
        
        layout.addWidget(self.input_widget, stretch=1)
    
    def get_value(self) -> Any:
        """Get value from input widget"""
        if hasattr(self.input_widget, 'text'):
            return self.input_widget.text()
        elif hasattr(self.input_widget, 'value'):
            return self.input_widget.value()
        elif hasattr(self.input_widget, 'currentText'):
            return self.input_widget.currentText()
        return None
    
    def set_value(self, value: Any):
        """Set value to input widget"""
        if hasattr(self.input_widget, 'setText'):
            self.input_widget.setText(str(value))
        elif hasattr(self.input_widget, 'setValue'):
            self.input_widget.setValue(value)
        elif hasattr(self.input_widget, 'setCurrentText'):
            self.input_widget.setCurrentText(str(value))

