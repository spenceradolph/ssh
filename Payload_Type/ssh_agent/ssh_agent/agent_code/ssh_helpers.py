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

    # add an sshfs for file transfer ease
    os.mkdir(f"/mnt/ssh_{payload_uuid}.sshfs")

    try:
        proc = subprocess.run([
            f"sshfs a:/ /mnt/ssh_{payload_uuid}.sshfs/ -o ssh_command='ssh -S /tmp/ssh_{payload_uuid}.socket'"
        ], capture_output=True, text=True, timeout=30, shell=True, start_new_session=True)
        output = proc.stdout
        errors = proc.stderr
    except Exception as e:
        output = ""
        errors = str(e)

    return output, errors


def exit_ssh(taskData: MythicCommandBase.PTTaskMessageAllData):
    payload_uuid = taskData.Payload.UUID
    socket_path = ["-S", f"/tmp/ssh_{payload_uuid}.socket"]

    # exit using the socket
    exit_options = ["-O", "exit"]

    # rm the sshfs first, else ssh will not exit fully?
    os.system(f"umount /mnt/ssh_{payload_uuid}.sshfs")

    # exit ssh
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

    os.rmdir(f"/mnt/ssh_{payload_uuid}.sshfs")
    
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


def download_file_via_sshfs(taskData: MythicCommandBase.PTTaskMessageAllData, remote_path: str) -> bytes:
    payload_uuid = taskData.Payload.UUID
    sshfs_path = f"/mnt/ssh_{payload_uuid}.sshfs"

    local_file_path = os.path.join(sshfs_path, remote_path.lstrip("/"))

    # TODO: standardize error handling (example, doesn't currently handle if file doesn't exist....etc)

    try:
        with open(local_file_path, "rb") as file:
            file_contents = file.read()
        return file_contents
    except Exception as e:
        return b""
    

# def directory_list_via_sshfs(taskData: MythicCommandBase.PTTaskMessageAllData, remote_path: str) -> str:
#     payload_uuid = taskData.Payload.UUID
#     sshfs_path = f"/tmp/ssh_{payload_uuid}.sshfs"
#     local_dir_path = os.path.join(sshfs_path, remote_path.lstrip("/"))
#     return list_directory(local_dir_path)
    

# def list_directory(path_str):
#     path = Path(path_str)
    
#     if not path.exists():
#         print(f"Error: Directory '{path}' does not exist.")
#         return ''
#     if not path.is_dir():
#         print(f"Error: '{path}' is not a directory.")
#         return ''

#     print(f"Contents of: {path.resolve()}\n")
#     print(f"{'Name':<40} {'Type':<10} {'Size':>12} {'Modified':<20}")
#     print("-" * 82)

#     # Sort items: directories first, then files
#     for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
#         if item.is_dir():
#             size = "<DIR>"
#             type_label = "directory"
#         else:
#             size_bytes = item.stat().st_size
#             # Human-readable size
#             for unit in ['B', 'KB', 'MB', 'GB']:
#                 if size_bytes < 1024:
#                     size = f"{size_bytes:.1f} {unit}"
#                     break
#                 size_bytes /= 1024
#             else:
#                 size = f"{size_bytes:.1f} TB"
#             type_label = "file"

#         # Modified time in nice format
#         mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item.stat().st_mtime))

#         print(f"{item.name:<40} {type_label:<10} {size:>12} {mtime}")

