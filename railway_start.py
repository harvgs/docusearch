#!/usr/bin/env python3
"""
Railway-specific startup script
"""

import os
import subprocess
import sys

def main():
    # Hardcode the port to avoid environment variable issues
    port = "8080"
    
    print(f"🚀 Starting DocuSearch Light on Railway")
    print(f"📡 Port: {port}")
    print(f"🔍 Environment PORT: {os.getenv('PORT')}")
    
    # Set cache directories
    os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
    os.environ['TORCH_HOME'] = '/tmp/torch_cache'
    os.environ['HF_HOME'] = '/tmp/hf_cache'
    
    # Create cache directories
    os.makedirs('/tmp/transformers_cache', exist_ok=True)
    os.makedirs('/tmp/torch_cache', exist_ok=True)
    os.makedirs('/tmp/hf_cache', exist_ok=True)
    
    # Start Streamlit with hardcoded port
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 'docusearch_light.py',
        '--server.port', port,
        '--server.address', '0.0.0.0'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()