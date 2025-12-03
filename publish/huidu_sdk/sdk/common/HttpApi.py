import uuid
import json
import hmac
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from sdk.common.Config import Config

class HttpApi:
    def __init__(self, host_url: Optional[str] = None):
        self.sdk_key = Config.sdk_key
        self.sdk_secret = Config.sdk_secret

        base_url = host_url if host_url else Config.host
        if not base_url:
            raise ValueError("API host URL is not configured")
        if not isinstance(base_url, str):
            raise TypeError(
                f"API host URL must be string, got {type(base_url).__name__}"
            )
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL protocol. Must start with http:// or https://")

        # Ensure URLs end with '/'
        base_url = base_url.rstrip('/')
        self.dev_api_url = f"{base_url}/api/device/"
        self.file_api_url = f"{base_url}/api/file/"
        self.program_api_url = f"{base_url}/api/program/"

    def device_list(self) -> str:
        api_url = self.dev_api_url + "list/"
        return self._get(api_url)

    def device(self, body: str) -> str:
        return self._post(self.dev_api_url, body)

    def program(self, body: str) -> str:
        return self._post(self.program_api_url, body, 60)

    def upload_file(self, file_path: str) -> str:
        return self._file(file_path)

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
            self._sign_header(headers, None)

            response = requests.post(
                self.file_api_url,
                data=multipart_data,
                headers=headers,
                timeout=4
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

    def _post(self, url: str, body: str, timeout_ms: int = 0) -> str:
        print(json.dumps(body, indent=2))
        response_string = None
        err_string = None

        try:
            headers = {'Content-Type': 'application/json'}
            if timeout_ms > 0:
                headers['timeout'] = str(timeout_ms)

            self._sign_header(headers, body)

            timeout_val = (timeout_ms / 1000.0 - 1) if timeout_ms > 0 else 4
            response = requests.post(
                url,
                data=body,
                headers=headers,
                timeout=timeout_val
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

    def _get(self, url: str) -> str:
        print(json.dumps(url, indent=2))
        response_string = None
        err_string = None

        try:
            headers = {}
            self._sign_header(headers, None)

            response = requests.get(
                url,
                headers=headers,
                timeout=4
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

    def _sign_header(self, headers: dict, body: Optional[str]) -> bool:
        if headers is None:
            return False

        # Generate unique request ID
        cuid = str(uuid.uuid4())
        headers['requestId'] = cuid

        # Set SDK key
        headers['sdkKey'] = self.sdk_key

        # Add current date (using Java-like format)
        current_date = datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')
        headers['date'] = current_date

        # Generate signature
        if body is None:
            sign_data = self.sdk_key + current_date
        else:
            sign_data = body + self.sdk_key + current_date

        headers['sign'] = self._hmac_md5(sign_data, self.sdk_secret)
        return True

    def _hmac_md5(self, data: str, key: str) -> str:
        try:
            key_bytes = key.encode('utf-8')
            data_bytes = data.encode('utf-8')
            hashed = hmac.new(key_bytes, data_bytes, hashlib.md5)
            return hashed.hexdigest()
        except Exception:
            return ""


