#!/usr/bin/env python3
"""
Test Context Handling for AI Browser Agent

This script tests that the AI agent properly handles context and doesn't let
browsing history override current user requests.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_context_handling.py
"""

import asyncio
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing Context Handling for AI Browser Agent...")

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

class ContextHandlingTest:
    """Test that the AI agent properly handles context and current requests."""
    
    def __init__(self):
        self.agent_interface = None
    
    async def run_tests(self):
        """Run comprehensive tests of context handling."""
        print("\n🚀 Starting Context Handling Tests")
        print("=" * 50)
        
        # Initialize agent
        await self._test_agent_initialization()
        
        # Test context separation
        await self._test_context_separation()
        
        # Test current request priority
        await self._test_current_request_priority()
        
        # Test history influence
        await self._test_history_influence()
        
        print("\n🎉 Context Handling Tests Complete!")
    
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
                print("🧠 Context-aware reasoning model ready for testing")
            else:
                print("❌ Failed to initialize DeepSeek agent")
                
        except Exception as e:
            print(f"❌ Initialization error: {e}")
    
    async def _test_context_separation(self):
        """Test that the agent properly separates current request from history."""
        print("\n2️⃣ Testing Context Separation")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing context separation...")
            
            # First request - should navigate to GitHub
            print("   Step 1: Requesting to open GitHub...")
            response1 = await self.agent_interface.ask("open github.com")
            
            if response1.get("success"):
                print("   ✅ First request successful")
                tool_calls1 = response1.get("tool_calls", [])
                if any(tc.get("name") == "open_url" for tc in tool_calls1):
                    print("   ✅ open_url tool called correctly for GitHub")
                else:
                    print("   ❌ open_url tool not called for GitHub")
            else:
                print(f"   ❌ First request failed: {response1.get('error')}")
            
            # Second request - should be different and not influenced by GitHub
            print("   Step 2: Requesting to research Python frameworks...")
            response2 = await self.agent_interface.ask("help me research Python frameworks")
            
            if response2.get("success"):
                print("   ✅ Second request successful")
                tool_calls2 = response2.get("tool_calls", [])
                
                # Check if it's doing something different from GitHub
                github_calls = [tc for tc in tool_calls2 if tc.get("name") == "open_url" and "github.com" in tc.get("parameters", {}).get("url", "")]
                
                if github_calls:
                    print("   ❌ Second request still went to GitHub (context not separated)")
                else:
                    print("   ✅ Second request was different from GitHub (context properly separated)")
                    
                    # Show what it actually did
                    for i, tool_call in enumerate(tool_calls2, 1):
                        tool_name = tool_call.get("name", "unknown")
                        params = tool_call.get("parameters", {})
                        print(f"      {i}. {tool_name}: {params}")
            else:
                print(f"   ❌ Second request failed: {response2.get('error')}")
                
        except Exception as e:
            print(f"❌ Context separation test error: {e}")
    
    async def _test_current_request_priority(self):
        """Test that the agent prioritizes current request over history."""
        print("\n3️⃣ Testing Current Request Priority")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing current request priority...")
            
            # Create a sequence of different requests
            test_sequence = [
                "open reddit.com",
                "search for machine learning tutorials",
                "open stackoverflow.com",
                "help me find Python documentation"
            ]
            
            for i, query in enumerate(test_sequence, 1):
                print(f"   Step {i}: '{query}'")
                
                response = await self.agent_interface.ask(query)
                
                if response.get("success"):
                    tool_calls = response.get("tool_calls", [])
                    
                    # Check if the response matches the current request
                    current_request_appropriate = self._check_request_appropriateness(query, tool_calls)
                    
                    if current_request_appropriate:
                        print(f"   ✅ Step {i}: Response appropriate for current request")
                    else:
                        print(f"   ❌ Step {i}: Response not appropriate for current request")
                        
                        # Show what it actually did
                        for j, tool_call in enumerate(tool_calls, 1):
                            tool_name = tool_call.get("name", "unknown")
                            params = tool_call.get("parameters", {})
                            print(f"      {j}. {tool_name}: {params}")
                else:
                    print(f"   ❌ Step {i} failed: {response.get('error')}")
                
                # Small delay between requests
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Current request priority test error: {e}")
    
    async def _test_history_influence(self):
        """Test that history provides context but doesn't override current intent."""
        print("\n4️⃣ Testing History Influence")
        print("-" * 30)
        
        if not self.agent_interface or not self.agent_interface.agent:
            print("❌ Agent not initialized, skipping test")
            return
        
        try:
            print("🧠 Testing history influence...")
            
            # Create a specific scenario
            print("   Scenario: Navigate to GitHub, then ask for Python research")
            
            # Step 1: Navigate to GitHub
            print("   Step 1: Navigating to GitHub...")
            response1 = await self.agent_interface.ask("open github.com")
            
            if not response1.get("success"):
                print(f"   ❌ Step 1 failed: {response1.get('error')}")
                return
            
            # Step 2: Ask for Python research (should NOT go back to GitHub)
            print("   Step 2: Asking for Python research...")
            response2 = await self.agent_interface.ask("I want to research Python frameworks and libraries")
            
            if response2.get("success"):
                tool_calls = response2.get("tool_calls", [])
                
                # Check if it's doing Python research (not going back to GitHub)
                github_calls = [tc for tc in tool_calls if tc.get("name") == "open_url" and "github.com" in tc.get("parameters", {}).get("url", "")]
                python_research_calls = [tc for tc in tool_calls if tc.get("name") == "open_url" and any(term in tc.get("parameters", {}).get("url", "").lower() for term in ["python", "pypi", "docs.python", "realpython"])]
                
                if github_calls and not python_research_calls:
                    print("   ❌ Still going to GitHub instead of Python research (history overriding current request)")
                elif python_research_calls:
                    print("   ✅ Doing Python research as requested (current request prioritized)")
                else:
                    print("   ⚠️  Neither GitHub nor Python research - showing what it did:")
                    for i, tool_call in enumerate(tool_calls, 1):
                        tool_name = tool_call.get("name", "unknown")
                        params = tool_call.get("parameters", {})
                        print(f"      {i}. {tool_name}: {params}")
            else:
                print(f"   ❌ Step 2 failed: {response2.get('error')}")
                
        except Exception as e:
            print(f"❌ History influence test error: {e}")
    
    def _check_request_appropriateness(self, query: str, tool_calls: list) -> bool:
        """Check if tool calls are appropriate for the given query."""
        query_lower = query.lower()
        
        # Define expected behaviors for different query types
        if "reddit" in query_lower:
            return any(tc.get("name") == "open_url" and "reddit.com" in tc.get("parameters", {}).get("url", "") for tc in tool_calls)
        elif "stackoverflow" in query_lower:
            return any(tc.get("name") == "open_url" and "stackoverflow.com" in tc.get("parameters", {}).get("url", "") for tc in tool_calls)
        elif "search" in query_lower and "machine learning" in query_lower:
            return any(tc.get("name") == "open_url" and any(term in tc.get("parameters", {}).get("url", "").lower() for term in ["google", "search", "ml", "machine-learning"]) for tc in tool_calls)
        elif "python" in query_lower and ("documentation" in query_lower or "research" in query_lower):
            return any(tc.get("name") == "open_url" and any(term in tc.get("parameters", {}).get("url", "").lower() for term in ["python", "docs.python", "pypi", "realpython"]) for tc in tool_calls)
        
        # Default: any tool call is acceptable
        return len(tool_calls) > 0

# Main execution
async def main():
    """Main test function."""
    tester = ContextHandlingTest()
    await tester.run_tests()

# Auto-run when script is loaded
if __name__ == "__main__" or True:  # Always run when imported in qutebrowser
    print("\n🚀 Loading Context Handling Test...")
    
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
    print("🧪 Context Handling Test Complete!")
    print("   The AI agent should now properly prioritize")
    print("   current requests over browsing history")
    print("=" * 50)
