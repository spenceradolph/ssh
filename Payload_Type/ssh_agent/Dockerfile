FROM itsafeaturemythic/mythic_python_base:latest

RUN apt-get update && apt-get install -y openssh-client sshfs

RUN pip install pytz

WORKDIR /Mythic/

CMD ["python3", "main.py"]