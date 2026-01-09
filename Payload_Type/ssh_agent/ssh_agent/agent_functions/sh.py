from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

from ..agent_code.ssh_helpers import run_ssh_command

class ShArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="command",
                type=ParameterType.String,
                description="Command to run"
            )
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class Sh(CommandBase):
    cmd = "sh"
    needs_admin = False
    help_cmd = "sh"
    description = "Execute a shell command"
    version = 1
    author = "Spencer Adolph"
    argument_class = ShArguments
    attackmapping = []

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        command = taskData.args.get_arg('command')
        quoted_command = f"'{command}'"
        # i need to surround command with single quotes so that sh -c treats it as a single command
        command_to_execute = ['/bin/sh', '-c'] + quoted_command.split(" ")
        output, errors = run_ssh_command(taskData, command_to_execute)

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
