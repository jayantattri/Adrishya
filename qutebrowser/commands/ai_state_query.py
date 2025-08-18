"""
AI-powered state query commands for qutebrowser.

This module provides AI-powered commands that can answer natural language questions
about the browser's current state, tabs, page content, performance, etc.
"""

import json
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime

# Add ai_agent_tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'ai_agent_tools'))

from qutebrowser.api import cmdutils
from qutebrowser.utils import message, objreg, debug, log, usertypes
from qutebrowser.commands import cmdexc

try:
    from ai_agent_tools.unified_state_tools import (
        get_quick_status, get_browser_overview, get_complete_browser_state,
        get_tab_summary, get_performance_summary, get_page_content_summary
    )
    AI_TOOLS_AVAILABLE = True
except ImportError as e:
    log.misc.warning(f"AI agent tools not available: {e}")
    AI_TOOLS_AVAILABLE = False
    # Create placeholder functions to avoid unbound variable errors
    def get_quick_status(*args, **kwargs): return {}
    def get_browser_overview(*args, **kwargs): return {}
    def get_complete_browser_state(*args, **kwargs): return {}
    def get_tab_summary(*args, **kwargs): return {}
    def get_performance_summary(*args, **kwargs): return {}
    def get_page_content_summary(*args, **kwargs): return {}


