FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim-bookworm AS runner

RUN useradd --system --no-create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser app ./app

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
