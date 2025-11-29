# SSH

An ssh agent for Mythic. 

## Why
Instead of running malware, just add a key 🤷‍♂️.

## Current How-To

- Payloads are just ssh private keys
    - These are tied to a username + host + port (actual host:port, not a tunnel)

- Generating a payload will output the public key in the build message

- Manually create a callback to establish the ssh connection
    - If using a tunnel, you must specify within 'ExtraInfo' the tunnel using format `host:port`
    - 'reconnect' will connect in this same way

### How its implemented

SSH lets us utilize control sockets so that the connection is only established once and kept open.

```bash
# when connecting, setup the socket and background
ssh -MS /tmp/ssh_{PayloadUUID}.socket -i {key} -p {port} {user}@{host} -fnNT

# running commands (host is only syntactically required, not used)
ssh -S /tmp/ssh_{PayloadUUID}.socket {host} {command}

# exit
ssh -S /tmp/ssh_{PayloadUUID}.socket -O exit {host}
```

## Current Supported Commands

- ps
- exit
- reconnect

## TODO

- figure out docker container requirments / github build
- optionally upload private keys as part of build
- optionally select previously built private keys?
- more error handling
- file upload/download over the socket
- tunnels (and socks proxy)

### Integrations TODO

- process tree
- file browser
- interactive shell
- socks proxy

