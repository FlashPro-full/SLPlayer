import sys
import atexit
import subprocess
import socket
import os
import time
from pathlib import Path
from datetime import datetime
if sys.platform != "win32":
    import fcntl
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtCore import QByteArray

from config.settings import settings
from utils.logger import get_logger
from utils.icon_manager import IconManager

logger = get_logger(__name__)

_api_server_process = None
_api_server_lock_file = None

def _stop_api_server():
    global _api_server_process, _api_server_lock_file
    if _api_server_process is not None:
        try:
            if _api_server_process.poll() is None:
                _api_server_process.terminate()
                try:
                    _api_server_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    _api_server_process.kill()
                    _api_server_process.wait()
                logger.info("Stopped Huidu API server process")
            _api_server_process = None
        except Exception as e:
            logger.debug(f"Error stopping API server process: {e}")
    
    _kill_existing_processes()
    
    if _api_server_lock_file:
        try:
            _api_server_lock_file.close()
            if getattr(sys, 'frozen', False):
                base_path = Path(sys.executable).parent
            else:
                base_path = Path(__file__).parent
            lock_file_path = base_path / ".huidu_api_server.lock"
            if lock_file_path.exists():
                lock_file_path.unlink()
        except Exception:
            pass
        _api_server_lock_file = None
    
    if sys.platform == "win32":
        try:
            import ctypes
            mutex_name = "Global\\HuiduAPIServerMutex"
            mutex = ctypes.windll.kernel32.OpenMutexW(0x001F03FF, False, mutex_name)
            if mutex:
                ctypes.windll.kernel32.CloseHandle(mutex)
        except Exception:
            pass

atexit.register(_stop_api_server)

def _is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def _kill_existing_processes():
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/IM", "cn.huidu.device.api.exe"],
                capture_output=True,
                timeout=3
            )
            time.sleep(0.5)
        except Exception:
            pass

