FROM python:3.11

RUN apt-get update -y && apt-get install socat -y

WORKDIR /app
COPY app .
COPY requirements.txt .
RUN useradd -ms /bin/bash ctf
RUN pip install -r requirements.txt

USER ctf

EXPOSE 5000

ENTRYPOINT ["python", "server.py"]