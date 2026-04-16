FROM python:3.11-slim

# Non-root user for security
RUN addgroup --gid 1001 appgroup && \
    adduser --uid 1001 --gid 1001 --no-create-home appuser

WORKDIR /app

COPY src/ ./src/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
