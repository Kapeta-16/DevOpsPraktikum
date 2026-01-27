FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py app.py

ENV GOOGLE_APPLICATION_CREDENTIALS=/secrets/AccountKey.json

EXPOSE 3000

CMD ["gunicorn", "-b", "0.0.0.0:3000", "app:app"]
