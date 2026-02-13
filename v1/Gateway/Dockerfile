FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --no-cache-dir \
    typing-extensions==4.12.2 \
    sqlalchemy==2.0.41 \
    sqlalchemy-jsonfield==1.0.2 \
    sqlalchemy-utils==0.41.2 \
    python-dotenv==1.0.1 \
    fastapi==0.115.4 \
    fastapi-cli==0.0.5 \
    asyncpg==0.29.0 \
    httpx>=0.27.0 \
    uvicorn[standard]

COPY ./app ./app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["uvicorn", "app.presentation.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
