from mythic_container.C2ProfileBase import *
from pathlib import Path


class SSH(C2Profile):
    name = "ssh"
    description = "Its literally ssh."
    author = "Spencer Adolph"

    semver = "0.0.1"
    is_server_routed = False
    agent_icon_path = Path(".") / "ssh_agent" / "agent_functions" / "ssh.svg"

    is_p2p = True
    server_folder_path = Path(".") / "server_folder_path_that_doesnt_exist"
    server_binary_path = server_folder_path / "server_that_does_not_exist.py"

    parameters = [
        C2ProfileParameter(name="username",
                        parameter_type=ParameterType.String,
                        description="Username to use during authentication.",
                        default_value="root", required=True),
        C2ProfileParameter(name="host",
                        parameter_type=ParameterType.String,
                        description="Host to connect to.",
                        default_value="127.0.0.1", required=True),
        C2ProfileParameter(name="port",
                        parameter_type=ParameterType.Number,
                        description="Port to connect to.",
                        default_value="22", required=True),
    ]
