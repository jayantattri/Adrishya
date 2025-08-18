#!/usr/bin/env python3
"""
JavaScript Execution Debug Tool for Qutebrowser AI Agent Tools

This script helps diagnose why JavaScript execution might be failing in the AI agent tools.
Run this from within qutebrowser to test JavaScript execution capabilities.
"""

import sys
import os
from typing import Optional, Any

# Add qutebrowser to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_javascript_execution():
    """Test JavaScript execution capabilities."""
    print("🔍 JavaScript Execution Debug Tool")
    print("=" * 50)
    
    try:
        from qutebrowser.utils import objreg, log
        from qutebrowser.api import config
        print("✅ Qutebrowser modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import qutebrowser modules: {e}")
        return False
    
    # Check JavaScript configuration
    try:
        js_enabled = config.val.content.javascript.enabled
        print(f"📋 JavaScript enabled in config: {js_enabled}")
        if not js_enabled:
            print("⚠️  JavaScript is disabled! Enable it with: :set content.javascript.enabled true")
            return False
    except Exception as e:
        print(f"⚠️  Could not check JavaScript configuration: {e}")
    
    # Get current tab
    try:
        tabbed_browser = objreg.get('tabbed-browser', scope='window', window=0)
        current_tab = tabbed_browser.widget.currentWidget()
        if not current_tab:
            print("❌ No current tab found")
            return False
            
        print(f"📄 Current tab type: {type(current_tab).__name__}")
        print(f"📄 Current tab URL: {current_tab.url().toString() if current_tab.url() else 'No URL'}")
        print(f"📄 Current tab title: {current_tab.title() if hasattr(current_tab, 'title') else 'No title'}")
        
    except Exception as e:
        print(f"❌ Error getting current tab: {e}")
        return False
    
    # Test JavaScript execution methods
    print("\n🧪 Testing JavaScript execution methods...")
    
    # Test 1: Check if run_js_async is available
    if hasattr(current_tab, 'run_js_async'):
        print("✅ run_js_async method available")
        
        # Test simple JavaScript execution
        try:
            result = {'value': None, 'error': None, 'completed': False}
            
            def callback(js_result):
                print(f"✅ JavaScript callback received: {js_result}")
                result['value'] = js_result
                result['completed'] = True
            
            # WebEngineTab.run_js_async only takes code and callback parameters
            print("🔄 Executing JavaScript: 1 + 1")
            current_tab.run_js_async('1 + 1', callback)
            
            # Wait for result
            import time
            timeout = 5.0
            start_time = time.time()
            sleep_interval = 0.1
            
            print("⏳ Waiting for JavaScript result...")
            while not result['completed'] and (time.time() - start_time) < timeout:
                time.sleep(sleep_interval)
                # Process Qt events
                try:
                    from qutebrowser.qt.widgets import QApplication
                    if QApplication.instance():
                        QApplication.processEvents()
                except:
                    pass
            
            if result['completed']:
                if result['error']:
                    print(f"❌ run_js_async failed: {result['error']}")
                else:
                    print(f"✅ run_js_async successful: {result['value']}")
            else:
                print("⏰ run_js_async timed out")
                print("💡 This might indicate:")
                print("   • JavaScript execution is blocked")
                print("   • Page security restrictions")
                print("   • Callback mechanism not working")
                
        except Exception as e:
            print(f"❌ run_js_async test failed: {e}")
    else:
        print("❌ run_js_async method not available")
    
    # Test 1.5: Try even simpler JavaScript
    print("\n🧪 Testing very simple JavaScript...")
    try:
        result = {'value': None, 'completed': False}
        
        def simple_callback(js_result):
            print(f"✅ Simple callback received: {js_result}")
            result['value'] = js_result
            result['completed'] = True
        
        print("🔄 Executing: 'hello'")
        current_tab.run_js_async("'hello'", simple_callback)
        
        import time
        timeout = 3.0
        start_time = time.time()
        
        while not result['completed'] and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            try:
                from qutebrowser.qt.widgets import QApplication
                if QApplication.instance():
                    QApplication.processEvents()
            except:
                pass
        
        if result['completed']:
            print(f"✅ Simple JavaScript successful: {result['value']}")
        else:
            print("⏰ Simple JavaScript timed out")
            
    except Exception as e:
        print(f"❌ Simple JavaScript test failed: {e}")
    
    # Test 2: Check if Qt WebEngine runJavaScript is available
    if hasattr(current_tab, 'page') and hasattr(current_tab.page(), 'runJavaScript'):
        print("✅ Qt WebEngine runJavaScript method available")
        
        try:
            page = current_tab.page()
            result = {'value': None, 'completed': False}
            
            def js_callback(js_result):
                result['value'] = js_result
                result['completed'] = True
            
            page.runJavaScript('2 + 2', js_callback)
            
            # Wait for result
            import time
            timeout = 3.0
            start_time = time.time()
            
            while not result['completed'] and (time.time() - start_time) < timeout:
                time.sleep(0.01)
            
            if result['completed']:
                print(f"✅ Qt WebEngine runJavaScript successful: {result['value']}")
            else:
                print("⏰ Qt WebEngine runJavaScript timed out")
                
        except Exception as e:
            print(f"❌ Qt WebEngine runJavaScript test failed: {e}")
    else:
        print("❌ Qt WebEngine runJavaScript method not available")
    
    # Test 3: Test document access
    print("\n🌐 Testing document access...")
    
    try:
        js_code = """
        (function() {
            return {
                readyState: document.readyState,
                title: document.title,
                url: window.location.href,
                hasBody: !!document.body,
                bodyTextLength: document.body ? document.body.innerText.length : 0
            };
        })();
        """
        
        result = {'value': None, 'error': None, 'completed': False}
        
        def callback(js_result):
            result['value'] = js_result
            result['completed'] = True
        
        print("🔄 Executing document access test...")
        current_tab.run_js_async(js_code, callback)
        
        # Wait for result
        import time
        timeout = 8.0
        start_time = time.time()
        sleep_interval = 0.1
        
        print("⏳ Waiting for document access result...")
        while not result['completed'] and (time.time() - start_time) < timeout:
            time.sleep(sleep_interval)
            # Process Qt events
            try:
                from qutebrowser.qt.widgets import QApplication
                if QApplication.instance():
                    QApplication.processEvents()
            except:
                pass
        
        if result['completed']:
            if result['error']:
                print(f"❌ Document access failed: {result['error']}")
            else:
                doc_info = result['value']
                print(f"✅ Document access successful:")
                print(f"   • Ready state: {doc_info.get('readyState', 'unknown')}")
                print(f"   • Title: {doc_info.get('title', 'unknown')}")
                print(f"   • URL: {doc_info.get('url', 'unknown')}")
                print(f"   • Has body: {doc_info.get('hasBody', False)}")
                print(f"   • Body text length: {doc_info.get('bodyTextLength', 0)}")
        else:
            print("⏰ Document access timed out")
            print("💡 This might indicate:")
            print("   • Page not fully loaded (readyState != 'complete')")
            print("   • JavaScript execution blocked")
            print("   • Security restrictions on the page")
            
    except Exception as e:
        print(f"❌ Document access test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Debug Summary:")
    print("If JavaScript execution is failing, check:")
    print("1. JavaScript is enabled: :set content.javascript.enabled true")
    print("2. Page is fully loaded (readyState should be 'complete')")
    print("3. Page is not a special page (chrome://, about:, etc.)")
    print("4. Page doesn't have security restrictions")
    print("5. Qutebrowser is using QtWebEngine backend")
    print("\n💡 Try navigating to a simple page like 'https://example.com'")
    print("   and run this debug tool again to test JavaScript execution.")
    
    return True

if __name__ == "__main__":
    test_javascript_execution()
