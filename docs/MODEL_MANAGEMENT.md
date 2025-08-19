# Model Management System

This document describes the model management system in AvatarMCP, which provides efficient loading, caching, and resource management for VRM models.

## Overview

The model management system is built around the `VRMModelManager` class, which provides:

- **LRU Caching**: Automatic caching of loaded models with configurable size limits
- **Resource Management**: Automatic cleanup of unused models to free memory
- **Validation**: Built-in VRM file validation
- **Performance Metrics**: Tracking of load times, cache hits, and memory usage

## Core Components

### VRMModelManager

The main class that manages model loading and caching:

```python
from avatarmcp import VRMModelManager

# Create a model manager with a maximum of 5 cached models
model_manager = VRMModelManager(max_cache_size=5)

# Load a model (will be cached for future use)
model = model_manager.load_model("path/to/model.vrm")

# Get cache statistics
cache_info = model_manager.get_cache_info()
```

### AvatarService Integration

The `AvatarService` class has been updated to work with the model manager:

```python
from avatarmcp import AvatarService

# Create a service with the default model manager
service = AvatarService()

# Load an avatar (will use the model manager internally)
avatar_id = "my_avatar"
metadata = service.load_vrm("path/to/model.vrm", avatar_id=avatar_id)

# Unload an avatar and remove it from the cache
service.unload_avatar(avatar_id, remove_from_cache=True)

# Get cache information
cache_info = service.get_cache_info()
```

## Features

### Model Caching

- Models are cached in memory for fast access
- Least Recently Used (LRU) eviction policy when cache is full
- Configurable maximum cache size

### Validation

```python
from avatarmcp import validate_vrm_file

# Validate a VRM file
is_valid, issues = validate_vrm_file("path/to/model.vrm")
if is_valid:
    print("Model is valid!")
else:
    print("Validation issues:", issues)
```

### Resource Management

- Automatic cleanup of unused models
- Manual cache control methods:
  - `clear_cache()`: Remove all models from the cache
  - `unload_model(file_path)`: Remove a specific model

## Performance Considerations

- **Memory Usage**: Each cached model consumes memory. Adjust `max_cache_size` based on available RAM.
- **File Monitoring**: The system detects when source files change and will automatically reload them.
- **Thread Safety**: The model manager is thread-safe and can be used from multiple threads.

## Best Practices

1. **Reuse Model Instances**: Always try to reuse loaded models instead of loading the same file multiple times.
2. **Monitor Cache Hit Rate**: Use `get_cache_info()` to monitor cache performance.
3. **Clean Up**: Explicitly unload models when they're no longer needed to free up memory.
4. **Validate Early**: Validate VRM files before attempting to load them for better error handling.

## Example Workflow

```python
from avatarmcp import AvatarService, validate_vrm_file

# Initialize
service = AvatarService()

# Validate before loading
is_valid, issues = validate_vrm_file("character.vrm")
if not is_valid:
    print("Validation failed:", issues)
    exit(1)

# Load the model
avatar_id = "main_character"
metadata = service.load_vrm("character.vrm", avatar_id=avatar_id)
print(f"Loaded {metadata['mesh_count']} meshes")

# Use the model...

# Clean up when done
service.unload_avatar(avatar_id, remove_from_cache=True)
```

## Troubleshooting

### Common Issues

1. **Memory Leaks**: Ensure you're properly unloading models when they're no longer needed.
2. **File Permissions**: Make sure the application has read access to the VRM files.
3. **Corrupt Files**: Always validate VRM files before loading them.

### Getting Help

For issues not covered here, please file an issue on the GitHub repository with:
- The VRM file (if possible)
- The exact error message
- Steps to reproduce the issue
