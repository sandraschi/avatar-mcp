# AvatarMCP Server Startup Fix Guide 🔧

**Date:** 2025-08-20  
**Issue:** Critical import error preventing server startup  
**Status:** ❌ Blocking - Server cannot start

## Problem Summary

AvatarMCP MCP server fails to start with import error:
```
ImportError: cannot import name 'BufferViewFormat' from 'pygltflib'
```

## Root Cause Analysis

### Primary Issue
- **Location:** `src/avatarmcp/vrm_loader.py` line 17
- **Problem:** Importing non-existent `BufferViewFormat` class from pygltflib
- **Impact:** Server process exits immediately after attempting to load module

### Import Statement (BROKEN):
```python
from pygltflib import GLTF2, BufferFormat, BufferViewFormat, BufferViewTarget, AccessorType, ComponentType
```

### Error Pattern:
1. ✅ Server starts and connects successfully  
2. ✅ MCP protocol initialization works
3. ❌ Import fails when loading avatarmcp module
4. ❌ Server process exits with ENOENT error

## Quick Fix Options

### Option 1: Fix Import Statement (RECOMMENDED)
Replace the broken import with correct pygltflib API:

```python
# BEFORE (BROKEN):
from pygltflib import GLTF2, BufferFormat, BufferViewFormat, BufferViewTarget, AccessorType, ComponentType

# AFTER (FIXED):
from pygltflib import GLTF2, BufferFormat, BufferViewTarget, AccessorType, ComponentType
# Remove BufferViewFormat - use BufferFormat instead
```

### Option 2: Check pygltflib Version Compatibility
```powershell
# Check current version
python -c "import pygltflib; print(pygltflib.__version__)"

# Check available classes
python -c "import pygltflib; print(dir(pygltflib))"
```

### Option 3: Restore Missing File
The `vrm_loader.py` file may be missing. Check if backup exists:
```powershell
# From avatarmcp root directory
Get-ChildItem -Path "src\avatarmcp" -Name "*.backup"
# If vrm_loader.py.backup exists, restore it and fix imports
```

## Step-by-Step Fix Process

### 1. Investigate Current State
```powershell
# Navigate to avatarmcp project
Set-Location "D:\Dev\repos\avatarmcp"

# Check if vrm_loader.py exists
Test-Path "src\avatarmcp\vrm_loader.py"

# List source files
Get-ChildItem "src\avatarmcp" -Filter "*.py"
```

### 2. Check pygltflib API
```powershell
# Test pygltflib imports
python -c "from pygltflib import GLTF2, BufferFormat, AccessorType, ComponentType; print('Basic imports OK')"

# Try the problematic import
python -c "from pygltflib import BufferViewFormat" 2>&1
```

### 3. Fix the Import (if file exists)
```powershell
# Edit vrm_loader.py and fix the import statement
# Replace BufferViewFormat with BufferFormat or remove if not needed
```

### 4. Test Module Loading
```powershell
# Test avatarmcp module can import
python -c "import avatarmcp; print('Module loads successfully')"

# Test server module specifically  
python -c "from avatarmcp import server; print('Server module OK')"
```

### 5. Test MCP Server Startup
```powershell
# Try starting server manually
python -m avatarmcp.server --vrm "examples\Nekomimi-chan.vrm"
```

## Alternative Workarounds

### Temporary Disable VRM Loading
If vrm_loader.py is causing issues, temporarily comment out VRM-related imports in `__init__.py`:

```python
# Comment out problematic imports temporarily
# from .vrm_loader import VRMModel, VRMBone, VRMBlendShape, VRMMaterial, VRMTexture
```

### Dependency Rollback
If pygltflib API changed, consider rolling back to compatible version:
```powershell
pip install pygltflib==2.15.1  # or whatever version was working
```

## Expected Success Indicators

### Working Server Startup:
```
✅ FastMCP 2.10+ stdio protocol
✅ Server name: avatarmcp  
✅ Transport: STDIO
✅ Tools loaded: help_avatarmcp, load_vrm, unload_vrm, play_animation, stop_animation, set_blend_shape, list_models
```

### Claude Desktop Integration:
- Server appears in MCP tools list
- No "Server disconnected" errors in logs
- Tools are callable from Claude interface

## Common Pitfalls

1. **Missing cwd in config**: Config missing `"cwd": "D:/Dev/repos/avatarmcp"`
2. **Python path issues**: Module not found due to wrong Python environment  
3. **Dependency conflicts**: Incompatible pygltflib version with existing code
4. **File organization**: Recent reorganization may have broken relative imports

## Validation Commands

```powershell
# Test complete stack
python -c "
import avatarmcp
from avatarmcp.server import app
print('✅ AvatarMCP server imports successfully')
"

# Verify MCP tools
python -m avatarmcp.server --help
```

## Emergency Rollback

If fixes don't work, rollback to last working state:
```powershell
# Check git log for last working commit
git log --oneline -10

# Rollback if needed
git checkout <working-commit-hash>
```

---

## Notes for Windsurf IDE

- Open `src/avatarmcp/vrm_loader.py` (or create if missing)
- Focus on line 17 with the problematic import
- Use Windsurf's Python support to validate imports
- Test with integrated terminal before committing changes

**Priority**: 🎯 **CRITICAL** - Blocks all AvatarMCP functionality