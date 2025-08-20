#!/usr/bin/env python3
"""
Test Tool Usage for AI Browser Agent

This script tests that the AI agent properly uses browser tools instead of giving manual instructions.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_tool_usage.py
"""

import asyncio
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing Tool Usage for AI Browser Agent...")

try:
    from agent_interface import AgentInterface, agent_interface
    print("✅ AI agent components imported successfully")
except ImportError as e:
    print(f"❌ Could not import AI agent components: {e}")
    sys.exit(1)

try:
    from qutebrowser.utils import message
    QUTEBROWSER_AVAILABLE = True
    print("✅ Qutebrowser integration available")
except ImportError:
    QUTEBROWSER_AVAILABLE = False
    print("⚠️  Qutebrowser integration not available (running standalone)")

class ToolUsageTest:
    """Test that the AI agent properly uses browser tools."""
    
    def __init__(self):
        self.agent_interface = None
    
    async def run_tests(self):
        """Run comprehensive tests of tool usage."""
        print("\n🚀 Starting Tool Usage Tests")
        print("=" * 50)
        
        # Initialize agent
        await self._test_agent_initialization()
        
        # Test navigation tool usage
        await self._test_navigation_tools()
        
        # Test search tool usage
        await self._test_search_tools()
        
        # Test complex tool usage
        await self._test_complex_tools()
        
        print("\n🎉 Tool Usage Tests Complete!")
    
    async def _test_agent_initialization(self):
        """Test agent initialization with DeepSeek profile."""
        print("\n1️⃣ Testing Agent Initialization")
        print("-" * 30)
        
        try:
            self.agent_interface = agent_interface
            
            # Initialize with DeepSeek profile
            print("🔧 Initializing DeepSeek R1 14B agent...")
            success = self.agent_interface.initialize_agent("deepseek_assistant")
            
            if success:
                print("✅ DeepSeek R1 14B agent initialized successfully!")
                print("🧠 Reasoning model ready for testing")
            else:
                print("❌ Failed to initialize DeepSeek agent")
                
        except Exception as e:
            print(f"❌ Initialization error: {e}")
    
    async def _test_navigation_tools(self):
        """Test that the agent uses navigation tools properly."""
        print("\n2️⃣ Testing Navigation Tool Usage")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing navigation tool usage...")
            test_query = "open github.com"
            
            response = await self.agent_interface.ask(test_query)
            
            if response.get("success"):
                print("✅ Navigation test successful!")
                
                # Check for tool usage
                tool_calls = response.get("tool_calls", [])
                reasoning = response.get("reasoning", "")
                action = response.get("message", "")
                
                if tool_calls:
                    print(f"🔧 Tools called: {len(tool_calls)}")
                    for i, tool_call in enumerate(tool_calls, 1):
                        tool_name = tool_call.get("name", "unknown")
                        params = tool_call.get("parameters", {})
                        print(f"   {i}. {tool_name}: {params}")
                    
                    # Check if open_url was called
                    open_url_called = any(tc.get("name") == "open_url" for tc in tool_calls)
                    if open_url_called:
                        print("✅ open_url tool was called correctly!")
                    else:
                        print("❌ open_url tool was not called")
                else:
                    print("❌ No tools were called")
                
                # Check for manual instructions
                manual_keywords = ["open your browser", "launch", "type in", "go to", "navigate to", "click on"]
                has_manual_instructions = any(keyword in action.lower() for keyword in manual_keywords)
                
                if has_manual_instructions:
                    print("❌ Response contains manual instructions instead of tool usage")
                else:
                    print("✅ Response does not contain manual instructions")
                
            else:
                print("❌ Navigation test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Navigation test error: {e}")
    
    async def _test_search_tools(self):
        """Test that the agent uses search tools properly."""
        print("\n3️⃣ Testing Search Tool Usage")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing search tool usage...")
            test_query = "search for Python on this page"
            
            response = await self.agent_interface.ask(test_query)
            
            if response.get("success"):
                print("✅ Search test successful!")
                
                # Check for tool usage
                tool_calls = response.get("tool_calls", [])
                reasoning = response.get("reasoning", "")
                action = response.get("message", "")
                
                if tool_calls:
                    print(f"🔧 Tools called: {len(tool_calls)}")
                    for i, tool_call in enumerate(tool_calls, 1):
                        tool_name = tool_call.get("name", "unknown")
                        params = tool_call.get("parameters", {})
                        print(f"   {i}. {tool_name}: {params}")
                    
                    # Check if search_page was called
                    search_called = any(tc.get("name") == "search_page" for tc in tool_calls)
                    if search_called:
                        print("✅ search_page tool was called correctly!")
                    else:
                        print("❌ search_page tool was not called")
                else:
                    print("❌ No tools were called")
                
            else:
                print("❌ Search test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Search test error: {e}")
    
    async def _test_complex_tools(self):
        """Test that the agent uses complex tools properly."""
        print("\n4️⃣ Testing Complex Tool Usage")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing complex tool usage...")
            test_query = "open reddit.com in a new tab and scroll down"
            
            response = await self.agent_interface.ask(test_query)
            
            if response.get("success"):
                print("✅ Complex tool test successful!")
                
                # Check for tool usage
                tool_calls = response.get("tool_calls", [])
                reasoning = response.get("reasoning", "")
                action = response.get("message", "")
                
                if tool_calls:
                    print(f"🔧 Tools called: {len(tool_calls)}")
                    for i, tool_call in enumerate(tool_calls, 1):
                        tool_name = tool_call.get("name", "unknown")
                        params = tool_call.get("parameters", {})
                        print(f"   {i}. {tool_name}: {params}")
                    
                    # Check for multiple tools
                    if len(tool_calls) >= 2:
                        print("✅ Multiple tools were called correctly!")
                    else:
                        print("⚠️  Expected multiple tools but got fewer")
                else:
                    print("❌ No tools were called")
                
            else:
                print("❌ Complex tool test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Complex tool test error: {e}")

# Main execution
async def main():
    """Main test function."""
    tester = ToolUsageTest()
    await tester.run_tests()

# Auto-run when script is loaded
if __name__ == "__main__" or True:  # Always run when imported in qutebrowser
    print("\n🚀 Loading Tool Usage Test...")
    
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
    print("🧪 Tool Usage Test Complete!")
    print("   The AI agent should now properly use browser tools")
    print("   instead of giving manual instructions")
    print("=" * 50)
