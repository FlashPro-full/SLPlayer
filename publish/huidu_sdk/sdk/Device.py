from sdk.common.BaseClient import BaseClient
from typing import List, Union, Dict, Optional

class Device(BaseClient):
    def get_online_devices(self) -> dict:
        return self.get_device()

    def set_device_name(self, device_id: str, name: str) -> dict:
        return self.set_device_property(device_id, "name", name)

    def set_screen_size(self, device_id: str, width: int, height: int) -> dict:
        properties = {
            "screen.width": str(width),
            "screen.height": str(height)
        }
        return self.set_device_property(device_id, properties)

    def get_device_property(self,
                            ids: Union[str, List[str]],
                            properties: Optional[Union[str, List[str]]] = None) -> dict:
        device_ids = self._normalize_ids(ids)
        property_list = self._normalize_properties(properties)

        return self.device(device_ids, "getDeviceProperty", property_list)

    def set_device_property(self,
                            ids: Union[str, List[str]],
                            properties: Union[str, Dict[str, str]],
                            value: Optional[str] = None) -> dict:
        device_ids = self._normalize_ids(ids)

        if isinstance(properties, str) and value is not None:
            prop_dict = {properties: value}
        elif isinstance(properties, dict):
            prop_dict = properties
        else:
            raise ValueError("Invalid properties format. "
                             "Must be either dict or str (with value parameter)")

        return self.device(device_ids, "setDeviceProperty", prop_dict)

    def get_device_status(self,
                          ids: Union[str, List[str]],
                          keys: Optional[Union[str, List[str]]] = None) -> dict:
        device_ids = self._normalize_ids(ids)
        key_list = self._normalize_properties(keys)

        return self.device(device_ids, "getDeviceStatus", key_list)

    def _normalize_ids(self, ids: Union[str, List[str]]) -> List[str]:
        if isinstance(ids, str):
            return [ids]
        return ids

    def _normalize_properties(self, properties: Union[None, str, List[str]]) -> List[str]:
        if properties is None:
            return []
        if isinstance(properties, str):
            return [properties]
        return properties