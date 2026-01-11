from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ..agent_code.ssh_helpers import exit_ssh

class ExitArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ExitCommand(CommandBase):
    cmd = "exit"
    needs_admin = False
    help_cmd = "exit"
    description = "Exit the SSH session"
    version = 1
    author = "Spencer Adolph"
    argument_class = ExitArguments
    is_exit = True
    supported_ui_features = ["callback_table:exit"]
    attackmapping = []

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        output, errors = await exit_ssh(taskData)

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
