# AvatarMCP - Windsurf Debug & Fix Guide 🎭

**Timestamp: 2025-08-21 11:45 CET**  
**Status: CRITICAL CONFIGURATION & API ISSUES IDENTIFIED**  
**Priority: URGENT FIX REQUIRED**

## 🚨 **CURRENT FAILURE STATE**

```
Error: No module named avatarmcp.server
Status: Server disconnected  
Command: python -m avatarmcp.server --vrm D:/Dev/repos/avatarmcp/examples/Nekomimi-chan.vrm
Config: Claude Desktop tries to invoke "avatarmcp.server" module
```

---

## 📋 **IDENTIFIED ISSUES**

### **1. INCORRECT CLAUDE DESKTOP CONFIG** ❌

**Issue**: Config references non-existent `avatarmcp.server` module

**Current (BROKEN)**:
```json
"avatarmcp": {
  "command": "python",
  "args": [
    "-m", "avatarmcp.server", 
    "--vrm", "D:/Dev/repos/avatarmcp/examples/Nekomimi-chan.vrm"
  ]
}
```

**Correct Options**:
```json
// Option A: Use main module (RECOMMENDED)
"avatarmcp": {
  "command": "python",
  "args": ["-m", "avatarmcp"],
  "cwd": "D:/Dev/repos/avatarmcp"
}

// Option B: Direct server file path
"avatarmcp": {
  "command": "python", 
  "args": ["D:/Dev/repos/avatarmcp/src/avatarmcp/network/server.py"],
  "cwd": "D:/Dev/repos/avatarmcp"
}

// Option C: Use script entry point (if installed)
"avatarmcp": {
  "command": "avatarmcp"
}
```

### **2. MISSING server.py MODULE** ❌

**Issue**: No `avatarmcp/server.py` file exists, only `avatarmcp/network/server.py`

**Files Found**:
- ✅ `src/avatarmcp/network/server.py` (MAIN SERVER - 44KB)
- ✅ `src/avatarmcp/core/mcp_server.py` (MCP PROTOCOL - 8KB)  
- ✅ `src/avatarmcp/__main__.py` (ENTRY POINT - 3KB)
- ❌ `src/avatarmcp/server.py` (MISSING - what config expects)

### **3. MODULE STRUCTURE MISMATCH** ⚠️

**Issue**: Entry point expects different architecture than what exists

**Current Structure**:
```
src/avatarmcp/
├── __main__.py          # Entry point - loads core.app.AvatarMCP
├── core/
│   ├── app.py          # Main app class - async server
│   └── mcp_server.py   # Custom MCP protocol impl  
└── network/
    └── server.py       # FastMCP 2.10 server with tools (REAL IMPL)
```

**Problem**: `__main__.py` loads `core.app.AvatarMCP` but the real implementation is in `network/server.py`

### **4. DUPLICATE/CONFLICTING SERVER IMPLEMENTATIONS** 🔄

**Issue**: Two different server architectures competing

#### **A. Core-based Server** (`core/app.py` + `core/mcp_server.py`):
- Custom async server using `AvatarMCP` class
- Custom MCP protocol implementation
- No FastMCP 2.10.1 tools registration
- Expects to be invoked via `__main__.py`

#### **B. Network-based Server** (`network/server.py`):
- ✅ FastMCP 2.10.1 compliant 
- ✅ Proper tool registration with `@mcp.tool()`
- ✅ Working VRM loader integration
- ✅ Complete feature set (44KB vs 8KB)
- ❌ Not accessible via standard module invocation

### **5. VRM LOADER DEPENDENCY ISSUES** 🧩

**Issue**: Complex dependency chain with potential import failures

**Found in `network/server.py`**:
```python
# Line 13: Relative import from models
from ..models.vrm_loader import VRMLoader, VRMModel

# Line 16: Relative import from core
from ..core.animation import AnimationController, AnimationClip, AnimationKeyframe

# Line 19: Relative import from current package  
from . import standard_animations
```

