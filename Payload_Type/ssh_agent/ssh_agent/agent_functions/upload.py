from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ..agent_code.ssh_helpers import upload_file_via_sshfs

class UploadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="local_path",
                description="local path to file",
                type=ParameterType.String
            ),
            CommandParameter(
                name="remote_path",
                description="remote path to file",
                type=ParameterType.String
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class UploadCommand(CommandBase):
    cmd = "upload"
    needs_admin = False
    help_cmd = "upload"
    description = "Upload a file"
    version = 1
    author = "Spencer Adolph"
    argument_class = UploadArguments
    attackmapping = []
    supported_ui_features = []

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        output = upload_file_via_sshfs(taskData, taskData.args.get_arg('local_path'), taskData.args.get_arg('remote_path'))

        # TODO: error handling

        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response='File uploaded successfully.'.encode('utf-8'),
        ))

        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True, # TODO: fix error handling from ssh helper function
            Completed=True,
            Stdout='',
            Stderr=''
        )
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
