
FROM python:3

run mkdir /app
COPY requirements.txt /app

RUN pip install -r /app/requirements.txt

COPY app.py /app/

cmd "python /app/app.py"