FROM python:3.12-slim

WORKDIR /app

# System deps needed by reportlab's font handling (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# SQLite data directory (mount a volume here in production so data persists)
RUN mkdir -p /app/data
VOLUME ["/app/data"]

EXPOSE 5000

ENV FLASK_DEBUG=0 \
    PORT=5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/healthz')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "60", "flask_app:app"]
