FROM python:3.9-slim

WORKDIR /usr/src/app

COPY ../*.py .
COPY ../requirements.txt .
COPY ../credentials.json .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./bot.py"]