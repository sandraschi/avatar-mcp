"""Script to reorganize the AvatarMCP codebase into a more structured layout."""
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent / "src" / "avatarmcp"

# Mapping of files to their new locations
FILE_MAPPING = {
    # AI/ML related files
    "ai_npc.py": "ai/npc_controller.py",
    "speech.py": "ai/speech.py",
    "vision.py": "ai/vision.py",
    
    # Core application files
    "app.py": "core/app.py",
    "animation.py": "core/animation.py",
    
    # Commands
    "commands/animation_commands.py": "core/commands/animation_commands.py",
    "commands/help_commands.py": "core/commands/help_commands.py",
    "commands/model_commands.py": "core/commands/model_commands.py",
    "commands/__init__.py": "core/commands/__init__.py",
    
    # Model related files
    "models/vrm_model.py": "models/vrm_model.py",
    "models/animation_controller.py": "models/animation_controller.py",
    "vrm_loader.py": "models/vrm_loader.py",
    "vrm_manager.py": "models/vrm_manager.py",
    "model_manager.py": "models/model_manager.py",
    "standard_animations.py": "models/standard_animations.py",
    
    # Network related files
    "server.py": "network/server.py",
    "api.py": "network/api.py",
    "osc_server.py": "network/osc/server.py",
    "osc_tools.py": "network/osc/tools.py",
    "oscmcp_integration.py": "network/mcp/integration.py",
    
    # Interface files
    "cli.py": "interfaces/cli.py",
    "service.py": "interfaces/service.py",
    
    # Help system
    "help_system.py": "core/help_system.py",
    "mcp_help.py": "core/mcp_help.py",
}

def create_init_files():
    """Create __init__.py files in all new directories."""
    dirs = {
        "ai", "core", "core/commands", "models", 
        "network", "network/osc", "network/mcp", 
        "interfaces", "utils"
    }
    
    for dir_name in dirs:
        init_file = BASE_DIR / dir_name / "__init__.py"
        init_file.parent.mkdir(parents=True, exist_ok=True)
        if not init_file.exists():
            init_file.touch()

def move_files():
    """Move files to their new locations."""
    # Create all necessary directories first
    for src, dst in FILE_MAPPING.items():
        src_path = BASE_DIR / src
        dst_path = BASE_DIR / dst
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        if src_path.exists():
            print(f"Moving {src} to {dst}")
            shutil.move(str(src_path), str(dst_path))
        else:
            print(f"Warning: Source file not found: {src}")

def main():
    print("Reorganizing AvatarMCP codebase...")
    print("Creating directory structure...")
    create_init_files()
    
    print("Moving files...")
    move_files()
    
    print("\nReorganization complete!")
    print("Note: You'll need to update the import statements in the moved files.")

if __name__ == "__main__":
    main()
