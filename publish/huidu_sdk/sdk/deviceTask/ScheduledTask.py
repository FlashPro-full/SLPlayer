from sdk.common.BaseClient import BaseClient
from typing import Union, List, Dict, Optional
from sdk.data.task.ScheduledTaskInfo import ScheduledTaskInfo

class ScheduledTask(BaseClient):
    def get_scheduled_task(
            self,
            device_ids: Union[str, List[str]],
            scheduled_tasks: Optional[Union[str, List[str]]] = None
    ) -> dict:
        if isinstance(device_ids, str):
            device_ids = [device_ids]

        if scheduled_tasks is not None:
            if isinstance(scheduled_tasks, str):
                scheduled_tasks = [scheduled_tasks]

        return self.device(device_ids, "getScheduledTask", scheduled_tasks)

    def set_scheduled_task(
            self,
            device_ids: Union[str, List[str]],
            task_infos: Dict[str, List[ScheduledTaskInfo]]
    ) -> dict:
        if isinstance(device_ids, str):
            device_ids = [device_ids]

        serializable_data = {}
        for task_id, tasks in task_infos.items():
            serializable_data[task_id] = [task.to_dict() for task in tasks]

        return self.device(device_ids, "setScheduledTask", serializable_data)

    def get_scheduled_task_for_device(self, device_id: str) -> dict:
        return self.get_scheduled_task(device_id)

    def set_scheduled_task_for_device(
            self,
            device_id: str,
            task_group: str,
            tasks: List[ScheduledTaskInfo]
    ) -> dict:
        return self.set_scheduled_task(
            device_id,
            {task_group: tasks}
        )