#!/usr/bin/env python3
"""
Quick script to test Ollama connection
"""
import requests
import json

def test_ollama():
    try:
        # Test if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("✅ Ollama is running!")
            print("Available models:")
            for model in models:
                print(f"  - {model.get('name', 'Unknown')}")
            
            # Test a simple generation
            print("\n🧪 Testing generation with qwen2.5:latest...")
            gen_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:latest",
                    "prompt": "Write one sentence about a knight in a medieval setting:",
                    "stream": False,
                    "options": {"num_predict": 50}
                },
                timeout=30
            )
            
            if gen_response.status_code == 200:
                result = gen_response.json()
                print(f"✅ Response: {result.get('response', 'No response')}")
            else:
                print(f"❌ Generation failed: {gen_response.status_code}")
                
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure Ollama is running: ollama serve")

if __name__ == "__main__":
    test_ollama()
