from typing import Optional
from PyQt5.QtWidgets import QMessageBox
from core.program_manager import ProgramManager
from core.screen_manager import ScreenManager
from services.controller_service import ControllerService
from services.ui_service import UIService
from utils.logger import get_logger
from config.i18n import tr

logger = get_logger(__name__)


class ProgramActionService:
    
    def __init__(self, program_manager: ProgramManager, controller_service: ControllerService, 
                 screen_manager: Optional[ScreenManager] = None):
        self.program_manager = program_manager
        self.controller_service = controller_service
        self.screen_manager = screen_manager
    
    def send_program(self, parent_widget=None) -> bool:
        if not self.controller_service.is_connected():
            UIService.show_warning(
                parent_widget,
                tr("action.send"),
                tr("toolbar.send") + "\n\n" + tr("message.no_controller_connected")
            )
            return False
        
        current_program = self.program_manager.current_program
        if not current_program and self.screen_manager:
            if self.screen_manager.current_screen and self.screen_manager.current_screen.programs:
                current_program = self.screen_manager.current_screen.programs[0]
        if not current_program:
            UIService.show_warning(
                parent_widget,
                tr("action.send"),
                tr("message.no_program_selected")
            )
            return False
        
        try:
            result = self.controller_service.send_program(current_program)
            if result:
                program_name = current_program.name if hasattr(current_program, 'name') else "Program"
                UIService.show_information(
                    parent_widget,
                    tr("action.send"),
                    tr("message.program_sent_success").replace("{name}", program_name)
                )
                logger.info(f"Program '{current_program.name}' sent successfully")
            else:
                UIService.show_warning(
                    parent_widget,
                    tr("action.send"),
                    tr("message.program_send_failed")
                )
            return result
        except Exception as e:
            logger.error(f"Error sending program: {e}", exc_info=True)
            UIService.show_error(
                parent_widget,
                tr("action.send"),
                tr("message.program_send_error").replace("{error}", str(e))
            )
            return False
    
    def export_to_usb(self, parent_widget=None) -> bool:
        current_program = self.program_manager.current_program
        if not current_program and self.screen_manager:
            if self.screen_manager.current_screen and self.screen_manager.current_screen.programs:
                current_program = self.screen_manager.current_screen.programs[0]
        if not current_program:
            UIService.show_warning(
                parent_widget,
                tr("action.export_to_usb"),
                tr("message.no_program_selected")
            )
            return False
        
        usb_path = UIService.select_directory(
            parent_widget,
            tr("action.export_to_usb"),
            ""
        )
        
        if not usb_path:
            return False
        
        try:
            result = self.controller_service.export_to_usb(current_program, usb_path)
            if result:
                program_name = current_program.name if hasattr(current_program, 'name') else "Program"
                message = tr("message.program_exported_success").replace("{name}", program_name).replace("{path}", usb_path)
                UIService.show_information(
                    parent_widget,
                    tr("action.export_to_usb"),
                    message
                )
                logger.info(f"Program '{current_program.name}' exported to USB: {usb_path}")
            else:
                UIService.show_warning(
                    parent_widget,
                    tr("action.export_to_usb"),
                    tr("message.program_export_failed")
                )
            return result
        except Exception as e:
            logger.error(f"Error exporting to USB: {e}", exc_info=True)
            UIService.show_error(
                parent_widget,
                tr("action.export_to_usb"),
                tr("message.program_export_error").replace("{error}", str(e))
            )
            return False
    
    def show_insert_instructions(self, parent_widget=None):
        UIService.show_information(
            parent_widget,
            tr("toolbar.insert"),
            tr("message.insert_usb_instructions")
        )
    
    def clear_program(self, parent_widget=None) -> bool:
        current_program = self.program_manager.current_program
        if not current_program and self.screen_manager:
            if self.screen_manager.current_screen and self.screen_manager.current_screen.programs:
                current_program = self.screen_manager.current_screen.programs[0]
        if not current_program:
            UIService.show_warning(
                parent_widget,
                tr("toolbar.clear_tooltip"),
                tr("message.no_program_selected")
            )
            return False
        
        program_name = current_program.name if hasattr(current_program, 'name') else "Program"
        reply = UIService.show_question(
            parent_widget,
            tr("toolbar.clear_tooltip"),
            tr("message.confirm_clear_program").replace("{name}", program_name),
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from datetime import datetime
            current_program.elements = []
            current_program.modified = datetime.now().isoformat()
            logger.info(f"Program '{current_program.name}' cleared")
            return True
        
        return False

