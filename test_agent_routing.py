#!/usr/bin/env python3
"""
Test script for agent routing system.

This script tests the agent router to ensure it can properly route requests
from the UI to the real AI agent.
"""

import asyncio
import sys
import os

# Add the ai_agent_tools directory to the path
ai_agent_tools_path = os.path.join(os.path.dirname(__file__), 'ai_agent_tools')
if ai_agent_tools_path not in sys.path:
    sys.path.insert(0, ai_agent_tools_path)

# Add qutebrowser commands to the path
qutebrowser_commands_path = os.path.join(os.path.dirname(__file__), 'qutebrowser', 'commands')
if qutebrowser_commands_path not in sys.path:
    sys.path.insert(0, qutebrowser_commands_path)


async def test_agent_router():
    """Test the agent router functionality."""
    print("🧪 Testing Agent Router...")
    
    try:
        # Import the agent router
        from ai_agent_router import get_agent_router
        
        # Get the router
        router = get_agent_router()
        print("✅ Agent router imported successfully")
        
        # Initialize the agent
        print("🔄 Initializing agent...")
        await router.initialize_agent()
        
        if router.is_initialized:
            print("✅ Agent initialized successfully")
            print(f"🤖 Agent type: {type(router.agent).__name__}")
        else:
            print("❌ Agent initialization failed")
            return False
        
        # Test with a simple query
        print("🧪 Testing with query: 'open youtube.com'")
        result = await router.process_query("open youtube.com")
        
        print("📊 Query Result:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Message: {result.get('message', 'No message')}")
        print(f"  Error: {result.get('error', 'None')}")
        print(f"  Tool Calls: {len(result.get('tool_calls', []))}")
        
        if result.get('execution_stats'):
            stats = result['execution_stats']
            print(f"  Execution Stats: {stats}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error testing agent router: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_direct_agent():
    """Test the agent directly without the router."""
    print("\n🧪 Testing Direct Agent...")
    
    try:
        # Try enhanced sequential agent first
        try:
            from enhanced_sequential_agent import create_enhanced_sequential_agent, SequentialAgentConfig
            
            config = SequentialAgentConfig(
                llm_provider="ollama",
                model="deepseek-r1:14b",
                debug=True,
                max_tool_calls=3,  # Limit for testing
                enable_loop_prevention=True,
                enable_state_tracking=True
            )
            
            agent = create_enhanced_sequential_agent(config)
            print("✅ Enhanced sequential agent created")
            
            # Test query
            response = await agent.process_query("open youtube.com")
            print(f"✅ Enhanced agent response: {response.success}")
            return True
            
        except ImportError:
            print("⚠️ Enhanced sequential agent not available, trying original agent")
            
            # Fall back to original agent
            from ai_browser_agent import create_ai_agent
            agent = create_ai_agent(provider="ollama", model="deepseek-r1:14b")
            print("✅ Original AI agent created")
            
            # Test query
            response = await agent.process_query("open youtube.com")
            print(f"✅ Original agent response: {response.success}")
            return True
            
    except Exception as e:
        print(f"❌ Error testing direct agent: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🚀 Starting Agent Routing Tests...\n")
    
    # Test 1: Direct agent
    direct_success = await test_direct_agent()
    
    # Test 2: Agent router
    router_success = await test_agent_router()
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"  Direct Agent: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"  Agent Router: {'✅ PASS' if router_success else '❌ FAIL'}")
    
    if direct_success and router_success:
        print("\n🎉 All tests passed! The agent routing system is working correctly.")
        print("You can now use :agent-ui and :agent-init in qutebrowser.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return direct_success and router_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
