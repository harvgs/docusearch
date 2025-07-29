#!/bin/bash

# Railway startup script for DocuSearch (Light Version)

echo "🚀 Starting DocuSearch Light on Railway..."

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable is not set"
    echo "   Users will need to enter their API key manually in the app"
fi

# Check if data files exist
if [ ! -f "embeddings/embeddings_light.json" ] && [ ! -f "embeddings/embeddings.json" ]; then
    echo "⚠️  Warning: No embeddings file found"
    echo "   Please ensure your data files are included in the deployment"
fi

# Set environment variables for optimization
export TRANSFORMERS_CACHE="/tmp/transformers_cache"
export TORCH_HOME="/tmp/torch_cache"
export HF_HOME="/tmp/huggingface_cache"

# Start Streamlit with optimized settings
echo "📱 Starting Streamlit application (Light Version)..."
exec streamlit run docusearch_light.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false