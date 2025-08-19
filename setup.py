from setuptools import setup, find_packages
import os

def read_requirements():
    """Read requirements from requirements.txt."""
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read the README for the long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="avatarmcp",
    version="0.2.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced VRM avatar management and animation server with REST API and WebSocket support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/avatarmcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        'console_scripts': [
            'avatarmcp=avatarmcp.cli:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/avatarmcp/issues',
        'Source': 'https://github.com/yourusername/avatarmcp',
    },
)
