#!/usr/bin/env python3
"""
Personal Assistant MODULAR - Setup Script
"""
from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="personal-assistant-modular",
    version="1.0.0",
    author="Nike Research",
    author_email="nike@example.com",
    description="A modular personal assistant with RAG, Discord integration, and health triage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nike/personal-assistant-modular",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pa-assistant=assistant_cli:main",
            "pa-discord=discord_bot:main",
            "pa-server=server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json", "*.env.example"],
    },
)