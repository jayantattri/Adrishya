#!/usr/bin/env python3
"""
Test Qutebrowser AI Agent Setup

This script tests the AI agent setup specifically within qutebrowser's environment.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_qutebrowser_setup.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing Qutebrowser AI Agent Setup...")

# Test 1: Check Python environment
print(f"\n1️⃣ Python Environment:")
print(f"   Python version: {sys.version}")
print(f"   Python executable: {sys.executable}")
print(f"   Python path: {sys.path[:3]}...")

# Test 2: Check required packages
print(f"\n2️⃣ Required Packages:")
try:
    import requests
    print("   ✅ requests module available")
except ImportError as e:
    print(f"   ❌ requests module not available: {e}")

try:
    import asyncio
    print("   ✅ asyncio module available")
except ImportError as e:
    print(f"   ❌ asyncio module not available: {e}")

# Test 3: Check qutebrowser integration
print(f"\n3️⃣ Qutebrowser Integration:")
try:
    from qutebrowser.utils import message
    from qutebrowser.api import cmdutils
    print("   ✅ Qutebrowser modules available")
    QUTEBROWSER_AVAILABLE = True
except ImportError as e:
    print(f"   ❌ Qutebrowser modules not available: {e}")
    QUTEBROWSER_AVAILABLE = False

# Test 4: Check AI agent components
print(f"\n4️⃣ AI Agent Components:")
try:
    from agent_interface import AgentInterface, agent_interface
    print("   ✅ Agent interface available")
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"   ❌ Agent interface not available: {e}")
    AGENT_AVAILABLE = False

try:
    from ai_browser_agent import AIBrowserAgent, AgentConfig
    print("   ✅ AI browser agent available")
    AI_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"   ❌ AI browser agent not available: {e}")
    AI_AGENT_AVAILABLE = False

# Test 5: Check Ollama connection
print(f"\n5️⃣ Ollama Connection:")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        print("   ✅ Ollama connection successful")
        
        # Check for DeepSeek model
        models = response.json().get("models", [])
        deepseek_found = any("deepseek-r1:14b" in model.get("name", "") for model in models)
        
        if deepseek_found:
            print("   ✅ DeepSeek R1 14B model found")
        else:
            print("   ⚠️  DeepSeek R1 14B model not found")
    else:
        print(f"   ❌ Ollama connection failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Ollama connection error: {e}")

# Test 6: Test agent initialization
print(f"\n6️⃣ Agent Initialization Test:")
if AGENT_AVAILABLE and AI_AGENT_AVAILABLE:
    try:
        # Create agent interface
        agent = agent_interface
        
        # Try to initialize with DeepSeek profile
        print("   🔧 Attempting to initialize DeepSeek agent...")
        success = agent.initialize_agent("deepseek_assistant")
        
        if success:
            print("   ✅ DeepSeek agent initialized successfully!")
            print(f"   🧠 Model: {agent.agent.config.model}")
            print(f"   🔗 Provider: {agent.agent.config.llm_provider}")
        else:
            print("   ❌ Failed to initialize DeepSeek agent")
            
    except Exception as e:
        print(f"   ❌ Agent initialization error: {e}")
else:
    print("   ⚠️  Skipping agent initialization test (components not available)")

# Summary
print(f"\n📊 Test Summary:")
print(f"   Python Environment: ✅")
print(f"   Required Packages: {'✅' if 'requests' in sys.modules else '❌'}")
print(f"   Qutebrowser Integration: {'✅' if QUTEBROWSER_AVAILABLE else '❌'}")
print(f"   AI Agent Components: {'✅' if AGENT_AVAILABLE and AI_AGENT_AVAILABLE else '❌'}")
print(f"   Ollama Connection: {'✅' if 'response' in locals() and response.status_code == 200 else '❌'}")

# Recommendations
print(f"\n💡 Recommendations:")
if not QUTEBROWSER_AVAILABLE:
    print("   • This script should be run from within qutebrowser")
    print("   • Use: :pyeval --file ai_agent_tools/test_qutebrowser_setup.py")

if AGENT_AVAILABLE and AI_AGENT_AVAILABLE:
    print("   • AI agent components are available")
    print("   • Try: :pyeval --file ai_agent_tools/load_ai_agent.py")
    print("   • Then: :ai-agent-init deepseek_assistant")
else:
    print("   • Install missing dependencies")
    print("   • Run: python3 install_dependencies.py")

print(f"\n" + "=" * 50)
print("🧪 Qutebrowser Setup Test Complete!")
print("=" * 50)
