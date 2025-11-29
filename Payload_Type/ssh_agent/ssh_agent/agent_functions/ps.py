from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from datetime import datetime
import pytz
from ..agent_code.ssh_helpers import run_ssh_command

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
    supported_ui_features = ["process_browser:list"]

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        # cmd is at the end because it can contain spaces, so we join everything after the other fields to capture it
        command_to_execute = ["ps", "--no-headers", "-ww", "-eo", "pid,ppid,user,comm,lstart,cmd"]
        output, errors = run_ssh_command(taskData, command_to_execute)

        processes = []
        for process in output.splitlines():
            process_info = process.split()
            pid = process_info[0]
            ppid = process_info[1]
            user = process_info[2]
            comm = process_info[3]
            lstart = " ".join(process_info[4:9])
            cmd = " ".join(process_info[9:])

            start_time = datetime.strptime(lstart, "%a %b %d %H:%M:%S %Y").replace(tzinfo=pytz.utc)
            epoch_time = int(start_time.timestamp())

            processes.append(
                MythicRPCProcessCreateData(
                    Host=taskData.Callback.Host,
                    ProcessID=int(pid),
                    ParentProcessID=int(ppid),
                    Name=comm,
                    User=user,
                    CommandLine=cmd,
                    StartTime=epoch_time * 1000, # in milliseconds
                    # UpdateDeleted=False
                )
            )
        
        await SendMythicRPCProcessCreate(MythicRPCProcessesCreateMessage(
            TaskID=taskData.Task.ID,
            Processes=processes,
        ))

        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=(output or "").encode("UTF8"),
        ))

        WasSuccess = False
        if errors == "":
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
