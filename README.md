# SSH

An ssh agent for Mythic.

### Current How-To

- manually build an ssh_agent payload
- manually create an ssh_agent callback
    - TODO: specify host, user, pass in this part?
- task normally, each task will connect, run command, then show the output

### TODO: figure out how to best implement

- when building a payload, should there be 1 payload for all ssh 'callbacks' that exist?
- is it useful to 'build' this part of the 'agent' prior to connecting / setting up
    - can generate ssh keys / passwords / usernames here
    - instructions for how to install
- with callbacks, technically the thing that is unique among all of them will be the ip to connect to
    - 1 payload (with 1 key), could be used on multiple computers
    - 1 user/pass could be installed on multiple computers
    - doesn't make sense to have more than 1 callback for the same server

