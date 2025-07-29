#!/bin/bash

# Hardcode the port to avoid environment variable issues
PORT=8080

echo "🚀 Starting DocuSearch Light on Railway"
echo "📡 Port: $PORT"

# Set cache directories
export TRANSFORMERS_CACHE="/tmp/transformers_cache"
export TORCH_HOME="/tmp/torch_cache"
export HF_HOME="/tmp/hf_cache"

# Create cache directories
mkdir -p /tmp/transformers_cache /tmp/torch_cache /tmp/hf_cache

# Start Streamlit
exec streamlit run docusearch_light.py --server.port=$PORT --server.address=0.0.0.0