# Multi-stage build to reduce final image size
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements_minimal.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Final stage with minimal runtime
FROM python:3.11-slim

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

# Create directories for data (will be mounted or uploaded separately)
RUN mkdir -p embeddings extracted_content connections

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Start the application
CMD ["streamlit", "run", "docusearch_light.py", "--server.port=8080", "--server.address=0.0.0.0"]