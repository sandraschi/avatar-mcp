# 🔍 Claude Desktop MCP Server Debugging Guide

**The Mystery of "Server Starts, Then Dies"**  
**Real-World Debugging Experience**

---

## 🎭 The Mysterious Behavior

### **What Users Experience**

You see this pattern in Claude Desktop logs:
```
2025-09-19T19:52:08.612Z [your-server] [info] Server started and connected successfully
2025-09-19T19:52:08.760Z [your-server] [info] Message from client: {"method":"initialize"...}
[... normal operation for 5-10 seconds ...]
2025-09-19 21:52:13,700 - your_server - INFO - Kill argument received - exiting gracefully  
2025-09-19T19:52:14.266Z [your-server] [info] Server transport closed
2025-09-19T19:52:14.266Z [your-server] [error] Server disconnected
```

### **What Users Think**
- "Claude is randomly killing my server!"
- "The connection is unstable!"  
- "Something is wrong with my Claude Desktop installation!"

### **The Reality**
**Claude Desktop NEVER randomly kills servers.** The `--kill` signal is always a response to the server crashing or becoming unresponsive during normal operation.

---

## 🕵️ The Investigation Process

### **Step 1: Understanding the Timeline**

```
T+0s:    Server process starts
T+0.1s:  Claude Desktop connects via STDIO
T+0.2s:  Initial handshake (method: "initialize")
T+0.3s:  Claude Desktop requests tool list (method: "tools/list")  ← **CRITICAL MOMENT**
T+0.5s:  Tool discovery and validation happens
T+?s:    Something crashes during tool loading/validation
T+5-10s: Claude Desktop detects server is unresponsive
T+10s:   Claude Desktop sends --kill to cleanup zombie process
```

**The crash usually happens at the "CRITICAL MOMENT" - during tool discovery.**

### **Step 2: The Real Culprits**

#### **Culprit #1: Import Errors in Tool Functions**
```python
@app.tool()
async def my_tool():
    from missing_module import function  # ❌ CRASH HERE!
    return {"result": "ok"}
```

**What happens**:
1. ✅ Server starts (imports are fine at startup)
2. ✅ Claude connects
3. ❌ Claude requests tool list → Python tries to import `missing_module`
4. ❌ ImportError → Server crashes
5. ❌ Claude detects crash → sends `--kill`

#### **Culprit #2: Configuration Validation Errors**
```python
@app.tool()
async def my_tool():
    config = MyConfig()  # ❌ CRASH HERE! Missing required fields
    return {"result": "ok"}
```

**What happens**:
1. ✅ Server starts (no config loaded yet)
2. ✅ Claude connects
3. ❌ Tool execution triggers config validation
4. ❌ Pydantic validation fails → unhandled exception
5. ❌ Server crashes → Claude sends `--kill`

#### **Culprit #3: Missing Dependencies**
```python
@app.tool()
async def my_tool():
    import requests  # ❌ CRASH HERE! Package not installed
    return {"result": "ok"}
```

---

## 🔍 **Step-by-Step Debugging Process**

### **Phase 1: Log File Analysis**

#### **Windows Log Location**
```
%APPDATA%\Claude\logs\
```

#### **Linux/Mac Log Location**
```
~/.config/claude-desktop/logs/
```

#### **What to Look For**
1. **Last successful operation** before disconnect
2. **Import errors** in stderr output
3. **Validation errors** from Pydantic
4. **Missing dependency** errors

### **Phase 2: Minimal Reproduction Test**

Create a minimal server to isolate the issue:

```python
from fastmcp import FastMCP

app = FastMCP("debug-server")

@app.tool()
async def hello_world() -> dict:
    """Simple test tool."""
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run()
```

**Test this first**. If it works, the issue is in your tool implementations.

### **Phase 3: Gradual Complexity Addition**

Add tools one by one to identify the problematic one:

