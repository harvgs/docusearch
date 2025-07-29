# Multi-stage build to reduce final image size
FROM python:3.11-slim as builder

# Set environment variables to prevent CUDA installation
ENV CUDA_VISIBLE_DEVICES=""
ENV TORCH_CUDA_ARCH_LIST=""
ENV FORCE_CUDA="0"
ENV TORCH_CUDA_VERSION=""
ENV CUDA_HOME=""

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements_cpu_only.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Final stage with minimal runtime
FROM python:3.11-slim

# Set environment variables to prevent CUDA usage
ENV CUDA_VISIBLE_DEVICES=""
ENV TORCH_CUDA_ARCH_LIST=""
ENV FORCE_CUDA="0"
ENV TORCH_CUDA_VERSION=""
ENV CUDA_HOME=""

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code (light version)
COPY docusearch_light.py .
COPY create_embeddings_light.py .
COPY start_app.py .
COPY verify_embeddings.py .

# Create directories for data (will be mounted or uploaded separately)
RUN mkdir -p embeddings extracted_content connections

# Copy embeddings files (required for app functionality)
COPY embeddings/embeddings_light.json ./embeddings/
COPY embeddings/embeddings.json ./embeddings/

# Verify embeddings files are present and valid
RUN python verify_embeddings.py

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Start the application using Python startup script
CMD ["python", "start_app.py"]