class AIStateQueryProcessor:
    """Processes natural language queries about browser state."""
    
    def __init__(self):
        self.state_collectors = {
            'quick': get_quick_status,
            'overview': get_browser_overview,
            'complete': lambda window_id=0: get_complete_browser_state(window_id).__dict__,
            'tabs': get_tab_summary,
            'performance': get_performance_summary,
            'content': get_page_content_summary,
        }
        
    def collect_relevant_state(self, query: str, window_id: int = 0) -> Dict[str, Any]:
        """Collect browser state relevant to the query."""
        query_lower = query.lower()
        collected_state = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'window_id': window_id
        }
        
        log.misc.debug(f"Processing query: '{query}' (lowercase: '{query_lower}')")
        
        # Determine what state to collect based on query keywords
        if any(word in query_lower for word in ['tab', 'tabs', 'switch', 'close', 'open']):
            log.misc.debug("Collecting tabs information")
            collected_state['tabs'] = self.state_collectors['tabs'](window_id)
            
        if any(word in query_lower for word in ['performance', 'speed', 'memory', 'cpu', 'slow', 'fast']):
            log.misc.debug("Collecting performance information")
            collected_state['performance'] = self.state_collectors['performance'](window_id)
            
        if any(word in query_lower for word in ['content', 'page', 'text', 'links', 'forms', 'images']):
            log.misc.debug("Collecting content information")
            collected_state['content'] = self.state_collectors['content'](window_id)
            
        if any(word in query_lower for word in ['window', 'fullscreen', 'size']):
            log.misc.debug("Collecting window information")
            collected_state['overview'] = self.state_collectors['overview'](window_id)
            
        # Always include quick status for basic context
        if not any(key in collected_state for key in ['tabs', 'performance', 'content', 'overview']):
            log.misc.debug("No specific state collected, using overview")
            collected_state['overview'] = self.state_collectors['overview'](window_id)
        else:
            log.misc.debug("Adding quick status for context")
            collected_state['quick'] = self.state_collectors['quick'](window_id)
            
        log.misc.debug(f"Collected state keys: {list(collected_state.keys())}")
        return collected_state
    
    def format_response(self, query: str, state_data: Dict[str, Any]) -> str:
        """Format a human-readable response based on the query and state data."""
        query_lower = query.lower()
        
        log.misc.debug(f"Formatting response for query: '{query}'")
        log.misc.debug(f"Available state data keys: {list(state_data.keys())}")
        
        # Handle different types of queries
        if 'how many tabs' in query_lower or 'tab count' in query_lower:
            log.misc.debug("Using tab count response")
            return self._format_tab_count_response(state_data)
            
        elif any(word in query_lower for word in ['current tab', 'active tab', 'this tab']):
            log.misc.debug("Using current tab response")
            return self._format_current_tab_response(state_data)
            
        elif any(word in query_lower for word in ['performance', 'speed', 'memory']):
            log.misc.debug("Using performance response")
            return self._format_performance_response(state_data)
            
        elif any(word in query_lower for word in ['content', 'page content', 'links', 'forms', 'images']):
            log.misc.debug("Using content response")
            return self._format_content_response(state_data)
            
        elif 'all tabs' in query_lower or 'list tabs' in query_lower:
            log.misc.debug("Using all tabs response")
            return self._format_all_tabs_response(state_data)
            
        else:
            log.misc.debug("Using general response")
            return self._format_general_response(query, state_data)
    
    def _format_tab_count_response(self, state_data: Dict[str, Any]) -> str:
        """Format response for tab count queries."""
        if 'tabs' in state_data:
            count = state_data['tabs'].get('count', 0)
            active_index = state_data['tabs'].get('active_index', -1)
            return f"You have {count} tabs open. The active tab is at index {active_index}."
        elif 'overview' in state_data:
            window = state_data['overview'].get('window_status', {})
            count = window.get('total_tabs', 0)
            return f"You have {count} tabs open."
        return "Unable to determine tab count."
    
    def _format_current_tab_response(self, state_data: Dict[str, Any]) -> str:
        """Format response for current tab queries."""
        current_tab = None
        
        if 'overview' in state_data:
            current_tab = state_data['overview'].get('active_tab')
        elif 'quick' in state_data:
            current_tab = state_data['quick'].get('current_page')
            
        if current_tab:
            title = current_tab.get('title', 'Unknown')
            url = current_tab.get('url', '')
            is_loading = current_tab.get('is_loading', False)
            
            response = f"Current tab: '{title}'"
            if url:
                response += f"\nURL: {url}"
            if is_loading:
                response += "\nStatus: Loading..."
            else:
                response += "\nStatus: Loaded"
            return response
            
        return "Unable to get current tab information."
    
    def _format_performance_response(self, state_data: Dict[str, Any]) -> str:
        """Format response for performance queries."""
        if 'performance' in state_data:
            perf = state_data['performance']
            score = perf.get('overall_score')
            system_health = perf.get('system_health', 'Unknown')
            browser_health = perf.get('browser_health', 'Unknown')
            
            response = f"Performance Status:\n"
            response += f"• System Health: {system_health}\n"
            response += f"• Browser Health: {browser_health}"
            
            if score is not None:
                response += f"\n• Overall Score: {score:.1f}/100"
                
            if 'system' in perf:
                sys_info = perf['system']
                response += f"\n• CPU Usage: {sys_info.get('cpu_percent', 0):.1f}%"
                response += f"\n• Memory Usage: {sys_info.get('memory_percent', 0):.1f}%"
                
            return response
            
        return "Unable to get performance information."
    
    def _format_content_response(self, state_data: Dict[str, Any]) -> str:
        """Format response for page content queries."""
        if 'content' in state_data:
            content = state_data['content']
            if 'error' in content:
                return f"Error getting page content: {content['error']}"
                
            response = f"Page Analysis: {content.get('title', 'Unknown')}\n"
            response += f"URL: {content.get('url', 'Unknown')}\n"
            response += "=" * 60 + "\n\n"
            
            # Page Structure Overview
            response += "📄 PAGE STRUCTURE:\n"
            response += "-" * 30 + "\n"
            
            # Navigation and Header Elements
            navigation_elements = []
            main_content = []
            sidebar_content = []
            footer_content = []
            
            # Organize content by page sections
            main_text = content.get('main_text', '')
            headings = content.get('headings', [])
            links = content.get('links', [])
            forms = content.get('forms', [])
            images = content.get('images', [])
            
            # Extract navigation elements (typically at top)
            nav_keywords = ['sign in', 'login', 'register', 'menu', 'home', 'search', 'filter', 'all', 'shorts', 'videos']
            nav_links = [link for link in links if any(keyword in link.get('text', '').lower() for keyword in nav_keywords)]
            
            # Extract main content (video listings, articles, etc.)
            main_content_links = [link for link in links if link not in nav_links and link.get('text', '').strip()]
            
            # Header/Navigation Section
            if nav_links:
                response += "🔍 NAVIGATION & HEADER:\n"
                for link in nav_links[:8]:  # Limit to first 8 nav elements
                    link_text = link.get('text', '').strip()
                    if link_text:
                        response += f"  • {link_text}\n"
                response += "\n"
            
            # Search/Form Section
            if forms:
                response += "🔎 SEARCH & FORMS:\n"
                for form in forms:
                    form_id = form.get('form_id', 'Search form')
                    inputs = form.get('inputs', [])
                    if inputs:
                        input_types = [inp.get('type', 'text') for inp in inputs]
                        response += f"  • {form_id}: {', '.join(input_types)} inputs\n"
                response += "\n"
            
            # Main Content Section
            response += "📺 MAIN CONTENT:\n"
            response += "-" * 20 + "\n"
            
            # Group content by headings to show structure
            if headings:
                current_section = ""
                for heading in headings[:10]:  # Limit to first 10 headings
                    level = heading.get('level', 'h?')
                    text = heading.get('text', '').strip()
                    if text:
                        if level in ['h1', 'h2']:
                            response += f"\n📋 {text}\n"
                            current_section = text
                        elif level in ['h3', 'h4']:
                            response += f"  • {text}\n"
                        else:
                            response += f"    - {text}\n"
            
            # Show key content links (videos, articles, etc.)
            if main_content_links:
                response += "\n🎯 KEY CONTENT ITEMS:\n"
                for i, link in enumerate(main_content_links[:5]):  # Show first 5 main content items
                    link_text = link.get('text', '').strip()
                    link_url = link.get('url', '')
                    if link_text and len(link_text) > 3:
                        # Truncate long titles
                        if len(link_text) > 80:
                            link_text = link_text[:77] + "..."
                        response += f"  {i+1}. {link_text}\n"
                        # Show URL if it's a video/article link
                        if any(keyword in link_url.lower() for keyword in ['watch', 'video', 'article', 'post']):
                            response += f"     → {link_url}\n"
            
            # Media Content
            if images:
                response += "\n🖼️ MEDIA CONTENT:\n"
                response += f"  • {len(images)} images found\n"
                # Show first few images with descriptions
                for i, img in enumerate(images[:3]):
                    img_alt = img.get('alt', '').strip()
                    if img_alt:
                        response += f"  {i+1}. {img_alt[:60]}\n"
            
            # Page Statistics
            response += "\n📊 PAGE STATISTICS:\n"
            response += "-" * 20 + "\n"
            response += f"• Total Content Length: {content.get('content_length', 0):,} characters\n"
            response += f"• Total Links: {len(links)} links\n"
            response += f"• Navigation Elements: {len(nav_links)} items\n"
            response += f"• Main Content Items: {len(main_content_links)} items\n"
            response += f"• Headings: {len(headings)} sections\n"
            response += f"• Forms: {len(forms)} interactive forms\n"
            response += f"• Images: {len(images)} media elements\n"
            
            # Page Type Classification
            response += "\n🏷️ PAGE TYPE & PURPOSE:\n"
            response += "-" * 25 + "\n"
            
            # Analyze page type based on content
            page_url = content.get('url', '').lower()
            page_title = content.get('title', '').lower()
            main_text_lower = main_text.lower()
            
            if 'youtube' in page_url or 'youtube' in page_title:
                response += "• Type: YouTube video platform\n"
                response += "• Purpose: Video search results and content discovery\n"
                response += "• Key Features: Video listings, search functionality, navigation filters\n"
            elif 'search' in page_url or 'results' in page_url:
                response += "• Type: Search results page\n"
                response += "• Purpose: Display search results and filtering options\n"
            elif any(word in main_text_lower for word in ['login', 'sign in', 'register']):
                response += "• Type: Authentication page\n"
                response += "• Purpose: User login or registration\n"
            elif len(forms) > 0:
                response += "• Type: Interactive form page\n"
                response += "• Purpose: Data input and submission\n"
            else:
                response += "• Type: Content page\n"
                response += "• Purpose: Information display and navigation\n"
            
            # User Action Suggestions
            response += "\n💡 AVAILABLE ACTIONS:\n"
            response += "-" * 20 + "\n"
            
            if forms:
                response += "• Fill out forms or search\n"
            if nav_links:
                response += "• Navigate to different sections\n"
            if main_content_links:
                response += "• Click on content items\n"
            if len(links) > 10:
                response += "• Browse through multiple links\n"
            
            # Check if we got limited information due to JavaScript issues
            if content.get('content_length', 0) == 0 or content.get('content_length', 0) < 100:
                response += "\n⚠️  Note: Limited content information available. "
                response += "This may be due to:\n"
                response += "• JavaScript being disabled\n"
                response += "• Page not fully loaded\n"
                response += "• Special page type (chrome://, about:, etc.)\n"
                response += "• Page security restrictions\n"
                response += "\nTry enabling JavaScript or waiting for the page to load completely."
                
            return response
            
        return "Unable to get page content information."
    
    def _format_all_tabs_response(self, state_data: Dict[str, Any]) -> str:
        """Format response for all tabs queries."""
        if 'tabs' in state_data:
            tabs_info = state_data['tabs']
            tabs = tabs_info.get('tabs', [])
            
            if not tabs:
                return "No tabs found."
                
            response = f"All Tabs ({len(tabs)} total):\n"
            for tab in tabs:
                status_indicators = []
                if tab.get('is_active'):
                    status_indicators.append('ACTIVE')
                if tab.get('is_pinned'):
                    status_indicators.append('PINNED')
                if tab.get('is_loading'):
                    status_indicators.append('LOADING')
                    
                status = f" [{', '.join(status_indicators)}]" if status_indicators else ""
                response += f"• Tab {tab.get('index', '?')}: {tab.get('title', 'Unknown')}{status}\n"
                
            return response
            
        return "Unable to get tabs information."
    
    def _format_general_response(self, query: str, state_data: Dict[str, Any]) -> str:
        """Format a general response when no specific handler matches."""
        # Try to provide a comprehensive overview
        response = f"Browser State Overview (for query: '{query}'):\n\n"
        
        # Add current tab info if available
        if 'overview' in state_data:
            overview = state_data['overview']
            active_tab = overview.get('active_tab')
            if active_tab:
                response += f"Current Tab: {active_tab.get('title', 'Unknown')}\n"
                
            window_status = overview.get('window_status', {})
            if window_status:
                response += f"Total Tabs: {window_status.get('total_tabs', 0)}\n"
                
        # Add performance if available
        if 'performance' in state_data:
            perf = state_data['performance']
            response += f"System Health: {perf.get('system_health', 'Unknown')}\n"
            response += f"Browser Health: {perf.get('browser_health', 'Unknown')}\n"
            
        # Add basic info from quick status
        elif 'quick' in state_data:
            quick = state_data['quick']
            current_page = quick.get('current_page')
            if current_page:
                response += f"Current Page: {current_page.get('title', 'Unknown')}\n"
                
            window = quick.get('window', {})
            if window:
                response += f"Total Tabs: {window.get('tab_count', 0)}\n"
                
        response += f"\nFor more specific information, try asking about:\n"
        response += "• 'How many tabs do I have?'\n"
        response += "• 'What is the current tab?'\n"
        response += "• 'Show me all tabs'\n"
        response += "• 'How is the performance?'\n"
        response += "• 'What content is on this page?'"
        
        return response


