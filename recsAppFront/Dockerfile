# Multi-stage build for optimized CPU-only performance
FROM python:3.14-slim AS builder

# Set build arguments for optimization
ARG PYTORCH_DEVICE=cpu

WORKDIR /app

# Install system dependencies for faster builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements.txt

# Install CPU-only PyTorch (much faster and smaller)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage - smaller image
FROM python:3.14-slim

WORKDIR /app

# Install runtime dependencies only (keep image small)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Ensure Python can find installed packages
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTORCH_ENABLE_MPS_FALLBACK=0 \
    OMP_NUM_THREADS=4 \
    MKL_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=4 \
    VECLIB_MAXIMUM_THREADS=4 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    PYTHONPATH=/usr/local/lib/python3.14/site-packages:$PYTHONPATH

# Health check for faster startup detection
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app/streamlit.py", "--server.port", "8501", "--server.address", "0.0.0.0"]