```python
# Step 1: Basic tool
@app.tool()
async def test_tool() -> dict:
    return {"status": "working"}

# Step 2: Add imports
@app.tool()
async def import_test() -> dict:
    import os  # Safe import
    return {"status": "imports work"}

# Step 3: Add your actual logic
@app.tool()
async def real_tool() -> dict:
    # Your actual implementation
    return {"result": "success"}
```

### **Phase 4: Comprehensive Logging**

Add detailed logging to catch issues:

```python
import logging
import sys

# Setup logging to stderr (appears in Claude Desktop logs)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

@app.tool()
async def debug_tool() -> dict:
    try:
        logger.info("Tool starting...")
        
        # Your tool logic here
        result = await some_operation()
        
        logger.info("Tool completed successfully")
        return {"status": "success", "result": result}
        
    except Exception as e:
        logger.error(f"Tool failed: {e}", exc_info=True)
        raise  # Re-raise to see the full traceback
```

---

## 🚨 **Common Error Patterns & Solutions**

### **Pattern 1: Import Errors**

#### **Error Message**
```
ImportError: No module named 'missing_module'
```

#### **Root Cause**
```python
@app.tool()
async def my_tool():
    from missing_module import function  # ❌ Import inside tool
    return {"result": "ok"}
```

#### **✅ Solution**
```python
# Move imports to module level
from missing_module import function

@app.tool()
async def my_tool():
    return {"result": function()}  # ✅ Use imported function
```

### **Pattern 2: Configuration Validation Errors**

#### **Error Message**
```
pydantic.error_wrappers.ValidationError: 1 validation error for MyConfig
field_name
  field required (type=value_error.missing)
```

#### **Root Cause**
```python
class MyConfig(BaseModel):
    field_name: str  # Required field

@app.tool()
async def my_tool():
    config = MyConfig()  # ❌ Missing required field
    return {"result": "ok"}
```

#### **✅ Solution**
```python
@app.tool()
async def my_tool():
    config = MyConfig(field_name="default_value")  # ✅ Provide required field
    return {"result": "ok"}
```

### **Pattern 3: Missing Dependencies**

#### **Error Message**
```
ModuleNotFoundError: No module named 'requests'
```

#### **Root Cause**
```python
@app.tool()
async def my_tool():
    import requests  # ❌ Package not installed
    return {"result": "ok"}
```

#### **✅ Solution**
```bash
# Install missing dependency
pip install requests
```

### **Pattern 4: Async/Await Issues**

#### **Error Message**
```
RuntimeError: coroutine was never awaited
```

#### **Root Cause**
```python
@app.tool()
async def my_tool():
    result = some_async_function()  # ❌ Missing await
    return {"result": result}
```

#### **✅ Solution**
```python
@app.tool()
async def my_tool():
    result = await some_async_function()  # ✅ Add await
    return {"result": result}
```

---

## 🔧 **Advanced Debugging Techniques**

### **Technique 1: Tool Registration Testing**

```python
def test_tool_registration():
    """Test that all tools can be imported without errors."""
    try:
        # Import all your tool modules
        from .tools import tool1, tool2, tool3
        logger.info("All tool modules imported successfully")
        
        # Test that required dependencies are available
        import aiohttp
        import pydantic
        logger.info("All dependencies available")
        
    except Exception as e:
        logger.error(f"Tool registration test failed: {e}", exc_info=True)
        raise

# Call this before app.run()
if __name__ == "__main__":
    test_tool_registration()
    app.run()
```

### **Technique 2: Environment Validation**

```python
def validate_environment():
    """Validate that the environment is properly configured."""
    import os
    import sys
    
    # Check Python version
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10+ required")
    
    # Check required environment variables
    required_vars = ["API_KEY", "CONFIG_PATH"]
    for var in required_vars:
        if not os.getenv(var):
            raise RuntimeError(f"Required environment variable {var} not set")
    
    logger.info("Environment validation passed")

if __name__ == "__main__":
    validate_environment()
    app.run()
```

