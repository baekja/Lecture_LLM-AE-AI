# Multi-stage build for RAG System
FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 raguser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/raguser/.local

# Copy application files
COPY scripts/ ./scripts/
COPY deployment/rag_system.py ./
COPY requirements.txt ./

# Create necessary directories
RUN mkdir -p docs/originals knowledge/md knowledge/index scratch && \
    chown -R raguser:raguser /app

# Switch to non-root user
USER raguser

# Update PATH
ENV PATH=/home/raguser/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Set entrypoint
ENTRYPOINT ["python", "rag_system.py"]
CMD ["--help"]