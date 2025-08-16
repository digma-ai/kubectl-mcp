# Dockerfile
FROM python:3.11-slim

# Versions & env
ARG KUBECTL_VERSION=v1.33.3
ARG TARGETARCH=arm64
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app

# System deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl" -o /usr/local/bin/kubectl && \
    chmod +x /usr/local/bin/kubectl

# App
WORKDIR /app

COPY requirements.txt .
# Python deps
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

RUN useradd -u 10001 -m appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["python", "src/mcp_server.py"]