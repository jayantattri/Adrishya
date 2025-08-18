"""
Test command for AI Agent Tools within qutebrowser

This file provides a qutebrowser command to test the AI agent tools
from within the browser environment.
"""

import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from qutebrowser.api import cmdutils
    from qutebrowser.utils import message, objreg
    QUTEBROWSER_AVAILABLE = True
except ImportError:
    QUTEBROWSER_AVAILABLE = False
    print("Warning: Not running within qutebrowser environment")

# Import our AI agent tools
try:
    from .unified_state_tools import (
        get_quick_status, 
        get_browser_overview, 
        get_page_content_summary,
        get_performance_summary
    )
except ImportError:
    # Fallback import when running as script
    try:
        from unified_state_tools import (
            get_quick_status, 
            get_browser_overview, 
            get_page_content_summary,
            get_performance_summary
        )
    except ImportError as e:
        print(f"Could not import AI agent tools: {e}")
        get_quick_status = lambda: {"error": "Tools not available"}
        get_browser_overview = lambda: {"error": "Tools not available"}
        get_page_content_summary = lambda: {"error": "Tools not available"}
        get_performance_summary = lambda: {"error": "Tools not available"}


def format_output(data: Dict[str, Any], title: str = "") -> str:
    """Format output for display in qutebrowser."""
    lines = []
    if title:
        lines.append(f"=== {title} ===")
        lines.append("")
    
    def format_dict(d, indent=0):
        prefix = "  " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                format_dict(value, indent + 1)
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}: [{len(value)} items]")
                for i, item in enumerate(value[:3]):  # Show first 3 items
                    if isinstance(item, dict):
                        lines.append(f"{prefix}  [{i}]:")
                        format_dict(item, indent + 2)
                    else:
                        lines.append(f"{prefix}  [{i}]: {item}")
                if len(value) > 3:
                    lines.append(f"{prefix}  ... and {len(value) - 3} more")
            else:
                lines.append(f"{prefix}{key}: {value}")
    
    format_dict(data)
    return "\n".join(lines)


if QUTEBROWSER_AVAILABLE:
    @cmdutils.register()
    def ai_test_quick():
        """Test AI agent tools - quick status."""
        try:
            status = get_quick_status()
            output = format_output(status, "AI Agent Tools - Quick Status")
            message.info(output)
        except Exception as e:
            message.error(f"Error testing AI tools: {e}")

    @cmdutils.register()
    def ai_test_overview():
        """Test AI agent tools - browser overview."""
        try:
            overview = get_browser_overview()
            output = format_output(overview, "AI Agent Tools - Browser Overview")
            message.info(output)
        except Exception as e:
            message.error(f"Error testing AI tools: {e}")

    @cmdutils.register()
    def ai_test_content():
        """Test AI agent tools - page content summary."""
        try:
            content = get_page_content_summary()
            output = format_output(content, "AI Agent Tools - Page Content")
            message.info(output)
        except Exception as e:
            message.error(f"Error testing AI tools: {e}")

    @cmdutils.register()
    def ai_test_performance():
        """Test AI agent tools - performance summary."""
        try:
            perf = get_performance_summary()
            output = format_output(perf, "AI Agent Tools - Performance")
            message.info(output)
        except Exception as e:
            message.error(f"Error testing AI tools: {e}")

    @cmdutils.register()
    def ai_test_all():
        """Test all AI agent tools."""
        try:
            message.info("=== AI Agent Tools - Complete Test ===\n")
            
            # Quick status
            status = get_quick_status()
            message.info(format_output(status, "Quick Status"))
            
            # Browser overview  
            overview = get_browser_overview()
            message.info(format_output(overview, "Browser Overview"))
            
            # Page content
            content = get_page_content_summary()
            message.info(format_output(content, "Page Content"))
            
            # Performance
            perf = get_performance_summary()
            message.info(format_output(perf, "Performance"))
            
            message.info("=== AI Agent Tools Test Complete ===")
            
        except Exception as e:
            message.error(f"Error testing AI tools: {e}")
            import traceback
            message.error(traceback.format_exc())

else:
    # Standalone testing when not in qutebrowser
    def test_tools():
        """Test the AI agent tools outside qutebrowser."""
        print("Testing AI Agent Tools (Standalone)")
        print("=" * 50)
        
        try:
            status = get_quick_status()
            print(format_output(status, "Quick Status"))
            print()
            
            overview = get_browser_overview()
            print(format_output(overview, "Browser Overview"))
            print()
            
            content = get_page_content_summary()
            print(format_output(content, "Page Content"))
            print()
            
            perf = get_performance_summary()
            print(format_output(perf, "Performance"))
            print()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        test_tools()
