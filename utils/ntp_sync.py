"""
NTP time synchronization utility
"""
import socket
import struct
import time
from datetime import datetime
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class NTPSync:
    """NTP time synchronization"""
    
    NTP_SERVER = "it.pool.ntp.org"
    NTP_PORT = 123
    TIMEOUT = 3.0
    
    @staticmethod
    def has_internet_connectivity() -> bool:
        """
        Check if LAN has internet connectivity.
        Returns True if internet is available, False otherwise.
        """
        try:
            test_hosts = ["8.8.8.8", "1.1.1.1", "it.pool.ntp.org"]
            for host in test_hosts:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((host, 53 if host in ["8.8.8.8", "1.1.1.1"] else 123))
                    sock.close()
                    if result == 0:
                        logger.info(f"Internet connectivity confirmed via {host}")
                        return True
                except Exception:
                    continue
            logger.warning("No internet connectivity detected")
            return False
        except Exception as e:
            logger.warning(f"Error checking internet connectivity: {e}")
            return False
    
    @staticmethod
    def get_ntp_time(server: str = None) -> Optional[datetime]:
        """
        Get time from NTP server.
        Only attempts NTP sync if internet connectivity is available.
        Returns datetime object or None if failed.
        """
        if not NTPSync.has_internet_connectivity():
            logger.warning("Skipping NTP sync - no internet connectivity detected")
            return None
        
        if server is None:
            server = NTPSync.NTP_SERVER
        
        try:
            # NTP packet format
            ntp_packet = bytearray(48)
            ntp_packet[0] = 0x1b  # NTP version 3, client mode
            
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(NTPSync.TIMEOUT)
            
            # Send request
            sock.sendto(ntp_packet, (server, NTPSync.NTP_PORT))
            
            # Receive response
            data, _ = sock.recvfrom(48)
            sock.close()
            
            # Parse NTP timestamp (seconds since 1900-01-01)
            ntp_timestamp = struct.unpack('!12I', data)[10]
            ntp_timestamp -= 2208988800  # Convert to Unix timestamp (seconds since 1970-01-01)
            
            # Convert to datetime
            ntp_time = datetime.fromtimestamp(ntp_timestamp)
            logger.info(f"Successfully synchronized time from NTP server {server}: {ntp_time}")
            return ntp_time
            
        except socket.timeout:
            logger.warning(f"NTP request to {server} timed out")
            return None
        except Exception as e:
            logger.exception(f"Error synchronizing time from NTP server {server}: {e}")
            return None
    
    @staticmethod
    def sync_controller_time(controller, use_ntp: bool = False) -> bool:
        """
        Sync controller time with PC or NTP.
        NTP sync only works if LAN has internet connectivity.
        Returns True if successful.
        """
        try:
            if use_ntp:
                # Check internet connectivity before attempting NTP sync
                if not NTPSync.has_internet_connectivity():
                    logger.warning("NTP sync skipped - no internet connectivity, falling back to PC time")
                    sync_time = datetime.now()
                else:
                    # Get time from NTP server
                    ntp_time = NTPSync.get_ntp_time()
                    if ntp_time is None:
                        logger.warning("NTP sync failed, falling back to PC time")
                        sync_time = datetime.now()
                    else:
                        sync_time = ntp_time
            else:
                # Use PC time
                sync_time = datetime.now()
            
            # Send time to controller
            if hasattr(controller, 'set_time'):
                return controller.set_time(sync_time)
            else:
                logger.warning("Controller does not support set_time method")
                return False
                
        except Exception as e:
            logger.exception(f"Error syncing controller time: {e}")
            return False

