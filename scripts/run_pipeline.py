#!/usr/bin/env python3
"""
Liquid Water Flux (LWF) Calculation Pipeline

This script demonstrates the complete workflow for calculating liquid water flux
using SNODAS SWE data and CaPA precipitation data.

Workflow:
1. Download/load SNODAS data
2. Load CaPA data
3. Resample SNODAS to CaPA grid
4. Calculate liquid water flux
5. Save results

Author: Sepehr Farhoodi
Date: 2024
"""

import sys
import os
from pathlib import Path
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta

# Add the parent directory to the path to import lwf_calc
sys.path.append(str(Path(__file__).parent.parent))

from lwf_calc import (
    calculate_lwf,
    resample_SNODAS_to_CaPA,
    load_SNODAS,
    load_CaPA,
    download_new_files,
    run_postprocessing
)

def main(start_date, end_date):
    """
    Main pipeline function that demonstrates the complete LWF calculation workflow.
    """
    print("=" * 60)
    print("Liquid Water Flux (LWF) Calculation Pipeline")
    print("=" * 60)
    
    # Configuration - use the command line arguments if provided, otherwise use the default values
    if start_date is None:
        start_date = "2025-06-01"
    if end_date is None:
        end_date = "2025-06-04"

    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    print(f"Processing period: {start_date} to {end_date}")
    print(f"Output directory: {output_dir.absolute()}")
    print()
    
    try:
        # Step 1: Check for new SNODAS files and download if needed and run post-processing
        print("Step 1: Checking for new SNODAS files...")
        download_new_files()
        print("✓ SNODAS file check completed")
        print()

        # Step 2: Load SNODAS data
        print("Step 2: Loading SNODAS SWE data...")
        try:
            snodas_swe = load_SNODAS(start_date, end_date, variable='SWE')
            print(f"✓ Loaded SNODAS SWE data: {snodas_swe.dims}")
            print(f"  Time range: {snodas_swe.time.min().values} to {snodas_swe.time.max().values}")
        except Exception as e:
            print(f"✗ Error loading SNODAS data: {e}")
            print("  Make sure SNODAS data files exist in the Archive directory")
            return
        print()
        
        # Step 4: Load CaPA data
        print("Step 4: Loading CaPA precipitation data...")
        try:
            capa_data = load_CaPA(start_date, end_date)
            print(f"✓ Loaded CaPA data: {capa_data.dims}")
            print(f"  Time range: {capa_data.time.min().values} to {capa_data.time.max().values}")
        except Exception as e:
            print(f"✗ Error loading CaPA data: {e}")
            print("  Make sure CaPA data files exist in the Archive_CaPA directory")
            return
        print()
        
        # Step 5: Resample SNODAS to CaPA grid
        print("Step 5: Resampling SNODAS to CaPA grid...")
        try:
            snodas_resampled, capa_cropped = resample_SNODAS_to_CaPA(snodas_swe, capa_data)
            print(f"✓ Resampling completed")
            print(f"  Resampled SNODAS shape: {snodas_resampled.swe_upscaled.shape}")
            print(f"  Cropped CaPA shape: {capa_cropped.accum_precip.shape}")
        except Exception as e:
            print(f"✗ Error during resampling: {e}")
            return
        print()
        
        # Step 6: Calculate Liquid Water Flux
        print("Step 6: Calculating Liquid Water Flux...")
        try:
            lwf_m_s, lwf_mm_day = calculate_lwf(snodas_resampled, capa_cropped)
            print(f"✓ LWF calculation completed")
            print(f"  LWF (m/s) shape: {lwf_m_s.lwf.shape}")
            print(f"  LWF (mm/day) shape: {lwf_mm_day.lwf.shape}")
        except Exception as e:
            print(f"✗ Error calculating LWF: {e}")
            return
        print()
        
        # Step 7: Save results
        print("Step 7: Saving results...")
        try:
            # Save LWF results
            lwf_m_s.to_netcdf(output_dir / f"lwf_m_s_{start_date}_{end_date}.nc")
            lwf_mm_day.to_netcdf(output_dir / f"lwf_mm_day_{start_date}_{end_date}.nc")
            
            # Save intermediate results for debugging
            snodas_resampled.to_netcdf(output_dir / f"snodas_resampled_{start_date}_{end_date}.nc")
            capa_cropped.to_netcdf(output_dir / f"capa_cropped_{start_date}_{end_date}.nc")
            
            print(f"✓ Results saved to {output_dir}")
            print(f"  - lwf_m_s_{start_date}_{end_date}.nc")
            print(f"  - lwf_mm_day_{start_date}_{end_date}.nc")
            print(f"  - snodas_resampled_{start_date}_{end_date}.nc")
            print(f"  - capa_cropped_{start_date}_{end_date}.nc")
        except Exception as e:
            print(f"✗ Error saving results: {e}")
            return
        print()
        
        # Step 8: Generate summary statistics
        print("Step 8: Generating summary statistics...")
        try:
            # Calculate basic statistics
            lwf_stats = {
                'mean_m_s': float(lwf_m_s.lwf.mean()),
                'max_m_s': float(lwf_m_s.lwf.max()),
                'min_m_s': float(lwf_m_s.lwf.min()),
                'std_m_s': float(lwf_m_s.lwf.std()),
                'mean_mm_day': float(lwf_mm_day.lwf.mean()),
                'max_mm_day': float(lwf_mm_day.lwf.max()),
                'min_mm_day': float(lwf_mm_day.lwf.min()),
                'std_mm_day': float(lwf_mm_day.lwf.std())
            }
            
            # Save statistics to CSV
            stats_df = pd.DataFrame([lwf_stats])
            stats_df.to_csv(output_dir / f"lwf_statistics_{start_date}_{end_date}.csv", index=False)
            
            print("✓ Summary statistics:")
            print(f"  LWF (m/s): mean={lwf_stats['mean_m_s']:.6f}, max={lwf_stats['max_m_s']:.6f}")
            print(f"  LWF (mm/day): mean={lwf_stats['mean_mm_day']:.2f}, max={lwf_stats['max_mm_day']:.2f}")
            print(f"  Statistics saved to: lwf_statistics_{start_date}_{end_date}.csv")
        except Exception as e:
            print(f"✗ Error generating statistics: {e}")
        print()
        
        print("=" * 60)
        print("Pipeline completed successfully!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nPipeline failed with error: {e}")
        sys.exit(1)

