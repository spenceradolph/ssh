from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ..agent_code.ssh_helpers import connect_to_ssh

class ReconnectArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ReconnectCommand(CommandBase):
    cmd = "reconnect"
    needs_admin = False
    help_cmd = "reconnect"
    description = "Reconnect the SSH session"
    version = 1
    author = "Spencer Adolph"
    argument_class = ReconnectArguments
    attackmapping = []

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        payload_uuid = taskData.Payload.UUID
        username = taskData.BuildParameters[0].Value
        connect_ip, connect_port = taskData.Callback.ExtraInfo.split(":")

        output, errors = await connect_to_ssh(payload_uuid, username, connect_ip, connect_port)

        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=(output or "").encode("UTF8"),
        ))

        WasSuccess = False
        if output == "":
            WasSuccess = True

        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=WasSuccess,
            Completed=WasSuccess,
            Stdout=output,
            Stderr=errors
        )
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