@cmdutils.register(maxsplit=0)
@cmdutils.argument('win_id', value=usertypes.CommandValue.win_id)
@cmdutils.argument('output', flag='o', choices=['message', 'tab', 'window'])
def ai_query(win_id: int, query: str, output: str = 'message') -> None:
    """Ask AI about the browser's current state.
    
    This command allows you to ask natural language questions about qutebrowser's
    current state, including tabs, performance, page content, and more.
    
    Args:
        query: The question to ask about the browser state
        output: Where to show the response ('message', 'tab', or 'window')
    """
    if not AI_TOOLS_AVAILABLE:
        raise cmdutils.CommandError("AI agent tools are not available. "
                                    "Please ensure the ai_agent_tools module is properly installed.")
    
    if not query.strip():
        raise cmdutils.CommandError("Please provide a query. Example: ':ai-query How many tabs do I have?'")
    
    try:
        # Initialize the AI query processor
        processor = AIStateQueryProcessor()
        
        # Collect relevant browser state
        state_data = processor.collect_relevant_state(query, win_id)
        
        # Generate response
        response = processor.format_response(query, state_data)
        
        # Display the response based on output parameter
        if output == 'message':
            message.info(f"AI Response: {response}")
        elif output == 'tab':
            # Create a new tab with the response
            _show_response_in_tab(win_id, query, response, state_data)
        elif output == 'window':
            # Show in a new window
            _show_response_in_window(win_id, query, response, state_data)
        else:
            raise cmdutils.CommandError(f"Invalid output option: {output}. Use 'message', 'tab', or 'window'.")
            
    except Exception as e:
        log.misc.exception("Error in ai_query command")
        raise cmdutils.CommandError(f"Error processing AI query: {str(e)}")


