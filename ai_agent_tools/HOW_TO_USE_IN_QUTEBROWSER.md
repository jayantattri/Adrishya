# How to Use AI Agent in Qutebrowser

## 🚀 Quick Start (Choose Your Method)

### Method 1: Load Commands (Recommended)
```
:pyeval --file ai_agent_tools/load_ai_agent.py
:ai-agent-init deepseek_assistant
:ai-agent-ask "open github.com"
```

### Method 2: Direct Python Usage
```
:pyeval --file ai_agent_tools/use_ai_agent.py
await agent.ask("open github.com")
```

### Method 3: Manual Setup
```
:pyeval --file ai_agent_tools/agent_interface.py
agent = agent_interface
agent.initialize_agent("deepseek_assistant")
await agent.ask("open github.com")
```

## 📋 Step-by-Step Instructions

### Step 1: Start Qutebrowser
```bash
qutebrowser
```

### Step 2: Load the AI Agent

#### Option A: Load Commands (Easiest)
In qutebrowser, type:
```
:pyeval --file ai_agent_tools/load_ai_agent.py
```

This will make these commands available:
- `:ai-agent-init <profile>`
- `:ai-agent-ask <query>`
- `:ai-agent-status`
- `:ai-agent-help`

#### Option B: Direct Python Usage
In qutebrowser, type:
```
:pyeval --file ai_agent_tools/use_ai_agent.py
```

This sets up the agent as a Python variable you can use directly.

### Step 3: Initialize the Agent

#### If using commands:
```
:ai-agent-init deepseek_assistant
```

#### If using Python directly:
```python
agent.initialize_agent("deepseek_assistant")
```

### Step 4: Start Using the Agent

#### Using commands:
```
:ai-agent-ask "open github.com"
:ai-agent-ask "help me research Python frameworks"
:ai-agent-ask "open reddit.com in a new tab"
```

#### Using Python directly:
```python
await agent.ask("open github.com")
await agent.ask("help me research Python frameworks")
await agent.ask("open reddit.com in a new tab")
```

## 🎯 Example Usage

### Basic Navigation
```
:ai-agent-ask "open stackoverflow.com"
:ai-agent-ask "go to reddit.com in a new tab"
:ai-agent-ask "open github.com and search for qutebrowser"
```

### Research Tasks
```
:ai-agent-ask "help me research AI tools by opening GitHub and searching for 'AI browser automation'"
:ai-agent-ask "compare React vs Vue by opening their documentation"
:ai-agent-ask "find information about Python web frameworks"
```

### Complex Workflows
```
:ai-agent-ask "research the best laptop under $1000 by checking Amazon, Best Buy, and Newegg"
:ai-agent-ask "help me gather information about machine learning by opening arXiv, Papers With Code, and Google Scholar"
```

### Form Automation
```
:ai-agent-ask "find the contact form on this page and fill it with my email"
:ai-agent-ask "fill out this job application form"
```

## 🔧 Troubleshooting

### Commands Not Available
If `:ai-agent-*` commands don't work:

1. **Check if commands were loaded:**
   ```
   :pyeval --file ai_agent_tools/load_ai_agent.py
   ```

2. **Use Python directly instead:**
   ```
   :pyeval --file ai_agent_tools/use_ai_agent.py
   ```

### Agent Not Initialized
If you get "agent not initialized" error:

1. **Initialize the agent:**
   ```
   :ai-agent-init deepseek_assistant
   ```

2. **Or use Python:**
   ```python
   agent.initialize_agent("deepseek_assistant")
   ```

### Ollama Not Running
If you get connection errors:

1. **Check if Ollama is running:**
   ```bash
   ollama list
   ```

2. **Start Ollama if needed:**
   ```bash
   ollama serve
   ```

3. **Verify DeepSeek model:**
   ```bash
   ollama list | grep deepseek-r1:14b
   ```

## 💡 Tips for Best Results

### 1. Be Specific
```
✅ Good: "open github.com and search for qutebrowser"
❌ Vague: "go to a website"
```

### 2. Break Complex Tasks
```
✅ Good: "open reddit.com in a new tab"
✅ Good: "scroll down to see more posts"
❌ Complex: "browse reddit and find interesting posts"
```

### 3. Provide Context
```
✅ Good: "on the current page, find the search box"
❌ Vague: "find the search box"
```

### 4. Be Patient
- DeepSeek R1 14B is a large model (14B parameters)
- Responses take 2-15 seconds depending on complexity
- Complex workflows may take 10-30 seconds

## 🎨 Advanced Usage

### Using Python Console Directly
```python
# Load agent interface
from ai_agent_tools.agent_interface import agent_interface

# Initialize agent
agent_interface.initialize_agent("deepseek_assistant")

# Ask questions
await agent_interface.ask("open github.com")

# Check status
agent_interface.get_status()

# List profiles
agent_interface.list_profiles()
```

### Creating Custom Workflows
```python
# Multi-step workflow
await agent.ask("""
Please help me research AI tools:
1. Open GitHub in a new tab
2. Search for 'AI browser automation'
3. Open the top 3 repositories
4. Summarize their key features
""")
```

### Error Handling
```python
try:
    response = await agent.ask("open github.com")
    if response.get("success"):
        print("Success:", response["message"])
    else:
        print("Error:", response.get("error"))
except Exception as e:
    print("Exception:", e)
```

## 📊 Available Profiles

| Profile | Model | Provider | Best For |
|---------|-------|----------|----------|
| `deepseek_assistant` | DeepSeek R1 14B | Ollama (local) | **Privacy, complex tasks** |
| `default` | GPT-4 | OpenAI (cloud) | General purpose |
| `research_assistant` | Claude | Anthropic (cloud) | Research tasks |
| `automation_expert` | GPT-4 | OpenAI (cloud) | Workflow automation |
| `local_assistant` | Llama2 | Ollama (local) | Basic local tasks |
| `quick_helper` | GPT-3.5 | OpenAI (cloud) | Fast responses |

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ `:ai-agent-init deepseek_assistant` shows "AI agent initialized"
2. ✅ `:ai-agent-ask "open example.com"` opens the website
3. ✅ Complex queries like "help me research X" work as expected
4. ✅ You see tool execution details in the console

## 🆘 Getting Help

### Built-in Help
```
:ai-agent-help
```

### Check Status
```
:ai-agent-status
```

### Manual Testing
```python
# Test basic functionality
await agent.ask("Hello! Can you help me with browser automation?")

# Test navigation
await agent.ask("open example.com")

# Test complex task
await agent.ask("help me research Python frameworks")
```

---

**🎯 You're now ready to use the most powerful local AI browser assistant!**

The DeepSeek R1 14B model provides excellent reasoning capabilities for complex browser automation tasks while maintaining complete privacy through local processing.
