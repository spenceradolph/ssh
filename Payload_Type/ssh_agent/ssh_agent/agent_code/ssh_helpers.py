from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import subprocess
import os


async def connect_to_ssh(payload_uuid: str, username: str, connect_ip: str, connect_port: str):
    ssh_key_payload = await SendMythicRPCPayloadGetContent(MythicRPCPayloadGetContentMessage(PayloadUUID=payload_uuid))

    # get the key that will be used to connect, write to file for ssh to use
    ssh_key = ssh_key_payload.Content.decode("utf-8")
    with open(f"/tmp/ssh_{payload_uuid}.key", "w") as file:
        file.write(ssh_key)

    os.chmod(f"/tmp/ssh_{payload_uuid}.key", 0o600)

    try:
        proc = subprocess.run([
            f"ssh -M -S /tmp/ssh_{payload_uuid}.socket -i /tmp/ssh_{payload_uuid}.key -fnNT -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -p {connect_port} {username}@{connect_ip}"
        ], capture_output=True, text=True, timeout=30, shell=True)
        output = proc.stdout
        errors = proc.stderr
    except Exception as e:
        output = ""
        errors = str(e)

    # now established, key no longer needed on disk
    os.remove(f"/tmp/ssh_{payload_uuid}.key")

    return output, errors


def exit_ssh(taskData: MythicCommandBase.PTTaskMessageAllData):
    payload_uuid = taskData.Payload.UUID
    socket_path = ["-S", f"/tmp/ssh_{payload_uuid}.socket"]

    # exit using the socket
    exit_options = ["-O", "exit"]

    try:
        proc = subprocess.run([
            "ssh",
            *socket_path,
            *exit_options,
            "dummyhost_required_for_ssh_syntax",
        ], capture_output=True, text=True, timeout=30)
        output = proc.stdout
        errors = proc.stderr
    except Exception as e:
        output = ""
        errors = str(e)

    return output, errors


def run_ssh_command(taskData: MythicCommandBase.PTTaskMessageAllData, command_to_execute: list[str]):
    payload_uuid = taskData.Payload.UUID
    socket_path = ["-S", f"/tmp/ssh_{payload_uuid}.socket"]

    if not os.path.exists(f"/tmp/ssh_{payload_uuid}.socket"):
        output = ""
        errors = "SSH session not established. Please run the 'reconnect' command first."
        return output, errors

    try:
        proc = subprocess.run([
            "ssh",
            *socket_path,
            "dummyhost_required_for_ssh_syntax",
            *command_to_execute
        ], capture_output=True, text=True, timeout=30)
        output = proc.stdout
        errors = proc.stderr
    except Exception as e:
        output = ""
        errors = str(e)

    return output, errors

