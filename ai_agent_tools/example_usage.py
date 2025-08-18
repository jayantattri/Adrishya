"""
Example Usage of Browser State Tools

This file demonstrates how to use the various browser state tools
to get information about qutebrowser's current state.
"""

import json
import time
from typing import Dict, Any

# Import the unified tools
from unified_state_tools import (
    get_complete_browser_state,
    get_browser_overview,
    get_tab_summary,
    get_performance_summary,
    get_page_content_summary,
    get_quick_status
)

# Import individual tools for specific use cases
from browser_state_tools import (
    get_current_tab_info,
    get_all_tabs_info,
    get_window_state,
    get_navigation_state
)

from page_content_tools import (
    get_page_text_content,
    get_page_links,
    get_page_forms
)

from performance_tools import (
    get_system_metrics,
    get_browser_process_metrics,
    get_performance_snapshot
)


def print_json(data: Dict[str, Any], title: str = ""):
    """Pretty print JSON data."""
    if title:
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}")
    
    print(json.dumps(data, indent=2, default=str))


def demo_basic_state_tools():
    """Demonstrate basic browser state tools."""
    print("\n🔍 Basic Browser State Tools")
    print("-" * 40)
    
    # Get current tab information
    current_tab = get_current_tab_info()
    if current_tab:
        print(f"Current Tab: {current_tab.title}")
        print(f"URL: {current_tab.url}")
        print(f"Loading: {current_tab.is_loading}")
        print(f"Can go back: {current_tab.can_go_back}")
        print(f"Can go forward: {current_tab.can_go_forward}")
    else:
        print("Could not get current tab info")
    
    # Get window state
    window_state = get_window_state()
    if window_state:
        print(f"\nWindow State:")
        print(f"  Total tabs: {window_state.total_tabs}")
        print(f"  Active tab index: {window_state.active_tab_index}")
        print(f"  Fullscreen: {window_state.is_fullscreen}")
        print(f"  Maximized: {window_state.is_maximized}")
    
    # Get navigation state
    nav_state = get_navigation_state()
    if nav_state:
        print(f"\nNavigation State:")
        print(f"  Can go back: {nav_state.can_go_back}")
        print(f"  Can go forward: {nav_state.can_go_forward}")
        print(f"  Page title: {nav_state.page_title}")


def demo_page_content_tools():
    """Demonstrate page content tools."""
    print("\n📄 Page Content Tools")
    print("-" * 40)
    
    # Get page text content
    text_content = get_page_text_content()
    if text_content:
        print(f"Page text length: {len(text_content)} characters")
        print(f"Preview: {text_content[:200]}...")
    else:
        print("Could not get page text content")
    
    # Get page links
    links = get_page_links()
    print(f"\nFound {len(links)} links on the page")
    
    # Get page forms
    forms = get_page_forms()
    print(f"Found {len(forms)} forms on the page")


def demo_performance_tools():
    """Demonstrate performance tools."""
    print("\n⚡ Performance Tools")
    print("-" * 40)
    
    # Get system metrics
    system_metrics = get_system_metrics()
    if system_metrics:
        print(f"System Metrics:")
        print(f"  CPU Usage: {system_metrics.cpu_percent}%")
        print(f"  Memory Usage: {system_metrics.memory_percent}%")
        print(f"  Available Memory: {system_metrics.memory_available / (1024**3):.2f} GB")
        print(f"  Total Memory: {system_metrics.memory_total / (1024**3):.2f} GB")
    
    # Get browser process metrics
    browser_process = get_browser_process_metrics()
    if browser_process:
        print(f"\nBrowser Process:")
        print(f"  Process ID: {browser_process.process_id}")
        print(f"  Memory Usage: {browser_process.memory_percent:.1f}%")
        print(f"  Memory (RSS): {browser_process.memory_rss / (1024**2):.1f} MB")
        print(f"  Threads: {browser_process.num_threads}")
    
    # Get performance snapshot
    snapshot = get_performance_snapshot()
    if snapshot and snapshot.overall_score is not None:
        print(f"\nOverall Performance Score: {snapshot.overall_score:.1f}/100")


