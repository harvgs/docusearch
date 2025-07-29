#!/usr/bin/env python3
"""
Simple OpenAI API Test Script
Tests connectivity and API key validity
"""

import json
import os
import sys
from pathlib import Path

def load_api_key():
    """Try to load API key from config file or get from user input"""
    # Try to load from config file
    config_paths = [
        "openai_config.json",
        os.path.join(Path(__file__).parent, "openai_config.json"),
        os.path.join(Path(__file__).parent, "config", "openai_config.json")
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    api_key = data.get('openai', {}).get('api_key')
                    if api_key and api_key != "your-openai-api-key-here":
                        print(f"✅ Loaded API key from {config_path}")
                        return api_key
            except Exception as e:
                print(f"⚠️  Could not load from {config_path}: {e}")
    
    # If no valid key found, ask user
    print("❌ No valid API key found in config files")
    api_key = input("Enter your OpenAI API key: ").strip()
    return api_key

def test_network_connectivity():
    """Test basic network connectivity to OpenAI"""
    print("\n🌐 Testing network connectivity...")
    try:
        import requests
        response = requests.get("https://api.openai.com", timeout=10)
        print("✅ Network connectivity OK")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ No internet connection")
        return False
    except requests.exceptions.Timeout:
        print("❌ Network timeout")
        return False
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def test_openai_api(api_key):
    """Test OpenAI API with the provided key"""
    print("\n🤖 Testing OpenAI API...")
    
    try:
        from openai import OpenAI
        
        # Create client
        client = OpenAI(api_key=api_key, timeout=30.0)
        
        # Test 1: Simple completion
        print("📝 Test 1: Simple chat completion...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Hello, API test successful!'"}],
            max_tokens=20
        )
        print(f"✅ Response: {response.choices[0].message.content}")
        
        # Test 2: Check model availability
        print("\n📋 Test 2: Checking model availability...")
        models = client.models.list()
        available_models = [model.id for model in models.data]
        if "gpt-4o-mini" in available_models:
            print("✅ gpt-4o-mini is available")
        else:
            print("⚠️  gpt-4o-mini not found in available models")
            print(f"Available models: {available_models[:5]}...")
        
        # Test 3: Test with longer context
        print("\n📚 Test 3: Testing with longer context...")
        long_message = "Please provide a brief summary of what you can do as an AI assistant."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": long_message}],
            max_tokens=100
        )
        print(f"✅ Response: {response.choices[0].message.content[:100]}...")
        
        return True
        
    except ImportError:
        print("❌ OpenAI package not installed. Run: pip install openai")
        return False
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower():
            print("❌ Authentication failed - Invalid API key")
        elif "rate_limit" in error_msg.lower():
            print("❌ Rate limit exceeded - Try again later")
        elif "quota" in error_msg.lower():
            print("❌ Quota exceeded - Check your OpenAI account")
        elif "connection" in error_msg.lower():
            print("❌ Connection error - Check your internet connection")
        else:
            print(f"❌ API error: {error_msg}")
        return False

def main():
    print("🔍 OpenAI API Test Script")
    print("=" * 40)
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("❌ No API key provided")
        return
    
    # Test network connectivity
    if not test_network_connectivity():
        print("\n❌ Network connectivity failed. Please check your internet connection.")
        return
    
    # Test OpenAI API
    if test_openai_api(api_key):
        print("\n🎉 All tests passed! Your OpenAI API key is working correctly.")
        print("\n💡 You can now use the docusearch_new.py application.")
    else:
        print("\n❌ API test failed. Please check your API key and try again.")
        print("\n🔧 Troubleshooting tips:")
        print("1. Verify your API key at https://platform.openai.com/api-keys")
        print("2. Check your account has credits")
        print("3. Ensure you have access to gpt-4o-mini model")
        print("4. Try again in a few minutes if rate limited")

if __name__ == "__main__":
    main()