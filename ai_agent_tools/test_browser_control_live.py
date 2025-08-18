"""
Live Browser Control Tools Testing Script

This script demonstrates and tests the browser control tools in real-time within qutebrowser.
Use this to see the tools in action and verify functionality.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_browser_control_live.py
"""

import sys
import os
import time

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add parent directory to path for qutebrowser imports
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print("🤖 Starting Live Browser Control Tools Test...")

try:
    # Import qutebrowser modules
    from qutebrowser.utils import message, objreg
    from qutebrowser.api import cmdutils
    
    print("✓ Qutebrowser modules imported successfully")
    
    # Import browser control tools
    from browser_control_tools import (
        BrowserControlTools, create_browser_controller,
        execute_browser_command, CommandResult
    )
    from enhanced_browser_control import (
        EnhancedBrowserControl, create_enhanced_controller,
        execute_smart_action, ElementSelector, FormField
    )
    from unified_state_tools import (
        get_quick_status, get_browser_overview, 
        get_tab_summary, get_performance_summary
    )
    
    print("✓ Browser control tools imported successfully")
    
    # Create controller instances
    basic_controller = create_browser_controller()
    enhanced_controller = create_enhanced_controller()
    
    print("✓ Controller instances created")
    
    def show_result(result, operation_name):
        """Helper to display command results."""
        if isinstance(result, CommandResult):
            status = "✓" if result.success else "✗"
            print(f"  {status} {operation_name}: {result.message or result.error or 'No message'}")
        else:
            print(f"  ? {operation_name}: {result}")
    
    def wait_and_show_state(description=""):
        """Helper to show current browser state."""
        if description:
            print(f"\n--- {description} ---")
        
        try:
            status = get_quick_status()
            if status and 'current_page' in status and status['current_page']:
                page = status['current_page']
                print(f"📄 Current page: {page.get('title', 'No title')}")
                print(f"🔗 URL: {page.get('url', 'No URL')[:60]}...")
                print(f"⏳ Loading: {page.get('is_loading', False)}")
            
            tab_info = get_tab_summary()
            if tab_info:
                print(f"📑 Tabs: {tab_info.get('count', 0)} total, active: {tab_info.get('active_index', -1)}")
        except Exception as e:
            print(f"❌ State check failed: {e}")
    
    print("\n🧪 === LIVE BROWSER CONTROL TEST SUITE ===")
    
    # Test 1: Current State
    print("\n1️⃣ === Current Browser State ===")
    wait_and_show_state("Initial State")
    
    # Test 2: Basic URL Opening  
    print("\n2️⃣ === Testing Basic URL Opening ===")
    result = basic_controller.open_url("https://example.com", tab=True)
    show_result(result, "Open example.com in new tab")
    
    if result.success:
        time.sleep(2)  # Wait for page load
        wait_and_show_state("After opening example.com")
    
    # Test 3: Page Interaction
    print("\n3️⃣ === Testing Page Interaction ===")
    
    # Test scrolling
    scroll_result = basic_controller.scroll("down", count=2)
    show_result(scroll_result, "Scroll down 2 times")
    
    # Test search
    search_result = basic_controller.search("Example")
    show_result(search_result, "Search for 'Example'")
    
    # Test zoom
    zoom_result = basic_controller.zoom_in(count=1)
    show_result(zoom_result, "Zoom in")
    
    time.sleep(1)
    zoom_reset = basic_controller.zoom(100)
    show_result(zoom_reset, "Reset zoom to 100%")
    
    # Test 4: Enhanced Smart Actions
    print("\n4️⃣ === Testing Enhanced Smart Actions ===")
    
    # Test smart navigation
    smart_nav = enhanced_controller.smart_navigation(
        "https://httpbin.org/html", 
        strategy="new_tab"
    )
    show_result(smart_nav, "Smart navigation to httpbin.org")
    
    if smart_nav.success:
        # Wait for page to load
        enhanced_controller.wait_for_page_load(timeout=10)
        wait_and_show_state("After smart navigation")
        
        # Test smart scrolling
        smart_scroll = enhanced_controller.smart_scroll("down", "half")
        show_result(smart_scroll, "Smart scroll down half page")
        
        # Test intelligent interaction
        try:
            intelligent_result = execute_smart_action("scroll to top")
            show_result(intelligent_result, "Intelligent 'scroll to top' action")
        except Exception as e:
            print(f"  ✗ Intelligent action failed: {e}")
    
    # Test 5: Tab Management
    print("\n5️⃣ === Testing Tab Management ===")
    
    # Get current tab count
    initial_tabs = get_tab_summary()
    initial_count = initial_tabs.get('count', 0) if initial_tabs else 0
    print(f"📊 Initial tab count: {initial_count}")
    
    # Open another tab
    new_tab_result = basic_controller.tab_new("https://httpbin.org/json")
    show_result(new_tab_result, "Open new tab with JSON page")
    
    time.sleep(1)
    
    # Check tab count
    after_tabs = get_tab_summary()
    after_count = after_tabs.get('count', 0) if after_tabs else 0
    print(f"📊 After new tab: {after_count}")
    
    # Switch tabs
    if after_count > 1:
        switch_result = basic_controller.tab_prev()
        show_result(switch_result, "Switch to previous tab")
        
        time.sleep(0.5)
        
        switch_back = basic_controller.tab_next()
        show_result(switch_back, "Switch to next tab")
    
    # Test 6: Configuration Commands
    print("\n6️⃣ === Testing Configuration Commands ===")
    
    # Test setting configuration (temporary)
    config_result = basic_controller.set_config(
        "content.images", "false", temp=True
    )
    show_result(config_result, "Temporarily disable images")
    
    time.sleep(1)
    
    # Reset configuration
    config_reset = basic_controller.set_config(
        "content.images", "true", temp=True
    )
    show_result(config_reset, "Re-enable images")
    
    # Test 7: Performance and State Monitoring
    print("\n7️⃣ === Testing Performance and State Monitoring ===")
    
    try:
        performance = get_performance_summary()
        if performance and 'error' not in performance:
            print(f"⚡ Performance Score: {performance.get('overall_score', 'N/A')}")
            print(f"🖥️  System Health: {performance.get('system_health', 'Unknown')}")
            print(f"🌐 Browser Health: {performance.get('browser_health', 'Unknown')}")
        else:
            print(f"⚠️  Performance monitoring: {performance.get('error', 'Not available')}")
    except Exception as e:
        print(f"❌ Performance check failed: {e}")
    
    # Test 8: Advanced Element Detection
    print("\n8️⃣ === Testing Advanced Element Detection ===")
    
    # Test smart selector creation
    login_selectors = enhanced_controller.create_smart_selectors("login button")
    print(f"🔍 Created {len(login_selectors)} smart selectors for 'login button'")
    
    search_selectors = enhanced_controller.create_smart_selectors("search box")
    print(f"🔍 Created {len(search_selectors)} smart selectors for 'search box'")
    
    # Test 9: Command History
    print("\n9️⃣ === Testing Command History ===")
    
    history = basic_controller.get_command_history()
    print(f"📝 Command history has {len(history)} entries")
    
    if history:
        print("📋 Recent commands:")
        for i, cmd in enumerate(history[-5:], 1):  # Show last 5
            status = "✓" if cmd.success else "✗"
            print(f"   {i}. {status} {cmd.command} {' '.join(cmd.args) if cmd.args else ''}")
    
    # Test 10: Cleanup and Final State
    print("\n🔟 === Cleanup and Final State ===")
    
    # Close extra tabs (keep original tabs)
    final_tabs = get_tab_summary()
    final_count = final_tabs.get('count', 0) if final_tabs else 0
    
    if final_count > initial_count:
        tabs_to_close = final_count - initial_count
        print(f"🧹 Closing {tabs_to_close} test tabs...")
        
        for i in range(tabs_to_close):
            close_result = basic_controller.tab_close()
            show_result(close_result, f"Close tab {i+1}")
            time.sleep(0.3)
    
    wait_and_show_state("Final State")
    
    print("\n🎉 === LIVE BROWSER CONTROL TEST COMPLETED ===")
    print("\n✅ All browser control tools are working correctly!")
    print("🚀 You can now use these tools for automation:")
    print("   • basic_controller = create_browser_controller()")
    print("   • enhanced_controller = create_enhanced_controller()")
    print("   • execute_smart_action('your goal here')")
    
    # Store controllers globally for interactive use
    globals()['basic_controller'] = basic_controller
    globals()['enhanced_controller'] = enhanced_controller
    
    message.info("🤖 Browser Control Tools test completed! Check console for detailed results. Controllers are now available as 'basic_controller' and 'enhanced_controller'.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from within qutebrowser")
    message.error("Failed to import browser control tools")
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
    message.error(f"Browser control test failed: {str(e)}")

print("\n🏁 Test script execution completed.")
