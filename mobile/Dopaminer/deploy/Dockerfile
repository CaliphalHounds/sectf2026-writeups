FROM python:3.11

RUN apt-get update -y

WORKDIR /app
COPY app .
COPY requirements.txt .
RUN useradd -ms /bin/bash ctf
RUN pip install -r requirements.txt

USER ctf

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "-t", "100", "-b", "0.0.0.0:5000", "server:app"]
