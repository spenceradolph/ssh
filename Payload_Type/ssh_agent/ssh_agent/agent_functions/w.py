from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ..agent_code.ssh_helpers import run_ssh_command

class WArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class WCommand(CommandBase):
    cmd = "w"
    needs_admin = False
    help_cmd = "w"
    description = "Run w command"
    version = 1
    author = "Spencer Adolph"
    argument_class = WArguments
    attackmapping = []
    supported_ui_features = []

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        command_to_execute = ["w"]
        output, errors = run_ssh_command(taskData, command_to_execute)

        # TODO: error handling

        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=output,
        ))

        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True, # TODO: fix error handling from ssh helper function
            Completed=True,
            Stdout=output,
            Stderr=''
        )
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
