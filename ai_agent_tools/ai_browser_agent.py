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
    print("Warning: requests package not available. Install with: pip install requests")


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
            raise ImportError("requests package not available. Install with: pip install requests")
        
        self.base_url = config.api_base or "http://localhost:11434"
        self.logger = logging.getLogger(__name__)
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              tools: List[Dict[str, Any]], execution_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using Ollama API with reasoning model handling."""
        try:
            # Create a specialized prompt for reasoning models with execution state
            system_prompt = self._create_reasoning_system_prompt(tools, execution_state)
            
            # Add tools to system message
            enhanced_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    enhanced_messages.append({
                        "role": "system", 
                        "content": system_prompt
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
            full_content = result_data.get("message", {}).get("content", "")
            
            # Separate reasoning from action response
            reasoning, action_response, tool_calls = self._parse_reasoning_response(full_content)
            
            return {
                "content": action_response,
                "reasoning": reasoning,
                "tool_calls": tool_calls,
                "full_response": full_content
            }
            
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _create_reasoning_system_prompt(self, tools: List[Dict[str, Any]], execution_state: Dict[str, Any] = None) -> str:
        """Create a system prompt optimized for reasoning models with execution state awareness."""
        tools_text = self._format_tools_for_prompt(tools)
        
        # Add execution state context
        state_context = ""
        if execution_state and execution_state.get('all_tool_calls'):
            state_context = f"""

CURRENT EXECUTION STATE:
- Tools already executed: {len(execution_state['all_tool_calls'])}
- Last tool executed: {execution_state['all_tool_calls'][-1]['name'] if execution_state['all_tool_calls'] else 'None'}
- Iteration: {execution_state.get('iteration_count', 0)}

PREVIOUS TOOL EXECUTIONS:
"""
            for i, tool_call in enumerate(execution_state['all_tool_calls'], 1):
                tool_name = tool_call['name']
                params = tool_call.get('parameters', {})
                state_context += f"- {i}. {tool_name}: {params}\n"
            
            state_context += "\nIMPORTANT: Do NOT repeat any of the above tools with the same parameters!"
        
        prompt = f"""You are an AI browser assistant that controls a real web browser. You have access to browser automation tools.

AVAILABLE BROWSER TOOLS:
{tools_text}{state_context}

RESPONSE FORMAT:
THINKING:
[Brief reasoning about what the user wants and next step]

ACTION:
[Simple action plan for the next tool]

EXECUTE:
[Single tool call in JSON format:
TOOL_CALL: {{"name": "tool_name", "parameters": {{"param": "value"}}}}
]

CRITICAL SEQUENTIAL EXECUTION RULES:
1. Execute ONE tool at a time
2. Wait for feedback before calling the next tool
3. Use feedback to decide the next step
4. Continue until task is complete
5. If task is complete, respond with "TASK COMPLETE"
6. NEVER call multiple tools in one response
7. NEVER repeat a tool that was already executed
8. ALWAYS provide the EXECUTE section with actual tool calls

SIMPLE EXAMPLES:
User: "open google.com"
THINKING: User wants to navigate to Google's homepage
ACTION: Open Google.com using open_url tool
EXECUTE:
TOOL_CALL: {{"name": "open_url", "parameters": {{"url": "https://www.google.com"}}}}

User: "search for Python tutorials"
THINKING: User wants to search for Python tutorials on Google
ACTION: Type "Python tutorials" in the search box
EXECUTE:
TOOL_CALL: {{"name": "type_text", "parameters": {{"text": "Python tutorials", "clear_first": true}}}}

User: "click the first result"
THINKING: User wants to click the first search result
ACTION: Click the first result on the page
EXECUTE:
TOOL_CALL: {{"name": "click_element", "parameters": {{"selector_type": "css", "selector_value": "h3"}}}}

SEQUENTIAL EXECUTION PATTERNS:
1. Navigation: open_url → wait for page load
2. Search: open_url → type_text → send_key(Enter)
3. Form filling: type_text → send_key(Enter)
4. Element interaction: click_element → wait for response
5. Tab management: tab_new → open_url

