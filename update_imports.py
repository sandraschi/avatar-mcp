"""Script to update imports after reorganizing the codebase."""

import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent / "src" / "avatarmcp"

# Mapping of old import paths to new ones
IMPORT_MAPPING = {
    # Old pattern: new pattern
    r"from \.commands\.": "from .core.commands.",
    r"from \.models\.": "from ..models.",
    r"from \.utils\.": "from ..utils.",
    r"from \.animation import": "from ..core.animation import",
    r"from \.app import": "from ..core.app import",
    r"from \.vrm_loader import": "from ..models.vrm_loader import",
    r"from \.vrm_manager import": "from ..models.vrm_manager import",
    r"from \.model_manager import": "from ..models.model_manager import",
    r"from \.animation_controller import": "from ..models.animation_controller import",
    r"from \.speech import": "from ..ai.speech import",
    r"from \.vision import": "from ..ai.vision import",
    r"from \.ai_npc import": "from ..ai.npc_controller import",
    r"from \.server import": "from ..network.server import",
    r"from \.api import": "from ..network.api import",
    r"from \.osc_server import": "from ..network.osc.server import",
    r"from \.osc_tools import": "from ..network.osc.tools import",
    r"from \.oscmcp_integration import": "from ..network.mcp.integration import",
    r"from \.cli import": "from ..interfaces.cli import",
    r"from \.service import": "from ..interfaces.service import",
    r"from \.help_system import": "from ..core.help_system import",
    r"from \.mcp_help import": "from ..core.mcp_help import",
}


def update_file_imports(file_path: Path):
    """Update imports in a single file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        updated = False

        for old_pattern, new_pattern in IMPORT_MAPPING.items():
            if re.search(old_pattern, content):
                content, count = re.subn(old_pattern, new_pattern, content)
                if count > 0:
                    updated = True
                    print(
                        f"  Updated {count} import(s) in {file_path.relative_to(BASE_DIR.parent.parent)}"
                    )

        if updated:
            file_path.write_text(content, encoding="utf-8")

    except Exception as e:
        print(f"  Error processing {file_path}: {e}")


def main():
    print("Updating imports in Python files...")

    # Process all Python files in the source directory
    for py_file in BASE_DIR.rglob("*.py"):
        # Skip __pycache__ and other special directories
        if "__pycache__" in str(py_file) or ".pytest_cache" in str(py_file):
            continue

        print(f"Processing {py_file.relative_to(BASE_DIR.parent.parent)}...")
        update_file_imports(py_file)

    print("\nImport updates complete!")
    print("Note: You may need to manually verify some imports, especially relative imports.")


if __name__ == "__main__":
    main()
