FROM python:3.10-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000 5000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & mlflow server --host 0.0.0.0 --port 5000"]
