"""
Load AI Agent Tools in Qutebrowser

This script should be executed within qutebrowser using the :pyeval command
to load and test the AI agent tools.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/load_in_qutebrowser.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add parent directory to path for qutebrowser imports
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print("Loading AI Agent Tools...")

try:
    # Import qutebrowser modules
    from qutebrowser.utils import message, objreg
    from qutebrowser.api import cmdutils
    
    print("✓ Qutebrowser modules imported successfully")
    
    # Import AI agent tools
    from unified_state_tools import (
        get_quick_status,
        get_browser_overview, 
        get_page_content_summary,
        get_performance_summary,
        get_complete_browser_state
    )
    
    print("✓ AI agent tools imported successfully")
    
    # Test the tools
    print("\n=== Testing AI Agent Tools ===")
    
    # Test 1: Quick Status
    try:
        status = get_quick_status()
        print(f"✓ Quick Status: {status.get('status', 'Unknown')}")
        if 'current_page' in status and status['current_page']:
            page = status['current_page']
            print(f"  Current page: {page.get('title', 'No title')}")
            print(f"  URL: {page.get('url', 'No URL')}")
        else:
            print("  No current page information")
    except Exception as e:
        print(f"✗ Quick Status failed: {e}")
    
    # Test 2: Browser Overview
    try:
        overview = get_browser_overview()
        print(f"✓ Browser Overview: {overview.get('tab_count', 0)} tabs")
        if overview.get('active_tab'):
            print(f"  Active tab: {overview['active_tab'].get('title', 'No title')}")
        else:
            print("  No active tab information")
    except Exception as e:
        print(f"✗ Browser Overview failed: {e}")
    
    # Test 3: Page Content
    try:
        content = get_page_content_summary()
        if 'error' in content:
            print(f"✗ Page Content: {content['error']}")
        else:
            print(f"✓ Page Content: {content.get('title', 'No title')}")
            print(f"  Content length: {content.get('content_length', 0)} chars")
            print(f"  Links: {content.get('link_count', 0)}")
            print(f"  Forms: {content.get('form_count', 0)}")
    except Exception as e:
        print(f"✗ Page Content failed: {e}")
    
    # Test 4: Performance
    try:
        perf = get_performance_summary()
        if 'error' in perf:
            print(f"✗ Performance: {perf['error']}")
        else:
            print(f"✓ Performance: Score {perf.get('overall_score', 'N/A')}")
            print(f"  System health: {perf.get('system_health', 'Unknown')}")
            print(f"  Browser health: {perf.get('browser_health', 'Unknown')}")
    except Exception as e:
        print(f"✗ Performance failed: {e}")
    
    print("\n=== AI Agent Tools Test Complete ===")
    
    # Try to get real browser instance
    try:
        browser = objreg.get('tabbed-browser', scope='window', window='current')
        if browser:
            print(f"✓ Got browser instance: {type(browser).__name__}")
            current_tab = browser.widget.currentWidget()
            if current_tab:
                print(f"✓ Got current tab: {type(current_tab).__name__}")
                print(f"  Tab URL: {current_tab.url().toString()}")
                print(f"  Tab title: {current_tab.title()}")
                
                # Try to execute JavaScript
                try:
                    def js_callback(result):
                        print(f"✓ JavaScript execution successful: {result}")
                    
                    def js_error_callback(error):
                        print(f"✗ JavaScript execution failed: {error}")
                    
                    js_code = "document.title"
                    if hasattr(current_tab, 'run_js_async'):
                        current_tab.run_js_async(js_code, js_callback, js_error_callback)
                        print("✓ JavaScript execution initiated")
                    else:
                        print("✗ No JavaScript execution method available")
                        
                except Exception as e:
                    print(f"✗ JavaScript test failed: {e}")
            else:
                print("✗ No current tab found")
        else:
            print("✗ No browser instance found")
    except Exception as e:
        print(f"✗ Browser instance test failed: {e}")
    
    message.info("AI Agent Tools loaded and tested successfully! Check the console output for details.")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from within qutebrowser")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
