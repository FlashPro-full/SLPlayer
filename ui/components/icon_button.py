"""
Reusable icon button component
"""
from PyQt6.QtWidgets import QToolButton
from PyQt6.QtCore import Qt, pyqtSignal


class IconButton(QToolButton):
    """Reusable icon button with consistent styling"""
    
    clicked = pyqtSignal()
    
    def __init__(self, icon_text: str, tooltip: str = "", parent=None):
        super().__init__(parent)
        self.setText(icon_text)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_style()
    
    def apply_style(self):
        """Apply consistent button styling"""
        self.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 4px;
                font-size: 14px;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #E0E0E0;
            }
            QToolButton:pressed {
                background-color: #BDBDBD;
            }
        """)

