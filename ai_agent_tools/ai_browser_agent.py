"""
AI Browser Agent for Qutebrowser

This module implements an intelligent browser assistant that uses LLMs to interpret
natural language queries and execute appropriate browser control actions.

Supported LLM providers:
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Ollama (Local models)
- Custom API endpoints
"""

import json
import os
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from browser_control_tools import (
        BrowserControlTools, CommandResult, create_browser_controller
    )
    from enhanced_browser_control import (
        EnhancedBrowserControl, create_enhanced_controller,
        WorkflowStep, BrowserWorkflow
    )
    from unified_state_tools import (
        get_quick_status, get_browser_overview, get_page_content_summary
    )
    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Browser tools not available: {e}")
    TOOLS_AVAILABLE = False
    # Create minimal placeholder classes
    class BrowserControlTools:
        def __init__(self, *args, **kwargs): pass
    class EnhancedBrowserControl:
        def __init__(self, *args, **kwargs): pass

# LLM Provider imports (optional)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class AgentConfig:
    """Configuration for the AI browser agent."""
    llm_provider: str = "openai"  # openai, anthropic, ollama, custom
    model: str = "gpt-4"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 1500
    timeout: int = 30
    max_tool_calls: int = 10
    debug: bool = False


@dataclass
class AgentResponse:
    """Response from the AI agent."""
    success: bool
    message: str
    tool_calls: List[Dict[str, Any]]
    execution_results: List[CommandResult]
    thinking: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class LLMProvider:
    """Base class for LLM providers."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate response with tool calling support."""
        raise NotImplementedError
    
    def format_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Format a tool call for the LLM."""
        return {
            "name": tool_name,
            "parameters": parameters
        }


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not available")
        
        self.client = openai.OpenAI(
            api_key=config.api_key or os.getenv("OPENAI_API_KEY"),
            base_url=config.api_base
        )
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        try:
            # Convert tools to OpenAI format
            openai_tools = []
            for tool in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"]
                    }
                })
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=openai_tools if openai_tools else None,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout
            )
            
            message = response.choices[0].message
            
            result = {
                "content": message.content or "",
                "tool_calls": []
            }
            
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result["tool_calls"].append({
                        "name": tool_call.function.name,
                        "parameters": json.loads(tool_call.function.arguments)
                    })
            
            return result
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not available")
        
        self.client = anthropic.Anthropic(
            api_key=config.api_key or os.getenv("ANTHROPIC_API_KEY")
        )
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate response using Anthropic API."""
        try:
            # Convert messages to Claude format
            system_message = ""
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    claude_messages.append(msg)
            
            # Convert tools to Claude format
            claude_tools = []
            for tool in tools:
                claude_tools.append({
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": tool["parameters"]
                })
            
            response = self.client.messages.create(
                model=self.config.model,
                system=system_message,
                messages=claude_messages,
                tools=claude_tools if claude_tools else None,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            result = {
                "content": "",
                "tool_calls": []
            }
            
            for content_block in response.content:
                if content_block.type == "text":
                    result["content"] += content_block.text
                elif content_block.type == "tool_use":
                    result["tool_calls"].append({
                        "name": content_block.name,
                        "parameters": content_block.input
                    })
            
            return result
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")


class OllamaProvider(LLMProvider):
    """Ollama local model provider."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests package not available")
        
        self.base_url = config.api_base or "http://localhost:11434"
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate response using Ollama API."""
        try:
            # Ollama doesn't support function calling yet, so we include tools in system prompt
            tools_text = self._format_tools_for_prompt(tools)
            
            # Add tools to system message
            enhanced_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    enhanced_content = msg["content"] + f"\n\nAvailable tools:\n{tools_text}"
                    enhanced_messages.append({
                        "role": "system", 
                        "content": enhanced_content
                    })
                else:
                    enhanced_messages.append(msg)
            
            payload = {
                "model": self.config.model,
                "messages": enhanced_messages,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result_data = response.json()
            content = result_data.get("message", {}).get("content", "")
            
            # Parse tool calls from content (basic implementation)
            tool_calls = self._extract_tool_calls_from_content(content)
            
            return {
                "content": content,
                "tool_calls": tool_calls
            }
            
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _format_tools_for_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """Format tools for inclusion in prompt."""
        tools_text = ""
        for tool in tools:
            tools_text += f"- {tool['name']}: {tool['description']}\n"
            if 'parameters' in tool:
                tools_text += f"  Parameters: {json.dumps(tool['parameters'], indent=2)}\n"
        return tools_text
    
    def _extract_tool_calls_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract tool calls from response content (basic parsing)."""
        tool_calls = []
        
        # Look for tool call patterns in the response
        # This is a simple implementation - could be enhanced with better parsing
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('TOOL_CALL:'):
                try:
                    tool_data = json.loads(line[10:])  # Remove 'TOOL_CALL:' prefix
                    tool_calls.append(tool_data)
                except json.JSONDecodeError:
                    continue
        
        return tool_calls


class AIBrowserAgent:
    """Main AI browser agent that combines LLM reasoning with browser control."""
    
    def __init__(self, config: AgentConfig = None, window_id: int = 0):
        """Initialize the AI browser agent.
        
        Args:
            config: Agent configuration
            window_id: Qutebrowser window ID to control
        """
        self.config = config or AgentConfig()
        self.window_id = window_id
        
        # Initialize browser control tools
        if TOOLS_AVAILABLE:
            self.browser_controller = create_browser_controller(window_id)
            self.enhanced_controller = create_enhanced_controller(window_id)
        else:
            self.browser_controller = None
            self.enhanced_controller = None
        
        # Initialize LLM provider
        self.llm_provider = self._create_llm_provider()
        
        # Load tools configuration
        self.tools_config = self._load_tools_config()
        
        # Agent state
        self.conversation_history = []
        self.last_response = None
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
    
    def _create_llm_provider(self) -> LLMProvider:
        """Create the appropriate LLM provider."""
        if self.config.llm_provider == "openai":
            return OpenAIProvider(self.config)
        elif self.config.llm_provider == "anthropic":
            return AnthropicProvider(self.config)
        elif self.config.llm_provider == "ollama":
            return OllamaProvider(self.config)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")
    
    def _load_tools_config(self) -> Dict[str, Any]:
        """Load tools configuration from JSON file."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "agent_tools.json")
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load tools config: {e}")
            return {"tools": [], "tool_categories": {}}
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent."""
        return """You are a powerful agentic AI browser assistant. You operate exclusively in Qutebrowser, the world's best browser.
You are pair browsing with a USER to solve their browsing tasks efficiently and intelligently.

<tool_calling>
You have comprehensive browser control tools at your disposal. Follow these rules regarding tool calls:

1. ALWAYS respond with appropriate tool calls when the user asks you to perform browser actions
2. Use the most appropriate tools for each task - prefer smart_action for complex tasks
3. Break down complex requests into logical steps using multiple tool calls
4. ALWAYS get current browser state before making navigation decisions
5. Wait for page loads before interacting with page elements
6. Use proper error handling and provide fallback strategies
7. Validate user inputs and ask for clarification when needed
8. Prefer reliable selectors (ID > CSS class > complex CSS)
9. Combine simple actions into workflows for repetitive tasks
10. Always verify successful completion of critical actions

Tool Usage Guidelines:
- get_browser_state(): Check current browser state before actions
- get_page_info(): Understand current page before interactions
- open_url(): Navigate to new pages
- tab_*(): Manage browser tabs
- scroll_page(), zoom_page(): Control page view
- click_element(), type_text(): Interact with page elements
- fill_form(): Automate form submissions
- search_page(): Find content on pages
- smart_action(): Handle complex multi-step tasks
- wait_for_load(): Ensure pages load before continuing
- execute_javascript(): Advanced page manipulation

Safety Rules:
- Always validate URLs before opening
- Be cautious with form submissions
- Respect website rate limits
- Use temporary settings when possible
- Never perform destructive actions without confirmation
</tool_calling>

<capabilities>
I can help you with:
- Website navigation and browsing
- Form filling and data entry
- Content extraction and analysis
- Tab and window management
- Search and information gathering
- Automated workflows and repetitive tasks
- Page interaction and element manipulation
- Browser configuration and customization

I understand natural language requests and convert them into precise browser actions.
I provide clear feedback about what I'm doing and why.
I handle errors gracefully and suggest alternatives when things don't work as expected.
</capabilities>

<context>
I have access to comprehensive browser state information and can perform any browser action that a human user could do.
I work within Qutebrowser's security model and respect website terms of service.
I prioritize user safety and data privacy in all operations.
</context>

Respond naturally and conversationally while using tools to accomplish the user's browser-related tasks."""

    def _get_current_context(self) -> Dict[str, Any]:
        """Get current browser context for the LLM."""
        context = {
            "timestamp": datetime.now().isoformat(),
            "browser_state": None,
            "page_info": None
        }
        
        try:
            if TOOLS_AVAILABLE:
                # Get browser state
                browser_state = get_quick_status()
                if browser_state:
                    context["browser_state"] = browser_state
                
                # Get page info if available
                page_info = get_page_content_summary()
                if page_info and "error" not in page_info:
                    # Truncate content for context efficiency
                    if "main_text" in page_info:
                        text = page_info["main_text"]
                        if len(text) > 500:
                            page_info["main_text"] = text[:500] + "..."
                    context["page_info"] = page_info
        except Exception as e:
            self.logger.debug(f"Could not get browser context: {e}")
        
        return context
    
    async def process_query(self, user_query: str) -> AgentResponse:
        """Process a natural language query and execute appropriate browser actions.
        
        Args:
            user_query: Natural language query from the user
            
        Returns:
            AgentResponse with results and tool executions
        """
        if not TOOLS_AVAILABLE:
            return AgentResponse(
                success=False,
                message="Browser control tools are not available",
                tool_calls=[],
                execution_results=[],
                error="Tools not loaded"
            )
        
        try:
            # Get current context
            context = self._get_current_context()
            
            # Prepare messages for LLM
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"Current browser context: {json.dumps(context, indent=2)}\n\nUser request: {user_query}"}
            ]
            
            # Add conversation history (last 5 exchanges)
            if self.conversation_history:
                recent_history = self.conversation_history[-10:]  # Last 5 exchanges (user + assistant)
                messages.extend(recent_history)
            
            # Get LLM response with tool calls
            llm_response = await self.llm_provider.generate_response(
                messages=messages,
                tools=self.tools_config.get("tools", [])
            )
            
            # Execute tool calls
            execution_results = []
            if llm_response.get("tool_calls"):
                execution_results = await self._execute_tool_calls(llm_response["tool_calls"])
            
            # Create response
            response = AgentResponse(
                success=True,
                message=llm_response.get("content", "Task completed"),
                tool_calls=llm_response.get("tool_calls", []),
                execution_results=execution_results,
                thinking=llm_response.get("thinking")
            )
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": response.message}
            ])
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            self.last_response = response
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return AgentResponse(
                success=False,
                message=f"Error processing your request: {str(e)}",
                tool_calls=[],
                execution_results=[],
                error=str(e)
            )
    
    async def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[CommandResult]:
        """Execute the tool calls returned by the LLM.
        
        Args:
            tool_calls: List of tool calls from LLM
            
        Returns:
            List of execution results
        """
        results = []
        
        for tool_call in tool_calls:
            try:
                tool_name = tool_call["name"]
                parameters = tool_call.get("parameters", {})
                
                self.logger.debug(f"Executing tool: {tool_name} with parameters: {parameters}")
                
                # Map tool names to actual methods
                result = await self._execute_single_tool(tool_name, parameters)
                results.append(result)
                
                # Stop if we hit max tool calls
                if len(results) >= self.config.max_tool_calls:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error executing tool {tool_call}: {e}")
                results.append(CommandResult(
                    success=False,
                    command=tool_call.get("name", "unknown"),
                    args=[],
                    error=str(e)
                ))
        
        return results
    
    async def _execute_single_tool(self, tool_name: str, parameters: Dict[str, Any]) -> CommandResult:
        """Execute a single tool call.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            CommandResult from tool execution
        """
        try:
            # Navigation tools
            if tool_name == "open_url":
                return self.browser_controller.open_url(**parameters)
            
            elif tool_name == "navigate_back":
                return self.browser_controller.go_back(**parameters)
            
            elif tool_name == "navigate_forward":
                return self.browser_controller.go_forward(**parameters)
            
            elif tool_name == "reload_page":
                return self.browser_controller.reload_page(**parameters)
            
            elif tool_name == "stop_loading":
                return self.browser_controller.stop_loading()
            
            # Page interaction tools
            elif tool_name == "scroll_page":
                direction = parameters["direction"]
                amount = parameters.get("amount", "page")
                count = parameters.get("count", 1)
                
                if amount == "page":
                    return self.browser_controller.scroll(direction, count=count)
                else:
                    return self.enhanced_controller.smart_scroll(direction, amount)
            
            elif tool_name == "scroll_to_position":
                return self.browser_controller.scroll_to_perc(
                    parameters["percentage"],
                    horizontal=parameters.get("horizontal", False)
                )
            
            elif tool_name == "zoom_page":
                action = parameters["action"]
                if action == "in":
                    return self.browser_controller.zoom_in(count=parameters.get("count", 1))
                elif action == "out":
                    return self.browser_controller.zoom_out(count=parameters.get("count", 1))
                elif action == "set":
                    return self.browser_controller.zoom(parameters["level"])
            
            elif tool_name == "search_page":
                return self.browser_controller.search(
                    parameters["text"],
                    reverse=parameters.get("reverse", False)
                )
            
            elif tool_name == "search_next":
                return self.browser_controller.search_next(count=parameters.get("count", 1))
            
            elif tool_name == "search_previous":
                return self.browser_controller.search_prev(count=parameters.get("count", 1))
            
            # Tab management tools
            elif tool_name == "tab_new":
                url = parameters.get("url")
                if url:
                    return self.browser_controller.open_url(
                        url, tab=True, bg=parameters.get("bg", False),
                        private=parameters.get("private", False)
                    )
                else:
                    return self.browser_controller.tab_new(bg=parameters.get("bg", False))
            
            elif tool_name == "tab_close":
                return self.browser_controller.tab_close(**parameters)
            
            elif tool_name == "tab_switch":
                direction = parameters.get("direction")
                index = parameters.get("index")
                count = parameters.get("count", 1)
                
                if index:
                    return self.browser_controller.tab_focus(index)
                elif direction == "next":
                    return self.browser_controller.tab_next(count=count)
                elif direction == "prev":
                    return self.browser_controller.tab_prev(count=count)
                elif direction == "first":
                    return self.browser_controller.tab_focus(1)
                elif direction == "last":
                    return self.browser_controller.tab_focus("last")
            
            elif tool_name == "tab_move":
                position = parameters.get("position")
                index = parameters.get("index")
                count = parameters.get("count", 1)
                
                if index:
                    return self.browser_controller.tab_move(index)
                elif position:
                    return self.browser_controller.tab_move(position, count=count)
            
            elif tool_name == "tab_pin":
                return self.browser_controller.tab_pin()
            
            elif tool_name == "tab_clone":
                return self.browser_controller.tab_clone(**parameters)
            
            # Element interaction tools
            elif tool_name == "click_element":
                return self.browser_controller.click_element(
                    parameters["selector_type"],
                    parameters.get("selector_value")
                )
            
            elif tool_name == "type_text":
                text = parameters["text"]
                clear_first = parameters.get("clear_first", False)
                
                if clear_first:
                    # Clear existing text first
                    self.browser_controller.fake_key("<Ctrl-a>")
                
                return self.browser_controller.insert_text(text)
            
            elif tool_name == "send_key":
                return self.browser_controller.fake_key(
                    parameters["key"],
                    global_=parameters.get("global", False)
                )
            
            elif tool_name == "fill_form":
                from enhanced_browser_control import FormField, ElementSelector
                
                # Convert parameters to FormField objects
                fields = []
                for field_data in parameters["fields"]:
                    selector = ElementSelector(
                        selector_type=field_data["selector_type"],
                        value=field_data["selector_value"],
                        description=f"{field_data['field_type']} field"
                    )
                    field = FormField(
                        selector=selector,
                        value=field_data["value"],
                        field_type=field_data.get("field_type", "text")
                    )
                    fields.append(field)
                
                results = self.enhanced_controller.fill_form(
                    fields, submit=parameters.get("submit", True)
                )
                return results[-1] if results else CommandResult(success=False, command="fill_form", args=[])
            
            # Information gathering tools
            elif tool_name == "get_page_info":
                try:
                    info = get_page_content_summary()
                    return CommandResult(
                        success=True,
                        command="get_page_info",
                        args=[],
                        message=json.dumps(info, indent=2)
                    )
                except Exception as e:
                    return CommandResult(
                        success=False,
                        command="get_page_info",
                        args=[],
                        error=str(e)
                    )
            
            elif tool_name == "get_browser_state":
                try:
                    state = get_browser_overview()
                    return CommandResult(
                        success=True,
                        command="get_browser_state",
                        args=[],
                        message=json.dumps(state, indent=2)
                    )
                except Exception as e:
                    return CommandResult(
                        success=False,
                        command="get_browser_state", 
                        args=[],
                        error=str(e)
                    )
            
            # Advanced tools
            elif tool_name == "execute_javascript":
                return self.browser_controller.execute_javascript(
                    parameters["code"],
                    quiet=parameters.get("quiet", False)
                )
            
            elif tool_name == "set_config":
                return self.browser_controller.set_config(
                    parameters["option"],
                    parameters["value"],
                    temp=parameters.get("temp", False)
                )
            
            elif tool_name == "smart_action":
                from enhanced_browser_control import execute_smart_action
                return execute_smart_action(
                    parameters["goal"],
                    context=parameters.get("context", {}),
                    window_id=self.window_id
                )
            
            # Waiting tools
            elif tool_name == "wait_for_load":
                success = self.enhanced_controller.wait_for_page_load(
                    timeout=parameters.get("timeout", 30)
                )
                return CommandResult(
                    success=success,
                    command="wait_for_load",
                    args=[],
                    message="Page loaded" if success else "Timeout waiting for page load"
                )
            
            # Utility tools
            elif tool_name == "take_screenshot":
                return self.browser_controller.execute_command("screenshot", [
                    arg for arg in [
                        "--to-file" if parameters.get("filename") else None,
                        parameters.get("filename") if parameters.get("filename") else None,
                        "--selection" if parameters.get("selection") else None
                    ] if arg is not None
                ])
            
            elif tool_name == "copy_to_clipboard":
                return self.browser_controller.yank(parameters["content_type"])
            
            else:
                return CommandResult(
                    success=False,
                    command=tool_name,
                    args=[],
                    error=f"Unknown tool: {tool_name}"
                )
                
        except Exception as e:
            return CommandResult(
                success=False,
                command=tool_name,
                args=list(parameters.values()) if parameters else [],
                error=f"Tool execution error: {str(e)}"
            )
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool["name"] for tool in self.tools_config.get("tools", [])]
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific tool."""
        for tool in self.tools_config.get("tools", []):
            if tool["name"] == tool_name:
                return tool
        return None


# Convenience functions for easy agent creation and usage
def create_ai_agent(provider: str = "openai", model: str = "gpt-4", 
                   api_key: str = None, window_id: int = 0) -> AIBrowserAgent:
    """Create an AI browser agent with specified configuration.
    
    Args:
        provider: LLM provider (openai, anthropic, ollama)
        model: Model name
        api_key: API key for the provider
        window_id: Qutebrowser window ID
        
    Returns:
        AIBrowserAgent instance
    """
    config = AgentConfig(
        llm_provider=provider,
        model=model,
        api_key=api_key
    )
    return AIBrowserAgent(config, window_id)


async def ask_ai_agent(query: str, agent: AIBrowserAgent = None) -> AgentResponse:
    """Ask the AI agent to perform a browser task.
    
    Args:
        query: Natural language query
        agent: AI agent instance (creates default if None)
        
    Returns:
        AgentResponse with results
    """
    if agent is None:
        agent = create_ai_agent()
    
    return await agent.process_query(query)


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_agent():
        """Test the AI agent with sample queries."""
        # Create agent
        agent = create_ai_agent(provider="openai", model="gpt-4")
        
        # Test queries
        test_queries = [
            "What page am I currently on?",
            "Open https://example.com in a new tab",
            "Search for 'qutebrowser' on this page",
            "Scroll down to see more content",
            "Go back to the previous page"
        ]
        
        for query in test_queries:
            print(f"\n🤖 Query: {query}")
            try:
                response = await agent.process_query(query)
                print(f"✅ Response: {response.message}")
                print(f"🔧 Tool calls: {len(response.tool_calls)}")
                if response.tool_calls:
                    for tool_call in response.tool_calls:
                        print(f"   - {tool_call['name']}: {tool_call.get('parameters', {})}")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Run test if executed directly
    asyncio.run(test_agent())
