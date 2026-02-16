FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src
COPY scripts /app/scripts
COPY dashboard /app/dashboard
COPY dbt /app/dbt
COPY sql /app/sql
COPY .env.example /app/.env.example

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e ".[dev]"

CMD ["python", "scripts/run_pipeline.py"]
