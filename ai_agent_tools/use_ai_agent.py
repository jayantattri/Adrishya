#!/usr/bin/env python3
"""
Use AI Agent Directly in Qutebrowser

This script sets up the AI agent for direct use in qutebrowser's Python console.
No commands needed - just use the agent directly.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/use_ai_agent.py
"""

import sys
import os
import asyncio

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🤖 Setting up AI Agent for Direct Use...")

try:
    # Import AI agent components
    from agent_interface import AgentInterface, agent_interface
    
    print("✅ AI agent components imported successfully")
    
    # Create global agent instance
    agent = agent_interface
    
    # Initialize with DeepSeek profile
    print("🔧 Initializing DeepSeek R1 14B agent...")
    success = agent.initialize_agent("deepseek_assistant")
    
    if success:
        print("✅ DeepSeek R1 14B agent initialized successfully!")
        print("🧠 Using DeepSeek R1 14B model via Ollama")
        
        print("\n🚀 Ready to use! Examples:")
        print("   await agent.ask('open github.com')")
        print("   await agent.ask('help me research Python frameworks')")
        print("   await agent.ask('open reddit.com in a new tab')")
        
        print("\n💡 Quick test:")
        print("   await agent.ask('Hello! Can you help me with browser automation?')")
        
        # Make agent available globally
        globals()['agent'] = agent
        print("\n✅ Agent is now available as 'agent' variable")
        
    else:
        print("❌ Failed to initialize DeepSeek agent")
        print("💡 You can still use the agent manually:")
        print("   agent = agent_interface")
        print("   agent.initialize_agent('deepseek_assistant')")
        print("   await agent.ask('your question')")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Please ensure all AI agent files are present")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🤖 AI Agent Setup Complete!")
print("   Use 'agent' variable to interact with the AI")
print("=" * 50)