def run_single_location(lat, lon, start_date, end_date):
    """
    Run the pipeline for a single location.
    
    Parameters:
    -----------
    lat : float
        Latitude of the location
    lon : float
        Longitude of the location
    start_date : str
        Start date in 'YYYY-MM-DD' format
    end_date : str
        End date in 'YYYY-MM-DD' format
    """
    print(f"Running pipeline for location: ({lat}, {lon})")
    print(f"Period: {start_date} to {end_date}")
    print()
    
    try:
        # Load data for specific location
        snodas_swe = load_SNODAS(start_date, end_date, variable='SWE', lat=lat, lon=lon)
        capa_data = load_CaPA(start_date, end_date, lat=lat, lon=lon)
        
        # Resample (for single location, this is mostly for consistency)
        snodas_resampled, capa_cropped = resample_SNODAS_to_CaPA(snodas_swe, capa_data)
        
        # Calculate LWF
        lwf_m_s, lwf_mm_day = calculate_lwf(snodas_resampled, capa_cropped)
        
        # Create time series
        time_series = pd.DataFrame({
            'date': lwf_m_s.time.values,
            'lwf_m_s': lwf_m_s.lwf.values.flatten(),
            'lwf_mm_day': lwf_mm_day.lwf.values.flatten()
        })
        
        # Save time series
        output_file = f"lwf_timeseries_{lat}_{lon}_{start_date}_{end_date}.csv"
        time_series.to_csv(output_file, index=False)
        
        print(f"✓ Time series saved to: {output_file}")
        print(f"  Number of data points: {len(time_series)}")
        print(f"  Mean LWF (mm/day): {time_series['lwf_mm_day'].mean():.2f}")
        
        return time_series
        
    except Exception as e:
        print(f"✗ Error processing single location: {e}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Liquid Water Flux Calculation Pipeline")
    parser.add_argument("--start-date", default="2025-06-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default="2025-06-04", help="End date (YYYY-MM-DD)")
    parser.add_argument("--lat", type=float, help="Latitude for single location analysis")
    parser.add_argument("--lon", type=float, help="Longitude for single location analysis")
    parser.add_argument("--single-location", action="store_true", help="Run for single location only")
    
    args = parser.parse_args()
    
    if args.single_location and args.lat is not None and args.lon is not None:
        run_single_location(args.lat, args.lon, args.start_date, args.end_date)
    else:
        main(start_date=args.start_date, end_date=args.end_date)
