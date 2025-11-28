FROM itsafeaturemythic/mythic_python_base:latest

# RUN pip install paramiko
RUN apt-get install -y openssh-client

WORKDIR /Mythic/

CMD ["python3", "main.py"]