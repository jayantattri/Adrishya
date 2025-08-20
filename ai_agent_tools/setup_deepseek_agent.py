
# AI Browser Agent Setup for DeepSeek R1 14B
# Run this in qutebrowser's Python console

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from agent_interface import AgentInterface
    
    # Create agent instance
    agent = AgentInterface()
    
    # Initialize with DeepSeek profile
    success = agent.initialize_agent("deepseek_assistant")
    
    if success:
        print("✅ AI Browser Agent initialized with DeepSeek R1 14B!")
        print("🎯 You can now use commands like:")
        print("   await agent.ask('open github.com')")
        print("   await agent.ask('help me research Python frameworks')")
        print("   await agent.ask('fill out the contact form')")
    else:
        print("❌ Failed to initialize AI agent")
        
except Exception as e:
    print(f"❌ Setup error: {e}")
