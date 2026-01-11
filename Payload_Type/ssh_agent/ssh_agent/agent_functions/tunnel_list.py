from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import base64

from ..agent_code.ssh_helpers import run_ssh_command

class TunnelListArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class TunnelList(CommandBase):
    cmd = "tunnel_list"
    needs_admin = False
    help_cmd = "tunnel_list"
    description = "List Tunnels Currently Active"
    version = 1
    author = "Spencer Adolph"
    argument_class = TunnelListArguments
    attackmapping = []

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        tunnel_list = await SendMythicRPCAgentStorageSearch(MythicRPCAgentStorageSearchMessage(
            SearchUniqueID=f'tunnels_{taskData.Payload.UUID}',
        ))

        tunnel_list_from_mythic = tunnel_list.AgentStorageMessages[0]['data']
        decoded_tunnel_list = base64.b64decode(tunnel_list_from_mythic).decode('utf-8')
        tunnel_list = json.loads(decoded_tunnel_list)

        output = ""
        if len(tunnel_list) == 0:
            output = "No active tunnels found."
            errors = ""
        else:
            output = "Active Tunnels:\n"
            for index, tunnel in enumerate(tunnel_list):
                arrow_direction = ">" if tunnel['direction'] == "forward" else "<"
                output += f"tunnel_id: {index} - {tunnel['direction']} {arrow_direction} {tunnel['listen_interface']}:{tunnel['listen_port']}:{tunnel['target_ip']}:{tunnel['target_port']} - {tunnel['description']}\n"
            errors = ""


        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=output.encode('utf-8'),
        ))

        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
            Completed=True,
            Stdout=output,
            Stderr=errors
        )
        return response


    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
