#!/usr/bin/env python3
"""
Startup script for Railway deployment
Handles PORT environment variable properly
"""

import os
import subprocess
import sys

def main():
    # Get port from environment variable, default to 8080
    port = os.getenv('PORT', '8080')
    
    print(f"🚀 Starting DocuSearch Light on port {port}")
    print("💻 Using CPU-only PyTorch for minimal deployment size")
    
    # Set cache directories to /tmp for Railway
    os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
    os.environ['TORCH_HOME'] = '/tmp/torch_cache'
    os.environ['HF_HOME'] = '/tmp/hf_cache'
    
    # Create cache directories
    os.makedirs('/tmp/transformers_cache', exist_ok=True)
    os.makedirs('/tmp/torch_cache', exist_ok=True)
    os.makedirs('/tmp/hf_cache', exist_ok=True)
    
    # Check if embeddings file exists
    if not os.path.exists('embeddings/embeddings_light.json'):
        print("⚠️  Warning: embeddings_light.json not found")
        print("   The app will need to generate embeddings.")
    
    # Start Streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'docusearch_light.py',
            '--server.port', port,
            '--server.address', '0.0.0.0'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()