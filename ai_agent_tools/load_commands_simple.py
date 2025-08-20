#!/usr/bin/env python3
"""
Simple AI Agent Command Loader

This is a simplified version that should work even with import issues.
It directly registers the commands without complex imports.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/load_commands_simple.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🚀 Loading AI Agent Commands (Simple Version)...")

try:
    # Import qutebrowser modules
    from qutebrowser.utils import message
    from qutebrowser.api import cmdutils
    
    print("✅ Qutebrowser modules imported successfully")
    
    # Import AI agent components with fallback
    try:
        from agent_interface import agent_interface
        print("✅ Agent interface imported successfully")
        agent = agent_interface
    except ImportError as e:
        print(f"⚠️  Agent interface import failed: {e}")
        print("   Creating minimal agent interface...")
        
        # Create a minimal agent interface
        class MinimalAgent:
            def __init__(self):
                self.agent = None
                self.current_profile = None
            
            def initialize_agent(self, profile, api_key=None):
                try:
                    from ai_browser_agent import AIBrowserAgent, AgentConfig
                    from agent_config import load_config
                    
                    config = load_config()
                    profile_config = config["agent_profiles"].get(profile, {})
                    
                    agent_config = AgentConfig(
                        llm_provider=profile_config.get("llm_provider", "ollama"),
                        model=profile_config.get("model", "deepseek-r1:14b"),
                        api_key=api_key,
                        temperature=0.1,
                        max_tokens=500
                    )
                    
                    self.agent = AIBrowserAgent(agent_config)
                    self.current_profile = profile
                    return True
                except Exception as e:
                    print(f"❌ Agent initialization failed: {e}")
                    return False
            
            async def ask(self, query):
                if not self.agent:
                    return {"error": "Agent not initialized"}
                
                try:
                    response = await self.agent.process_query(query)
                    return {
                        "success": response.success,
                        "message": response.message,
                        "tool_calls": response.tool_calls,
                        "execution_results": response.execution_results,
                        "error": response.error
                    }
                except Exception as e:
                    return {"error": str(e)}
        
        agent = MinimalAgent()
    
    # Register commands
    @cmdutils.register(scope='global')
    def ai_agent_init(profile: str = "deepseek_assistant", api_key: str = None):
        """Initialize AI browser agent.
        
        Args:
            profile: Agent profile to use (default: deepseek_assistant)
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
            error_msg = f"Error processing query: {e}"
            message.error(f"❌ {error_msg}")
            print(f"❌ {error_msg}")
    
    @cmdutils.register(scope='global')
    def ai_agent_status():
        """Show AI agent status."""
        if agent.agent:
            profile = agent.current_profile or "unknown"
            print(f"🤖 AI Agent Status:")
            print(f"   Profile: {profile}")
            print(f"   Status: Active")
            print(f"   Agent: {type(agent.agent).__name__}")
        else:
            print("🤖 AI Agent Status: Not initialized")
            print("💡 Use :ai-agent-init to initialize")
    
    @cmdutils.register(scope='global')
    def ai_agent_help():
        """Show AI agent help."""
        print("🤖 AI Browser Agent Help")
        print("=" * 40)
        print("Commands:")
        print("  :ai-agent-init [profile] - Initialize the AI agent")
        print("  :ai-agent-ask <query>    - Ask the AI agent to perform a task")
        print("  :ai-agent-status         - Show agent status")
        print("  :ai-agent-help           - Show this help")
        print()
        print("Profiles:")
        print("  deepseek_assistant - DeepSeek R1 14B via Ollama (recommended)")
        print("  default           - Default OpenAI GPT-4")
        print()
        print("Examples:")
        print("  :ai-agent-init deepseek_assistant")
        print("  :ai-agent-ask 'open google.com'")
        print("  :ai-agent-ask 'search for Python tutorials'")
        print("  :ai-agent-ask 'click the first result'")
    
    print("✅ AI agent commands registered successfully!")
    print("📋 Available commands:")
    print("   :ai-agent-init [profile] - Initialize the AI agent")
    print("   :ai-agent-ask <query>    - Ask the AI agent to perform a task")
    print("   :ai-agent-status         - Show agent status")
    print("   :ai-agent-help           - Show help")
    print()
    print("🚀 Ready to use! Try:")
    print("   :ai-agent-init deepseek_assistant")
    print("   :ai-agent-ask 'open google.com'")

except ImportError as e:
    print(f"❌ Failed to load commands: {e}")
    print("💡 Make sure you're running this in Qutebrowser")
    print("   Use: :pyeval --file ai_agent_tools/load_commands_simple.py")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
