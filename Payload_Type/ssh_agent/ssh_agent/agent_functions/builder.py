from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import subprocess
import os
from ..agent_code.ssh_helpers import connect_to_ssh


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
    c2_profiles = []
    build_parameters = [
        BuildParameter(
            name="username",
            parameter_type=BuildParameterType.String,
            default_value="root",
            description="Username to use during authentication.",
            required=True
        ),
        BuildParameter(
            name="host",
            parameter_type=BuildParameterType.String,
            default_value="127.0.0.1",
            description="Host to connect to.",
            required=True
        ),
        BuildParameter(
            name="port",
            parameter_type=BuildParameterType.Number,
            default_value="22",
            description="Port to connect to.",
            required=True
        ),
    ]

    async def build(self) -> BuildResponse:
        if os.path.exists('/tmp/ssh_agent_key'):
            os.remove('/tmp/ssh_agent_key')

        if os.path.exists('/tmp/ssh_agent_key.pub'):
            os.remove('/tmp/ssh_agent_key.pub')

        proc = subprocess.run([
            "ssh-keygen -b 2048 -t rsa -f /tmp/ssh_agent_key -q -N ''"
        ], capture_output=True, text=True, timeout=30, shell=True)

        ssh_key_file = open("/tmp/ssh_agent_key", "r").read()

        ssh_pub_key_file = open("/tmp/ssh_agent_key.pub", "r").read()
        thing_to_echo = ' '.join(ssh_pub_key_file.split(' ')[:-1])

        os.remove("/tmp/ssh_agent_key")
        os.remove("/tmp/ssh_agent_key.pub")

        resp = BuildResponse(
            status=BuildStatus.Success,
            payload=ssh_key_file.encode("utf-8"),
            build_message=f"\nUse the following command to add the key:\necho '{thing_to_echo}' >> ~/.ssh/authorized_keys",
        )
        return resp
    
    async def on_new_callback(self, newCallback: PTOnNewCallbackAllData) -> PTOnNewCallbackResponse:
        # create the ssh connection in the background
        connect_ip, connect_port = newCallback.Callback.ExtraInfo.split(":")
        username = newCallback.BuildParameters[0].Value
        payload_uuid = newCallback.Payload.UUID

        output, errors = await connect_to_ssh(payload_uuid, username, connect_ip, connect_port)

        return PTOnNewCallbackResponse(AgentCallbackID=newCallback.Callback.AgentCallbackID, Success=True)
