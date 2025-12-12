import sys
import atexit
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow
from config.settings import settings
from core.startup_service import StartupService
from utils.logger import get_logger
from utils.icon_manager import IconManager

logger = get_logger(__name__)

def cleanup_api_server():
    """Cleanup function to stop the API server on exit"""
    try:
        from controllers.huidu_sdk import _stop_api_server
        _stop_api_server()
    except Exception as e:
        logger.error(f"Error stopping API server during cleanup: {e}")

atexit.register(cleanup_api_server)


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
        
        if getattr(sys, 'frozen', False):
            base_path = Path(sys.executable).parent
        else:
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
        
        from ui.device_selection_dialog import DeviceSelectionDialog
        device_dialog = DeviceSelectionDialog()
        device_dialog.show()
        
        window = MainWindow()
        window.resize(window_width, window_height)
        window.move(window_x, window_y)
        window.hide()
        
        device_dialog.set_main_window(window)
        
        def on_device_selected(ip, port, controller_type, device_id):
            try:
                success = window.controller_service.connect_to_controller(
                    ip,
                    port,
                    controller_type
                )
                if success:
                    logger.info(f"Connected to device {device_id} at {ip}:{port}")
                    
                    from core.controller_database import get_controller_database
                    db = get_controller_database()
                    device_info = db.get_controller(device_id)
                    
                    if device_info:
                        width = device_info.get('width')
                        height = device_info.get('height')
                        
                        if not width or not height:
                            display_resolution = device_info.get('display_resolution', '')
                            if display_resolution and 'x' in display_resolution.lower():
                                try:
                                    parts = display_resolution.lower().replace(' ', '').split('x')
                                    if len(parts) == 2:
                                        width = int(parts[0])
                                        height = int(parts[1])
                                except (ValueError, IndexError):
                                    pass
                        
                        if width and height:
                            from core.screen_config import set_screen_config
                            brand = device_info.get('model', '') or controller_type
                            model = device_info.get('model', '') or ''
                            set_screen_config(brand, model, width, height, 0, None)
                            logger.info(f"Set screen resolution from device: {width}x{height}")
                        else:
                            logger.warning(f"Could not extract resolution from device info")
                        
                        reply = QMessageBox.question(
                            window,
                            "Download Program",
                            "Do you want to download a program from the device?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.Yes
                        )
                        
                        download_success = False
                        if reply == QMessageBox.Yes:
                            try:
                                controller = window.controller_service.current_controller
                                if controller:
                                    program_data = controller.download_program()
                                    if program_data and program_data.get('elements'):
                                        from core.program_manager import Program
                                        program = Program()
                                        program.name = program_data.get('name', 'Downloaded Program')
                                        program.width = width or 64
                                        program.height = height or 32
                                        program.elements = program_data.get('elements', [])
                                        program.properties = program_data.get('properties', program.properties)
                                        program.play_mode = program_data.get('play_mode', program.play_mode)
                                        program.play_control = program_data.get('play_control', program.play_control)
                                        
                                        screen_name = window.screen_list_panel.add_new_screen()
                                        if screen_name and hasattr(window.screen_list_panel, 'add_program_to_screen'):
                                            screen = window.screen_manager.get_screen_by_name(screen_name)
                                            if screen:
                                                screen.add_program(program)
                                                window.screen_list_panel.refresh_screens(debounce=False)
                                                download_success = True
                                                logger.info("Program downloaded and loaded successfully")
                                    else:
                                        logger.warning("Downloaded program data is empty or invalid")
                            except Exception as e:
                                logger.error(f"Error downloading program: {e}", exc_info=True)
                                QMessageBox.warning(window, "Download Failed", f"Failed to download program from device:\n{str(e)}")
                        
                        if not download_success:
                            _create_new_screen_with_device_info(window, device_info, width, height, controller_type)
                    else:
                        _create_new_screen_with_device_info(window, {}, None, None, controller_type)
                else:
                    logger.warning(f"Failed to connect to device {device_id} at {ip}:{port}")
            except Exception as e:
                logger.error(f"Error connecting to device: {e}", exc_info=True)
            
            window.show()
            window.raise_()
            window.activateWindow()
        
        def _create_new_screen_with_device_info(window, device_info, width, height, controller_type):
            try:
                from core.screen_config import set_screen_config, get_screen_config
                from core.program_manager import Program
                
                if not width or not height:
                    width = device_info.get('width') or 64
                    height = device_info.get('height') or 32
                    if not width or not height:
                        display_resolution = device_info.get('display_resolution', '')
                        if display_resolution and 'x' in display_resolution.lower():
                            try:
                                parts = display_resolution.lower().replace(' ', '').split('x')
                                if len(parts) == 2:
                                    width = int(parts[0])
                                    height = int(parts[1])
                            except (ValueError, IndexError):
                                pass
                
                brand = device_info.get('model', '') or controller_type
                model = device_info.get('model', '') or ''
                set_screen_config(brand, model, width, height, 0, None)
                
                screen_name = window.screen_list_panel.add_new_screen()
                if screen_name:
                    screen = window.screen_manager.get_screen_by_name(screen_name)
                    if screen:
                        program = window.program_manager.create_program("New Program", width, height)
                        screen.add_program(program)
                        
                        if "screen" not in program.properties:
                            program.properties["screen"] = {}
                        program.properties["screen"]["screen_model"] = model or brand
                        program.properties["screen"]["screen_resolution"] = f"{width}x{height}"
                        
                        from utils.app_data import get_app_data_dir
                        import os
                        save_dir = get_app_data_dir() / "programs"
                        save_dir.mkdir(parents=True, exist_ok=True)
                        program.properties["screen"]["program_file_saving_path"] = str(save_dir)
                        
                        controller = window.controller_service.current_controller
                        if controller and hasattr(controller, 'get_device_info'):
                            try:
                                dev_info = controller.get_device_info()
                                if dev_info:
                                    if "play_control" not in program.properties:
                                        program.properties["play_control"] = {}
                                    play_control = program.play_control
                                    if play_control:
                                        if dev_info.get("play_control"):
                                            sdk_play_control = dev_info.get("play_control")
                                            if sdk_play_control.get("specified_time"):
                                                play_control["specified_time"]["enabled"] = sdk_play_control["specified_time"].get("enabled", False)
                                                play_control["specified_time"]["time"] = sdk_play_control["specified_time"].get("time", "")
                                            if sdk_play_control.get("specify_week"):
                                                play_control["specify_week"]["enabled"] = sdk_play_control["specify_week"].get("enabled", False)
                                                play_control["specify_week"]["days"] = sdk_play_control["specify_week"].get("days", [])
                                            if sdk_play_control.get("specify_date"):
                                                play_control["specify_date"]["enabled"] = sdk_play_control["specify_date"].get("enabled", False)
                                                play_control["specify_date"]["date"] = sdk_play_control["specify_date"].get("date", "")
                            except Exception as e:
                                logger.warning(f"Error loading play control from device: {e}")
                        
                        window.screen_list_panel.refresh_screens(debounce=False)
                        logger.info(f"Created new screen '{screen_name}' with program using device info")
            except Exception as e:
                logger.error(f"Error creating new screen with device info: {e}", exc_info=True)
        
        device_dialog.device_selected.connect(on_device_selected)
        
        window._device_dialog = device_dialog
        
        if soo_file_path:
            logger.info(f"Loading specific .soo file from command-line: {soo_file_path}")
            window.load_soo_file(soo_file_path, clear_existing=True, async_load=True)
        else:
            logger.info("No specific .soo file provided, loading all autosaved files")
            window._load_autosaved_files()
        
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
        except Exception:
            # Last resort error handling - can't show message box if QApplication failed
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

