# Troubleshooting Guide for AI Browser Agent

## 🔧 Common Issues and Solutions

### Issue 1: "requests package not available"

**Error Message:**
```
❌ Failed to initialize agent: requests package not available
```

**Cause:** The `requests` package is not installed in qutebrowser's Python environment.

**Solutions:**

#### Solution A: Install via pip (Recommended)
```bash
pip install requests
```

#### Solution B: Install via pip3
```bash
pip3 install requests
```

#### Solution C: Use the installation script
```bash
python3 ai_agent_tools/install_dependencies.py
```

#### Solution D: Install in qutebrowser's environment
If qutebrowser uses a different Python environment, find its Python path:
```python
# In qutebrowser Python console
import sys
print(sys.executable)
# Then use that Python to install packages
```

### Issue 2: "ai-agent-init is not a class method"

**Error Message:**
```
TypeError: ai-agent-init is not a class method, but instance was given!
```

**Cause:** Command registration issue in qutebrowser.

**Solution:** This has been fixed in the latest version. Use the updated scripts:
```
:pyeval --file ai_agent_tools/load_ai_agent.py
```

### Issue 3: "Ollama connection failed"

**Error Message:**
```
❌ Ollama connection error: HTTPConnectionPool(host='localhost', port=11434)
```

**Cause:** Ollama is not running or not accessible.

**Solutions:**

#### Solution A: Start Ollama
```bash
ollama serve
```

#### Solution B: Check if Ollama is running
```bash
ollama list
```

#### Solution C: Check Ollama status
```bash
curl http://localhost:11434/api/tags
```

### Issue 4: "DeepSeek model not found"

**Error Message:**
```
⚠️ DeepSeek R1 14B model not found
```

**Cause:** The DeepSeek model is not downloaded.

**Solution:**
```bash
ollama pull deepseek-r1:14b
```

### Issue 5: "Timeout error"

**Error Message:**
```
Read timed out. (read timeout=120)
```

**Cause:** The 14B model takes time to respond.

**Solutions:**

#### Solution A: Increase timeout
Edit `ai_agent_tools/agent_config.json`:
```json
{
  "deepseek_assistant": {
    "timeout": 180
  }
}
```

#### Solution B: Use a smaller model
```bash
ollama pull deepseek-coder:6.7b
```

#### Solution C: Be patient
14B models naturally take 10-30 seconds to respond.

### Issue 6: "Qutebrowser modules not available"

**Error Message:**
```
No module named 'PyQt6.QtCore'
```

**Cause:** Script is not running in qutebrowser environment.

**Solution:** Run the script from within qutebrowser:
```
:pyeval --file ai_agent_tools/load_ai_agent.py
```

### Issue 7: "Memory issues"

**Error Message:**
```
Out of memory
```

**Cause:** 14B model requires significant RAM.

**Solutions:**

#### Solution A: Close other applications
Free up RAM by closing other applications.

#### Solution B: Use a smaller model
```bash
ollama pull deepseek-coder:6.7b
```

#### Solution C: Check available RAM
```bash
free -h  # Linux
top       # macOS
```

## 🧪 Diagnostic Tools

### 1. Test Dependencies
```bash
python3 ai_agent_tools/install_dependencies.py
```

### 2. Test Qutebrowser Setup
```
:pyeval --file ai_agent_tools/test_qutebrowser_setup.py
```

### 3. Test Commands
```
:pyeval --file ai_agent_tools/test_commands.py
```

### 4. Test Reasoning Separation
```
:pyeval --file ai_agent_tools/test_reasoning_separation.py
```

### 5. Quick DeepSeek Test
```bash
python3 ai_agent_tools/quick_deepseek_test.py
```

## 🔍 Step-by-Step Debugging

### Step 1: Check Python Environment
```python
# In qutebrowser Python console
import sys
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")
```

### Step 2: Check Required Packages
```python
# In qutebrowser Python console
try:
    import requests
    print("✅ requests available")
except ImportError:
    print("❌ requests not available")

try:
    import asyncio
    print("✅ asyncio available")
except ImportError:
    print("❌ asyncio not available")
```

### Step 3: Check Ollama
```bash
# In terminal
ollama list
curl http://localhost:11434/api/tags
```

### Step 4: Test AI Agent
```python
# In qutebrowser Python console
from ai_agent_tools.agent_interface import agent_interface
agent_interface.initialize_agent("deepseek_assistant")
```

### Step 5: Test Commands
```
:pyeval --file ai_agent_tools/load_ai_agent.py
:ai-agent-init deepseek_assistant
:ai-agent-ask "Hello"
```

## 🚀 Quick Fixes

### Fix 1: Complete Reset
```bash
# 1. Stop qutebrowser
# 2. Install dependencies
python3 ai_agent_tools/install_dependencies.py

# 3. Start qutebrowser
qutebrowser

# 4. Load agent
:pyeval --file ai_agent_tools/load_ai_agent.py
:ai-agent-init deepseek_assistant
```

### Fix 2: Alternative Setup
```bash
# 1. Use direct Python instead of commands
:pyeval --file ai_agent_tools/use_ai_agent.py

# 2. Use agent directly
await agent.ask("open github.com")
```

### Fix 3: Minimal Setup
```python
# In qutebrowser Python console
from ai_agent_tools.agent_interface import agent_interface
agent_interface.initialize_agent("deepseek_assistant")
await agent_interface.ask("open github.com")
```

## 📋 Environment Checklist

Before using the AI agent, ensure:

- [ ] Python 3.8+ installed
- [ ] `requests` package installed
- [ ] `asyncio` package available
- [ ] Ollama installed and running
- [ ] DeepSeek R1 14B model downloaded
- [ ] Qutebrowser running
- [ ] Commands loaded in qutebrowser

## 🆘 Getting Help

### 1. Check Logs
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Test Individual Components
```bash
# Test Ollama
ollama run deepseek-r1:14b "Hello"

# Test requests
python3 -c "import requests; print('OK')"

# Test AI agent
python3 ai_agent_tools/quick_deepseek_test.py
```

### 3. Common Commands
```bash
# Check Ollama status
ollama list
ollama logs

# Check Python packages
pip list | grep requests
pip list | grep asyncio

# Check system resources
htop  # or top
free -h
```

---

**💡 Most issues can be resolved by ensuring all dependencies are properly installed and Ollama is running with the DeepSeek model downloaded.**
