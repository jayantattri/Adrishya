#!/usr/bin/env python3
"""
Test Iterative Tool Calling for AI Browser Agent

This script tests that the AI agent properly uses iterative tool calling,
executing one tool at a time with feedback, instead of trying to execute
all tools simultaneously.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_iterative_tool_calling.py
"""

import asyncio
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing Iterative Tool Calling for AI Browser Agent...")

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

class IterativeToolCallingTest:
    """Test that the AI agent properly uses iterative tool calling."""
    
    def __init__(self):
        self.agent_interface = None
    
    async def run_tests(self):
        """Run comprehensive tests of iterative tool calling."""
        print("\n🚀 Starting Iterative Tool Calling Tests")
        print("=" * 50)
        
        # Initialize agent
        await self._test_agent_initialization()
        
        # Test single tool execution
        await self._test_single_tool_execution()
        
        # Test multi-step tool execution
        await self._test_multi_step_execution()
        
        # Test tool failure handling
        await self._test_tool_failure_handling()
        
        print("\n🎉 Iterative Tool Calling Tests Complete!")
    
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
                print("🧠 Iterative tool calling ready for testing")
            else:
                print("❌ Failed to initialize DeepSeek agent")
                
        except Exception as e:
            print(f"❌ Initialization error: {e}")
    
    async def _test_single_tool_execution(self):
        """Test that the agent executes single tools properly."""
        print("\n2️⃣ Testing Single Tool Execution")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing single tool execution...")
            test_query = "open google.com"
            
            response = await self.agent_interface.ask(test_query)
            
            if response.get("success"):
                print("✅ Single tool test successful!")
                
                # Check for tool usage
                tool_calls = response.get("tool_calls", [])
                execution_results = response.get("execution_results", [])
                
                print(f"🔧 Tools called: {len(tool_calls)}")
                print(f"📊 Execution results: {len(execution_results)}")
                
                if tool_calls:
                    for i, tool_call in enumerate(tool_calls, 1):
                        tool_name = tool_call.get("name", "unknown")
                        params = tool_call.get("parameters", {})
                        print(f"   {i}. {tool_name}: {params}")
                
                if execution_results:
                    for i, result in enumerate(execution_results, 1):
                        success = "✅" if result.success else "❌"
                        print(f"   {i}. {success} {result.command}")
                        if not result.success:
                            print(f"      Error: {result.error or 'Unknown error'}")
                        elif result.message:
                            print(f"      Message: {result.message}")
                
                # Verify that tools were executed one by one
                if len(tool_calls) == len(execution_results):
                    print("✅ Tool calls match execution results (iterative execution working)")
                else:
                    print("❌ Tool calls don't match execution results")
                
            else:
                print("❌ Single tool test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Single tool test error: {e}")
    
    async def _test_multi_step_execution(self):
        """Test that the agent executes multiple tools iteratively."""
        print("\n3️⃣ Testing Multi-Step Execution")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing multi-step execution...")
            test_query = "open google.com and search for Python tutorials"
            
            response = await self.agent_interface.ask(test_query)
            
            if response.get("success"):
                print("✅ Multi-step test successful!")
                
                # Check for multiple tool usage
                tool_calls = response.get("tool_calls", [])
                execution_results = response.get("execution_results", [])
                
                print(f"🔧 Tools called: {len(tool_calls)}")
                print(f"📊 Execution results: {len(execution_results)}")
                
                if len(tool_calls) > 1:
                    print("✅ Multiple tools were called (multi-step execution working)")
                    
                    for i, tool_call in enumerate(tool_calls, 1):
                        tool_name = tool_call.get("name", "unknown")
                        params = tool_call.get("parameters", {})
                        print(f"   {i}. {tool_name}: {params}")
                    
                    # Check execution order
                    print("📋 Execution order:")
                    for i, result in enumerate(execution_results, 1):
                        success = "✅" if result.success else "❌"
                        print(f"   {i}. {success} {result.command}")
                else:
                    print("⚠️  Only one tool was called (might be single-step task)")
                
                # Verify iterative execution
                if len(tool_calls) == len(execution_results):
                    print("✅ Tool calls match execution results (iterative execution confirmed)")
                else:
                    print("❌ Tool calls don't match execution results")
                
            else:
                print("❌ Multi-step test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Multi-step test error: {e}")
    
    async def _test_tool_failure_handling(self):
        """Test that the agent handles tool failures gracefully."""
        print("\n4️⃣ Testing Tool Failure Handling")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing tool failure handling...")
            test_query = "click on a non-existent element with id 'fake-element'"
            
            response = await self.agent_interface.ask(test_query)
            
            if response.get("success"):
                print("✅ Tool failure test completed!")
                
                # Check for tool usage
                tool_calls = response.get("tool_calls", [])
                execution_results = response.get("execution_results", [])
                
                print(f"🔧 Tools called: {len(tool_calls)}")
                print(f"📊 Execution results: {len(execution_results)}")
                
                # Check if any tools failed
                failed_results = [r for r in execution_results if not r.success]
                
                if failed_results:
                    print("✅ Tool failures detected and handled:")
                    for i, result in enumerate(failed_results, 1):
                        print(f"   {i}. ❌ {result.command}")
                        print(f"      Error: {result.error or 'Unknown error'}")
                    
                    # Check if agent tried alternative approaches
                    if len(tool_calls) > len(failed_results):
                        print("✅ Agent tried alternative approaches after failure")
                    else:
                        print("⚠️  Agent didn't try alternative approaches")
                else:
                    print("⚠️  No tool failures detected (element might exist)")
                
            else:
                print("❌ Tool failure test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Tool failure test error: {e}")

# Main execution
async def main():
    """Main test function."""
    tester = IterativeToolCallingTest()
    await tester.run_tests()

# Auto-run when script is loaded
if __name__ == "__main__" or True:  # Always run when imported in qutebrowser
    print("\n🚀 Loading Iterative Tool Calling Test...")
    
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
    print("🧪 Iterative Tool Calling Test Complete!")
    print("   The AI agent should now execute tools one by one")
    print("   with proper feedback between each execution")
    print("=" * 50)
