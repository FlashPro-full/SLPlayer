from typing import Union, List
from sdk.common.BaseClient import BaseClient
from sdk.data.task.PeriodicTaskInfo import PeriodicTaskInfo


class PeriodicTask(BaseClient):
    def get_periodic_task(self, device_ids: Union[str, List[str]]) -> dict:
        if isinstance(device_ids, str):
            device_ids = [device_ids]

        return self.device(device_ids, "getPeriodicTask", None)

    def set_periodic_task(
            self,
            device_ids: Union[str, List[str]],
            task_infos: Union[PeriodicTaskInfo, List[PeriodicTaskInfo]]
    ) -> dict:
        if isinstance(device_ids, str):
            device_ids = [device_ids]

        if isinstance(task_infos, PeriodicTaskInfo):
            task_infos = [task_infos]

        task_data = [task.to_dict() for task in task_infos]

        return self.device(device_ids, "setPeriodicTask", task_data)