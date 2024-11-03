FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY application.py application.py

EXPOSE 5000

ENTRYPOINT [ "flask", "--app", "application.py", "--debug", "run", "--host", "0.0.0.0"]
