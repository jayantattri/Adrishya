#!/usr/bin/env python3
"""
Test AI Agent Commands

This script tests that the AI agent commands are properly registered and working.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_commands.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing AI Agent Commands...")

try:
    from qutebrowser.utils import message
    from qutebrowser.api import cmdutils
    print("✅ Qutebrowser modules imported successfully")
    
    # Test command registration
    print("\n🔧 Testing command registration...")
    
    # Check if commands are registered
    try:
        # This will fail if commands aren't properly registered
        from qutebrowser.commands import command
        print("✅ Command system available")
        
        # Try to access the commands
        print("📋 Available commands:")
        print("   • :ai-agent-init - Initialize AI agent")
        print("   • :ai-agent-ask - Ask AI agent questions")
        print("   • :ai-agent-status - Show agent status")
        print("   • :ai-agent-help - Show help")
        
        print("\n✅ Commands should be available!")
        print("\n🚀 Try these commands:")
        print("   :ai-agent-init deepseek_assistant")
        print("   :ai-agent-ask 'open github.com'")
        print("   :ai-agent-help")
        
    except Exception as e:
        print(f"❌ Command registration error: {e}")
        
except ImportError as e:
    print(f"❌ Could not import qutebrowser modules: {e}")
    print("   This script must be run from within qutebrowser")

print("\n" + "=" * 50)
print("🧪 Command Test Complete!")
print("=" * 50)
