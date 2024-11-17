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
    build_parameters = []
    c2_profiles = []

    async def build(self) -> BuildResponse:
        resp = BuildResponse(status=BuildStatus.Success)
        return resp
