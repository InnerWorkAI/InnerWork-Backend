FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port dynamically via Render's $PORT
EXPOSE 8000

# Production entrypoint: use $PORT, no --reload
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]