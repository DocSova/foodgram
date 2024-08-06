FROM python:3.9-slim-buster
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
RUN chmod +x /app/up.sh