IMPORTANT:
- Call ONLY ONE tool per response
- Use feedback to determine next action
- If no more actions needed, say "TASK COMPLETE"
- If tool fails, try alternative approach
- Always include EXECUTE section with tool call
- NEVER repeat previously executed tools
"""
        return prompt
    
    def _parse_reasoning_response(self, content: str) -> tuple:
        """Parse reasoning model response to separate thinking from actions."""
        reasoning = ""
        action_response = ""
        tool_calls = []
        
        # Split content into sections
        sections = content.split('\n')
        current_section = None
        
        for line in sections:
            line = line.strip()
            
            if line.startswith('THINKING:'):
                current_section = 'thinking'
                continue
            elif line.startswith('ACTION:'):
                current_section = 'action'
                continue
            elif line.startswith('EXECUTE:'):
                current_section = 'execute'
                continue
            elif line.startswith('TOOL_CALL:'):
                current_section = 'execute'
                # Parse tool call
                try:
                    tool_data = json.loads(line[10:])  # Remove 'TOOL_CALL:' prefix
                    tool_calls.append(tool_data)
                except json.JSONDecodeError:
                    # Try to extract JSON from the line
                    try:
                        # Look for JSON-like content after TOOL_CALL:
                        json_start = line.find('{')
                        if json_start != -1:
                            json_content = line[json_start:]
                            tool_data = json.loads(json_content)
                            tool_calls.append(tool_data)
                    except:
                        continue
                continue
            
            # Add content to appropriate section
            if current_section == 'thinking':
                reasoning += line + '\n'
            elif current_section == 'action':
                action_response += line + '\n'
            elif current_section == 'execute' and not line.startswith('TOOL_CALL:'):
                action_response += line + '\n'
        
        # Clean up whitespace
        reasoning = reasoning.strip()
        action_response = action_response.strip()
        
        # If no clear sections found, try to extract reasoning from the beginning
        if not reasoning and not action_response:
            # Look for reasoning patterns in the full response
            lines = content.split('\n')
            reasoning_lines = []
            action_lines = []
            
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['think', 'reason', 'analyze', 'consider', 'need to', 'should']):
                    reasoning_lines.append(line)
                elif any(keyword in line.lower() for keyword in ['open', 'navigate', 'click', 'fill', 'search', 'tool_call']):
                    action_lines.append(line)
                elif line.startswith('TOOL_CALL:'):
                    try:
                        tool_data = json.loads(line[10:])
                        tool_calls.append(tool_data)
                    except json.JSONDecodeError:
                        # Try to extract JSON from the line
                        try:
                            json_start = line.find('{')
                            if json_start != -1:
                                json_content = line[json_start:]
                                tool_data = json.loads(json_content)
                                tool_calls.append(tool_data)
                        except:
                            continue
            
            reasoning = '\n'.join(reasoning_lines)
            action_response = '\n'.join(action_lines)
        
        return reasoning, action_response, tool_calls
    
    def _format_tools_for_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """Format tools for inclusion in prompt."""
        tools_text = ""
        for tool in tools:
            tools_text += f"\n{tool['name']}: {tool['description']}\n"
            if 'parameters' in tool and 'properties' in tool['parameters']:
                props = tool['parameters']['properties']
                if props:
                    tools_text += "  Parameters: "
                    param_list = []
                    for param_name, param_info in props.items():
                        param_type = param_info.get('type', 'any')
                        required = param_name in tool['parameters'].get('required', [])
                        req_text = "*" if required else ""
                        param_list.append(f"{param_name}{req_text} ({param_type})")
                    tools_text += ", ".join(param_list) + "\n"
        
        return tools_text
    
    def _extract_tool_calls_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract tool calls from response content (enhanced parsing for sequential execution)."""
        tool_calls = []
        
        # Look for tool call patterns in the response
        lines = content.split('\n')
        execute_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check for section markers
            if line == "EXECUTE:":
                execute_section = True
                continue
            elif line in ["THINKING:", "ACTION:", "TASK COMPLETE", "NO MORE TOOLS"]:
                execute_section = False
                continue
            
            # Extract tool calls from TOOL_CALL: format
            if line.startswith('TOOL_CALL:'):
                try:
                    tool_data = json.loads(line[10:])  # Remove 'TOOL_CALL:' prefix
                    tool_calls.append(tool_data)
                except json.JSONDecodeError as e:
                    self.logger.debug(f"Failed to parse tool call '{line}': {e}")
                    # Try to extract JSON from the line
                    try:
                        json_start = line.find('{')
                        if json_start != -1:
                            json_content = line[json_start:]
                            tool_data = json.loads(json_content)
                            tool_calls.append(tool_data)
                    except:
                        continue
                continue
            
            # If in EXECUTE section, try to parse JSON lines
            if execute_section and line and line.startswith('{'):
                try:
                    tool_data = json.loads(line)
                    if 'name' in tool_data and 'parameters' in tool_data:
                        tool_calls.append(tool_data)
                except json.JSONDecodeError:
                    continue
        
        # Validate tool calls
        valid_tool_calls = []
        for tool_call in tool_calls:
            if isinstance(tool_call, dict) and 'name' in tool_call:
                # Ensure parameters is a dict
                if 'parameters' not in tool_call:
                    tool_call['parameters'] = {}
                elif not isinstance(tool_call['parameters'], dict):
                    tool_call['parameters'] = {}
                
                valid_tool_calls.append(tool_call)
        
        self.logger.debug(f"Extracted {len(valid_tool_calls)} valid tool calls from content")
        return valid_tool_calls


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
    
    def _build_enhanced_context(self, user_query: str, context: Dict[str, Any]) -> str:
        """Build enhanced context with clear separation between current request and history."""
        context_parts = []
        
        # Start with clear current request section
        context_parts.append("🎯 CURRENT USER REQUEST:")
        context_parts.append(f"   {user_query}")
        context_parts.append("")
        
        # Add current browser state
        if context.get("browser_state"):
            browser_state = context["browser_state"]
            context_parts.append("📍 CURRENT BROWSER STATE:")
            
            if browser_state.get("url"):
                context_parts.append(f"   Current URL: {browser_state['url']}")
            if browser_state.get("title"):
                context_parts.append(f"   Page Title: {browser_state['title']}")
            if browser_state.get("tabs"):
                context_parts.append(f"   Open Tabs: {len(browser_state['tabs'])}")
            
            context_parts.append("")
        
        # Add page info if available
        if context.get("page_info"):
            page_info = context["page_info"]
            context_parts.append("📄 CURRENT PAGE INFO:")
            
            if page_info.get("title"):
                context_parts.append(f"   Title: {page_info['title']}")
            if page_info.get("main_text"):
                text = page_info["main_text"]
                context_parts.append(f"   Content Preview: {text[:200]}...")
            
            context_parts.append("")
        
        # Add clear instruction
        context_parts.append("⚠️  INSTRUCTION: Focus on the CURRENT REQUEST above. Use browser tools to accomplish this specific task.")
        context_parts.append("")
        
        return "\n".join(context_parts)
    
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
            # Initialize execution state
            execution_state = {
                'iteration_count': 0,
                'max_iterations': min(self.config.max_tool_calls, 8),  # Increased limit
                'all_tool_calls': [],
                'all_execution_results': [],
                'executed_tool_signatures': set(),  # Track executed tools to prevent loops
                'current_context': self._get_current_context(),
                'task_completed': False,
                'last_error': None
            }
            
            # Get current context
            context = self._get_current_context()
            
            # Build enhanced context with clear separation
            enhanced_context = self._build_enhanced_context(user_query, context)
            
            # Prepare messages for LLM with clear current request focus
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": enhanced_context}
            ]
            
            # Add conversation history with clear separation (last 3 exchanges only)
            if self.conversation_history:
                recent_history = self.conversation_history[-6:]  # Last 3 exchanges (user + assistant)
                # Add history with clear context marker
                history_context = "\n\n📚 PREVIOUS CONVERSATION (for context only - focus on current request above):\n"
                for entry in recent_history:
                    role = entry.get("role", "unknown")
                    content = entry.get("content", "")
                    if role == "user":
                        history_context += f"👤 User: {content}\n"
                    elif role == "assistant":
                        # Truncate long assistant responses
                        short_content = content[:200] + "..." if len(content) > 200 else content
                        history_context += f"🤖 Assistant: {short_content}\n"
                
                history_context += "\n⚠️  REMEMBER: The CURRENT REQUEST above is your priority!"
                
                # Add history as a separate message
                messages.append({"role": "user", "content": history_context})
            
            # Execute iterative tool calling with improved state management
            final_response = await self._execute_iterative_tool_calling(
                messages, user_query, execution_state
            )
            
            # Create response with reasoning
            response = AgentResponse(
                success=True,
                message=final_response.get("content", "Task completed"),
                tool_calls=execution_state['all_tool_calls'],
                execution_results=execution_state['all_execution_results'],
                thinking=final_response.get("reasoning"),
                error=execution_state['last_error']
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
    
    async def _execute_iterative_tool_calling(self, initial_messages: List[Dict[str, Any]], 
                                            user_query: str, execution_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute iterative tool calling with improved state management and loop prevention.
        
        Args:
            initial_messages: Initial messages for the LLM
            user_query: Original user query
            execution_state: State tracking dictionary
            
        Returns:
            Final LLM response
        """
        messages = initial_messages.copy()
        final_response = None
        
        while (execution_state['iteration_count'] < execution_state['max_iterations'] and 
               not execution_state['task_completed']):
            
            execution_state['iteration_count'] += 1
            self.logger.debug(f"Starting iteration {execution_state['iteration_count']}")
            
            # Get LLM response with potential tool calls
            try:
                llm_response = await self.llm_provider.generate_response(
                    messages=messages,
                    tools=self.tools_config.get("tools", []),
                    execution_state=execution_state
                )
            except Exception as e:
                self.logger.error(f"LLM API error in iteration {execution_state['iteration_count']}: {e}")
                execution_state['last_error'] = f"LLM API error: {str(e)}"
                break
            
            # Debug: Log the full response
            self.logger.debug(f"LLM Response (iteration {execution_state['iteration_count']}): {llm_response}")
            
            # Check if LLM wants to call tools
            tool_calls = llm_response.get("tool_calls", [])
            
            # If no tool calls in response, try to extract from content
            if not tool_calls:
                content = llm_response.get("content", "")
                tool_calls = self.llm_provider._extract_tool_calls_from_content(content)
                self.logger.debug(f"Extracted tool calls from content: {tool_calls}")
            
            # Check if LLM indicates task is complete
            content = llm_response.get("content", "").lower()
            if any(phrase in content for phrase in ["task complete", "no more tools", "task finished", "completed"]):
                self.logger.debug("LLM indicated task is complete")
                execution_state['task_completed'] = True
                final_response = llm_response
                break
            
            if not tool_calls:
                # No tool calls found - check if this is appropriate
                self.logger.debug("No tool calls found in LLM response")
                
                # Check if this looks like a simple navigation request that should have a tool call
                user_query_lower = user_query.lower()
                if any(keyword in user_query_lower for keyword in ['open', 'go to', 'navigate', 'visit', 'search']):
                    self.logger.warning("Navigation/search request detected but no tool call provided")
                    # Add error context and continue
                    error_message = f"Your request '{user_query}' requires browser actions, but no tools were called. Please use appropriate browser tools to complete the task."
                    messages.append({"role": "user", "content": error_message})
                    continue
                
                # No more tool calls, we're done
                self.logger.debug("No more tool calls, task completed")
                execution_state['task_completed'] = True
                final_response = llm_response
                break
            
            # Execute ONLY the first tool call - enforce true iterative execution
            if tool_calls:
                # Take only the FIRST tool call, ignore any others
                first_tool_call = tool_calls[0]
                tool_name = first_tool_call["name"]
                parameters = first_tool_call.get("parameters", {})
                
                # Create tool signature for duplicate detection
                tool_signature = self._create_tool_signature(tool_name, parameters)
                
                # Check for duplicate tool calls to prevent infinite loops
                if tool_signature in execution_state['executed_tool_signatures']:
                    self.logger.warning(f"Duplicate tool call detected: {tool_signature}")
                    self.logger.debug("Stopping execution to prevent infinite loops")
                    
                    # Add feedback about the duplicate and force task completion
                    duplicate_message = f"Tool {tool_name} with parameters {parameters} was already executed. Task is complete - no more actions needed."
                    messages.append({"role": "user", "content": duplicate_message})
                    execution_state['task_completed'] = True
                    final_response = {"content": "Task completed - duplicate tool call prevented"}
                    break
                
                # Add to executed signatures
                execution_state['executed_tool_signatures'].add(tool_signature)
                
                self.logger.debug(f"Executing tool: {tool_name} with parameters: {parameters}")
                
                # Execute the tool
                try:
                    result = await self._execute_single_tool(tool_name, parameters)
                except Exception as e:
                    self.logger.error(f"Error executing tool {tool_name}: {e}")
                    result = CommandResult(
                        success=False,
                        command=tool_name,
                        args=[],
                        error=str(e)
                    )
                
                # Add to our tracking
                execution_state['all_tool_calls'].append(first_tool_call)
                execution_state['all_execution_results'].append(result)
                
                # Create comprehensive feedback message for the LLM
                feedback_message = self._create_enhanced_tool_feedback_message(
                    first_tool_call, result, execution_state
                )
                
                # Add the feedback to messages for next iteration
                messages.append({"role": "assistant", "content": f"I executed: {tool_name}({parameters})"})
                messages.append({"role": "user", "content": feedback_message})
                
                # Add explicit instruction to prevent duplicates
                if len(execution_state['all_tool_calls']) > 1:
                    duplicate_prevention = f"\n\n⚠️  CRITICAL: Do NOT repeat any of the previously executed tools. Choose a different tool or indicate task completion."
                    messages.append({"role": "user", "content": duplicate_prevention})
                
                # Check if we should continue based on tool result
                if not result.success:
                    self.logger.warning(f"Tool {tool_name} failed: {result.error}")
                    execution_state['last_error'] = result.error
                    
                    # Add error context and continue
                    error_message = f"Tool {tool_name} failed with error: {result.error}. Please try a different approach or provide more specific instructions."
                    messages.append({"role": "user", "content": error_message})
                
                # Update final response
                final_response = llm_response
            
            # Small delay to prevent overwhelming the system
            await asyncio.sleep(0.5)
        
        # If we hit max iterations, log warning
        if execution_state['iteration_count'] >= execution_state['max_iterations']:
            self.logger.warning(f"Reached maximum iterations ({execution_state['max_iterations']}), stopping tool execution")
        
        return final_response or {"content": "Task processing completed"}
    
    def _create_tool_signature(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Create a unique signature for a tool call to detect duplicates.
        
        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            
        Returns:
            Unique signature string
        """
        # Create a normalized signature that ignores order and handles common variations
        normalized_params = {}
        for key, value in parameters.items():
            # Normalize common parameter variations
            if key == "url" and isinstance(value, str):
                # Normalize URLs
                normalized_params[key] = value.lower().rstrip('/')
            elif isinstance(value, (str, int, float, bool)):
                normalized_params[key] = value
            else:
                # For complex objects, use string representation
                normalized_params[key] = str(value)
        
        # Sort parameters for consistent signature
        sorted_params = sorted(normalized_params.items())
        param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        
        return f"{tool_name}:{param_str}"
    
    def _create_enhanced_tool_feedback_message(self, tool_call: Dict[str, Any], result: CommandResult, 
                                             execution_state: Dict[str, Any]) -> str:
        """Create a comprehensive feedback message for the LLM after tool execution.
        
        Args:
            tool_call: The tool call that was executed
            result: The result of the tool execution
            execution_state: Current execution state
            
        Returns:
            Enhanced feedback message for the LLM
        """
        tool_name = tool_call["name"]
        parameters = tool_call.get("parameters", {})
        iteration = execution_state['iteration_count']
        
        feedback_parts = []
        feedback_parts.append(f"🔧 TOOL EXECUTION FEEDBACK (Iteration {iteration}):")
        feedback_parts.append(f"   Tool: {tool_name}")
        feedback_parts.append(f"   Parameters: {parameters}")
        
        if result.success:
            feedback_parts.append(f"   ✅ Status: SUCCESS")
            if result.message:
                feedback_parts.append(f"   📤 Message: {result.message}")
        else:
            feedback_parts.append(f"   ❌ Status: FAILED")
            if result.error:
                feedback_parts.append(f"   🚨 Error: {result.error}")
        
        # Add summary of all previous executions
        if len(execution_state['all_tool_calls']) > 1:
            feedback_parts.append("")
            feedback_parts.append("📋 PREVIOUS TOOL EXECUTIONS:")
            for i, (prev_call, prev_result) in enumerate(zip(execution_state['all_tool_calls'][:-1], 
                                                           execution_state['all_execution_results'][:-1]), 1):
                prev_tool = prev_call["name"]
                prev_success = "✅" if prev_result.success else "❌"
                feedback_parts.append(f"   {i}. {prev_tool}: {prev_success}")
        
        # Add execution statistics
        feedback_parts.append("")
        feedback_parts.append("📊 EXECUTION STATISTICS:")
        feedback_parts.append(f"   Total tools executed: {len(execution_state['all_tool_calls'])}")
        feedback_parts.append(f"   Successful: {sum(1 for r in execution_state['all_execution_results'] if r.success)}")
        feedback_parts.append(f"   Failed: {sum(1 for r in execution_state['all_execution_results'] if not r.success)}")
        feedback_parts.append(f"   Iterations remaining: {execution_state['max_iterations'] - iteration}")
        
        # Add intelligent next step guidance
        feedback_parts.append("")
        feedback_parts.append("🎯 NEXT STEP GUIDANCE:")
        
        if result.success:
            # Provide context-aware guidance based on the tool executed
            if tool_name == "open_url" and "url" in parameters:
                url = parameters["url"]
                if "google.com" in url.lower():
                    feedback_parts.append("   ✅ Google opened successfully. If you need to search, use 'type_text' to enter search terms and 'send_key' with 'Enter' to submit.")
                elif "youtube.com" in url.lower():
                    feedback_parts.append("   ✅ YouTube opened successfully. You can now browse videos or search for content.")
                else:
                    feedback_parts.append("   ✅ Page opened successfully. You can now interact with the page content.")
            elif tool_name == "type_text":
                feedback_parts.append("   ✅ Text entered successfully. Use 'send_key' with 'Enter' to submit forms or search.")
            elif tool_name == "send_key":
                feedback_parts.append("   ✅ Key sent successfully. The action should be completed.")
            else:
                feedback_parts.append("   ✅ Tool executed successfully. Continue with the next step to complete the task.")
            
            # Check if this might complete the task
            if tool_name in ["open_url", "send_key"] and iteration >= 2:
                feedback_parts.append("   💡 If this completes your task, respond with 'TASK COMPLETE'. Otherwise, continue with the next step.")
        else:
            feedback_parts.append("   ❌ Tool failed. Please try a different approach or provide more specific instructions.")
            feedback_parts.append("   💡 Consider using different parameters or a different tool to achieve the same goal.")
        
        return "\n".join(feedback_parts)
    
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
