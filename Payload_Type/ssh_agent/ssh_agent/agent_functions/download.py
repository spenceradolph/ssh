from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ..agent_code.ssh_helpers import download_file_via_sshfs

class DownloadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="full_path",
                description="path to file",
                type=ParameterType.String
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class DownloadCommand(CommandBase):
    cmd = "download"
    needs_admin = False
    help_cmd = "download"
    description = "Download a file"
    version = 1
    author = "Spencer Adolph"
    argument_class = DownloadArguments
    attackmapping = []
    supported_ui_features = ["file_browser:download"]

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        # command_to_execute = ["cat", taskData.args.get_arg('full_path')]
        # output, errors = run_ssh_command(taskData, command_to_execute)

        output = download_file_via_sshfs(taskData, taskData.args.get_arg('full_path'))

        # TODO: error handling

        # update the file browser and indicate it was downloaded
        await SendMythicRPCFileCreate(MythicRPCFileCreateMessage(
            TaskID=taskData.Task.ID,
            RemotePathOnTarget=taskData.args.get_arg('full_path'),
            FileContents=output,
            IsScreenshot=False,
            IsDownloadFromAgent=True,
        ))

        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=output,
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
