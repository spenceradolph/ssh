from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import base64

from ..agent_code.ssh_helpers import run_ssh_command

class TunnelRemoveArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        # direction (forward/reverse), listen_interface, listen_port, target_ip, target_port, description
        self.args = [
            CommandParameter(
                name="tunnel_id",
                type=ParameterType.Number,
                description="ID of the tunnel to remove"
            )
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class TunnelRemove(CommandBase):
    cmd = "tunnel_remove"
    needs_admin = False
    help_cmd = "tunnel_remove"
    description = "Remove a tunnel"
    version = 1
    author = "Spencer Adolph"
    argument_class = TunnelRemoveArguments
    attackmapping = []

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        tunnel_list = await SendMythicRPCAgentStorageSearch(MythicRPCAgentStorageSearchMessage(
            SearchUniqueID=f'tunnels_{taskData.Payload.UUID}',
        ))

        tunnel_list_from_mythic = tunnel_list.AgentStorageMessages[0]['data']
        decoded_tunnel_list = base64.b64decode(tunnel_list_from_mythic).decode('utf-8')
        tunnel_list: list = json.loads(decoded_tunnel_list)

        # TODO: look to see if tunnel already exists?

        tunnel_id = taskData.args.get_arg('tunnel_id')

        tunnel_to_remove = tunnel_list.pop(tunnel_id)

        direction = '-L' if tunnel_to_remove['direction'] == 'forward' else '-R'
        listen_interface = tunnel_to_remove['listen_interface']
        listen_port = tunnel_to_remove['listen_port']
        target_ip = tunnel_to_remove['target_ip']
        target_port = tunnel_to_remove['target_port']

        command_to_execute = ['-O', 'cancel', direction, f"{listen_interface}:{listen_port}:{target_ip}:{target_port}"]
        output, errors = run_ssh_command(taskData, command_to_execute)

        await SendMythicRPCAgentStorageRemove(MythicRPCAgentStorageRemoveMessage(
            UniqueID=f'tunnels_{taskData.Payload.UUID}',
        ))
        await SendMythicRPCAgentStorageCreate(MythicRPCAgentstorageCreateMessage(
            UniqueID=f'tunnels_{taskData.Payload.UUID}',
            DataToStore=json.dumps(tunnel_list).encode('utf-8'),
        ))

        output = "Tunnel removed successfully."

        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=output.encode('utf-8'),
        ))

        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
            Completed=True,
            Stdout=output,
            Stderr=''
        )
        return response


    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
