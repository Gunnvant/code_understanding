FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install --no-cache-dir .

COPY etl ./etl
COPY dashboard ./dashboard
COPY main.py ./

ENV PYTHONPATH=/app

CMD ["python", "-m", "etl.cli", "run"]
