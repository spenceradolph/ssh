# SSH

An ssh (wrapper) agent for Mythic. Great for LOTL.

## Overview

The Mythic 'payload' is a generated private key. This is tied to a target using username+host+port. Building will output the corresponding public key to enable access. Once added to the target's authorized_keys, generate a (fake) callback to establish the connection and use.

## Installing

Standard Install:
```bash
# Current local tunnel port range defined with MYTHIC_SERVER_DYNAMIC_PORTS (defaults to 7000-7010)
# Edit Mythic/.env and set MYTHIC_DOCKER_NETWORKING="host" to allow any dynamic port range for tunnels

# install
sudo ./mythic-cli install github https://github.com/spenceradolph/ssh
```


For local development:
```bash
# apt install -y openssh-client sshfs
git clone https://github.com/spenceradolph/ssh
cd ssh

# edit ./Payload_Type/ssh_agent/rabbitmq_config.json to point to mythic install

python3 -m venv ./.venv
source ./.venv/bin/activate
pip install mythic_container pytz
python3 ./Payload_Type/ssh_agent/main.py
# see the service show up in Mythic!
# Or alternatively, run using the vscode debugger in order to set breakpoints and easily restart the service when making changes.
```

### How its implemented

SSH lets us utilize control sockets so that the connection is only established once and kept open.

```bash
# when connecting, setup the socket and background
ssh -MS /tmp/ssh_{PayloadUUID}.socket -i {key_generated_by_mythic} -p {port} {user}@{host} -fnNT
# running commands (host is only syntactically required, not used) through the socket
ssh -S /tmp/ssh_{PayloadUUID}.socket {host} {command_passed_from_mythic}
# sshfs is also used for easier file system interactions
sshfs a:/ /mnt/ssh_{payload_uuid}.sshfs/ -o ssh_command='ssh -S /tmp/ssh_{payload_uuid}.socket'
```

## Current Supported Commands

- ps
    - integrated with process browser
- ls
    - integrated with file browser (list)
    - ex: `ls /etc`
- download
    - integrated with file browser (download)
    - ex: `download /etc/shadow`
- sh (pass any command to /bin/sh -c)
    - ex: `sh cat /var/log/syslog | egrep thing`
- interactive
    - integrated with interactive tasking ui
    - spawns /bin/bash on target
- tunnel_list
- tunnel_add, tunnel_add_proxy
- tunnel_remove
- exit
- reconnect

> [!TIP]  
> If connecting through a tunnel, create the callback with 'ExtraInfo' format `host:port`

### TODO

- file upload via file browser
- process kill via process browser
- look into password support (instead of key based)
- specify keys when building payload
- community bof support

### Things to request from Cody?

- sort process browser by start time (and/or filter by it?)
- last column in process should stick to right edge (ui preference)
- figure out deleted process updates to tree (and deleted files update)
