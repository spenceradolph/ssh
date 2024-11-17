from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

import paramiko


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
        # TODO: abstract this away in a helper library / folder, don't repeat this in each 'task'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('10.0.0.21', username='ubuntu', password='ubuntu')
        stdin, stdout, stderr = ssh.exec_command('ps -ef')
        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')
        ssh.close()
        
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=output.encode("UTF8"),
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
