from asyncio.subprocess import Process
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from mythic_container.LoggingBase import *
from mythic_container.MythicGoRPC import *
from mythic_container.PayloadBuilder import *

import asyncio

shell_global_dict = {}

class InteractiveArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class Interactive(CommandBase):
    cmd = "interactive"
    needs_admin = False
    help_cmd = "interactive"
    description = "Interactive Shell"
    version = 1
    author = "Spencer Adolph"
    argument_class = InteractiveArguments
    attackmapping = []
    supported_ui_features = ["task_response:interactive"]

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        await create_shell(taskData)

        taskResponse = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
            Completed=True
        )
        return taskResponse

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        pass


async def create_shell(taskData: MythicCommandBase.PTTaskMessageAllData):
    proc = await asyncio.create_subprocess_exec(
        'ssh', '-S', f"/tmp/ssh_{taskData.Payload.UUID}.socket", "dummy", "/bin/bash",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # save it for later, need to be able to write user input to it
    shell_global_dict['proc'] = proc

    async def read_shell_output():
        async for line in proc.stdout:
            await MythicRPC().execute("create_output", task_id=taskData.Task.ID, output=line.decode('utf-8'))
            
    # TODO: figure out if this is running forever and needs a mechanism to stop it
    asyncio.create_task(read_shell_output())


class InteractiveCommandReader(Log):
    name = "InteractiveCommandReader"
    description = "Reads commands from Mythic and sends them to the interactive shell"

    async def new_task(self, msg: LoggingMessage) -> None:
        print('got something')
        if (not msg.Data.IsInteractiveTask):
            return
        if msg.Data.DisplayParams == '':
            return
        
        # TODO: prevent follow up tasks after 'exit'

        # logger.info(msg)

        # TODO: check if for this session / task, etc...

        # TODO: get the python object that has access to the shell
        proc: Process = shell_global_dict['proc']

        proc.stdin.write(msg.Data.DisplayParams.encode('utf-8'))
        await proc.stdin.drain()

        if msg.Data.DisplayParams == 'exit\n':           
            await SendMythicRPCTaskUpdate(MythicRPCTaskUpdateMessage(
                TaskID=msg.Data.ID,
                UpdateCompleted=True,
                UpdateStatus="finished",
            ))
            return

        # TODO: get control characters from InteractiveMessageType
        # if msg.Data.InteractiveTaskType != 0:
        #     data.Data = InteractiveMessageType[msg.Data.InteractiveTaskType][1].to_bytes()
        # else:
        #     data.Data = f"{msg.Data.DisplayParams}".encode('utf-8')
        # await _tunnelStream.write(data)
        
        await SendMythicRPCTaskUpdate(MythicRPCTaskUpdateMessage(
            TaskID=msg.Data.ID,
            UpdateCompleted=True,
            UpdateStatus="success",
        ))
