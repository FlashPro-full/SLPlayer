from typing import Optional
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from config.i18n import tr


class UIService:
    
    @staticmethod
    def show_warning(parent: Optional[QWidget], title: str, message: str):
        QMessageBox.warning(parent, title, message)
    
    @staticmethod
    def show_information(parent: Optional[QWidget], title: str, message: str):
        QMessageBox.information(parent, title, message)
    
    @staticmethod
    def show_error(parent: Optional[QWidget], title: str, message: str):
        QMessageBox.critical(parent, title, message)
    
    @staticmethod
    def show_question(parent: Optional[QWidget], title: str, message: str, 
                     default_button: QMessageBox.StandardButton = QMessageBox.No) -> QMessageBox.StandardButton:
        return QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            default_button
        )
    
    @staticmethod
    def select_directory(parent: Optional[QWidget], title: str, start_path: str = "") -> Optional[str]:
        path = QFileDialog.getExistingDirectory(
            parent,
            title,
            start_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        return path if path else None
    
    @staticmethod
    def select_file(parent: Optional[QWidget], title: str, filter: str = "", 
                   start_path: str = "") -> Optional[str]:
        path, _ = QFileDialog.getOpenFileName(
            parent,
            title,
            start_path,
            filter
        )
        return path if path else None
    
    @staticmethod
    def save_file(parent: Optional[QWidget], title: str, filter: str = "", 
                 start_path: str = "") -> Optional[str]:
        path, _ = QFileDialog.getSaveFileName(
            parent,
            title,
            start_path,
            filter
        )
        return path if path else None

