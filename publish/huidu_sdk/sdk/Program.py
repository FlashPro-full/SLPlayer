from typing import List, Optional, Union, Any
from sdk.common.BaseClient import BaseClient
from sdk.data.ProgramNode import ProgramNode


class Program(BaseClient):
    def __init__(self, host_url: Optional[str] = None):
        super().__init__(host_url)
        self.data_ex: Optional[Any] = None

    def set_data_ex(self, obj: Any):
        self.data_ex = obj

    def append(self, device_ids: Union[str, List[str]], program_nodes: Union[ProgramNode, List[ProgramNode]]) -> dict:
        return self._execute_program_command(device_ids, "append", program_nodes)

    def update(self, device_ids: Union[str, List[str]], program_nodes: Union[ProgramNode, List[ProgramNode]]) -> dict:
        return self._execute_program_command(device_ids, "update", program_nodes)

    def replace(self, device_ids: Union[str, List[str]], program_nodes: Union[ProgramNode, List[ProgramNode]]) -> dict:
        return self._execute_program_command(device_ids, "replace", program_nodes)

    def remove(self, device_ids: Union[str, List[str]], program_ids: Union[str, List[str]]) -> dict:
        device_ids_list = self._to_list(device_ids)
        program_ids_list = self._to_list(program_ids)

        program_nodes = []
        for program_id in program_ids_list:
            node = ProgramNode()
            node.id = program_id
            program_nodes.append(node)

        return self.program(
            dev_ids=device_ids_list,
            method="remove",
            program_nodes=program_nodes,
            data_ex=self.data_ex
        )

    def get_program_ids(self, device_ids: Union[str, List[str]]) -> dict:
        device_ids_list = self._to_list(device_ids)
        return self.program(
            dev_ids=device_ids_list,
            method="getAll",
            program_nodes=[],
            data_ex=self.data_ex
        )

    def _execute_program_command(self, device_ids: Union[str, List[str]],
                                 method: str,
                                 program_nodes: Union[ProgramNode, List[ProgramNode]]) -> dict:
        device_ids_list = self._to_list(device_ids)
        program_nodes_list = self._to_list(program_nodes)

        return self.program(
            dev_ids=device_ids_list,
            method=method,
            program_nodes=program_nodes_list,
            data_ex=self.data_ex
        )

    @staticmethod
    def _to_list(value: Union[Any, List[Any]]) -> List[Any]:
        if isinstance(value, list):
            return value
        return [value]