from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import subprocess

class PsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class PsCommand(CommandBase):
    cmd = "ps"
    needs_admin = False
    help_cmd = "ps"
    description = "Get process listing"
    version = 1
    author = "Spencer Adolph"
    argument_class = PsArguments
    attackmapping = []

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        socket_path = ["-S", "/tmp/ssh_socket"]
        default_options = ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-T"]
        command_to_execute = ["ps", "-efH"]

        try:
            proc = subprocess.run([
                "ssh",
                *socket_path,
                *default_options,
                "dummyhost_required_for_ssh_syntax",
                *command_to_execute
            ], capture_output=True, text=True, timeout=30)
            output = proc.stdout
            errors = proc.stderr
        except Exception as e:
            output = ""
            errors = str(e)

        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=(output or "").encode("UTF8"),
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
