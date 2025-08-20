#!/usr/bin/env python3
"""
Test DeepSeek R1 14B AI Browser Agent

This script tests the AI browser agent with the DeepSeek R1 14B model via Ollama.
It verifies that the model can understand and respond to browser automation requests.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_deepseek_agent.py
"""

import asyncio
import sys
import os
import time

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing DeepSeek R1 14B AI Browser Agent...")

try:
    from agent_interface import AgentInterface
    from ai_browser_agent import create_ai_agent, AgentConfig
    print("✅ AI agent components imported successfully")
except ImportError as e:
    print(f"❌ Could not import AI agent components: {e}")
    print("   Please ensure all required files are present")
    sys.exit(1)

try:
    from qutebrowser.utils import message
    QUTEBROWSER_AVAILABLE = True
    print("✅ Qutebrowser integration available")
except ImportError:
    QUTEBROWSER_AVAILABLE = False
    print("⚠️  Qutebrowser integration not available (running standalone)")

class DeepSeekAgentTest:
    """Test the DeepSeek R1 14B AI browser agent."""
    
    def __init__(self):
        self.agent_interface = None
        self.test_results = {}
    
    async def run_tests(self):
        """Run comprehensive tests of the DeepSeek agent."""
        print("\n🚀 Starting DeepSeek R1 14B Agent Tests")
        print("=" * 50)
        
        # Test 1: Agent Initialization
        await self._test_agent_initialization()
        
        # Test 2: Model Communication
        await self._test_model_communication()
        
        # Test 3: Tool Understanding
        await self._test_tool_understanding()
        
        # Test 4: Browser Commands (if in qutebrowser)
        if QUTEBROWSER_AVAILABLE:
            await self._test_browser_commands()
        
        # Show results
        self._show_test_results()
    
    async def _test_agent_initialization(self):
        """Test agent initialization with DeepSeek profile."""
        print("\n1️⃣ Testing Agent Initialization")
        print("-" * 30)
        
        try:
            # Create agent interface
            self.agent_interface = AgentInterface()
            
            # Initialize with DeepSeek profile
            print("🔧 Initializing agent with 'deepseek_assistant' profile...")
            success = self.agent_interface.initialize_agent("deepseek_assistant")
            
            if success:
                print("✅ Agent initialized successfully")
                print(f"   Provider: {self.agent_interface.agent.config.llm_provider}")
                print(f"   Model: {self.agent_interface.agent.config.model}")
                print(f"   API Base: {self.agent_interface.agent.config.api_base}")
                self.test_results["initialization"] = "✅ Success"
            else:
                print("❌ Agent initialization failed")
                self.test_results["initialization"] = "❌ Failed"
                
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            self.test_results["initialization"] = f"❌ Error: {e}"
    
    async def _test_model_communication(self):
        """Test basic communication with the DeepSeek model."""
        print("\n2️⃣ Testing Model Communication")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping model test")
            self.test_results["model_communication"] = "❌ Skipped"
            return
        
        try:
            # Test simple query
            print("🧠 Testing model with simple query...")
            test_query = "Hello! Can you help me with browser automation?"
            
            response = await self.agent_interface.ask(test_query)
            
            if response and response.get("success"):
                print("✅ Model communication successful")
                print(f"   Response: {response.get('message', 'No message')[:100]}...")
                self.test_results["model_communication"] = "✅ Success"
            else:
                print("❌ Model communication failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                self.test_results["model_communication"] = "❌ Failed"
                
        except Exception as e:
            print(f"❌ Model communication error: {e}")
            self.test_results["model_communication"] = f"❌ Error: {e}"
    
    async def _test_tool_understanding(self):
        """Test if the model understands available browser tools."""
        print("\n3️⃣ Testing Tool Understanding")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping tool test")
            self.test_results["tool_understanding"] = "❌ Skipped"
            return
        
        try:
            # Test tool-aware query
            print("🔧 Testing model with tool-aware query...")
            test_query = "What browser tools are available for opening a new tab?"
            
            response = await self.agent_interface.ask(test_query)
            
            if response and response.get("success"):
                print("✅ Tool understanding test successful")
                print(f"   Response: {response.get('message', 'No message')[:150]}...")
                
                # Check if tool calls were made
                tool_calls = response.get("tool_calls", [])
                if tool_calls:
                    print(f"   Tool calls made: {len(tool_calls)}")
                    for tool_call in tool_calls:
                        print(f"     - {tool_call.get('name', 'Unknown tool')}")
                
                self.test_results["tool_understanding"] = "✅ Success"
            else:
                print("❌ Tool understanding test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                self.test_results["tool_understanding"] = "❌ Failed"
                
        except Exception as e:
            print(f"❌ Tool understanding error: {e}")
            self.test_results["tool_understanding"] = f"❌ Error: {e}"
    
    async def _test_browser_commands(self):
        """Test actual browser commands (only in qutebrowser)."""
        print("\n4️⃣ Testing Browser Commands")
        print("-" * 30)
        
        if not QUTEBROWSER_AVAILABLE:
            print("⚠️  Not in qutebrowser, skipping browser command test")
            self.test_results["browser_commands"] = "⚠️  Skipped (not in qutebrowser)"
            return
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping browser test")
            self.test_results["browser_commands"] = "❌ Skipped"
            return
        
        try:
            # Test simple browser command
            print("🌐 Testing browser command...")
            test_query = "Open https://example.com in a new tab"
            
            response = await self.agent_interface.ask(test_query)
            
            if response and response.get("success"):
                print("✅ Browser command test successful")
                print(f"   Response: {response.get('message', 'No message')[:100]}...")
                
                # Check execution results
                execution_results = response.get("execution_results", [])
                if execution_results:
                    print(f"   Commands executed: {len(execution_results)}")
                    for result in execution_results:
                        status = "✅" if result.get("success") else "❌"
                        print(f"     {status} {result.get('tool_name', 'Unknown')}: {result.get('message', 'No message')}")
                
                self.test_results["browser_commands"] = "✅ Success"
            else:
                print("❌ Browser command test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                self.test_results["browser_commands"] = "❌ Failed"
                
        except Exception as e:
            print(f"❌ Browser command error: {e}")
            self.test_results["browser_commands"] = f"❌ Error: {e}"
    
    def _show_test_results(self):
        """Show comprehensive test results."""
        print("\n📊 Test Results Summary")
        print("=" * 50)
        
        for test_name, result in self.test_results.items():
            print(f"   {result} {test_name.replace('_', ' ').title()}")
        
        # Overall assessment
        success_count = sum(1 for result in self.test_results.values() if result.startswith("✅"))
        total_count = len(self.test_results)
        
        print(f"\n🎯 Overall: {success_count}/{total_count} tests passed")
        
        if success_count == total_count:
            print("🎉 All tests passed! DeepSeek R1 14B agent is ready to use.")
        elif success_count > 0:
            print("⚠️  Some tests passed. Agent may work with limitations.")
        else:
            print("❌ No tests passed. Please check your setup.")
        
        print("\n🚀 Next Steps:")
        if success_count > 0:
            print("1. Use the agent in qutebrowser:")
            print("   :ai-agent-init deepseek_assistant")
            print("   :ai-agent-ask 'open github.com'")
            print("\n2. Or use Python console:")
            print("   agent = agent_interface")
            print("   await agent.ask('help me research Python frameworks')")
        else:
            print("1. Check Ollama installation: ollama --version")
            print("2. Verify model is downloaded: ollama list")
            print("3. Test model directly: ollama run deepseek-r1:14b 'Hello'")
        
        if QUTEBROWSER_AVAILABLE and message:
            message.info("🧪 DeepSeek R1 14B agent test completed! Check console for results.")

# Main execution
async def main():
    """Main test function."""
    tester = DeepSeekAgentTest()
    await tester.run_tests()

# Auto-run when script is loaded
if __name__ == "__main__" or True:  # Always run when imported in qutebrowser
    print("\n🚀 Loading DeepSeek R1 14B Agent Test...")
    
    try:
        # Try to run in existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create task in existing loop
            task = loop.create_task(main())
            print("📋 Test scheduled to run in background event loop")
        else:
            # Run in new loop
            asyncio.run(main())
    except RuntimeError:
        # Fallback for different environments
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
            loop.close()
        except Exception as e:
            print(f"⚠️  Could not run async test: {e}")
            print("   Run manually with: await main()")
    
    print("\n" + "=" * 50)
    print("🧪 DeepSeek R1 14B Agent Test Complete!")
    print("   Check results above for next steps")
    print("=" * 50)
