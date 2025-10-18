#!/usr/bin/env python3
"""
SOTA CI Template Setup Script

This script helps you set up a modern CI workflow for your Python project
using the state-of-the-art template.

Usage:
    python setup_sota_ci.py --project-name myproject --package-name src/mypackage
"""

import argparse
import os
import re
import sys
from pathlib import Path


def replace_placeholders(content: str, replacements: dict) -> str:
    """Replace template placeholders with actual values."""
    for placeholder, value in replacements.items():
        content = content.replace(f"{{{{{placeholder}}}}}", value)
    return content


def setup_ci_workflow(project_name: str, package_name: str, min_python: str = "3.10"):
    """Set up the CI workflow."""
    template_path = Path(".github/templates/ci-workflow.yml")
    output_path = Path(".github/workflows/ci.yml")
    
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return False
    
    # Create .github/workflows directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace placeholders
    replacements = {
        "PROJECT_NAME": project_name,
        "PACKAGE_NAME": package_name,
        "MIN_PYTHON_VERSION": min_python,
        "PYTHON_MATRIX": f'["{min_python}", "3.11", "3.12"]'
    }
    
    content = replace_placeholders(content, replacements)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created CI workflow: {output_path}")
    return True


def setup_ruff_config(min_python: str = "3.10"):
    """Set up Ruff configuration in pyproject.toml."""
    template_path = Path(".github/templates/ruff-config.toml")
    pyproject_path = Path("pyproject.toml")
    
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return False
    
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace placeholders
    content = replace_placeholders(content, {"MIN_PYTHON_VERSION": min_python})
    
    # Extract just the configuration part (skip comments)
    config_lines = []
    in_config = False
    for line in content.split('\n'):
        if line.startswith('[tool.ruff]'):
            in_config = True
        if in_config:
            config_lines.append(line)
    
    config_content = '\n'.join(config_lines)
    
    # Append to pyproject.toml
    if pyproject_path.exists():
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Check if ruff config already exists
        if '[tool.ruff]' in existing_content:
            print("⚠️  Ruff configuration already exists in pyproject.toml")
            return True
        
        with open(pyproject_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{config_content}\n")
    else:
        # Create new pyproject.toml
        with open(pyproject_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
    
    print(f"✅ Added Ruff configuration to {pyproject_path}")
    return True


def setup_dependency_review():
    """Set up dependency review configuration."""
    template_path = Path(".github/templates/dependency-review-config.yml")
    output_path = Path(".github/dependency-review-config.yml")
    
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return False
    
    # Create .github directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created dependency review config: {output_path}")
    return True


def update_requirements():
    """Update requirements.txt with modern tools."""
    requirements_path = Path("requirements.txt")
    
    modern_tools = [
        "ruff>=0.1.0",
        "mypy>=1.0.0", 
        "pytest>=7.0.0",
        "pytest-cov>=3.0.0",
        "bandit>=1.7.0",
        "build>=0.10.0",
        "twine>=4.0.0",
    ]
    
    if requirements_path.exists():
        with open(requirements_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Check which tools are already present
        missing_tools = []
        for tool in modern_tools:
            tool_name = tool.split('>=')[0]
            if tool_name not in existing_content:
                missing_tools.append(tool)
        
        if missing_tools:
            with open(requirements_path, 'a', encoding='utf-8') as f:
                f.write(f"\n# Modern CI tools\n")
                for tool in missing_tools:
                    f.write(f"{tool}\n")
            print(f"✅ Added modern tools to {requirements_path}")
        else:
            print(f"✅ All modern tools already in {requirements_path}")
    else:
        # Create new requirements.txt
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write("# Modern Python CI tools\n")
            for tool in modern_tools:
                f.write(f"{tool}\n")
        print(f"✅ Created {requirements_path} with modern tools")


def main():
    parser = argparse.ArgumentParser(description="Set up SOTA CI workflow for Python projects")
    parser.add_argument("--project-name", required=True, help="Name of your project")
    parser.add_argument("--package-name", required=True, help="Package directory (e.g., src/mypackage)")
    parser.add_argument("--min-python", default="3.10", help="Minimum Python version (default: 3.10)")
    
    args = parser.parse_args()
    
    print("🚀 Setting up SOTA CI workflow...")
    print(f"   Project: {args.project_name}")
    print(f"   Package: {args.package_name}")
    print(f"   Min Python: {args.min_python}")
    print()
    
    success = True
    
    # Set up components
    success &= setup_ci_workflow(args.project_name, args.package_name, args.min_python)
    success &= setup_ruff_config(args.min_python)
    success &= setup_dependency_review()
    update_requirements()
    
    if success:
        print()
        print("🎉 SOTA CI setup complete!")
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test locally: ruff check src/ && ruff format --check src/")
        print("3. Run tests: pytest")
        print("4. Commit and push to trigger CI")
    else:
        print()
        print("❌ Setup failed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
