# --- 1. Use a lightweight base image ---
    FROM python:3.11-slim AS base

    # --- 2. Set environment flags ---
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    
    # --- 3. Install system deps ---
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        && rm -rf /var/lib/apt/lists/*
    
    # --- 4. Create working directory ---
    WORKDIR /app
    
    # --- 5. Copy requirements first (layer caching) ---
    COPY requirements.txt .
    
    # --- 6. Install Python deps ---
    RUN pip install --upgrade pip && pip install -r requirements.txt
    
    # --- 7. Copy the rest of the application ---
    COPY . .
    
    # --- 8. Create a non-root user for security ---
    RUN useradd -m fastapiuser
    USER fastapiuser
    
    # --- 9. Expose API port (FastAPI default = 8000) ---
    EXPOSE 8000
    
    # --- 10. Start server with Gunicorn + Uvicorn workers ---
    CMD ["sh", "-c", "uvicorn main_agent:app --host 0.0.0.0 --port ${PORT} --workers 1"]

    