**Potential Problems**:
- `standard_animations` module may be missing
- VRM loader dependencies (pygltflib, trimesh, etc.)
- Animation system completeness

### **6. FASTMCP 2.10.1 COMPLIANCE ISSUES** ⚠️

**Issue**: Mixed API patterns and potential deprecation usage

**Found Patterns**:
```python
# Line 137: DEPRECATED @mcp.command() pattern
@mcp.command("load_vrm")
def cmd_load_vrm(file_path: str) -> Dict[str, Any]:

# Line 304: CORRECT @mcp.tool() pattern  
@mcp.tool()
def load_vrm(file_path: str) -> Dict[str, Any]:
```

**Problem**: Using both `@mcp.command()` AND `@mcp.tool()` for same functions

### **7. MISSING/STUB IMPLEMENTATIONS** 🚧

**Potential Stub Files** (need verification):

#### **A. standard_animations Module**:
```python
# Line 19: from . import standard_animations
# Functions: list_standard_animations(), get_standard_animation()
```

#### **B. VRM Dependencies**:
- `pygltflib` - for VRM file parsing
- `trimesh` - for 3D mesh operations  
- `pyvista` - for visualization
- `python-osc` - for VRChat integration

#### **C. Zero-byte Files**:
- `src/avatarmcp/__init__.py` (0 bytes)
- `src/avatarmcp/models/__init__.py` (0 bytes)
- `src/avatarmcp/core/__init__.py` (0 bytes)

### **8. ARGUMENT HANDLING MISMATCH** 📝

**Issue**: Server expects different arguments than config provides

**Config Provides**: `--vrm D:/Dev/repos/avatarmcp/examples/Nekomimi-chan.vrm`  
**Server Expects**: No argument parsing in `main()` function

---

## 🎯 **IMMEDIATE FIX PRIORITY ORDER**

### **Phase 1: Configuration Fix (10 mins)**

1. **Fix Claude Desktop config**:
```json
"avatarmcp": {
  "command": "python",
  "args": ["D:/Dev/repos/avatarmcp/src/avatarmcp/network/server.py"],
  "cwd": "D:/Dev/repos/avatarmcp",
  "env": {
    "PYTHONPATH": "D:/Dev/repos/avatarmcp/src",
    "PYTHONUNBUFFERED": "1"
  }
}
```

### **Phase 2: Module Structure Fix (30 mins)**

2. **Create missing server.py module**:
```python
# src/avatarmcp/server.py
"""Compatibility module for Claude Desktop config."""
from .network.server import main

if __name__ == "__main__":
    main()
```

3. **Fix __main__.py to use correct server**:
```python
# src/avatarmcp/__main__.py  
from .network.server import main

if __name__ == "__main__":
    main()
```

### **Phase 3: API Compliance (20 mins)**

4. **Remove deprecated @mcp.command() decorators**:
   - Keep only `@mcp.tool()` patterns
   - Remove duplicate command registrations
   - Fix registration order in `main()`

5. **Fix missing standard_animations**:
   - Check if `src/avatarmcp/network/standard_animations.py` exists
   - If missing, create stub or remove import

### **Phase 4: Dependencies & Testing (40 mins)**

6. **Verify VRM dependencies**:
```bash
pip install pygltflib trimesh pyvista python-osc
```

7. **Test basic import**:
```bash
cd D:/Dev/repos/avatarmcp
python -c "from src.avatarmcp.network.server import main; print('Import OK')"
```

8. **Test server startup**:
```bash
python src/avatarmcp/network/server.py
# Should start FastMCP stdio server
```

---

## 🧪 **VALIDATION CHECKLIST**

### **Configuration Checks**:
- [ ] Claude Desktop config points to correct server file
- [ ] PYTHONPATH includes src directory  
- [ ] No module path conflicts

### **Module Structure Checks**:
- [ ] `avatarmcp.server` module exists (compatibility)
- [ ] `__main__.py` uses correct server implementation
- [ ] No conflicting server architectures active

