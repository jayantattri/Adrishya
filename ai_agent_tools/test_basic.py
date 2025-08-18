#!/usr/bin/env python3
"""
Basic Test Script for AI Agent Tools

This script tests basic import functionality and creates mock data
to verify the tools work correctly.
"""

import sys
import os
from typing import Dict, Any

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test basic imports
        from browser_state_tools import TabInfo, WindowState, NavigationState
        print("✅ Basic dataclasses imported successfully")
        
        from page_content_tools import PageContent, LinkInfo, FormInfo
        print("✅ Page content dataclasses imported successfully")
        
        from performance_tools import SystemMetrics, BrowserProcessMetrics
        print("✅ Performance dataclasses imported successfully")
        
        from unified_state_tools import CompleteBrowserState
        print("✅ Unified state dataclasses imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_dataclass_creation():
    """Test that dataclasses can be created with mock data."""
    print("\nTesting dataclass creation...")
    
    try:
        from browser_state_tools import TabInfo, WindowState, NavigationState
        
        # Create mock TabInfo
        tab_info = TabInfo(
            index=0,
            url="https://example.com",
            title="Example Page",
            is_active=True,
            is_loading=False,
            is_pinned=False,
            can_go_back=False,
            can_go_forward=False
        )
        print("✅ TabInfo created successfully")
        
        # Create mock WindowState
        window_state = WindowState(
            window_id=0,
            is_fullscreen=False,
            is_maximized=False,
            active_tab_index=0,
            total_tabs=1
        )
        print("✅ WindowState created successfully")
        
        # Create mock NavigationState
        nav_state = NavigationState(
            can_go_back=False,
            can_go_forward=False,
            current_url="https://example.com",
            page_title="Example Page",
            is_loading=False
        )
        print("✅ NavigationState created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Dataclass creation error: {e}")
        return False


def test_page_content_dataclasses():
    """Test page content dataclass creation."""
    print("\nTesting page content dataclasses...")
    
    try:
        from page_content_tools import PageContent, LinkInfo, FormInfo
        
        # Create mock LinkInfo
        link_info = LinkInfo(
            url="https://example.com/link",
            text="Example Link",
            title="Link Title",
            is_external=False,
            is_download=False
        )
        print("✅ LinkInfo created successfully")
        
        # Create mock FormInfo
        form_info = FormInfo(
            form_id="test-form",
            action_url="https://example.com/submit",
            method="POST",
            inputs=[],
            submit_buttons=[]
        )
        print("✅ FormInfo created successfully")
        
        # Create mock PageContent
        page_content = PageContent(
            url="https://example.com",
            title="Example Page",
            main_text="This is example content",
            links=[link_info],
            forms=[form_info],
            images=[],
            headings=[],
            meta_tags={},
            page_structure={}
        )
        print("✅ PageContent created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Page content dataclass error: {e}")
        return False


def test_performance_dataclasses():
    """Test performance dataclass creation."""
    print("\nTesting performance dataclasses...")
    
    try:
        from performance_tools import SystemMetrics, BrowserProcessMetrics
        
        # Create mock SystemMetrics
        system_metrics = SystemMetrics(
            cpu_percent=25.0,
            memory_percent=60.0,
            memory_available=8589934592,  # 8GB
            memory_total=17179869184,     # 16GB
            memory_used=10307921510,      # ~9.6GB
            disk_usage_percent=45.0,
            network_io={'bytes_sent': 1024, 'bytes_recv': 2048},
            process_count=150
        )
        print("✅ SystemMetrics created successfully")
        
        # Create mock BrowserProcessMetrics
        browser_process = BrowserProcessMetrics(
            process_id=12345,
            cpu_percent=5.0,
            memory_percent=15.0,
            memory_rss=268435456,  # 256MB
            memory_vms=536870912,  # 512MB
            num_threads=8,
            create_time=1640995200.0,
            status="running"
        )
        print("✅ BrowserProcessMetrics created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance dataclass error: {e}")
        return False


def test_unified_dataclasses():
    """Test unified state dataclass creation."""
    print("\nTesting unified state dataclasses...")
    
    try:
        from unified_state_tools import CompleteBrowserState
        
        # Create mock CompleteBrowserState
        complete_state = CompleteBrowserState(
            timestamp="2024-01-01T12:00:00",
            window_id=0,
            current_tab=None,
            all_tabs=[],
            window_state=None,
            navigation_state=None,
            browser_metrics=None,
            page_content=None,
            system_metrics=None,
            browser_process=None,
            tab_performance=[],
            network_metrics=None,
            performance_score=None,
            summary=None
        )
        print("✅ CompleteBrowserState created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified state dataclass error: {e}")
        return False


def test_json_serialization():
    """Test that dataclasses can be converted to JSON-serializable format."""
    print("\nTesting JSON serialization...")
    
    try:
        from dataclasses import asdict
        from browser_state_tools import TabInfo
        
        # Create a mock TabInfo
        tab_info = TabInfo(
            index=0,
            url="https://example.com",
            title="Example Page",
            is_active=True,
            is_loading=False,
            is_pinned=False,
            can_go_back=False,
            can_go_forward=False
        )
        
        # Convert to dictionary
        tab_dict = asdict(tab_info)
        
        # Test JSON serialization
        import json
        json_str = json.dumps(tab_dict)
        print("✅ JSON serialization successful")
        
        # Verify we can parse it back
        parsed_dict = json.loads(json_str)
        assert parsed_dict['url'] == "https://example.com"
        print("✅ JSON parsing successful")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization error: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 AI Agent Tools - Basic Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Dataclass Creation", test_dataclass_creation),
        ("Page Content Dataclasses", test_page_content_dataclasses),
        ("Performance Dataclasses", test_performance_dataclasses),
        ("Unified State Dataclasses", test_unified_dataclasses),
        ("JSON Serialization", test_json_serialization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The tools are ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

