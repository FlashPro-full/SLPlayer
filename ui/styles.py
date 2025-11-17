"""
Centralized styling for pixel-perfect UI/UX
"""
from typing import Dict


class Styles:
    """Centralized style definitions"""
    
    # Color palette
    COLORS = {
        "primary": "#2196F3",
        "primary_dark": "#1976D2",
        "primary_light": "#BBDEFB",
        "secondary": "#FF9800",
        "success": "#4CAF50",
        "error": "#F44336",
        "warning": "#FF9800",
        "background": "#F5F5F5",
        "surface": "#FFFFFF",
        "text_primary": "#212121",
        "text_secondary": "#757575",
        "divider": "#BDBDBD",
        "toolbar_bg": "#D6D6D6",
        "menubar_bg": "#E5E5E5",
    }
    
    # Main window styles
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {COLORS["background"]};
        }}
    """
    
    # Menu bar styles
    MENUBAR = f"""
        QMenuBar {{
            background-color: {COLORS["menubar_bg"]};
            border-bottom: 1px solid {COLORS["divider"]};
            padding: 2px;
        }}
        QMenuBar::item {{
            padding: 4px 8px;
            border-radius: 3px;
        }}
        QMenuBar::item:selected {{
            background-color: {COLORS["background"]};
        }}
        QMenu {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["divider"]};
            padding: 4px;
        }}
        QMenu::item {{
            padding: 6px 24px;
            border-radius: 2px;
        }}
        QMenu::item:selected {{
            background-color: {COLORS["background"]};
        }}
    """
    
    # Toolbar styles
    TOOLBAR = f"""
        QWidget {{
            background-color: {COLORS["toolbar_bg"]};
        }}
        QToolButton {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["divider"]};
            border-radius: 3px;
            padding: 4px 8px;
            margin: 0px;
            font-size: 14px;
        }}
        QToolButton:hover {{
            background-color: {COLORS["background"]};
            border: 1px solid {COLORS["divider"]};
        }}
        QToolButton:pressed {{
            background-color: {COLORS["divider"]};
            color: {COLORS["text_primary"]};
        }}
    """
    
    # Button styles
    BUTTON_PRIMARY = f"""
        QPushButton {{
            background-color: {COLORS["primary"]};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 11pt;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {COLORS["primary_dark"]};
        }}
        QPushButton:pressed {{
            background-color: {COLORS["primary_dark"]};
        }}
        QPushButton:disabled {{
            background-color: {COLORS["divider"]};
            color: {COLORS["text_secondary"]};
        }}
    """
    
    BUTTON_SECONDARY = f"""
        QPushButton {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text_primary"]};
            border: 1px solid {COLORS["divider"]};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 11pt;
        }}
        QPushButton:hover {{
            background-color: {COLORS["background"]};
            border: 1px solid {COLORS["primary"]};
        }}
    """
    
    # Input styles
    INPUT = f"""
        QLineEdit, QSpinBox, QComboBox, QTimeEdit {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["divider"]};
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 11pt;
        }}
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTimeEdit:focus {{
            border: 2px solid {COLORS["primary"]};
        }}
    """
    
    # Group box styles
    GROUPBOX = f"""
        QGroupBox {{
            font-size: 12px;
            font-weight: 600;
            border: none;
            margin-top: 12px;
            padding-top: 8px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 4px;
            color: {COLORS["text_primary"]};
        }}
    """
    
    # Tree widget styles
    TREE_WIDGET = f"""
        QTreeWidget {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["divider"]};
            border-radius: 4px;
            padding: 4px;
        }}
        QTreeWidget::item {{
            padding: 4px;
            border-radius: 2px;
        }}
        QTreeWidget::item:selected {{
            background-color: {COLORS["background"]};
            color: {COLORS["text_primary"]};
        }}
        QTreeWidget::item:hover {{
            background-color: {COLORS["background"]};
        }}
    """
    
    # Status bar styles
    STATUS_BAR = f"""
        QStatusBar {{
            background-color: {COLORS["surface"]};
            border-top: 1px solid {COLORS["divider"]};
            padding: 4px;
        }}
    """
    
    @staticmethod
    def get_style(component: str) -> str:
        """Get style for component"""
        styles = {
            "main_window": Styles.MAIN_WINDOW,
            "menubar": Styles.MENUBAR,
            "toolbar": Styles.TOOLBAR,
            "button_primary": Styles.BUTTON_PRIMARY,
            "button_secondary": Styles.BUTTON_SECONDARY,
            "input": Styles.INPUT,
            "groupbox": Styles.GROUPBOX,
            "tree_widget": Styles.TREE_WIDGET,
            "status_bar": Styles.STATUS_BAR,
        }
        return styles.get(component, "")

