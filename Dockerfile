FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    libglib2.0-0 \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md .
COPY src/ src/

RUN pip install --no-cache-dir uv && uv sync --no-dev

RUN mkdir -p /app/models /app/logs

EXPOSE 10793

ENV HOST=0.0.0.0
ENV PORT=10793
ENV MODELS_DIR=/app/models
ENV LOG_LEVEL=INFO

CMD ["uv", "run", "uvicorn", "avatarmcp.http_server:app", "--host", "0.0.0.0", "--port", "10793", "--log-level", "info"]