### **Technique 3: Graceful Error Handling**

```python
@app.tool()
async def robust_tool(param: str) -> dict:
    """Tool with comprehensive error handling."""
    try:
        # Validate input
        if not param:
            return {"error": "Parameter cannot be empty"}
        
        # Your tool logic
        result = await some_operation(param)
        
        return {"success": True, "result": result}
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return {"error": f"Invalid input: {e}"}
        
    except aiohttp.ClientError as e:
        logger.error(f"Network error: {e}")
        return {"error": f"Network error: {e}"}
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {"error": "Internal server error"}
```

---

## 📊 **Log Analysis Checklist**

### **What to Check in Logs**

- [ ] **Server startup**: Does the server start successfully?
- [ ] **Claude connection**: Does Claude Desktop connect?
- [ ] **Tool discovery**: Does tool listing work?
- [ ] **Tool execution**: Do tools execute without errors?
- [ ] **Error messages**: Any exceptions or errors?
- [ ] **Timing**: When exactly does the crash occur?

### **Log Patterns to Watch For**

#### **✅ Healthy Pattern**
```
[info] Server started and connected successfully
[info] Message from client: {"method":"initialize"...}
[info] Message from client: {"method":"tools/list"...}
[info] Tool execution successful
```

#### **❌ Problematic Pattern**
```
[info] Server started and connected successfully
[info] Message from client: {"method":"initialize"...}
[error] ImportError: No module named 'missing_module'
[info] Kill argument received - exiting gracefully
```

---

## 🎯 **Prevention Strategies**

### **Strategy 1: Comprehensive Testing**

```python
# Add this test function
async def test_all_tools():
    """Test that all tools can be called without errors."""
    test_cases = [
        ("hello_world", {}),
        ("test_tool", {"param": "test"}),
    ]
    
    for tool_name, params in test_cases:
        try:
            # Get the tool function
            tool_func = globals()[tool_name]
            result = await tool_func(**params)
            logger.info(f"✅ {tool_name}: {result}")
        except Exception as e:
            logger.error(f"❌ {tool_name}: {e}")
            raise

# Run tests before starting server
if __name__ == "__main__":
    asyncio.run(test_all_tools())
    app.run()
```

### **Strategy 2: Dependency Management**

```python
# requirements.txt
fastmcp>=2.12.0
aiohttp>=3.8.0
pydantic>=2.0.0
# Add all your dependencies here
```

### **Strategy 3: Configuration Validation**

```python
def validate_config():
    """Validate configuration before starting server."""
    try:
        config = MyConfig()
        logger.info("Configuration validation passed")
        return config
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

if __name__ == "__main__":
    config = validate_config()
    app.run()
```

---

## 🏆 **Success Indicators**

### **✅ Your Server is Working When:**

1. **Logs show successful startup**
2. **Tools appear in Claude Desktop**
3. **Tools execute without errors**
4. **No "kill" messages in logs**
5. **Server stays connected indefinitely**

### **❌ Your Server Has Issues When:**

1. **"Kill argument received" appears**
2. **Tools don't appear in Claude Desktop**
3. **Import errors in logs**
4. **Validation errors in logs**
5. **Server disconnects after a few seconds**

---

## 🎯 **Final Debugging Checklist**

- [ ] **Check log files** for error messages
- [ ] **Test minimal server** first
- [ ] **Add tools gradually** to isolate issues
- [ ] **Validate all imports** are at module level
- [ ] **Check configuration** has all required fields
- [ ] **Install all dependencies** from requirements.txt
- [ ] **Add comprehensive logging** to catch issues
- [ ] **Test tool execution** before deployment

**Remember**: Claude Desktop doesn't kill servers randomly. It kills them because they crash during normal operation. The key is to identify and fix the root cause of the crash. 🔧✨
