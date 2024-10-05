FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV APP_ENV=prod

EXPOSE 8080

ENTRYPOINT ["python3", "main.py"]
