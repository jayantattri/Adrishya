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
        
        # Determine what state to collect based on query keywords
        if any(word in query_lower for word in ['tab', 'tabs', 'switch', 'close', 'open']):
            collected_state['tabs'] = self.state_collectors['tabs'](window_id)
            
        if any(word in query_lower for word in ['performance', 'speed', 'memory', 'cpu', 'slow', 'fast']):
            collected_state['performance'] = self.state_collectors['performance'](window_id)
            
        if any(word in query_lower for word in ['content', 'page', 'text', 'links', 'forms', 'images']):
            collected_state['content'] = self.state_collectors['content'](window_id)
            
        if any(word in query_lower for word in ['window', 'fullscreen', 'size']):
            collected_state['overview'] = self.state_collectors['overview'](window_id)
            
        # Always include quick status for basic context
        if not any(key in collected_state for key in ['tabs', 'performance', 'content', 'overview']):
            collected_state['overview'] = self.state_collectors['overview'](window_id)
        else:
            collected_state['quick'] = self.state_collectors['quick'](window_id)
            
        return collected_state
    
    def format_response(self, query: str, state_data: Dict[str, Any]) -> str:
        """Format a human-readable response based on the query and state data."""
        query_lower = query.lower()
        
        # Handle different types of queries
        if 'how many tabs' in query_lower or 'tab count' in query_lower:
            return self._format_tab_count_response(state_data)
            
        elif any(word in query_lower for word in ['current tab', 'active tab', 'this tab']):
            return self._format_current_tab_response(state_data)
            
        elif any(word in query_lower for word in ['performance', 'speed', 'memory']):
            return self._format_performance_response(state_data)
            
        elif any(word in query_lower for word in ['page content', 'links', 'forms']):
            return self._format_content_response(state_data)
            
        elif 'all tabs' in query_lower or 'list tabs' in query_lower:
            return self._format_all_tabs_response(state_data)
            
        else:
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
                
            response = f"Page Content Summary:\n"
            response += f"• Title: {content.get('title', 'Unknown')}\n"
            response += f"• Content Length: {content.get('content_length', 0)} characters\n"
            
            links = content.get('links', {})
            response += f"• Links: {links.get('count', 0)} total"
            if links.get('external_count', 0) > 0:
                response += f" ({links['external_count']} external)"
            response += "\n"
            
            forms = content.get('forms', {})
            if forms.get('count', 0) > 0:
                response += f"• Forms: {forms['count']} forms with {forms.get('input_count', 0)} inputs\n"
                
            images = content.get('images', {})
            if images.get('count', 0) > 0:
                response += f"• Images: {images['count']} images\n"
                
            headings = content.get('headings', {})
            if headings.get('count', 0) > 0:
                response += f"• Headings: {headings['count']} headings\n"
                
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
