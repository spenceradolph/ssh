import mythic_container
import asyncio

# import the ssh agent
import ssh_agent

# import the ssh c2 'profile'
from ssh_profile.ssh import *

mythic_container.mythic_service.start_and_run_forever()