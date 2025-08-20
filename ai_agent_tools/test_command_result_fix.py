#!/usr/bin/env python3
"""
Test CommandResult Attribute Fix

This script tests that the CommandResult objects are handled correctly
without the 'output' attribute error.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_command_result_fix.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing CommandResult Attribute Fix...")

try:
    from ai_browser_agent import CommandResult
    print("✅ CommandResult imported successfully")
except ImportError as e:
    print(f"❌ Could not import CommandResult: {e}")
    sys.exit(1)

def test_command_result_attributes():
    """Test that CommandResult has the correct attributes."""
    print("\n🔧 Testing CommandResult attributes...")
    
    # Test successful result
    success_result = CommandResult(
        success=True,
        command="open_url",
        args=["https://example.com"],
        message="URL opened successfully"
    )
    
    print(f"✅ Success result:")
    print(f"   success: {success_result.success}")
    print(f"   command: {success_result.command}")
    print(f"   args: {success_result.args}")
    print(f"   message: {success_result.message}")
    print(f"   error: {success_result.error}")
    
    # Test failed result
    failed_result = CommandResult(
        success=False,
        command="click_element",
        args=["#nonexistent"],
        error="Element not found"
    )
    
    print(f"\n❌ Failed result:")
    print(f"   success: {failed_result.success}")
    print(f"   command: {failed_result.command}")
    print(f"   args: {failed_result.args}")
    print(f"   message: {failed_result.message}")
    print(f"   error: {failed_result.error}")
    
    # Test that 'output' attribute doesn't exist
    try:
        output_value = success_result.output
        print(f"\n❌ 'output' attribute exists: {output_value}")
    except AttributeError:
        print(f"\n✅ 'output' attribute correctly doesn't exist")
    
    print("\n🎉 CommandResult attribute test completed!")

def test_feedback_message_creation():
    """Test that feedback message creation works correctly."""
    print("\n📝 Testing feedback message creation...")
    
    try:
        from ai_browser_agent import AIBrowserAgent
        
        # Create a mock agent instance
        agent = AIBrowserAgent()
        
        # Create test tool call and result
        tool_call = {
            "name": "open_url",
            "parameters": {"url": "https://example.com"}
        }
        
        result = CommandResult(
            success=True,
            command="open_url",
            args=["https://example.com"],
            message="URL opened successfully"
        )
        
        # Test feedback message creation
        feedback = agent._create_tool_feedback_message(
            tool_call, result, 1, [tool_call], [result]
        )
        
        print("✅ Feedback message created successfully:")
        print(feedback)
        
    except Exception as e:
        print(f"❌ Feedback message creation failed: {e}")
        import traceback
        traceback.print_exc()

# Run tests
if __name__ == "__main__":
    test_command_result_attributes()
    test_feedback_message_creation()
    
    print("\n" + "=" * 50)
    print("🧪 CommandResult Fix Test Complete!")
    print("   The CommandResult objects should now work correctly")
    print("   without the 'output' attribute error")
    print("=" * 50)
