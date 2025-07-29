#!/bin/bash

# Railway startup script for DocuSearch

echo "🚀 Starting DocuSearch on Railway..."

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable is not set"
    echo "   Users will need to enter their API key manually in the app"
fi

# Check if data files exist
if [ ! -f "embeddings/embeddings.json" ]; then
    echo "⚠️  Warning: embeddings/embeddings.json not found"
    echo "   Please ensure your data files are included in the deployment"
fi

# Start Streamlit
echo "📱 Starting Streamlit application..."
exec streamlit run docusearch_new.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false