def _start_api_server():
    global _api_server_process, _api_server_lock_file
    
    _kill_existing_processes()
    
    if _is_port_open("127.0.0.1", 30080, timeout=0.5):
        logger.info("Huidu API server port 30080 is already in use, API server is running")
        return
    
    if sys.platform == "win32":
        try:
            import ctypes
            
            mutex_name = "Global\\HuiduAPIServerMutex"
            mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
            last_error = ctypes.windll.kernel32.GetLastError()
            
            if last_error == 183:
                logger.info("Huidu API server mutex already exists, but port is not open - cleaning up and starting")
                try:
                    ctypes.windll.kernel32.CloseHandle(mutex)
                except Exception:
                    pass
                _kill_existing_processes()
                time.sleep(0.5)
            
            if not mutex:
                logger.warning("Failed to create mutex, continuing anyway")
        except Exception as e:
            logger.debug(f"Could not create mutex: {e}")
    
    if _api_server_process is not None:
        if _api_server_process.poll() is None:
            logger.info("Huidu API server process is already running")
            return
        else:
            _api_server_process = None
    
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent
    
    lock_file_path = base_path / ".huidu_api_server.lock"
    
    try:
        if sys.platform == "win32":
            if lock_file_path.exists():
                try:
                    with open(lock_file_path, 'r') as f:
                        old_pid = f.read().strip()
                        try:
                            os.kill(int(old_pid), 0)
                            logger.info("Another process has the API server lock, skipping start")
                            return
                        except (OSError, ValueError):
                            pass
                except Exception:
                    pass
            _api_server_lock_file = open(lock_file_path, 'w')
            try:
                _api_server_lock_file.write(str(os.getpid()))
                _api_server_lock_file.flush()
            except Exception:
                pass
        else:
            _api_server_lock_file = open(lock_file_path, 'w')
            fcntl.flock(_api_server_lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            _api_server_lock_file.write(str(os.getpid()))
            _api_server_lock_file.flush()
    except (IOError, OSError):
        logger.info("Another process has the API server lock, skipping start")
        return
    
    api_exe_path = base_path / "publish" / "huidu_sdk" / "cn.huidu.device.api.exe"
    if not api_exe_path.exists():
        api_exe_path = base_path / "_internal" / "publish" / "huidu_sdk" / "cn.huidu.device.api.exe"
    
    if not api_exe_path.exists():
        logger.error(f"Huidu API server executable not found. Checked: {base_path / 'publish' / 'huidu_sdk' / 'cn.huidu.device.api.exe'} and {base_path / '_internal' / 'publish' / 'huidu_sdk' / 'cn.huidu.device.api.exe'}")
        if _api_server_lock_file:
            try:
                _api_server_lock_file.close()
                if lock_file_path.exists():
                    lock_file_path.unlink()
            except Exception:
                pass
            _api_server_lock_file = None
        return
    
    try:
        log_file_path = None
        try:
            log_file_path = api_exe_path.parent / "logs" / f"HDAPI_{datetime.now().strftime('%Y%m%d')}.log"
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            log_file = open(log_file_path, 'a')
        except Exception as e:
            logger.debug(f"Could not open log file: {e}")
            log_file = subprocess.DEVNULL
            log_file_path = None
        
        if sys.platform == "win32":
            if getattr(sys, 'frozen', False):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                _api_server_process = subprocess.Popen(
                    [str(api_exe_path)],
                    cwd=str(api_exe_path.parent),
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    startupinfo=startupinfo
                )
            else:
                _api_server_process = subprocess.Popen(
                    [str(api_exe_path)],
                    cwd=str(api_exe_path.parent),
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
        else:
            _api_server_process = subprocess.Popen(
                [str(api_exe_path)],
                cwd=str(api_exe_path.parent),
                stdout=log_file,
                stderr=subprocess.STDOUT
            )
        logger.info(f"Started Huidu API server: {api_exe_path} (PID: {_api_server_process.pid})")
        
        max_wait_time = 5.0
        check_interval = 0.5
        waited = 0.0
        port_open = False
        
        while waited < max_wait_time:
            if _api_server_process.poll() is not None:
                logger.error(f"Huidu API server process exited with code {_api_server_process.returncode}. Check log file: {log_file_path}")
                _api_server_process = None
                if _api_server_lock_file:
                    try:
                        _api_server_lock_file.close()
                        if lock_file_path.exists():
                            lock_file_path.unlink()
                    except Exception:
                        pass
                    _api_server_lock_file = None
                return
            
            if _is_port_open("127.0.0.1", 30080, timeout=0.3):
                port_open = True
                logger.info(f"Huidu API server is ready on port 30080 (waited {waited:.1f}s)")
                break
            
            time.sleep(check_interval)
            waited += check_interval
        
        if not port_open:
            log_msg = f" Check log file: {log_file_path}" if log_file_path else ""
            logger.warning(f"Huidu API server started but port 30080 is not open after {max_wait_time}s.{log_msg}")
            if _api_server_process and _api_server_process.poll() is None:
                logger.warning(f"Process is still running (PID: {_api_server_process.pid}) but port is not accessible")
    except Exception as e:
        logger.error(f"Failed to start Huidu API server: {e}", exc_info=True)
        _api_server_process = None
        if _api_server_lock_file:
            try:
                _api_server_lock_file.close()
                if lock_file_path.exists():
                    lock_file_path.unlink()
            except Exception:
                pass
            _api_server_lock_file = None
        if _api_server_lock_file:
            try:
                _api_server_lock_file.close()
                if lock_file_path.exists():
                    lock_file_path.unlink()
            except Exception:
                pass
            _api_server_lock_file = None

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
        
        app = QApplication(sys.argv)
        app.setApplicationName("SLPlayer")
        app.setOrganizationName("SLPlayer")
        
        logger.info("Checking for existing application instance")
        server_name = "SLPlayer_SingleInstance_Server"
        socket = QLocalSocket()
        socket.connectToServer(server_name)
        
        if socket.waitForConnected(500):
            logger.info("Another instance detected, activating existing instance and exiting")
            socket.write(QByteArray(b"activate"))
            socket.flush()
            socket.waitForBytesWritten(1000)
            socket.close()
            sys.exit(0)
        
        logger.info("No existing instance found, starting new instance")
        local_server = QLocalServer()
        if not local_server.listen(server_name):
            logger.debug("Failed to listen on server name, attempting cleanup")
            old_server = QLocalServer()
            if old_server.listen(server_name):
                old_server.close()
                logger.debug("Cleaned up old server instance")
            if not local_server.listen(server_name):
                logger.error("Failed to start local server for single instance check")
                sys.exit(1)
        
        logger.info("Local server started for single instance management")
        
        _start_api_server()
        
        def handle_new_connection():
            logger.info("Received activation request from another instance")
            connection = local_server.nextPendingConnection()
            if connection:
                connection.waitForReadyRead(1000)
                connection.close()
                logger.info("Quitting application due to activation request")
                app.quit()
        
        local_server.newConnection.connect(handle_new_connection)
        
        logger.info("Starting SLPlayer application")
        
        if getattr(sys, 'frozen', False):
            base_path = Path(sys.executable).parent
        else:
            base_path = Path(__file__).parent
        IconManager.setup_application_icon(app, base_path)
        
        first_launch_complete = settings.get("first_launch_complete", False)
        if not first_launch_complete:
            from ui.network_setup_dialog import NetworkSetupDialog
            network_dialog = NetworkSetupDialog()
            network_dialog.exec()
            settings.set("first_launch_complete", True)
            logger.info("First launch network setup completed")
        
        from ui.controller_dialog import ControllerDialog
        controller_dialog = ControllerDialog()
        controller_dialog.show()
        
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
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

