"""DXT build script for AvatarMCP.

This script handles the packaging of AvatarMCP into a DXT package.
"""

import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, List

# Package information
PACKAGE_NAME = "avatarmcp"
VERSION = "0.1.0"
DIST_DIR = Path("dist")
DIST_DIR.mkdir(exist_ok=True)

# Source directories
SRC_DIR = Path("src") / PACKAGE_NAME

# Files to include in the package
PACKAGE_FILES = [
    "__init__.py",
    "__main__.py",
    "server.py",
    "service.py",
    "vrm_loader.py",
    "animation.py",
]

def validate_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Validate the DXT manifest file.
    
    Args:
        manifest_path: Path to the manifest file
        
    Returns:
        The parsed manifest as a dictionary
        
    Raises:
        ValueError: If the manifest is invalid
    """
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Check required fields
        required_fields = ["name", "version", "display_name", "description", "server", "tools"]
        for field in required_fields:
            if field not in manifest:
                raise ValueError(f"Missing required field in manifest: {field}")
        
        # Ensure server configuration is valid
        server = manifest["server"]
        if "command" not in server or not isinstance(server["command"], list):
            raise ValueError("Invalid or missing 'command' in server configuration")
        
        # Ensure tools are properly defined
        tools = manifest.get("tools", [])
        if not isinstance(tools, list):
            raise ValueError("'tools' must be a list")
            
        for tool in tools:
            if not all(key in tool for key in ["name", "description", "parameters"]):
                raise ValueError("Each tool must have 'name', 'description', and 'parameters'")
        
        return manifest
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in manifest: {e}")

def copy_required_files(temp_dir: Path) -> None:
    """Copy required files to the temporary directory.
    
    Args:
        temp_dir: Temporary directory to copy files to
    """
    # Create package directory
    pkg_dir = temp_dir / PACKAGE_NAME
    pkg_dir.mkdir(exist_ok=True, parents=True)
    
    # Copy Python package files
    for file_name in PACKAGE_FILES:
        src_path = SRC_DIR / file_name
        if src_path.exists():
            shutil.copy2(src_path, pkg_dir / file_name)
            print(f"Copied {src_path} to {pkg_dir / file_name}")
    
    # Copy the manifest file
    shutil.copy2("dxt_manifest.json", temp_dir / "dxt_manifest.json")
    print("Copied dxt_manifest.json")
    
    # Create __init__.py if it doesn't exist
    if not (pkg_dir / "__init__.py").exists():
        (pkg_dir / "__init__.py").write_text("# AvatarMCP package\n")
        print("Created empty __init__.py")
    
    # Create a simple README if it doesn't exist
    if not (temp_dir / "README.md").exists():
        (temp_dir / "README.md").write_text("# AvatarMCP\n\nMCP server for managing and animating VRM avatars.\n")
        print("Created README.md")

def create_dxt_package() -> bool:
    """Create the DXT package.
    # Validate the manifest first
    manifest = validate_manifest(Path("dxt_manifest.json"))
    version = manifest.get("version", VERSION)
    
    # Create temporary directory for packaging
    temp_dir = Path("dist") / f"{PACKAGE_NAME}-{version}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    try:
        # Copy required files
        copy_required_files(temp_dir)
        
        # Create the zip archive
        output_file = DIST_DIR / f"{PACKAGE_NAME}-{version}.dxt"
        if output_file.exists():
            output_file.unlink()
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Successfully created DXT package: {output_file}")
        return True
    
    except Exception as e:
        print(f"Error creating DXT package: {e}", file=sys.stderr)
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    if create_dxt_package():
        sys.exit(0)
    else:
        sys.exit(1)