@cmdutils.register()
@cmdutils.argument('win_id', value=usertypes.CommandValue.win_id)
def ai_debug_js(win_id: int) -> None:
    """Debug JavaScript execution for AI agent tools.
    
    This command helps diagnose why JavaScript execution might be failing
    in the AI agent tools.
    """
    try:
        # Import and run the debug tool
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'ai_agent_tools'))
        
        from test_javascript_debug import test_javascript_execution
        
        # Run the debug tool
        result = test_javascript_execution()
        
        if result:
            message.info("JavaScript debug completed. Check the console output for details.")
        else:
            message.error("JavaScript debug failed. Check the console output for errors.")
            
    except ImportError as e:
        message.error(f"Could not import debug tool: {e}")
    except Exception as e:
        log.misc.exception("Error in ai_debug_js command")
        message.error(f"Error running JavaScript debug: {str(e)}")


def _show_response_in_tab(win_id: int, query: str, response: str, state_data: Dict[str, Any]) -> None:
    """Show the AI response in a new tab."""
    try:
        tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
        
        # Create HTML content for the response
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Query Result</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 40px; 
                    line-height: 1.6;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .query {{
                    background-color: #e3f2fd;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #2196f3;
                    margin-bottom: 20px;
                }}
                .response {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 5px;
                    white-space: pre-line;
                    border-left: 4px solid #4caf50;
                }}
                .timestamp {{
                    color: #666;
                    font-size: 0.9em;
                    margin-bottom: 20px;
                }}
                .debug {{
                    margin-top: 30px;
                    padding: 15px;
                    background-color: #f5f5f5;
                    border-radius: 5px;
                    font-size: 0.9em;
                    color: #666;
                }}
                details {{
                    margin-top: 10px;
                }}
                summary {{
                    cursor: pointer;
                    font-weight: bold;
                    color: #333;
                }}
                pre {{
                    background-color: #f0f0f0;
                    padding: 10px;
                    border-radius: 3px;
                    overflow-x: auto;
                    font-size: 0.8em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 AI Browser State Query</h1>
                
                <div class="timestamp">
                    Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                
                <div class="query">
                    <h3>Your Question:</h3>
                    <p><strong>{query}</strong></p>
                </div>
                
                <div class="response">
                    <h3>AI Response:</h3>
                    <p>{response}</p>
                </div>
                
                <div class="debug">
                    <details>
                        <summary>Raw State Data (for debugging)</summary>
                        <pre>{json.dumps(state_data, indent=2, default=str)}</pre>
                    </details>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create a data URL with the HTML content
        from qutebrowser.qt.core import QUrl
        import urllib.parse
        
        encoded_html = urllib.parse.quote(html_content.encode('utf-8'))
        data_url = QUrl(f"data:text/html;charset=utf-8,{encoded_html}")
        
        # Open in new tab
        tabbed_browser.tabopen(data_url, background=False)
        
    except Exception as e:
        log.misc.exception("Error showing response in tab")
        message.error(f"Could not show response in tab: {str(e)}")
        # Fall back to message display
        message.info(f"AI Response: {response}")


def _show_response_in_window(win_id: int, query: str, response: str, state_data: Dict[str, Any]) -> None:
    """Show the AI response in a new window."""
    try:
        # For now, fall back to showing in a new tab
        # TODO: Implement actual new window creation
        _show_response_in_tab(win_id, query, response, state_data)
        
    except Exception as e:
        log.misc.exception("Error showing response in window")
        message.error(f"Could not show response in window: {str(e)}")
        # Fall back to message display
        message.info(f"AI Response: {response}")
