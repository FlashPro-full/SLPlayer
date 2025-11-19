import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow
from config.settings import settings
from core.startup_service import StartupService
from utils.logger import get_logger
from utils.icon_manager import IconManager

logger = get_logger(__name__)


def main():
    try:
        if "--reset-first-launch" in sys.argv or "--reset-first" in sys.argv:
            settings.set("first_launch_complete", False)
            print("✓ First launch flag has been reset!")
            print("The Network Setup Dialog will appear on next application start.")
            return
        
        skip_license = "--skip-license" in sys.argv or "--skip-lic" in sys.argv
        
        soo_file_path = None
        for arg in sys.argv[1:]:
            if arg.startswith('--'):
                continue
            potential_path = Path(arg)
            if potential_path.suffix.lower() == '.soo':
                if not potential_path.exists():
                    potential_path = potential_path.resolve()
                if potential_path.exists():
                    soo_file_path = str(potential_path.absolute())
                    break
        
        logger.info("Starting SLPlayer application")
        app = QApplication(sys.argv)
        app.setApplicationName("SLPlayer")
        app.setOrganizationName("SLPlayer")
        
        base_path = Path(__file__).parent
        IconManager.setup_application_icon(app, base_path)
        
        window_width = settings.get("window.width", 1400)
        window_height = settings.get("window.height", 900)
        window_x = settings.get("window.x", 100)
        window_y = settings.get("window.y", 100)
        
        first_launch_complete = settings.get("first_launch_complete", False)
        if not first_launch_complete:
            from ui.network_setup_dialog import NetworkSetupDialog
            network_dialog = NetworkSetupDialog()
            network_dialog.exec()
            settings.set("first_launch_complete", True)
            logger.info("First launch network setup completed")
        
        # Initialize controller database with comprehensive research data
        try:
            from core.controller_research_service import ControllerResearchService
            ControllerResearchService.populate_database(force_update=False)
            logger.info("Controller database populated with research data")
        except Exception as e:
            logger.warning(f"Could not populate controller database at startup: {e}")
        
        startup_service = StartupService()
        controller_id, valid_license_found = startup_service.verify_license_at_startup()
        
        if not skip_license and not valid_license_found:
            from ui.login_dialog import LoginDialog
            login_dialog = LoginDialog(controller_id=controller_id)
            
            if not controller_id:
                logger.info("No valid license found - showing license activation dialog for online activation")
            
            dialog_result = login_dialog.exec()
            
            if not dialog_result:
                logger.info("User cancelled license activation - application exit required")
                sys.exit(0)
            
            controller_id = login_dialog.controller_id or controller_id
            
            if not login_dialog.is_license_valid() or (controller_id and not startup_service.check_license_after_activation(controller_id)):
                    sys.exit(1)
        elif valid_license_found:
            logger.info(f"Valid license found for controller: {controller_id} - skipping activation dialog")
        else:
            logger.info("License dialog skipped via command-line argument")
        
        window = MainWindow()
        window.resize(window_width, window_height)
        window.move(window_x, window_y)
        window.show()
        
        # Use async loading for better performance
        if soo_file_path:
            logger.info(f"Loading specific .soo file from command-line: {soo_file_path}")
            window.load_soo_file(soo_file_path, clear_existing=True, async_load=True)
            # Note: File loading happens in background, status checked via signal
        else:
            logger.info("No specific .soo file provided, loading all autosaved files")
            window.load_latest_soo_files_async()
            # Note: File loading happens in background, status checked via signal
        
        IconManager.setup_taskbar_icon(window, base_path)
        
        sys.exit(app.exec())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error starting application: {e}", exc_info=True)
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Fatal Error",
                f"Application failed to start:\n{str(e)}\n\nCheck logs for details."
            )
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

