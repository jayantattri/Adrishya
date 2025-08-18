#!/bin/bash
# Qutebrowser startup script

# Activate virtual environment
source .venv/bin/activate

# Set basic Qt environment for macOS
export QT_QPA_PLATFORM="cocoa"

echo "Starting qutebrowser with PyQt5..."

# Run qutebrowser
python3 qutebrowser.py
