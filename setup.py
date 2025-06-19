#!/usr/bin/env python3
"""
Setup script for Liquid Water Flux (LWF) Calculation Package
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="lwf_calc",
    version="1.0.0",
    author="Sepehr Farhoodi",
    author_email="sepehr.farhoodi@gmail.com",
    description="Liquid Water Flux calculation using SNODAS and CaPA data",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lwf_calc",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Hydrology",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
        "viz": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
        ],
        "performance": [
            "numba>=0.56.0",
            "dask>=2022.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lwf-calc=lwf_calc.scripts.run_pipeline:main",
        ],
    },
    include_package_data=True,
    package_data={
        "lwf_calc": [
            "Archive_CaPA/*",
        ],
    },
    keywords=[
        "hydrology",
        "snow",
        "precipitation",
        "liquid water flux",
        "SNODAS",
        "CaPA",
        "climate",
        "meteorology",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/lwf_calc/issues",
        "Source": "https://github.com/yourusername/lwf_calc",
        "Documentation": "https://github.com/yourusername/lwf_calc#readme",
    },
) 