### **API Compliance Checks**:
- [ ] Only `@mcp.tool()` decorators used (no `@mcp.command()`)
- [ ] FastMCP 2.10.1 `mcp.run()` pattern (not `run_stdio()`)
- [ ] Proper tool registration order

### **Dependency Checks**:  
- [ ] All VRM processing dependencies installed
- [ ] standard_animations module exists or import removed
- [ ] No missing relative imports

### **Integration Checks**:
- [ ] Module imports successfully: `python -c "import avatarmcp"`
- [ ] Server starts: Direct invocation works
- [ ] Claude Desktop connects successfully
- [ ] Basic tools work (list_models, load_vrm if VRM available)

---

## 🔨 **MOCK DATA & STUBS IDENTIFICATION**

### **High Priority - Verify These Are Real**:

1. **VRMLoader Implementation** (`models/vrm_loader.py` - 47KB):
   ```python
   # CHECK: Does VRMLoader.from_file() actually work?
   # LOOK FOR: Stub methods that just return empty data
   ```

2. **standard_animations Module**:
   ```python
   # CHECK: Does src/avatarmcp/network/standard_animations.py exist?
   # FUNCTIONS: list_standard_animations(), get_standard_animation()
   ```

3. **Animation System** (`core/animation.py` - 25KB):
   ```python
   # CHECK: AnimationController, AnimationClip classes
   # LOOK FOR: Empty play_animation() methods
   ```

### **Medium Priority - Functional Stubs OK**:

4. **VRChat OSC Integration** (`network/osc/`):
   - Can be stubbed for initial testing
   - Real implementation needed for actual avatar control

5. **3D Processing Dependencies**:
   - trimesh, pyvista, pygltflib
   - Can fail gracefully if missing

---

## 🚀 **EXPECTED TIMELINE**

**Total Fix Time**: ~1.5 hours
- **Phase 1 (Config)**: 10 minutes ⚡
- **Phase 2 (Module)**: 30 minutes 🔧  
- **Phase 3 (API)**: 20 minutes 📝
- **Phase 4 (Test)**: 40 minutes ✅

**Success Criteria**: 
- Server starts without import errors
- Claude Desktop successfully connects  
- At least basic tools work (list_models, help commands)
- VRM loading works if dependencies installed

---

## 📚 **CORRECT FASTMCP 2.10.1 PATTERNS**

### **Server Creation & Tools**:
```python
from fastmcp import FastMCP

# Server initialization
mcp = FastMCP(
    name="avatarmcp",
    version="0.1.0", 
    description="MCP server for VRM avatar management"
)

# Tool registration (CORRECT)
@mcp.tool()
def load_vrm(file_path: str) -> Dict[str, Any]:
    # Implementation
    pass

# Command registration (DEPRECATED - Remove)  
@mcp.command("load_vrm")  # ❌ REMOVE THIS
def cmd_load_vrm(file_path: str):
    return load_vrm(file_path)

# Server startup
mcp.run()  # ✅ CORRECT stdio mode
```

### **DEPRECATED Patterns (Remove)**:
```python
# ❌ DEPRECATED:
@mcp.command("tool_name")
mcp.register(function)
mcp.run_stdio()
```

---

## 🎭 **AVATARMCP ARCHITECTURE DECISION**

**Recommendation**: Use `network/server.py` as primary implementation
- ✅ Complete FastMCP 2.10.1 implementation
- ✅ Comprehensive VRM tool set
- ✅ Proper dependency management
- ✅ 44KB vs 8KB (substantial implementation)

**Deprecate**: `core/app.py` custom server architecture
- ❌ Custom MCP protocol (non-standard)
- ❌ Complex async architecture  
- ❌ Not accessible via standard patterns

---

**Tags**: ["avatarmcp", "fastmcp", "fix", "windsurf", "debug", "claude-config", "module-structure"]
