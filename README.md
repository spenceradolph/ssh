# SSH

An ssh agent for Mythic. 

## Why
Instead of running malware, just add a key 🤷‍♂️.

## Current How-To

- Payloads are just ssh private keys
    - These are tied to a username, host, port (actual host:port, not a tunnel)

- Generating a payload will output the public key in the build message

- Manually create a callback to establish the ssh connection
    - If using a tunnel, you must specify within 'ExtraInfo' the tunnel using format `host:port`
    - 'reconnect' will connect in this same way

## Current Supported Commands

- ps
- exit
- reconnect

## TODO

- optionally upload private keys as part of build
- optionally select previously built private keys?
- more error handling

### Integrations TODO

- process tree
- file browser
- interactive shell


