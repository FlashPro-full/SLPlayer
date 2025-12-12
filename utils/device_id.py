import platform
import hashlib
import uuid
from pathlib import Path
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def get_machine_id() -> str:
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                        for elements in range(0, 2*6, 2)][::-1])
        
        system_info = f"{platform.system()}{platform.node()}{platform.processor()}"
        
        combined = f"{mac}{system_info}".encode('utf-8')
        machine_id = hashlib.sha256(combined).hexdigest()[:16].upper()
        
        return f"PC-{machine_id}"
    except Exception as e:
        logger.exception(f"Error generating machine ID: {e}")
        fallback_id = str(uuid.uuid4()).replace('-', '').upper()[:16]
        return f"PC-{fallback_id}"


def get_device_id() -> str:

    config_dir = Path.home() / ".slplayer"
    device_id_file = config_dir / "device_id.txt"
    
    if device_id_file.exists():
        try:
            with open(device_id_file, 'r', encoding='utf-8') as f:
                device_id = f.read().strip()
            if device_id:
                return device_id
        except Exception as e:
            logger.warning(f"Error reading device ID file: {e}")
    
    device_id = get_machine_id()
    
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(device_id_file, 'w', encoding='utf-8') as f:
            f.write(device_id)
        logger.info(f"Generated and saved device ID: {device_id}")
    except Exception as e:
        logger.warning(f"Error saving device ID: {e}")
    
    return device_id

