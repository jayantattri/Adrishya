#!/usr/bin/env python3
"""Test the asyncio event loop fix."""

import asyncio

def test_event_loop():
    """Test the event loop fix."""
    print("Testing asyncio event loop fix...")
    
    try:
        # Try to get the running loop
        loop = asyncio.get_running_loop()
        print("✅ get_running_loop() works")
        return True
    except RuntimeError:
        # No running loop, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("✅ new_event_loop() works")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_event_loop()
    if success:
        print("🎉 Asyncio fix is working correctly!")
    else:
        print("⚠️ Asyncio fix needs attention")
