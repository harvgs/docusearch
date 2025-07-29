#!/bin/bash

# Get port from environment variable, default to 8080
PORT=${PORT:-8080}

echo "🚀 Starting DocuSearch Light on port $PORT"
echo "💻 Using CPU-only PyTorch for minimal deployment size"

# Set cache directories to /tmp for Railway
export TRANSFORMERS_CACHE="/tmp/transformers_cache"
export TORCH_HOME="/tmp/torch_cache"
export HF_HOME="/tmp/hf_cache"

# Create cache directories
mkdir -p /tmp/transformers_cache /tmp/torch_cache /tmp/hf_cache

# Check if embeddings file exists
if [ ! -f "embeddings/embeddings_light.json" ]; then
    echo "⚠️  Warning: embeddings_light.json not found"
    echo "   The app will need to generate embeddings."
fi

# Start Streamlit with explicit port
exec streamlit run docusearch_light.py --server.port=$PORT --server.address=0.0.0.0