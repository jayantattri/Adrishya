#!/usr/bin/env python3
"""
Quick DeepSeek R1 14B Test

This script quickly tests if the AI agent can communicate with the DeepSeek model.
"""

import requests
import json
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_ollama_connection():
    """Test basic connection to Ollama."""
    print("🔍 Testing Ollama connection...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            deepseek_found = any("deepseek-r1:14b" in model.get("name", "") for model in models)
            
            if deepseek_found:
                print("✅ Ollama is running and DeepSeek model is available")
                return True
            else:
                print("⚠️  Ollama is running but DeepSeek model not found")
                return False
        else:
            print(f"❌ Ollama connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama connection error: {e}")
        return False

def test_deepseek_model():
    """Test DeepSeek model with a simple query."""
    print("\n🧠 Testing DeepSeek model...")
    
    try:
        payload = {
            "model": "deepseek-r1:14b",
            "prompt": "Hello! Can you help me with browser automation? Just say 'Yes, I can help with browser automation!'",
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            
            print("✅ DeepSeek model responded successfully")
            print(f"   Response: {response_text[:100]}...")
            return True
        else:
            print(f"❌ DeepSeek model test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek model test error: {e}")
        return False

def test_ai_agent_components():
    """Test if AI agent components can be imported."""
    print("\n🤖 Testing AI agent components...")
    
    try:
        from agent_interface import AgentInterface
        print("✅ Agent interface imported successfully")
        
        # Try to create agent instance
        agent = AgentInterface()
        print("✅ Agent interface created successfully")
        
        # Check available profiles
        profiles = agent.list_profiles()
        if "deepseek_assistant" in profiles:
            print("✅ DeepSeek assistant profile found")
            return True
        else:
            print("⚠️  DeepSeek assistant profile not found")
            print(f"   Available profiles: {profiles}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Agent component error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Quick DeepSeek R1 14B Test")
    print("=" * 40)
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("DeepSeek Model", test_deepseek_model),
        ("AI Agent Components", test_ai_agent_components)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Show results
    print("\n📊 Test Results")
    print("-" * 40)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    # Overall assessment
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DeepSeek R1 14B agent is ready to use.")
        print("\n🚀 Next steps:")
        print("1. In qutebrowser: :ai-agent-init deepseek_assistant")
        print("2. Test command: :ai-agent-ask 'open github.com'")
    elif passed > 0:
        print("⚠️  Some tests passed. Agent may work with limitations.")
    else:
        print("❌ No tests passed. Please check your setup.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
