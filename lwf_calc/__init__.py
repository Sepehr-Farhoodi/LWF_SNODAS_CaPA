"""
Liquid Water Flux (LWF) Calculation Package

This package provides tools for calculating liquid water flux using SNODAS SWE data
and CaPA precipitation data. The main formula used is:
LWF(t) = SWE(t-1) - SWE(t) + P(t)

Main Components:
- SNODAS data processing and downloading
- CaPA data loading
- Data resampling and interpolation
- Liquid water flux calculation
- Data loading utilities

Author: Sepehr Farhoodi
Version: 1.0.0
"""

# Import main functions from each module
from .lwf import calculate_lwf
from .resample import resample_SNODAS_to_CaPA
from .load_data import load_SNODAS, load_CaPA
from .snodas import (
    get_file_list,
    process_tar_file,
    run_postprocessing,
    download_new_files
)

# Define what gets imported with "from lwf_calc import *"
__all__ = [
    # Main calculation function
    'calculate_lwf',
    
    # Data processing functions
    'resample_SNODAS_to_CaPA',
    
    # Data loading functions
    'load_SNODAS',
    'load_CaPA',
    
    # SNODAS processing functions
    'get_file_list',
    'process_tar_file',
    'run_postprocessing',
    'download_new_files'
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Sepehr Farhoodi"
__email__ = "sepehr.farhoodi@gmail.com"
__description__ = "Liquid Water Flux calculation using SNODAS and CaPA data"

# Package documentation
__doc__ = """
Liquid Water Flux (LWF) Calculation Package

This package provides a comprehensive toolkit for calculating liquid water flux
using SNODAS (Snow Data Assimilation System) SWE (Snow Water Equivalent) data
and CaPA (Canadian Precipitation Analysis) precipitation data.

Key Features:
- Download and process SNODAS data from NOAA servers
- Load and process CaPA precipitation data
- Resample SNODAS data to match CaPA grid resolution
- Calculate liquid water flux using the formula: LWF(t) = SWE(t-1) - SWE(t) + P(t)
- Support for both m/s and mm/day output units
- Data loading utilities for specific date ranges and locations

Example Usage:
    from lwf_calc import calculate_lwf, load_SNODAS, load_CaPA
    
    # Load data
    snodas_data = load_SNODAS('2024-01-01', '2024-01-31')
    capa_data = load_CaPA('2024-01-01', '2024-01-31')
    
    # Calculate LWF
    lwf_m_s, lwf_mm_day = calculate_lwf(snodas_data, capa_data)
"""
