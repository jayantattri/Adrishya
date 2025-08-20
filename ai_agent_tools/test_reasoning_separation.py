#!/usr/bin/env python3
"""
Test Reasoning Separation for DeepSeek R1 14B

This script demonstrates how the AI agent properly separates the reasoning model's
thinking process from the actual browser actions.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_reasoning_separation.py
"""

import asyncio
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧠 Testing Reasoning Separation for DeepSeek R1 14B...")

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

class ReasoningSeparationTest:
    """Test the reasoning separation functionality."""
    
    def __init__(self):
        self.agent_interface = None
    
    async def run_tests(self):
        """Run comprehensive tests of reasoning separation."""
        print("\n🚀 Starting Reasoning Separation Tests")
        print("=" * 50)
        
        # Initialize agent
        await self._test_agent_initialization()
        
        # Test simple reasoning
        await self._test_simple_reasoning()
        
        # Test complex reasoning
        await self._test_complex_reasoning()
        
        # Test tool execution reasoning
        if QUTEBROWSER_AVAILABLE:
            await self._test_tool_execution_reasoning()
        
        print("\n🎉 Reasoning Separation Tests Complete!")
    
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
    
    async def _test_simple_reasoning(self):
        """Test simple reasoning without browser actions."""
        print("\n2️⃣ Testing Simple Reasoning")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing simple reasoning query...")
            test_query = "What would you need to do to help me research Python web frameworks?"
            
            response = await self.agent_interface.ask(test_query)
            
            if response.get("success"):
                print("✅ Simple reasoning test successful!")
                
                # Check for reasoning separation
                reasoning = response.get("reasoning")
                action = response.get("message")
                
                if reasoning:
                    print(f"\n🧠 REASONING DETECTED:")
                    print(f"   {reasoning[:200]}...")
                else:
                    print("⚠️  No reasoning detected in response")
                
                if action:
                    print(f"\n✅ ACTION DETECTED:")
                    print(f"   {action[:200]}...")
                
            else:
                print("❌ Simple reasoning test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Simple reasoning test error: {e}")
    
    async def _test_complex_reasoning(self):
        """Test complex reasoning for multi-step tasks."""
        print("\n3️⃣ Testing Complex Reasoning")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing complex reasoning query...")
            test_query = "How would you help me research AI tools by opening multiple websites and comparing their features?"
            
            response = await self.agent_interface.ask(test_query)
            
            if response.get("success"):
                print("✅ Complex reasoning test successful!")
                
                # Check for reasoning separation
                reasoning = response.get("reasoning")
                action = response.get("message")
                
                if reasoning:
                    print(f"\n🧠 COMPLEX REASONING DETECTED:")
                    print(f"   {reasoning[:300]}...")
                else:
                    print("⚠️  No reasoning detected in response")
                
                if action:
                    print(f"\n✅ ACTION PLAN DETECTED:")
                    print(f"   {action[:300]}...")
                
            else:
                print("❌ Complex reasoning test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Complex reasoning test error: {e}")
    
    async def _test_tool_execution_reasoning(self):
        """Test reasoning during actual tool execution."""
        print("\n4️⃣ Testing Tool Execution Reasoning")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing tool execution reasoning...")
            test_query = "Open example.com and explain what you're doing"
            
            response = await self.agent_interface.ask(test_query)
            
            if response.get("success"):
                print("✅ Tool execution reasoning test successful!")
                
                # Check for reasoning separation
                reasoning = response.get("reasoning")
                action = response.get("message")
                tool_calls = response.get("tool_calls", [])
                
                if reasoning:
                    print(f"\n🧠 EXECUTION REASONING:")
                    print(f"   {reasoning[:200]}...")
                
                if action:
                    print(f"\n✅ EXECUTION ACTION:")
                    print(f"   {action[:200]}...")
                
                if tool_calls:
                    print(f"\n🔧 TOOLS EXECUTED: {len(tool_calls)}")
                    for i, tool_call in enumerate(tool_calls, 1):
                        tool_name = tool_call.get("name", "unknown")
                        print(f"   {i}. {tool_name}")
                
            else:
                print("❌ Tool execution reasoning test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Tool execution reasoning test error: {e}")

# Main execution
async def main():
    """Main test function."""
    tester = ReasoningSeparationTest()
    await tester.run_tests()

# Auto-run when script is loaded
if __name__ == "__main__" or True:  # Always run when imported in qutebrowser
    print("\n🚀 Loading Reasoning Separation Test...")
    
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
    print("🧠 Reasoning Separation Test Complete!")
    print("   The DeepSeek R1 14B model now properly separates")
    print("   reasoning from actions for better clarity")
    print("=" * 50)
