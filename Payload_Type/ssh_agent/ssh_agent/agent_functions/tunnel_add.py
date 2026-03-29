from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import base64

from ..agent_code.ssh_helpers import run_ssh_command

class TunnelAddArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        # direction (forward/reverse), listen_interface, listen_port, target_ip, target_port, description
        self.args = [
            CommandParameter(
                name="direction",
                type=ParameterType.ChooseOne,
                description="Direction of the tunnel (forward/reverse)",
                choices=["forward", "reverse"]
            ),
            CommandParameter(
                name="listen_interface",
                type=ParameterType.String,
                description="Interface to listen on"
            ),
            CommandParameter(
                name="listen_port",
                type=ParameterType.String,
                description="Port to listen on"
            ),
            CommandParameter(
                name="target_ip",
                type=ParameterType.String,
                description="Target IP address"
            ),
            CommandParameter(
                name="target_port",
                type=ParameterType.String,
                description="Target port"
            ),
            CommandParameter(
                name="description",
                type=ParameterType.String,
                description="Description of the tunnel",
            )
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class TunnelAdd(CommandBase):
    cmd = "tunnel_add"
    needs_admin = False
    help_cmd = "tunnel_add"
    description = "Add a new tunnel"
    version = 1
    author = "Spencer Adolph"
    argument_class = TunnelAddArguments
    attackmapping = []

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        tunnel_list = await SendMythicRPCAgentStorageSearch(MythicRPCAgentStorageSearchMessage(
            SearchUniqueID=f'tunnels_{taskData.Payload.UUID}',
        ))

        tunnel_list_from_mythic = tunnel_list.AgentStorageMessages[0]['data']
        decoded_tunnel_list = base64.b64decode(tunnel_list_from_mythic).decode('utf-8')
        tunnel_list: list = json.loads(decoded_tunnel_list)

        # TODO: look to see if tunnel already exists?

        direction = '-L' if taskData.args.get_arg('direction') == 'forward' else '-R'
        listen_interface = taskData.args.get_arg('listen_interface')
        listen_port = taskData.args.get_arg('listen_port')
        target_ip = taskData.args.get_arg('target_ip')
        target_port = taskData.args.get_arg('target_port')
        description = taskData.args.get_arg('description')

        command_to_execute = ['-O', 'forward', direction, f"{listen_interface}:{listen_port}:{target_ip}:{target_port}"]
        output, errors = run_ssh_command(taskData, command_to_execute)

        tunnel_list.append({
            "direction": taskData.args.get_arg('direction'),
            'listen_interface': listen_interface,
            "listen_port": listen_port,
            "target_ip": target_ip,
            "target_port": target_port,
            "description": description
        })

        thing_to_store = json.dumps(tunnel_list)

        await SendMythicRPCAgentStorageRemove(MythicRPCAgentStorageRemoveMessage(
            UniqueID=f'tunnels_{taskData.Payload.UUID}',
        ))

        response = await SendMythicRPCAgentStorageCreate(MythicRPCAgentstorageCreateMessage(
            UniqueID=f'tunnels_{taskData.Payload.UUID}',
            DataToStore=thing_to_store.encode('utf-8'),
        ))

        output = "Tunnel added successfully."

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
