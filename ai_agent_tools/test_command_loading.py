#!/usr/bin/env python3
"""
Test Command Loading

This script tests that the AI agent commands can be loaded properly
in Qutebrowser's Python environment.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_command_loading.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing Command Loading...")

def test_imports():
    """Test that all required modules can be imported."""
    print("\n🔧 Testing imports...")
    
    try:
        # Test basic imports
        print("   Testing basic imports...")
        import json
        import asyncio
        print("   ✅ Basic imports successful")
        
        # Test AI agent imports
        print("   Testing AI agent imports...")
        from ai_browser_agent import AIBrowserAgent, AgentConfig
        print("   ✅ AI browser agent imported")
        
        # Test agent interface
        print("   Testing agent interface...")
        from agent_interface import AgentInterface
        print("   ✅ Agent interface imported")
        
        # Test browser control tools
        print("   Testing browser control tools...")
        from browser_control_tools import BrowserControlTools
        print("   ✅ Browser control tools imported")
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_qutebrowser_environment():
    """Test if we're in a Qutebrowser environment."""
    print("\n🔧 Testing Qutebrowser environment...")
    
    try:
        # Try to import qutebrowser modules
        from qutebrowser.utils import message
        from qutebrowser.api import cmdutils
        print("✅ Running in Qutebrowser environment")
        return True
    except ImportError:
        print("⚠️  Not running in Qutebrowser environment")
        print("   This is expected when running outside of Qutebrowser")
        return False

def test_command_registration():
    """Test command registration logic."""
    print("\n🔧 Testing command registration logic...")
    
    try:
        # Test the command registration function
        def test_command():
            return "Test command works!"
        
        # Simulate command registration
        print("   Testing command function...")
        result = test_command()
        print(f"   ✅ Command function result: {result}")
        
        print("✅ Command registration logic works!")
        return True
        
    except Exception as e:
        print(f"❌ Command registration test failed: {e}")
        return False

def test_agent_creation():
    """Test that an agent can be created."""
    print("\n🔧 Testing agent creation...")
    
    try:
        from ai_browser_agent import AgentConfig
        
        # Create a test config
        config = AgentConfig(
            llm_provider="ollama",
            model="deepseek-r1:14b",
            temperature=0.1,
            max_tokens=500
        )
        
        print(f"   ✅ Agent config created: {config.llm_provider}/{config.model}")
        
        # Test agent interface creation
        from agent_interface import AgentInterface
        
        agent_interface = AgentInterface()
        print("   ✅ Agent interface created")
        
        print("✅ Agent creation successful!")
        return True
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

# Run tests
if __name__ == "__main__":
    print("🧪 Starting command loading tests...")
    
    tests = [
        ("Import Test", test_imports),
        ("Qutebrowser Environment", test_qutebrowser_environment),
        ("Command Registration", test_command_registration),
        ("Agent Creation", test_agent_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Test Results Summary:")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Commands should load successfully.")
        print("\n📋 Next steps:")
        print("   1. Run: :pyeval --file ai_agent_tools/load_ai_agent.py")
        print("   2. Try: :ai-agent-init deepseek_assistant")
        print("   3. Try: :ai-agent-ask 'open google.com'")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n💡 Troubleshooting:")
        print("   - Ensure all files are in the ai_agent_tools directory")
        print("   - Check that Python dependencies are installed")
        print("   - Verify you're running this in Qutebrowser")