def demo_unified_tools():
    """Demonstrate unified tools."""
    print("\n🔗 Unified Browser State Tools")
    print("-" * 40)
    
    # Get quick status
    quick_status = get_quick_status()
    print_json(quick_status, "Quick Status")
    
    # Get browser overview
    overview = get_browser_overview()
    print_json(overview, "Browser Overview")
    
    # Get tab summary
    tab_summary = get_tab_summary()
    print_json(tab_summary, "Tab Summary")
    
    # Get performance summary
    perf_summary = get_performance_summary()
    print_json(perf_summary, "Performance Summary")
    
    # Get page content summary
    content_summary = get_page_content_summary()
    print_json(content_summary, "Page Content Summary")


def demo_complete_state():
    """Demonstrate getting complete browser state."""
    print("\n🌐 Complete Browser State")
    print("-" * 40)
    
    # Get complete state (this might take a moment)
    print("Getting complete browser state...")
    complete_state = get_complete_browser_state()
    
    if hasattr(complete_state, 'error'):
        print(f"Error: {complete_state.error}")
    else:
        print(f"Timestamp: {complete_state.timestamp}")
        print(f"Window ID: {complete_state.window_id}")
        
        if complete_state.current_tab:
            print(f"Current Tab: {complete_state.current_tab.get('title', 'Unknown')}")
        
        if complete_state.all_tabs:
            print(f"Total Tabs: {len(complete_state.all_tabs)}")
        
        if complete_state.performance_score is not None:
            print(f"Performance Score: {complete_state.performance_score:.1f}/100")
        
        if complete_state.summary:
            print(f"System Health: {complete_state.summary.get('system_health', 'Unknown')}")
            print(f"Browser Health: {complete_state.summary.get('browser_health', 'Unknown')}")


def demo_monitoring():
    """Demonstrate continuous monitoring."""
    print("\n📊 Continuous Monitoring")
    print("-" * 40)
    
    print("Monitoring browser state for 30 seconds...")
    print("Press Ctrl+C to stop")
    
    try:
        start_time = time.time()
        while time.time() - start_time < 30:
            # Get quick status
            status = get_quick_status()
            
            # Clear screen and show current status
            print("\033[2J\033[H")  # Clear screen
            print(f"Monitoring Browser State - {time.strftime('%H:%M:%S')}")
            print("-" * 50)
            
            if status.get('current_page'):
                page = status['current_page']
                print(f"Current Page: {page.get('title', 'Unknown')}")
                print(f"URL: {page.get('url', '')}")
                print(f"Loading: {page.get('is_loading', False)}")
            
            if status.get('window'):
                window = status['window']
                print(f"Tabs: {window.get('tab_count', 0)}")
                print(f"Active Tab: {window.get('active_tab_index', -1)}")
            
            if status.get('system'):
                system = status['system']
                print(f"CPU: {system.get('cpu_percent', 0):.1f}%")
                print(f"Memory: {system.get('memory_percent', 0):.1f}%")
                print(f"Health: {system.get('health', 'Unknown')}")
            
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")


def main():
    """Main demonstration function."""
    print("🚀 Qutebrowser AI Agent Tools - Demo")
    print("=" * 60)
    print("This demo shows how to use the browser state tools to get")
    print("information about qutebrowser's current state.")
    print("\nNote: These tools need to be run from within qutebrowser")
    print("or with proper access to qutebrowser's internal state.")
    
    try:
        # Run demonstrations
        demo_basic_state_tools()
        demo_page_content_tools()
        demo_performance_tools()
        demo_unified_tools()
        demo_complete_state()
        
        # Ask if user wants to see monitoring
        response = input("\nWould you like to see continuous monitoring? (y/n): ")
        if response.lower() in ['y', 'yes']:
            demo_monitoring()
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("This might be because the tools are not running within qutebrowser")
        print("or there are import issues.")


if __name__ == "__main__":
    main()

