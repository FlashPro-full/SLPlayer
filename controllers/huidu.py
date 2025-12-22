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
from requests_toolbelt.multipart.encoder import MultipartEncoder # type: ignore
from pathlib import Path

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

    def _file(self, file_path: str) -> str:
        loc_file_path = Path(file_path)
        if not loc_file_path.exists():
            return json.dumps({
                "message": "failed",
                "data": f"Not found file [{file_path}]"
            })

        response_string = None
        err_string = None

        try:
            file_name = loc_file_path.name
            multipart_data = MultipartEncoder(
                fields={'file': (file_name, open(file_path, 'rb'), 'application/octet-stream')}
            )

            headers = {
                'Content-Type': multipart_data.content_type
            }

            url = f"{self.host}/api/file"
            
            result = self._sign_header(self.headers, multipart_data, url)
            if isinstance(result, str):
                url = result

            response = requests.post(
                url,
                data=multipart_data,
                headers=headers
            )
            response.raise_for_status()
            response_string = response.text
        except Exception as e:
            err_string = str(e)

        if not response_string:
            return json.dumps({
                "message": "failed",
                "data": err_string or "Unknown error"
            })
        return response_string
    
    def get_online_devices(self) -> Dict:
        try:
            response = self._get(f"{self.host}/api/device/list")
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error getting online devices: {e}")
            return {"message": "error", "data": str(e)}
    
    def get_all_device_property(self, device_ids: Optional[List[str]] = None) -> Dict:
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
    
    def get_device_property(self, device_ids: Optional[List[str]] = None, property_keys: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "getDeviceProperty",
                "data": property_keys,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
    
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error getting device property: {e}")
            return {"message": "error", "data": str(e)}

    def get_time_info(self, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            url = f"{self.host}/raw/{device_id_str}"
            headers = {
                'Content-Type': 'application/xml',
                'sdkKey': self.sdk_key,
            }
            body = """
            <?xml version='1.0' encoding='utf-8'?>
                <sdk guid="##GUID">
                    <in method="GetTimeInfo"/>
                </sdk>
            """
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
            logger.error(f"Error getting time info: {e}")
            return {"message": "error", "data": str(e)}

    def set_time_info(self, device_ids: Optional[List[str]] = None, sync: Optional[str] = None, timezone: Optional[str] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            url = f"{self.host}/raw/{device_id_str}"
            headers = {
                'Content-Type': 'application/xml',
                'sdkKey': self.sdk_key,
            }
            sync_xml = ""
            if sync == "ntp":
                sync_xml = '<sync value="ntp"/><ntp value="ntp.huidu.cn" />'
            else:
                sync_xml = '<sync value="none" />'
            body = f"""
            <?xml version='1.0' encoding='utf-8'?>
                <sdk guid="##GUID">
                    <in method="SetTimeInfo">
                        <timezone value="{timezone}"/>
                        <summer enable="false"/>
                        {sync_xml}
                        <time value=""/>
                    </in>
                </sdk>
            """
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
            logger.error(f"Error setting time info: {e}")
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
    
    def _upload_files_and_update_program(self, program: List[Dict]) -> List[Dict]:
        updated_program = []
        for prog in program:
            prog_copy = json.loads(json.dumps(prog))
            areas = prog_copy.get("area", [])
            
            for area in areas:
                items = area.get("item", [])
                for item in items:
                    item_type = item.get("type", "")
                    
                    if item_type == "image":
                        file_path = item.get("file", "") or item.get("localPath", "")
                        if file_path:
                            local_path = Path(file_path)
                            if local_path.exists() and not self._is_url(str(file_path)):
                                file_response = self._file(str(file_path))
                                try:
                                    file_data = json.loads(file_response)
                                    if file_data.get("message") == "ok" and file_data.get("data"):
                                        file_info = file_data["data"][0]
                                        if file_info.get("message") == "ok":
                                            item["file"] = file_info.get("data", file_path)
                                            item["fileSize"] = int(file_info.get("size", 0))
                                            item["fileMd5"] = file_info.get("md5", "")
                                            if "localPath" not in item:
                                                item["localPath"] = str(file_path)
                                except Exception as e:
                                    logger.error(f"Error processing image file upload response: {e}")
                    
                    elif item_type == "video":
                        file_path = item.get("file", "") or item.get("localPath", "")
                        if file_path:
                            local_path = Path(file_path)
                            if local_path.exists() and not self._is_url(str(file_path)):
                                file_response = self._file(str(file_path))
                                try:
                                    file_data = json.loads(file_response)
                                    if file_data.get("message") == "ok" and file_data.get("data"):
                                        file_info = file_data["data"][0]
                                        if file_info.get("message") == "ok":
                                            item["file"] = file_info.get("data", file_path)
                                            item["fileSize"] = int(file_info.get("size", 0))
                                            item["fileMd5"] = file_info.get("md5", "")
                                            if "localPath" not in item:
                                                item["localPath"] = str(file_path)
                                except Exception as e:
                                    logger.error(f"Error processing video file upload response: {e}")
            
            updated_program.append(prog_copy)
        return updated_program
    
    def _is_url(self, path: str) -> bool:
        return path.startswith(("http://", "https://"))
    
    def replace_program(self, program: Optional[List[Dict[str, str | bool | int | List[Dict[str, str | bool | int]]]]] = None, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            if not program:
                return {"message": "error", "data": "No program data provided"}
            
            updated_program = self._upload_files_and_update_program(program)
            
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "replace",
                "data": updated_program,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/program", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error replacing program: {e}")
            return {"message": "error", "data": str(e)}
    
    def update_program(self, program: Optional[List[Dict[str, str | bool | int | List[Dict[str, str | bool | int]]]]] = None, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            if not program:
                return {"message": "error", "data": "No program data provided"}
            
            updated_program = self._upload_files_and_update_program(program)
            
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "update",
                "data": updated_program,
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/program", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error updating program: {e}")
            return {"message": "error", "data": str(e)}

    def add_program(self, program: Optional[List[Dict[str, str | bool | int | List[Dict[str, str | bool | int]]]]] = None, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            if not program:
                return {"message": "error", "data": "No program data provided"}
            
            updated_program = self._upload_files_and_update_program(program)
            
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "append",
                "data": updated_program,
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
    
    def get_program_list(self) -> List[Dict]:
        try:
            from publish.huidu_sdk.sdk.Program import Program
            from publish.huidu_sdk.sdk.common.Config import Config
            
            Config.sdk_key = self.sdk_key
            Config.sdk_secret = self.sdk_secret
            Config.host = self.host
            
            program_client = Program(self.host)
            response = program_client.get_program_ids("")
            if response.get("message") == "ok" and response.get("data"):
                program_list = []
                for item in response.get("data", []):
                    if item.get("message") == "ok" and item.get("data"):
                        programs = item.get("data", [])
                        for prog in programs:
                            program_list.append({
                                "id": prog.get("uuid", ""),
                                "name": prog.get("name", "")
                            })
                return program_list
            return []
        except Exception as e:
            logger.error(f"Error getting program list: {e}")
            return []
    
    def download_program(self, program_id: Optional[str] = None) -> Optional[Dict]:
        try:
            from publish.huidu_sdk.sdk.Program import Program
            from publish.huidu_sdk.sdk.data.ProgramNode import ProgramNode
            from publish.huidu_sdk.sdk.common.Config import Config
            
            Config.sdk_key = self.sdk_key
            Config.sdk_secret = self.sdk_secret
            Config.host = self.host
            
            program_client = Program(self.host)
            response = program_client.get_program_ids("")
            if response.get("message") == "ok" and response.get("data"):
                for item in response.get("data", []):
                    if item.get("message") == "ok" and item.get("data"):
                        programs = item.get("data", [])
                        for prog_data in programs:
                            prog_uuid = prog_data.get("uuid", "")
                            if not program_id or prog_uuid == program_id:
                                if isinstance(prog_data, dict) and "area" in prog_data:
                                    return prog_data
                                else:
                                    program_node = ProgramNode(prog_data)
                                    program_dict = program_node.to_dict()
                                    return program_dict
            return None
        except Exception as e:
            logger.error(f"Error downloading program: {e}")
            return None