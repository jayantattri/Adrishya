"""
AI Agent Router for Qutebrowser

This module handles routing requests from the agent UI to the real AI agent
and manages the communication between the UI and the agent backend.
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Try to import qutebrowser modules, but handle gracefully if not available
try:
    from qutebrowser.api import cmdutils, message, objreg
    from qutebrowser.utils import log
    QUTEBROWSER_AVAILABLE = True
except ImportError:
    QUTEBROWSER_AVAILABLE = False
    # Create mock objects for testing
    class MockCmdutils:
        def register(self):
            def decorator(func):
                return func
            return decorator
        CommandValue = type('CommandValue', (), {'win_id': 'win_id', 'quoted_string': 'quoted_string'})
    
    class MockMessage:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
    
    class MockLog:
        def exception(self, msg): print(f"EXCEPTION: {msg}")
    
    cmdutils = MockCmdutils()
    message = MockMessage()
    log = MockLog()


class AgentRouter:
    """Routes requests from the agent UI to the real AI agent."""
    
    def __init__(self):
        self.agent = None
        self.is_initialized = False
    
    async def initialize_agent(self):
        """Initialize the AI agent."""
        try:
            # Import the enhanced sequential agent
            import sys
            import os
            
            # Add the ai_agent_tools directory to the path
            ai_agent_tools_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ai_agent_tools')
            if ai_agent_tools_path not in sys.path:
                sys.path.insert(0, ai_agent_tools_path)
            
            # Try to import the enhanced sequential agent
            try:
                from enhanced_sequential_agent import (
                    create_enhanced_sequential_agent, 
                    SequentialAgentConfig
                )
                
                # Create agent configuration
                config = SequentialAgentConfig(
                    llm_provider="ollama",
                    model="deepseek-r1:14b",
                    debug=True,
                    max_tool_calls=8,
                    enable_loop_prevention=True,
                    enable_state_tracking=True
                )
                
                # Create the agent
                self.agent = create_enhanced_sequential_agent(config)
                self.is_initialized = True
                logger.info("Enhanced sequential agent initialized successfully")
                
            except ImportError as e:
                logger.warning(f"Enhanced sequential agent not available: {e}")
                # Fall back to the original AI agent
                try:
                    from ai_browser_agent import create_ai_agent
                    
                    # Create agent
                    self.agent = create_ai_agent(provider="ollama", model="deepseek-r1:14b")
                    self.is_initialized = True
                    logger.info("Original AI agent initialized successfully")
                    
                except ImportError as e2:
                    logger.error(f"Original AI agent also not available: {e2}")
                    self.is_initialized = False
                    
        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            self.is_initialized = False
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query with the AI agent.
        
        Args:
            query: The user's query string
            
        Returns:
            Dictionary with agent response data
        """
        if not self.is_initialized or not self.agent:
            # Try to initialize if not already done
            await self.initialize_agent()
            
            if not self.is_initialized:
                return {
                    "success": False,
                    "error": "AI agent not available",
                    "message": "Failed to initialize AI agent"
                }
        
        try:
            # Process the query
            response = await self.agent.process_query(query)
            
            # Format the response for the UI
            result = {
                "success": response.success,
                "message": response.message,
                "reasoning": getattr(response, 'thinking', None),
                "tool_calls": response.tool_calls,
                "error": getattr(response, 'error', None)
            }
            
            # Add execution stats if available
            if hasattr(response, 'execution_stats'):
                result["execution_stats"] = response.execution_stats
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "success": False,
                "error": f"Agent processing failed: {str(e)}",
                "message": "Failed to process request with AI agent"
            }


# Global agent router instance
agent_router = AgentRouter()


# Only register commands if qutebrowser is available
if QUTEBROWSER_AVAILABLE:
    @cmdutils.register()
    @cmdutils.argument('win_id', value=cmdutils.CommandValue.win_id)
    def agent_init(win_id: int) -> None:
        """Initialize the AI agent for use with the agent UI."""
        try:
            # Initialize the agent asynchronously
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.create_task(agent_router.initialize_agent())
            
            message.info("🤖 AI Agent initialization started...")
            
        except Exception as e:
            log.misc.exception("Error initializing agent")
            message.error(f"Could not initialize AI agent: {str(e)}")


    @cmdutils.register(maxsplit=0)
    @cmdutils.argument('win_id', value=cmdutils.CommandValue.win_id)
    def agent_query(win_id: int, query: str) -> None:
        """Process a query with the AI agent and display the result.
        
        Args:
            win_id: Window ID
            query: The query to process
        """
        try:
            # Process the query asynchronously
            async def process_and_display():
                result = await agent_router.process_query(query)
                
                if result["success"]:
                    # Display success message
                    message.info(f"✅ {result['message']}")
                    
                    # Log tool calls if any
                    if result.get("tool_calls"):
                        tool_count = len(result["tool_calls"])
                        message.info(f"🔧 Executed {tool_count} tool(s)")
                        
                    # Log execution stats if available
                    if result.get("execution_stats"):
                        stats = result["execution_stats"]
                        message.info(f"📊 Execution: {stats.get('total_tools_executed', 0)} tools, {stats.get('execution_time', 0):.2f}s")
                        
                else:
                    # Display error message
                    error_msg = result.get("error", "Unknown error")
                    message.error(f"❌ {error_msg}")
            
            # Run the async function
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.create_task(process_and_display())
            
        except Exception as e:
            log.misc.exception("Error processing agent query")
            message.error(f"Could not process query: {str(e)}")


    @cmdutils.register()
    @cmdutils.argument('win_id', value=cmdutils.CommandValue.win_id)
    def agent_status(win_id: int) -> None:
        """Check the status of the AI agent."""
        try:
            if agent_router.is_initialized and agent_router.agent:
                message.info("🤖 AI Agent is ready and initialized")
            else:
                message.warning("⚠️ AI Agent is not initialized. Run :agent-init to initialize.")
                
        except Exception as e:
            log.misc.exception("Error checking agent status")
            message.error(f"Could not check agent status: {str(e)}")


# Function to get agent router instance (for use by other modules)
def get_agent_router() -> AgentRouter:
    """Get the global agent router instance."""
    return agent_router
