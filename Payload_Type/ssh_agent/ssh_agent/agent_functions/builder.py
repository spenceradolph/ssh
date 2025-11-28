from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


class SSH(PayloadType):
    name = "ssh"
    file_extension = ""
    author = "Spencer Adolph"
    supported_os = [
        SupportedOS.Linux
    ]
    wrapper = False
    wrapped_payloads = []
    note = "This payload connects to ssh servers."
    supports_dynamic_loading = False
    mythic_encrypts = False
    translation_container = None
    agent_path = pathlib.Path(".") / "ssh_agent"
    agent_icon_path = agent_path / "agent_functions" / "ssh.svg"
    agent_code_path = agent_path / "agent_code"
    c2_profiles = ["ssh"]
    build_parameters = [
        # TODO: build parameters (key, user, host, port)
    ]

    async def build(self) -> BuildResponse:
        # TODO: generate an ssh key and track it to use later when connecting
        resp = BuildResponse(status=BuildStatus.Success)
        return resp
