#!/usr/bin/env python3
"""
Simple Google Gemini API Test Script
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
        "gemini_config.json",
        os.path.join(Path(__file__).parent, "gemini_config.json"),
        os.path.join(Path(__file__).parent, "config", "gemini_config.json")
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    api_key = data.get('gemini', {}).get('api_key')
                    if api_key and api_key != "your-gemini-api-key-here":
                        print(f"✅ Loaded API key from {config_path}")
                        return api_key
            except Exception as e:
                print(f"⚠️  Could not load from {config_path}: {e}")
    
    # If no valid key found, ask user
    print("❌ No valid API key found in config files")
    api_key = input("Enter your Google Gemini API key: ").strip()
    return api_key

def test_network_connectivity():
    """Test basic network connectivity to Google AI"""
    print("\n🌐 Testing network connectivity...")
    try:
        import requests
        response = requests.get("https://generativelanguage.googleapis.com", timeout=10)
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

def test_gemini_api(api_key):
    """Test Gemini API with the provided key"""
    print("\n🤖 Testing Google Gemini API...")
    
    try:
        import google.generativeai as genai
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Test 1: Simple completion
        print("📝 Test 1: Simple chat completion...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'Hello, Gemini API test successful!'")
        print(f"✅ Response: {response.text}")
        
        # Test 2: Check model availability
        print("\n📋 Test 2: Checking model availability...")
        models = genai.list_models()
        available_models = [model.name for model in models]
        gemini_models = [m for m in available_models if 'gemini' in m.lower()]
        if gemini_models:
            print(f"✅ Found Gemini models: {gemini_models[:3]}...")
        else:
            print("⚠️  No Gemini models found")
            print(f"Available models: {available_models[:5]}...")
        
        # Test 3: Test with longer context
        print("\n📚 Test 3: Testing with longer context...")
        long_message = "Please provide a brief summary of what you can do as an AI assistant."
        response = model.generate_content(long_message)
        print(f"✅ Response: {response.text[:100]}...")
        
        # Test 4: Test chat functionality
        print("\n💬 Test 4: Testing chat functionality...")
        chat = model.start_chat(history=[])
        response = chat.send_message("What's 2+2?")
        print(f"✅ Chat response: {response.text}")
        
        return True
        
    except ImportError:
        print("❌ Google Generative AI package not installed. Run: pip install google-generativeai")
        return False
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
            print("❌ Authentication failed - Invalid API key")
        elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
            print("❌ Rate limit/quota exceeded - Try again later")
        elif "connection" in error_msg.lower():
            print("❌ Connection error - Check your internet connection")
        elif "permission" in error_msg.lower():
            print("❌ Permission denied - Check your API key permissions")
        else:
            print(f"❌ API error: {error_msg}")
        return False

def create_gemini_config():
    """Create a sample Gemini config file"""
    config = {
        "gemini": {
            "api_key": "your-gemini-api-key-here"
        }
    }
    
    config_path = "gemini_config.json"
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✅ Created sample config file: {config_path}")
        print("💡 Please edit this file and replace 'your-gemini-api-key-here' with your actual API key")
    except Exception as e:
        print(f"❌ Could not create config file: {e}")

def main():
    print("🔍 Google Gemini API Test Script")
    print("=" * 40)
    
    # Check if config file exists, create if not
    if not os.path.exists("gemini_config.json"):
        print("📝 No config file found. Creating sample...")
        create_gemini_config()
        print()
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("❌ No API key provided")
        return
    
    # Test network connectivity
    if not test_network_connectivity():
        print("\n❌ Network connectivity failed. Please check your internet connection.")
        return
    
    # Test Gemini API
    if test_gemini_api(api_key):
        print("\n🎉 All tests passed! Your Google Gemini API key is working correctly.")
        print("\n💡 You can now use Gemini in your applications.")
    else:
        print("\n❌ API test failed. Please check your API key and try again.")
        print("\n🔧 Troubleshooting tips:")
        print("1. Get your API key from https://makersuite.google.com/app/apikey")
        print("2. Check your account has credits/quota")
        print("3. Ensure you have access to Gemini models")
        print("4. Try again in a few minutes if rate limited")
        print("5. Make sure you're in a supported region")

if __name__ == "__main__":
    main()