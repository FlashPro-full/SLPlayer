import json
import time
import uuid
import hmac
import hashlib
from typing import Optional, Dict, List
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from utils.logger import get_logger
import requests # type: ignore

logger = get_logger(__name__)

DEFAULT_SDK_KEY = "a718fbe8aaa8aeef"
DEFAULT_SDK_SECRET = "8fd529ef3f88986d40e6ef8d4d7f2d0c"
DEFAULT_HOST = "http://127.0.0.1:30080"

class HuiduController:
    
    def __init__(self):
        self.host = DEFAULT_HOST
        self.sdk_key = DEFAULT_SDK_KEY
        self.sdk_secret = DEFAULT_SDK_SECRET
        self.headers = {
            "Content-Type": "application/json",
            "sdkKey": self.sdk_key,
        }
    
    def _sign_header(self, headers: dict, body: Optional[str], url: Optional[str] = None) -> Optional[str]:
        request_id = str(uuid.uuid4())
        headers['requestId'] = request_id
        
        date_data = datetime.now(timezone.utc)
        date_str = date_data.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        sign_text = self.sdk_key + date_str
        if body is not None:
            sign_text = body + sign_text
        
        sign = hmac.new(
            self.sdk_secret.encode('utf-8'),
            sign_text.encode('utf-8'),
            hashlib.md5
        ).hexdigest()
        
        if 'sdkKey' in headers:
            headers['sdkKey'] = self.sdk_key
            headers['date'] = date_str
            headers['sign'] = sign
            return None
        elif url:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query, keep_blank_values=True)
            if 'sdkKey' in query_params:
                query_params['sdkKey'] = [self.sdk_key]
                query_params['date'] = [date_str]
                query_params['sign'] = [sign]
                new_query = urlencode(query_params, doseq=True)
                new_url = urlunparse(parsed._replace(query=new_query))
                return new_url
        
        return None
    
    def _post(self, url: str, body: str) -> str:
        try:
            result = self._sign_header(self.headers, body, url)
            if isinstance(result, str):
                url = result
            logger.info(f"SDK API Request: POST {url}")
            logger.info(f"SDK API Request Body: {body}")
            response = requests.post(url, data=body, headers=self.headers)
            response.raise_for_status()
            response_text = response.text
            logger.info(f"SDK API Response Body: {response_text}")
            return response_text
        except Exception as e:
            logger.error(f"HTTP POST error: {e}")
            error_response = json.dumps({"message": "error", "data": str(e)})
            logger.error(f"SDK API Error Response: {error_response}")
            return error_response
    
    def _get(self, url: str) -> str:
        try:
            result = self._sign_header(self.headers, None, url)
            if isinstance(result, str):
                url = result
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response_text = response.text
            logger.info(f"SDK API Response Body: {response_text}")
            return response_text
        except Exception as e:
            logger.error(f"HTTP GET error: {e}")
            error_response = json.dumps({"message": "error", "data": str(e)})
            logger.error(f"SDK API Error Response: {error_response}")
            return error_response
    
    def get_online_devices(self) -> Dict:
        try:
            response = self._get(f"{self.host}/api/device/list")
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error getting online devices: {e}")
            return {"message": "error", "data": str(e)}
    
    def get_device_property(self, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "getDeviceProperty",
                "data": [],
                "id": device_id_str
            }
            response_text = self._post(f"{self.host}/api/device", json.dumps(body))
            response = json.loads(response_text)
            data = []
            if response.get("message") == "ok" and response.get("data"):
                data = response.get("data")

            properties_group = [
                ["time", "time.timeZone", "time.sync"],
                ["volume", "volume.mode"],
                ["luminance", "luminance.mode"],
                ["eth.dhcp", "eth.ip"],
                ["wifi.enabled", "wifi.mode", "wifi.ap.ssid", "wifi.ap.passwd", "wifi.ap.channel"],
                ["sync"],
                ["gsm.apn"]             
            ]
            
            for group in properties_group:
                body = {
                    "method": "getDeviceProperty",
                    "data": group,
                    "id": device_id_str
                }
                while True:
                    response_text = self._post(f"{self.host}/api/device", json.dumps(body))
                    response = json.loads(response_text)
                    if response.get("message") == "ok" and response.get("data"):
                        success = True
                        for item in response.get("data"):
                            if item.get("message") != "ok":
                                success = False
                                break
                        if success:
                            for i in range(len(response.get("data"))):
                                device_data = response.get("data")[i].get("data", {})
                                if "data" not in data[i]:
                                    data[i]["data"] = {}
                                for key, value in device_data.items():
                                    data[i]["data"][key] = value
                            break
                    time.sleep(0.2)
            
            logger.info(f"Device property: {data}")
            
            return {"message": "ok", "data": data} if data else {"message": "error", "data": []}
        except Exception as e:
            logger.error(f"Error getting device property: {e}")
            return {"message": "error", "data": str(e)}
    
    def get_device_status(self, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "getDeviceStatus",
                "data": [],
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            return {"message": "error", "data": str(e)}
    
    def set_device_property(self, properties: Dict, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "setDeviceProperty",
                "data": properties,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error setting device property: {e}")
            return {"message": "error", "data": str(e)}
    
    def get_schedule_task(self, device_ids: Optional[List[str]] = None, data: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "getScheduleTask",    
                "data": data,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error getting schedule task: {e}")
            return {"message": "error", "data": str(e)}

    def set_schedule_task(self, device_ids: Optional[List[str]] = None, data: Optional[Dict[str, Optional[List[Dict[str, str | bool | int]]]]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "setScheduleTask",
                "data": data,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error setting schedule task: {e}")
            return {"message": "error", "data": str(e)}

    def get_period_task(self, device_ids: Optional[List[str]] = None, data: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "getPeriodTask",
                "data": data,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error getting period task: {e}")
            return {"message": "error", "data": str(e)}

    def set_period_task(self, device_ids: Optional[List[str]] = None, data: Optional[List[Dict[str, str | bool | int]]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""  
            body = {
                "method": "setPeriodTask",
                "data": data,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error setting period task: {e}")
            return {"message": "error", "data": str(e)}

    def reboot_device(self, device_ids: Optional[List[str]] = None, data: Optional[Dict[str, str | bool | int]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "rebootDevice",
                "data": data,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error rebooting device: {e}")
            return {"message": "error", "data": str(e)}

    def turn_on_screen(self, device_ids: Optional[List[str]] = None, data: Optional[Dict[str, str | bool | int]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "openDeviceScreen",
                "data": data,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error turning on screen: {e}")
            return {"message": "error", "data": str(e)}

    def turn_off_screen(self, device_ids: Optional[List[str]] = None, data: Optional[Dict[str, str | bool | int]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "closeDeviceScreen",
                "data": data,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error turning off screen: {e}")
            return {"message": "error", "data": str(e)}
    
    def get_programs(self, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            url = f"{self.host}/raw/{device_id_str}"
            headers = {
                "Content-Type": "application/xml",
                "sdkKey": self.sdk_key,
            }
            body = """<?xml version='1.0' encoding='utf-8'?>
                        <sdk guid="##GUID">
                        <in method="GetProgram"/>
                        </sdk>"""
            result = self._sign_header(headers, body, url)
            if isinstance(result, str):
                url = result
            logger.info(f"SDK API Request: POST {url}")
            logger.info(f"SDK API Request Body: {body}")
            response = requests.post(url, data=body, headers=headers)
            response.raise_for_status()
            response_text = response.text
            logger.info(f"SDK API Response Body: {response_text}")
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error getting programs: {e}")
            return {"message": "error", "data": str(e)}
    
    def replace_program(self, program: Optional[List[Dict[str, str | bool | int | List[Dict[str, str | bool | int]]]]] = None, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "replace",
                "data": program,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/program", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error replacing program: {e}")
            return {"message": "error", "data": str(e)}
    
    def update_program(self, program: Optional[List[Dict[str, str | bool | int | List[Dict[str, str | bool | int]]]]] = None, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "update",
                "data": program,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/program", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error updating program: {e}")
            return {"message": "error", "data": str(e)}

    def add_program(self, program: Optional[List[Dict[str, str | bool | int | List[Dict[str, str | bool | int]]]]] = None, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "append",
                "data": program,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/program", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error adding program: {e}")
            return {"message": "error", "data": str(e)}

    def remove_program(self, program: Optional[List[Dict[str, str]]] = None, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "remove",
                "data": program,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/program", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error removing program: {e}")
            return {"message": "error", "data": str(e)}