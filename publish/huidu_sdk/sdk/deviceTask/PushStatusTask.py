from typing import Union, List, Dict, Optional, Any
from sdk.common.BaseClient import BaseClient


class PushStatusTask(BaseClient):
    def push_status(
            self,
            device_ids: Union[str, List[str]],
            key_values: Union[str, Dict[str, str]],
            value: Optional[str] = None
    ) -> Dict[str, Any]:
        device_ids = [device_ids] if isinstance(device_ids, str) else list(device_ids)

        if isinstance(key_values, str):
            if value is None:
                raise ValueError("When key_values is a string, the value parameter must be provided")
            payload = {key_values: value}
        else:
            payload = dict(key_values)

        if not payload:
            raise ValueError("At least one key-value pair needs to be provided")

        return self.device(device_ids, "pushStatus", payload)

    def push_single_status(
            self,
            device_id: str,
            key: str,
            value: str
    ) -> Dict[str, Any]:
        return self.push_status(device_id, key, value)

    def push_multiple_status(
            self,
            device_ids: List[str],
            status_map: Dict[str, str]
    ) -> Dict[str, Any]:
        return self.push_status(device_ids, status_map)