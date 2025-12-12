import re
import json
from typing import List, Optional, Any
from sdk.data.ProgramNode import ProgramNode
from sdk.data.other.FileInfo import FileInfo
from sdk.common.HttpApi import HttpApi


class BaseClient:
    def __init__(self, host_url: Optional[str] = None):
        self.client = HttpApi(host_url if host_url else "")

    def set_host_url(self, host_url: str):
        self.client = HttpApi(host_url)

    def get_device(self) -> dict:
        response = self.client.device_list()
        return self._to_json_object(response)

    def device(self, dev_ids: List[str], method: str, data: Optional[Any] = None) -> dict:
        json_method = {
            "method": method
        }
        
        if data is not None:
            json_method["data"] = data

        if dev_ids:
            json_method["id"] = ",".join(dev_ids)

        response = self.client.device(json.dumps(json_method))
        return self._to_json_object(response)

    def program(self, dev_ids: List[str], method: str,
                program_nodes: List[ProgramNode], data_ex: Optional[Any] = None) -> dict:
        # Upload files and update program structure
        ret_json = self._upload_and_update_files(program_nodes)
        if ret_json.get("message") != "ok":
            return ret_json

        # Prepare program command
        json_method = {
            "method": method,
            "data": [node.to_dict() for node in program_nodes]
        }

        if data_ex is not None:
            json_method["dataEx"] = data_ex

        if dev_ids:
            json_method["id"] = ",".join(dev_ids)

        response = self.client.program(json.dumps(json_method))
        return self._to_json_object(response)

    def file(self, file_path: str) -> dict:
        response = self.client.upload_file(file_path)
        return self._to_json_object(response)

    def _upload_and_update_files(self, program_nodes: List[ProgramNode]) -> dict:
        # Collect unique files from the program structure
        file_infos = self._collect_file_info(program_nodes)

        # Upload files and update metadata
        ret = True
        error_data = None

        for info in file_infos:
            # Skip URLs with valid metadata
            if self._is_url(info.localFile) and info.md5 and info.size > 0:
                info.url = info.localFile
                continue

            # Upload local file
            result = self.file(info.localFile)
            if result.get("message") != "ok":
                ret = False
                error_data = result
                break

            # Process response data
            data_array = result.get("data", [])
            if not data_array:
                ret = False
                error_data = result
                break

            data_obj = data_array[0]
            if not data_obj or data_obj.get("message") != "ok":
                ret = False
                error_data = result
                break

            # Update file metadata
            info.md5 = data_obj.get("md5", "")
            info.size = data_obj.get("size", 0)
            info.url = data_obj.get("data", "")

        # Update program structure if all uploads succeeded
        if ret and file_infos:
            files_array = list(file_infos)
            self._update_program_files(program_nodes, files_array)

        # Return result
        return {
            "message": "ok" if ret else "failed",
            "data": error_data if not ret else None
        }

    def _collect_file_info(self, program_nodes: List[ProgramNode]) -> set:
        file_infos = set()

        if not program_nodes:
            return file_infos

        for program_node in program_nodes:
            # Program-level files
            for info in program_node.get_files_info() or []:
                file_infos.add(info)

            # Area-level files
            for area in program_node.get_area() or []:
                for info in area.get_files_info() or []:
                    file_infos.add(info)

                # Content-level files
                for content in area.get_item() or []:
                    for info in content.get_files_info() or []:
                        file_infos.add(info)

        return file_infos

    def _update_program_files(self, program_nodes: List[ProgramNode], files: List[FileInfo]):
        for program_node in program_nodes:
            program_node.update_files_info(files)

            for area in program_node.get_area() or []:
                area.update_files_info(files)

                for content in area.get_item() or []:
                    content.update_files_info(files)

    @staticmethod
    def _is_url(path: str) -> bool:
        # Convert to lowercase for case-insensitive matching
        path = path.lower()

        # Regular expression to match URLs
        regex = (
            r"^((https|http)://)"  # Protocol
            r"?(([0-9a-z_!~*'().&=+$%-]+: )?[0-9a-z_!~*'().&=+$%-]+@)?"  # User info
            r"(([0-9]{1,3}\.){3}[0-9]{1,3}"  # IP address
            r"|"  # OR
            r"([0-9a-z_!~*'()-]+\.)*"  # Domain prefix
            r"([0-9a-z][0-9a-z-]{0,61})?[0-9a-z]\."  # Domain name
            r"[a-z]{2,6})"  # TLD
            r"(:[0-9]{1,5})?"  # Port
            r"((/?)|"  # Path separator
            r"(/[0-9a-z_!~*'().;?:@&=+$,%#-]+)+/?)$"  # Path
        )

        return bool(re.match(regex, path))

    @staticmethod
    def _to_json_object(response: str) -> dict:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "message": "failed",
                "data": response
            }

