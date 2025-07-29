#!/bin/bash

# Debug: Print all environment variables
echo "🔍 Environment variables:"
env | grep -i port || echo "No PORT variables found"

# Try to get port from various sources
PORT_VAR=""
if [ ! -z "$PORT" ]; then
    PORT_VAR="$PORT"
    echo "Found PORT=$PORT_VAR"
elif [ ! -z "$STREAMLIT_SERVER_PORT" ]; then
    PORT_VAR="$STREAMLIT_SERVER_PORT"
    echo "Found STREAMLIT_SERVER_PORT=$PORT_VAR"
else
    PORT_VAR="8080"
    echo "Using default port $PORT_VAR"
fi

# Clean up the port value
PORT_VAR=$(echo $PORT_VAR | tr -d '"' | tr -d "'" | tr -d ' ')

echo "🚀 Starting DocuSearch Light on port $PORT_VAR"
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

# Start Streamlit with the cleaned port value
echo "Starting Streamlit on port $PORT_VAR"
streamlit run docusearch_light.py --server.port=$PORT_VAR --server.address=0.0.0.0