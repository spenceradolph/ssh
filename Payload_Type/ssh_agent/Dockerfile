FROM itsafeaturemythic/mythic_python_base:latest

# TODO: figure out if this needs to run with SYS_ADMIN and DEVICE_FUSE capabilities
RUN apt-get install -y openssh-client sshfs

WORKDIR /Mythic/

CMD ["python3", "main.py"]