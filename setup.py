#!/usr/bin/env python3
"""
Setup script for AvatarMCP - MCP server for VRM avatar management and animation.

This setup.py is provided for backward compatibility. For modern Python packaging,
use pyproject.toml instead.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read requirements
def read_requirements(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="avatarmcp",
    version="0.1.0",
    description="MCP server for managing and animating VRM avatars",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="AvatarMCP Team",
    author_email="dev@avatarmcp.example.com",
    url="https://github.com/yourusername/avatarmcp",
    license="MIT",

    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,

    # Python requirements
    python_requires=">=3.9",
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('requirements-dev.txt') if os.path.exists('requirements-dev.txt') else [],
        'ai-npc': read_requirements('requirements-ai-npc.txt') if os.path.exists('requirements-ai-npc.txt') else [],
        'visualization': read_requirements('requirements-visualization.txt') if os.path.exists('requirements-visualization.txt') else [],
    },

    # Entry points
    entry_points={
        'console_scripts': [
            'avatarmcp=avatarmcp.__main__:main',
        ],
        'mcp.server': [
            'avatarmcp=avatarmcp.server:AvatarMCPServer',
        ],
    },

    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Framework :: FastMCP",
    ],

    # Keywords
    keywords="mcp avatar vrm 3d animation osc claude-desktop",

    # Project URLs
    project_urls={
        "Homepage": "https://github.com/yourusername/avatarmcp",
        "Documentation": "https://github.com/yourusername/avatarmcp#readme",
        "Repository": "https://github.com/yourusername/avatarmcp.git",
        "Issues": "https://github.com/yourusername/avatarmcp/issues",
        "Changelog": "https://github.com/yourusername/avatarmcp/blob/main/CHANGELOG.md",
    },

    # Additional files
    zip_safe=False,
)