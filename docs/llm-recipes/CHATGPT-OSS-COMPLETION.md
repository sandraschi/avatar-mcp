# ChatGPT-OSS Implementation Recipe for AvatarMCP

**Model**: ChatGPT-OSS 20B  
**Performance**: ⭐⭐⭐⭐ (Very Good)  
**Thinking Time**: ~3 minutes initial, then fast execution  
**Best For**: Complex implementation tasks, architectural understanding  

## 🎯 **Optimal Usage Pattern**

### **Initial Prompt Strategy**
The model needs substantial context upfront but then performs excellently. Key pattern:

1. **Long Context Setup** - Provide comprehensive background
2. **Wait for "Thinking Phase"** - Model takes ~3 minutes to process
3. **Fast Execution Phase** - Once started, output is rapid and high-quality

### **Recommended Prompt Structure**

```markdown
# AvatarMCP VRM Loader Implementation

## Project Context
- FastMCP 2.10.1+ compliant server for VRM avatar management
- Current repo structure: [detailed file tree]
- Architecture: VRMLoader -> AvatarService -> MCPServer
- Dependencies: pygltflib, trimesh, numpy, fastmcp

## Current Status
[Paste current implementation status from analysis]

## Specific Task
Implement the VRMLoader.from_file() method in src/avatarmcp/vrm_loader.py
Lines 85-120 need actual GLB/VRM parsing implementation.

## Requirements
- Parse GLB files with pygltflib
- Extract mesh data with trimesh
- Build bone hierarchy from GLTF nodes
- Extract blend shapes from morph targets
- Handle VRM 2.0 extensions

## Code Context
[Paste current VRMLoader class structure]

Please implement the missing from_file() method with proper error handling.
```

## 🔧 **Implementation Recipe**

### **Phase 1: Context Loading (3-5 minutes)**
```
User: [Comprehensive context as above]
Model: [Thinking... processing context... understanding architecture...]
```

**Wait Pattern**: Model shows thinking indicators, don't interrupt. This preparation phase is critical for quality output.

### **Phase 2: Rapid Implementation (5-10 minutes)**
Once thinking completes, the model produces:
- ✅ Well-structured code implementations
- ✅ Proper error handling patterns
- ✅ Type annotations and documentation
- ✅ Integration with existing architecture

### **Phase 3: Refinement Prompts**
Follow-up prompts work quickly:
```
"Add VRM 2.0 extension parsing"
"Include blend shape weight extraction"
"Add material and texture loading"
```

## 📊 **Performance Characteristics**

### **Strengths**
- **Architectural Understanding**: Grasps complex project structure quickly
- **Code Quality**: Produces production-ready implementations
- **Error Handling**: Good at anticipating edge cases
- **Integration**: Maintains consistency with existing patterns
- **Documentation**: Includes helpful comments and docstrings

### **Timing Breakdown**
- **Context Processing**: 2-3 minutes (thinking phase)
- **Initial Implementation**: 3-5 minutes (fast output)
- **Refinements**: 30-60 seconds each
- **Total Session**: 15-20 minutes for complete feature

### **Best Results When**
- ✅ Given comprehensive project context upfront
- ✅ Allowed full thinking time before expecting output
- ✅ Asked for complete implementations (not fragments)
- ✅ Provided with existing code patterns to follow

### **Avoid**
- ❌ Interrupting during thinking phase
- ❌ Asking for quick snippets without context
- ❌ Switching contexts rapidly
- ❌ Expecting immediate responses

## 🎯 **AvatarMCP Specific Recipe**

### **VRM Loading Implementation Session**
```markdown
Context Setup:
1. Project overview and architecture
2. Current vrm_loader.py structure
3. Target functionality requirements
4. Integration points with service.py

Thinking Phase (3 min):
- Model processes VRM/GLB format requirements
- Understands pygltflib integration patterns
- Plans bone hierarchy extraction approach

Implementation Phase (5 min):
- Complete from_file() method
- Proper error handling
- Type annotations
- Integration patterns

Refinement Phase (2-3 iterations):
- Add VRM-specific extensions
- Enhance material loading
- Optimize mesh processing
```

### **Expected Output Quality**
The model typically produces:

```python
@classmethod
def from_file(cls, file_path: Union[str, Path]) -> VRMModel:
    """Load a VRM model from file with comprehensive parsing."""
    try:
        path = Path(file_path).resolve()
        
        # Validate file
        if not path.exists():
            raise FileNotFoundError(f"VRM file not found: {path}")
        
        # Load with pygltflib
        gltf = GLTF2.load(path)
        
        # [Full implementation with proper error handling]
        
    except Exception as e:
        logger.error(f"Failed to load VRM: {e}")
        raise
```

## 🎯 **Session Management Tips**

### **Optimal Session Structure**
1. **Single Long Context** (better than multiple short prompts)
2. **Wait for Thinking** (quality over speed)
3. **Complete Features** (rather than fragments)
4. **Iterative Refinement** (quick follow-ups work well)

### **Context Refresh Signals**
Refresh context when model starts:
- Losing track of project structure
- Producing inconsistent patterns
- Asking for information already provided

### **Quality Indicators**
Good session when model:
- ✅ References existing class structures correctly
- ✅ Maintains consistent naming conventions
- ✅ Includes proper imports and dependencies
- ✅ Adds appropriate error handling
- ✅ Follows established patterns

## 🎯 **Example Success Session**

**Input**: [Comprehensive AvatarMCP context + VRM loading requirements]
**Thinking**: 3 minutes processing
**Output**: Complete VRMLoader.from_file() implementation with:
- Proper GLB parsing with pygltflib
- Mesh extraction with trimesh
- Bone hierarchy building
- Blend shape extraction
- VRM extension handling
- Error handling and logging
- Type annotations

**Follow-up**: "Add material and texture loading"
**Response Time**: 45 seconds
**Quality**: Consistent with initial implementation

## 📝 **Recipe Summary**

**For AvatarMCP development with ChatGPT-OSS 20B:**

1. **Front-load context** - Provide complete project understanding
2. **Allow thinking time** - 3+ minutes for complex tasks
3. **Expect quality** - Output is typically production-ready
4. **Iterate quickly** - Follow-up prompts are fast
5. **Stay in context** - Avoid switching topics mid-session

**Result**: High-quality implementations that integrate well with existing codebase and require minimal refactoring.

---

*Recipe validated on AvatarMCP VRM loading implementation task - August 2025*
