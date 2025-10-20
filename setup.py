"""
Setup script for STT Analytics Platform
Minimal setup for Streamlit Cloud deployment
"""

from setuptools import setup, find_packages

setup(
    name="stta",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        # Core dependencies are in requirements.txt
        # This just installs the package structure
    ],
    author="STT Analytics Team",
    description="Speech-to-Text Analytics Platform",
    long_description="A deterministic analytics platform for call transcript analysis",
)
