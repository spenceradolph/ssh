import os
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

from ..agent_code.ssh_helpers import run_ssh_command

class LsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="full_path",
                description="absolute path to the file/folder",
                default_value='.',
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class Ls(CommandBase):
    cmd = "ls"
    needs_admin = False
    help_cmd = "ls"
    description = "List current directory"
    version = 1
    author = "Spencer Adolph"
    argument_class = LsArguments
    attackmapping = []
    supported_ui_features = ["file_browser:list"]

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        # TODO: error handling

        payload_uuid = taskData.Payload.UUID
        sshfs_path = f"/mnt/ssh_{payload_uuid}.sshfs"
        local_dir_path = os.path.join(sshfs_path, taskData.args.get_arg('full_path').lstrip("/"))
        path = Path(local_dir_path)

        # i need to surround command with single quotes so that sh -c treats it as a single command
        output, errors = run_ssh_command(taskData, ["ls", "-latr", taskData.args.get_arg('full_path')])
        
        files = []
        for file in path.iterdir():
            files.append(MythicRPCFileBrowserDataChildren(
                Name=file.name,
                IsFile=file.is_file(),
                Permissions=oct(file.stat(follow_symlinks=False).st_mode)[-3:],
                Size=file.stat(follow_symlinks=False).st_size,
                ModifyTime=int(file.stat(follow_symlinks=False).st_mtime),
            ))

        real_parent = f"/{'/'.join(str(path.parent).split('/')[3:])}"

        searched_path = path.name
        if path.name == f"ssh_{payload_uuid}.sshfs":
            searched_path = '/'
            real_parent = ''

        await SendMythicRPCFileBrowserCreate(MythicRPCFileBrowserCreateMessage(
            TaskID=taskData.Task.ID,
            FileBrowser=MythicRPCFileBrowserData(
                Name=searched_path,
                ParentPath=real_parent,  
                IsFile=False,
                Files=files
            )
        ))

        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=output.encode('utf-8'),
        ))

        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True, # TODO: fix error handling from ssh helper function
            Completed=True,
            Stdout=output,
            Stderr=errors
        )
        return response


    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
