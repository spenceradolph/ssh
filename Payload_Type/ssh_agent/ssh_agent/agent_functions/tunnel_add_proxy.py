from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import base64

from ..agent_code.ssh_helpers import run_ssh_command

class TunnelAddProxyArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        # direction (forward/reverse), listen_interface, listen_port, target_ip, target_port, description
        self.args = [
            CommandParameter(
                name="proxy_port",
                type=ParameterType.String,
                description="proxy_port",
                default_value="9050",
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )]
            ),
            CommandParameter(
                name="proxy_interface",
                type=ParameterType.String,
                description="proxy_interface",
                default_value="127.0.0.1",
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class TunnelAddProxy(CommandBase):
    cmd = "tunnel_add_proxy"
    needs_admin = False
    help_cmd = "tunnel_add_proxy"
    description = "Add a new proxy tunnel"
    version = 1
    author = "Spencer Adolph"
    argument_class = TunnelAddProxyArguments
    attackmapping = []

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        tunnel_list = await SendMythicRPCAgentStorageSearch(MythicRPCAgentStorageSearchMessage(
            SearchUniqueID=f'tunnels_{taskData.Payload.UUID}',
        ))

        tunnel_list_from_mythic = tunnel_list.AgentStorageMessages[0]['data']
        decoded_tunnel_list = base64.b64decode(tunnel_list_from_mythic).decode('utf-8')
        tunnel_list: list = json.loads(decoded_tunnel_list)

        # TODO: look to see if tunnel already exists?

        proxy_port = taskData.args.get_arg('proxy_port')
        proxy_interface = taskData.args.get_arg('proxy_interface')

        command_to_execute = ['-O', 'forward', '-D', f"{proxy_interface}:{proxy_port}"]
        output, errors = run_ssh_command(taskData, command_to_execute)

        tunnel_list.append({
            "direction": 'dynamic',
            'proxy_interface': proxy_interface,
            "proxy_port": proxy_port,
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
