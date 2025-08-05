"""DXT build script for AvatarMCP.

This script handles the packaging of AvatarMCP into a DXT package.
"""

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any

# Package information
PACKAGE_NAME = "avatarmcp"
VERSION = "0.1.0"
DIST_DIR = Path("dist")
DIST_DIR.mkdir(exist_ok=True)

def validate_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Validate the DXT manifest file."""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Check required fields
        required_fields = ["name", "version", "display_name", "description", "server"]
        for field in required_fields:
            if field not in manifest:
                raise ValueError(f"Missing required field in manifest: {field}")
        
        # Ensure server configuration is valid
        server = manifest["server"]
        if "command" not in server or not isinstance(server["command"], list):
            raise ValueError("Invalid or missing 'command' in server configuration")
        
        return manifest
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in manifest: {e}")

def copy_required_files(temp_dir: Path):
    """Copy required files to the temporary directory."""
    # Create necessary directories
    (temp_dir / PACKAGE_NAME).mkdir(exist_ok=True)
    
    # Copy Python package files
    files_to_copy = [
        "__init__.py",
        "service.py",
        "models.py",
        "vrm_loader.py"
    ]
    
    for file in files_to_copy:
        src = Path(file)
        if src.exists():
            shutil.copy2(src, temp_dir / PACKAGE_NAME / src.name)
    
    # Copy the manifest
    shutil.copy2("dxt_manifest.json", temp_dir)
    
    # Create __init__.py if it doesn't exist
    init_file = temp_dir / PACKAGE_NAME / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# AvatarMCP package\n")

def create_dxt_package():
    """Create the DXT package."""
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
