#!/usr/bin/env python3
"""
Load AI Agent Commands into Qutebrowser

This script loads the AI browser agent commands into qutebrowser so they become
available as :ai-agent-* commands.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/load_ai_agent.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🚀 Loading AI Agent Commands into Qutebrowser...")

try:
    # Import qutebrowser modules
    from qutebrowser.utils import message, objreg
    from qutebrowser.api import cmdutils
    
    print("✅ Qutebrowser modules imported successfully")
    
    # Import AI agent components with better error handling
    try:
        from agent_interface import AgentInterface, agent_interface
        print("✅ AI agent components imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Trying alternative import path...")
        
        # Try importing with explicit path
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        try:
            from agent_interface import AgentInterface, agent_interface
            print("✅ AI agent components imported successfully (alternative path)")
        except ImportError as e2:
            print(f"❌ Alternative import also failed: {e2}")
            print("   Please ensure all AI agent files are present")
            raise
    
    # Create global agent instance
    agent = agent_interface
    
    # Register commands manually since the decorators might not work in all contexts
    def register_ai_agent_commands():
        """Register AI agent commands with qutebrowser."""
        
        @cmdutils.register(scope='global')
        def ai_agent_init(profile: str = "default", api_key: str = None):
            """Initialize AI browser agent.
            
            Args:
                profile: Agent profile to use (default, deepseek_assistant, etc.)
                api_key: API key for LLM provider (not needed for Ollama)
            """
            try:
                success = agent.initialize_agent(profile, api_key)
                if success:
                    message.info(f"✅ AI agent initialized with profile: {profile}")
                    print(f"🤖 AI agent ready! Profile: {profile}")
                    if profile == "deepseek_assistant":
                        print("🧠 Using DeepSeek R1 14B model via Ollama")
                else:
                    message.error("❌ Failed to initialize AI agent")
            except Exception as e:
                message.error(f"❌ AI agent initialization error: {e}")
                print(f"Error details: {e}")
        
        @cmdutils.register(scope='global')
        def ai_agent_ask(query: str):
            """Ask the AI agent to perform a browser task.
            
            Args:
                query: Natural language query (e.g., "open github.com")
            """
            if not agent.agent:
                message.error("❌ AI agent not initialized. Use :ai-agent-init first")
                print("💡 Try: :ai-agent-init deepseek_assistant")
                return
            
            try:
                print(f"🤖 Processing: {query}")
                message.info(f"🤖 AI agent processing: {query}")
                
                # Run async query in event loop
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(agent.ask(query))
                loop.close()
                
                if response.get("success"):
                    message.info(f"✅ AI agent: {response['message']}")
                    print(f"✅ Success: {response['message']}")
                    
                    # Show tool execution details
                    tool_calls = response.get("tool_calls", [])
                    if tool_calls:
                        print(f"🔧 Tools used: {len(tool_calls)}")
                        for tool_call in tool_calls:
                            print(f"   - {tool_call.get('name', 'Unknown tool')}")
                else:
                    error_msg = response.get('error', 'Unknown error')
                    message.error(f"❌ AI agent error: {error_msg}")
                    print(f"❌ Error: {error_msg}")
                    
            except Exception as e:
                message.error(f"❌ AI agent query error: {e}")
                print(f"❌ Exception: {e}")
        
        @cmdutils.register(scope='global')
        def ai_agent_status():
            """Show AI agent status and available profiles."""
            try:
                status = agent.get_status()
                print("🤖 AI Agent Status:")
                print(f"   Initialized: {status.get('initialized', False)}")
                print(f"   Provider: {status.get('provider', 'None')}")
                print(f"   Model: {status.get('model', 'None')}")
                
                profiles = agent.list_profiles()
                print(f"\n📋 Available Profiles:")
                for profile in profiles:
                    print(f"   • {profile}")
                
                message.info("🤖 AI agent status displayed in console")
                
            except Exception as e:
                message.error(f"❌ AI agent status error: {e}")
        
        @cmdutils.register(scope='global')
        def ai_agent_help():
            """Show AI agent help and examples."""
            help_text = """
🤖 AI Browser Agent Help
========================

Commands:
  :ai-agent-init <profile>     Initialize AI agent with profile
  :ai-agent-ask <query>        Ask AI agent to perform browser task
  :ai-agent-status             Show agent status and profiles
  :ai-agent-help               Show this help

Profiles:
  • deepseek_assistant    DeepSeek R1 14B (local, privacy-focused)
  • default              OpenAI GPT-4 (cloud, general-purpose)
  • research_assistant   Anthropic Claude (cloud, research-focused)
  • automation_expert    OpenAI GPT-4 (cloud, automation-focused)
  • local_assistant      Llama2 (local, basic)
  • quick_helper         OpenAI GPT-3.5 (cloud, fast)

Examples:
  :ai-agent-init deepseek_assistant
  :ai-agent-ask "open github.com"
  :ai-agent-ask "help me research Python frameworks"
  :ai-agent-ask "open reddit.com in a new tab"
  :ai-agent-ask "find the contact form and fill it with my email"

For DeepSeek R1 14B (recommended):
  :ai-agent-init deepseek_assistant
  :ai-agent-ask "open stackoverflow and search for qutebrowser"
"""
            print(help_text)
            message.info("🤖 AI agent help displayed in console")
        
        print("✅ AI agent commands registered successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to register commands: {e}")
        return False
    
    # Register the commands
    if register_ai_agent_commands():
        print("\n🎉 AI Agent Commands Loaded Successfully!")
        print("=" * 50)
        print("Available commands:")
        print("  :ai-agent-init <profile>     Initialize AI agent")
        print("  :ai-agent-ask <query>        Ask AI agent to perform task")
        print("  :ai-agent-status             Show agent status")
        print("  :ai-agent-help               Show help")
        print("\n🚀 Quick Start:")
        print("1. :ai-agent-init deepseek_assistant")
        print("2. :ai-agent-ask 'open github.com'")
        print("\n💡 Type :ai-agent-help for more examples")
        print("=" * 50)
        
        message.info("🤖 AI agent commands loaded! Use :ai-agent-help for examples")
        
    else:
        print("❌ Failed to load AI agent commands")
        message.error("❌ Failed to load AI agent commands")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   This script must be run from within qutebrowser")
    print("   Use: :pyeval --file ai_agent_tools/load_ai_agent.py")

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

# Make agent available globally for manual use
if 'agent' not in globals():
    try:
        from agent_interface import agent_interface
        globals()['agent'] = agent_interface
        print("✅ Agent interface available as 'agent' variable")
    except:
        pass
