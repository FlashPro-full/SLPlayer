import json
import time
import uuid
import hmac
import hashlib
import shutil
from typing import Optional, Dict, List
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from xml.sax.saxutils import escape as xml_escape
from utils.logger import get_logger
from utils.xml_converter import XMLToJSONConverter
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

    # def _file(self, file_path: str) -> str:
    #     loc_file_path = Path(file_path)
    #     if not loc_file_path.exists():
    #         return json.dumps({
    #             "message": "failed",
    #             "data": f"Not found file [{file_path}]"
    #         })

    #     response_string = None
    #     err_string = None

    #     try:
    #         file_name = loc_file_path.name
    #         multipart_data = MultipartEncoder(
    #             fields={'file': (file_name, open(file_path, 'rb'), 'application/octet-stream')}
    #         )

    #         headers = {
    #             'Content-Type': multipart_data.content_type
    #         }

    #         url = f"{self.host}/api/file"
            
    #         result = self._sign_header(headers, multipart_data, url)
    #         if isinstance(result, str):
    #             url = result

    #         response = requests.post(
    #             url,
    #             data=multipart_data,
    #             headers=headers
    #         )
    #         response.raise_for_status()
    #         response_string = response.text
    #     except Exception as e:
    #         err_string = str(e)

    #     if not response_string:
    #         return json.dumps({
    #             "message": "failed",
    #             "data": err_string or "Unknown error"
    #         })
    #     return response_string
    
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

    def set_device_property(self, device_ids: Optional[List[str]] = None, properties: Optional[Dict] = None) -> Dict:
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
    
    def get_luminance_info(self, device_ids: Optional[List[str]] = None) -> Dict:
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
                    <in method="GetLuminancePloy"/>
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

    def set_luminance_info(self, device_ids: Optional[List[str]] = None, properties: Optional[Dict[str, str | int | List[Dict[str, str]]]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            url = f"{self.host}/raw/{device_id_str}"
            headers = {
                'Content-Type': 'application/xml',
                'sdkKey': self.sdk_key,
            }

            if properties is None:
                properties = {}
            
            mode = properties.get('mode', None)
            default = properties.get('default', None)
            sensor_max = properties.get('sensor.max', None)
            sensor_min = properties.get('sensor.min', None)
            sensor_time = properties.get('sensor.time', None)
            ploy_items = properties.get('ploy.item', [])
            if not isinstance(ploy_items, list):
                ploy_items = []
            ploy_item = ""
            for item in ploy_items:
                if isinstance(item, dict):
                    ploy_item += f"""
                        <item enable="{item.get('enable', 'false')}" start="{item.get('start', '08:00:00')}" percent="{item.get('percent', '100')}" />
                        """

            body = f"""
                <?xml version='1.0' encoding='utf-8'?>
                    <sdk guid="##GUID">
                        <in method="SetLuminancePloy">
                            <mode value="{mode}"/>
                            <default value="{default}"/>
                            <sensor max="{sensor_max}" min="{sensor_min}" time="{sensor_time}" />
                            <ploy>
                                {ploy_item}    
                            </ploy>
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

    def get_network_info(self, device_ids: Optional[List[str]] = None) -> Dict:
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
                    <in method="GetNetworkInfo"/>
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
            logger.error(f"Error getting network info: {e}")
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
    
    def get_schedule_task(self, device_ids: Optional[List[str]] = None, data: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "getScheduledTask",    
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
                "method": "setScheduledTask",
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

    def reboot_device(self, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "rebootDevice",
                "data": {
                    "delay": 5
                },
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error rebooting device: {e}")
            return {"message": "error", "data": str(e)}

    def turn_on_screen(self, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "openDeviceScreen",
                "data": {},
                "id": device_id_str
            }
            response = self._post(f"{self.host}/api/device", json.dumps(body))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error turning on screen: {e}")
            return {"message": "error", "data": str(e)}

    def turn_off_screen(self, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            device_id_str = ",".join(device_ids) if device_ids else ""
            body = {
                "method": "closeDeviceScreen",
                "data": {},
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
                'Content-Type': 'application/xml',
                'sdkKey': self.sdk_key,
            }
            body = """
            <?xml version='1.0' encoding='utf-8'?>
                <sdk guid="##GUID">
                    <in method="GetProgram"/>
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
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return {"message": "ok", "data": response_text}
        except Exception as e:
            logger.error(f"Error getting programs: {e}")
            return {"message": "error", "data": str(e)}
    
    def _calculate_file_info(self, file_path: str) -> Dict:
        """Calculate file size and MD5 hash.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with 'size' and 'md5' keys, or empty dict on error
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"File does not exist: {file_path}")
                return {}
            
            # Calculate file size
            file_size = file_path_obj.stat().st_size
            
            # Calculate MD5 hash
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            md5_value = md5_hash.hexdigest()
            
            return {
                "size": file_size,
                "md5": md5_value
            }
        except Exception as e:
            logger.error(f"Error calculating file info for {file_path}: {e}")
            return {}
    
    def _send_add_files_xml_request(self, file_path: str, file_type: str, device_ids: Optional[List[str]] = None) -> Dict:
        """Send AddFiles XML request with file information.
        
        Args:
            file_path: Path to the file to add
            file_type: Type of file ('image' or 'video')
            device_ids: Optional list of device IDs to send the request to
            
        Returns:
            Response dictionary from the API
        """
        try:
            # Calculate file info
            file_info = self._calculate_file_info(file_path)
            if not file_info:
                return {"message": "error", "data": "Failed to calculate file info"}
            
            file_size = file_info["size"]
            file_md5 = file_info["md5"]
            file_name = Path(file_path).name
            
            # Build XML request with local file path
            # Convert Windows path to forward slashes if needed
            local_file_path = str(file_path).replace('\\', '/')
            
            body = f"""<?xml version='1.0' encoding='utf-8'?>
                        <sdk guid="##GUID">
                            <in method="AddFiles">
                                <files>
                                    <file remote="{local_file_path}" size="{file_size}" md5="{file_md5}" type="{file_type}" name="{file_name}"/>
                                </files>
                            </in>
                        </sdk>"""
            
            # Send request
            device_id_str = ",".join(device_ids) if device_ids else ""
            url = f"{self.host}/raw/{device_id_str}"
            headers = {
                'Content-Type': 'application/xml',
                'sdkKey': self.sdk_key,
            }
            
            result = self._sign_header(headers, body, url)
            if isinstance(result, str):
                url = result
            logger.info(f"SDK API Request: POST {url}")
            logger.info(f"SDK API Request Body: {body}")
            response = requests.post(url, data=body, headers=headers)
            response.raise_for_status()
            response_text = response.text
            logger.info(f"SDK API Response Body: {response_text}")
            
            # Parse XML response
            json_data = XMLToJSONConverter.convert(response_text)
            if not json_data:
                return {"message": "error", "data": "Failed to parse XML response"}
            
            # Check for result in out element
            if isinstance(json_data, dict):
                out_element = json_data.get("out", {})
                if isinstance(out_element, dict):
                    result_attr = out_element.get("@attributes", {})
                    if isinstance(result_attr, dict):
                        result_value = result_attr.get("result", "")
                        if result_value == "kSuccess":
                            return {"message": "ok", "data": "File added successfully"}
                        else:
                            error_msg = result_value or "Unknown error"
                            return {"message": "error", "data": f"AddFiles failed: {error_msg}"}
            
            # Fallback if structure is unexpected
            return {"message": "ok", "data": response_text}
        except Exception as e:
            logger.error(f"Error sending AddFiles XML request: {e}")
            return {"message": "error", "data": str(e)}
    
    def _upload_files(self, program: List[Dict], device_ids: Optional[List[str]] = None) -> List[Dict]:
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
                                # Copy file to resources/custom/images with encoded name
                                copied_file_path = self._copy_file_to_resources(str(file_path), "image")
                                if copied_file_path:
                                    # Send XML request with copied file
                                    xml_response = self._send_add_files_xml_request(copied_file_path, "image", device_ids)
                                    try:
                                        if xml_response.get("message") == "ok":
                                            # Update item with file information from response if available
                                            file_info = self._calculate_file_info(copied_file_path)
                                            if file_info:
                                                item["fileSize"] = file_info.get("size", 0)
                                                item["fileMd5"] = file_info.get("md5", "")
                                            logger.info(f"Successfully sent AddFiles XML request for image: {copied_file_path}")
                                        else:
                                            logger.error(f"AddFiles XML request failed: {xml_response.get('data', 'Unknown error')}")
                                    except Exception as e:
                                        logger.error(f"Error processing AddFiles XML response: {e}")
                                else:
                                    logger.error(f"Failed to copy image file to resources/custom: {file_path}")
                    
                    elif item_type == "video":
                        file_path = item.get("file", "") or item.get("localPath", "")
                        if file_path:
                            local_path = Path(file_path)
                            if local_path.exists() and not self._is_url(str(file_path)):
                                # Copy file to resources/custom/videos with encoded name
                                copied_file_path = self._copy_file_to_resources(str(file_path), "video")
                                if copied_file_path:
                                    # Upload the copied file instead of the original
                                    xml_response = self._send_add_files_xml_request(copied_file_path, "video", device_ids)
                                    try:
                                        if xml_response.get("message") == "ok":
                                            # Update item with file information from response if available
                                            file_info = self._calculate_file_info(copied_file_path)
                                            if file_info:
                                                item["fileSize"] = file_info.get("size", 0)
                                                item["fileMd5"] = file_info.get("md5", "")
                                            logger.info(f"Successfully sent AddFiles XML request for video: {copied_file_path}")
                                        else:
                                            logger.error(f"AddFiles XML request failed: {xml_response.get('data', 'Unknown error')}")
                                    except Exception as e:
                                        logger.error(f"Error processing AddFiles XML response: {e}")
                                else:
                                    logger.error(f"Failed to copy video file to resources/custom: {file_path}")
        return program
    
    def _is_url(self, path: str) -> bool:
        return path.startswith(("http://", "https://"))
    
    def _get_resources_custom_dir(self) -> Path:
        """Get the resources/custom directory path at project root, creating it if necessary."""
        # Always use project root (where huidu.py is located: controllers/ -> project root)
        base_path = Path(__file__).parent.parent
        resources_dir = base_path / "resources" / "custom"
        resources_dir.mkdir(parents=True, exist_ok=True)
        return resources_dir
    
    def _generate_encoded_filename(self, original_path: str, file_type: str) -> str:
        """Generate a distinct encoded filename for the copied file.
        
        Args:
            original_path: The original file path
            file_type: Either 'image' or 'video'
            
        Returns:
            A distinct encoded filename
        """
        original_path_obj = Path(original_path)
        original_name = original_path_obj.name
        original_stem = original_path_obj.stem
        original_suffix = original_path_obj.suffix
        
        # Create a hash from the original path and current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        hash_input = f"{original_path}_{timestamp}"
        hash_value = hashlib.md5(hash_input.encode('utf-8')).hexdigest()[:12]
        
        # Generate distinct filename: hash_timestamp_originalname.ext
        encoded_name = f"{hash_value}_{timestamp}_{original_stem}{original_suffix}"
        
        return encoded_name
    
    def _copy_file_to_resources(self, file_path: str, file_type: str) -> Optional[str]:
        """Copy a file to resources/custom with distinct encoded name.
        
        Args:
            file_path: Path to the original file
            file_type: Either 'image' or 'video'
            
        Returns:
            Path to the copied file, or None if copy failed
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                logger.error(f"Source file does not exist: {file_path}")
                return None
            
            # Determine subfolder based on file type
            subfolder = "images" if file_type == "image" else "videos"
            resources_dir = self._get_resources_custom_dir()
            target_dir = resources_dir / subfolder
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate distinct encoded filename
            encoded_filename = self._generate_encoded_filename(file_path, file_type)
            target_path = target_dir / encoded_filename
            
            # Copy the file
            shutil.copy2(source_path, target_path)
            logger.info(f"Copied file from {file_path} to {target_path}")
            
            return str(target_path)
        except Exception as e:
            logger.error(f"Error copying file to resources/custom: {e}", exc_info=True)
            return None
    
    def _escape_xml_attr(self, value: str) -> str:
        """Escape XML attribute value (escapes &, <, >, and quotes)."""
        if not isinstance(value, str):
            value = str(value)
        # Escape XML special characters
        value = value.replace("&", "&amp;")
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")
        value = value.replace('"', "&quot;")
        return value
    
    def _program_dict_to_xml(self, program: Dict) -> str:
        """Convert program dictionary to XML format for UpdateProgram request.
        
        Args:
            program: Program dictionary with name, type, uuid, area, playControl, etc.
            
        Returns:
            XML string for the program element
        """
        program_type = program.get("type", "normal")
        program_id = program.get("id", "0")
        program_name = self._escape_xml_attr(program.get("name", ""))
        program_guid = program.get("uuid", "") or program.get("guid", "")
        # Convert uuid to guid format if needed (remove curly braces, ensure UUID format)
        if program_guid:
            # Remove curly braces if present
            program_guid = program_guid.strip("{}")
            # Format as GUID: add dashes if needed
            if len(program_guid) == 12:
                # Convert to full UUID format
                program_guid = f"{program_guid[:8]}-{program_guid[8:12]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:12]}"
            elif len(program_guid) == 32 and "-" not in program_guid:
                # Format as UUID with dashes
                program_guid = f"{program_guid[:8]}-{program_guid[8:12]}-{program_guid[12:16]}-{program_guid[16:20]}-{program_guid[20:]}"
        else:
            # Generate new UUID if not provided
            program_guid = str(uuid.uuid4())
        
        # Build backgroundMusic element
        background_music_xml = "<backgroundMusic></backgroundMusic>"
        properties = program.get("_properties", {})
        if properties:
            bg_music = properties.get("background_music", {})
            if bg_music and bg_music.get("enabled", False):
                file_path = self._escape_xml_attr(bg_music.get("file", ""))
                volume = bg_music.get("volume", 0)
                background_music_xml = f'<backgroundMusic file="{file_path}" volume="{volume}"></backgroundMusic>'
        
        # Build playControl element
        play_control_xml = '<playControl disabled="false" count="1"/>'
        play_control = program.get("playControl", {})
        if play_control:
            disabled = "true" if play_control.get("disabled", False) else "false"
            count = play_control.get("count", 1)
            play_control_xml = f'<playControl disabled="{disabled}" count="{count}"/>'
        
        # Build areas XML
        areas_xml = ""
        areas = program.get("area", [])
        for area in areas:
            area_guid = area.get("guid", "") or area.get("uuid", "")
            if not area_guid:
                area_guid = str(uuid.uuid4())
            # Remove curly braces if present (request format doesn't use braces)
            area_guid = area_guid.strip("{}")
            # Ensure UUID format with dashes
            if len(area_guid) == 32 and "-" not in area_guid:
                area_guid = f"{area_guid[:8]}-{area_guid[8:12]}-{area_guid[12:16]}-{area_guid[16:20]}-{area_guid[20:]}"
            
            alpha = area.get("alpha", 255)
            x = area.get("x", 0)
            y = area.get("y", 0)
            width = area.get("width", 0)
            height = area.get("height", 0)
            
            # Build rectangle element
            rectangle_xml = f'<rectangle x="{x}" y="{y}" width="{width}" height="{height}"/>'
            
            # Build resource elements from items
            resource_xml = ""
            items = area.get("item", [])
            for item in items:
                item_type = item.get("type", "")
                item_guid = item.get("guid", "") or item.get("uuid", "")
                if not item_guid:
                    item_guid = str(uuid.uuid4())
                # Remove curly braces if present (request format doesn't use braces)
                item_guid = item_guid.strip("{}")
                # Ensure UUID format with dashes
                if len(item_guid) == 32 and "-" not in item_guid:
                    item_guid = f"{item_guid[:8]}-{item_guid[8:12]}-{item_guid[12:16]}-{item_guid[16:20]}-{item_guid[20:]}"
                
                if item_type == "image":
                    file_name = self._escape_xml_attr(item.get("file", "") or item.get("name", ""))
                    effect_in = item.get("effect", {}).get("in", 0) if isinstance(item.get("effect"), dict) else 0
                    effect_out = item.get("effect", {}).get("out", 20) if isinstance(item.get("effect"), dict) else 20
                    effect_in_speed = item.get("effect", {}).get("inSpeed", 4) if isinstance(item.get("effect"), dict) else 4
                    effect_out_speed = item.get("effect", {}).get("outSpeed", 0) if isinstance(item.get("effect"), dict) else 0
                    effect_duration = item.get("effect", {}).get("duration", 50) if isinstance(item.get("effect"), dict) else 50
                    
                    resource_xml += f"""
                        <resource>
                            <image guid="{item_guid}">
                                <file name="{file_name}"/>
                                <effect in="{effect_in}" out="{effect_out}" inSpeed="{effect_in_speed}" outSpeed="{effect_out_speed}" duration="{effect_duration}"/>
                            </image>
                        </resource>"""
                elif item_type == "video":
                    file_name = self._escape_xml_attr(item.get("file", "") or item.get("name", ""))
                    effect_in = item.get("effect", {}).get("in", 0) if isinstance(item.get("effect"), dict) else 0
                    effect_out = item.get("effect", {}).get("out", 20) if isinstance(item.get("effect"), dict) else 20
                    effect_in_speed = item.get("effect", {}).get("inSpeed", 4) if isinstance(item.get("effect"), dict) else 4
                    effect_out_speed = item.get("effect", {}).get("outSpeed", 0) if isinstance(item.get("effect"), dict) else 0
                    effect_duration = item.get("effect", {}).get("duration", 50) if isinstance(item.get("effect"), dict) else 50
                    
                    resource_xml += f"""
                        <resource>
                            <video guid="{item_guid}">
                                <file name="{file_name}"/>
                                <effect in="{effect_in}" out="{effect_out}" inSpeed="{effect_in_speed}" outSpeed="{effect_out_speed}" duration="{effect_duration}"/>
                            </video>
                        </resource>"""
                elif item_type in ["text", "singleline_text"]:
                    text_content = xml_escape(item.get("text", "") or item.get("content", ""))
                    font_family = self._escape_xml_attr(item.get("font", {}).get("family", "Arial") if isinstance(item.get("font"), dict) else item.get("fontFamily", "Arial"))
                    font_size = item.get("font", {}).get("size", 24) if isinstance(item.get("font"), dict) else item.get("fontSize", 24)
                    font_color = self._escape_xml_attr(item.get("font", {}).get("color", "#000000") if isinstance(item.get("font"), dict) else item.get("fontColor", "#000000"))
                    
                    resource_xml += f"""
                        <resource>
                            <text guid="{item_guid}">
                                <content>{text_content}</content>
                                <font family="{font_family}" size="{font_size}" color="{font_color}"/>
                            </text>
                        </resource>"""
            
            if resource_xml:
                areas_xml += f"""
                <area guid="{area_guid}" alpha="{alpha}">
                    {rectangle_xml}
                    {resource_xml}
                </area>"""
        
        # Build complete program XML
        program_xml = f"""<program type="{program_type}" id="{program_id}" name="{program_name}" guid="{program_guid}">
                {background_music_xml}
                {play_control_xml}
                {areas_xml}
            </program>"""
        
        return program_xml
    
    def update_program(self, program: Optional[List[Dict[str, str | bool | int | List[Dict[str, str | bool | int]]]]] = None, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            if not program:
                return {"message": "error", "data": "No program data provided"}
            
            updated_program = self._upload_files(program, device_ids)
            
            device_id_str = ",".join(device_ids) if device_ids else ""
            url = f"{self.host}/raw/{device_id_str}"
            headers = {
                'Content-Type': 'application/xml',
                'sdkKey': self.sdk_key,
            }
            
            # Build XML body from program list
            programs_xml = ""
            for prog in updated_program:
                programs_xml += self._program_dict_to_xml(prog)
            
            body = f"""<?xml version='1.0' encoding='utf-8'?>
<sdk guid="##GUID">
    <in method="UpdateProgram">
        <screen timeStamps="0">
            {programs_xml}
        </screen>
    </in>
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
            
            # Parse XML response
            try:
                json_data = XMLToJSONConverter.convert(response_text)
                if json_data:
                    # Check for result in out element (response format: <sdk><out method="UpdateProgram" result="kSuccess"/></sdk>)
                    if isinstance(json_data, dict):
                        # Try direct access first
                        out_element = json_data.get("out", {})
                        # If not found, try accessing through sdk wrapper
                        if not out_element and "sdk" in json_data:
                            sdk_element = json_data.get("sdk", {})
                            if isinstance(sdk_element, dict):
                                out_element = sdk_element.get("out", {})
                        
                        if isinstance(out_element, dict):
                            result_attr = out_element.get("@attributes", {})
                            if isinstance(result_attr, dict):
                                result_value = result_attr.get("result", "")
                                if result_value == "kSuccess":
                                    return {"message": "ok", "data": "Program updated successfully"}
                                else:
                                    error_msg = result_value or "Unknown error"
                                    return {"message": "error", "data": f"UpdateProgram failed: {error_msg}"}
                    # Fallback: return parsed JSON
                    return {"message": "ok", "data": json_data}
                else:
                    return {"message": "ok", "data": response_text}
            except Exception as parse_error:
                logger.warning(f"Failed to parse XML response, returning raw text: {parse_error}")
                return {"message": "ok", "data": response_text}
        except Exception as e:
            logger.error(f"Error updating program: {e}")
            return {"message": "error", "data": str(e)}

    def add_program(self, program: Optional[List[Dict[str, str | bool | int | List[Dict[str, str | bool | int]]]]] = None, device_ids: Optional[List[str]] = None) -> Dict:
        try:
            if not program:
                return {"message": "error", "data": "No program data provided"}
            
            updated_program = self._upload_files(program, device_ids)
            
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