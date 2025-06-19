# Resampling SNODAS to CaPA grid

import numpy as np
from scipy.interpolate import griddata
import xarray as xr

def resample_SNODAS_to_CaPA(SNODAS_SWE, CaPA):

    """
    Resample SNODAS SWE data to CaPA grid resolution using linear interpolation.
    
    Parameters:
    -----------
    SNODAS_SWE : str or xarray.Dataset
        Path to SNODAS SWE NetCDF file or loaded xarray Dataset containing SWE data
    CaPA : str or xarray.Dataset
        Path to CaPA NetCDF file or loaded xarray Dataset containing precipitation data
    
    Returns:
    --------
    xarray.Dataset
        Dataset containing resampled SWE data on CaPA grid with dimensions:
        - time: time dimension from SNODAS data
        - latitude: latitude dimension from CaPA grid
        - longitude: longitude dimension from CaPA grid
        - SWE: resampled SWE values (mm)
    
    Notes:
    ------
    - SNODAS data is upscaled to CaPA grid resolution using linear interpolation
    - CaPA grid is cropped to match SNODAS spatial extent
    - NaN values in SNODAS data are excluded from interpolation
    - Output maintains the same time dimension as input SNODAS data
    """

    # Load the datasets
    #SNODAS_SWE = xr.open_dataset(SNODAS_SWE)
    #CaPA = xr.open_dataset(CaPA)

    SNODAS_lat_range = SNODAS_SWE['lat'].values
    SNODAS_lon_range = SNODAS_SWE['lon'].values

    # Cut CaPA to the same extent as SNODAS
    CaPA = CaPA.where((CaPA['longitude'] >= SNODAS_lon_range[0]) & 
                              (CaPA['longitude'] <= SNODAS_lon_range[-1]) &
                              (CaPA['latitude'] >= SNODAS_lat_range[0]) &
                              (CaPA['latitude'] <= SNODAS_lat_range[-1]), drop=True)

    # Get the CaPA grid
    CaPA_lat_range = CaPA['latitude'].values
    CaPA_lon_range = CaPA['longitude'].values


    # Initialize an empty array for upscaled SWE with CaPA dimensions
    time_dim = len(SNODAS_SWE['time'])
    upscaled_swe = np.zeros((time_dim, len(CaPA_lat_range), len(CaPA_lon_range)))


    snodas_lon, snodas_lat = np.meshgrid(SNODAS_lon_range, SNODAS_lat_range)
    capa_lon, capa_lat = np.meshgrid(CaPA_lon_range, CaPA_lat_range)


    for t in range(time_dim):
        swe_values = SNODAS_SWE['SWE'].isel(time=t).values
    
        # Flatten coordinates and values for interpolation
        points = np.column_stack((snodas_lat.flatten(), snodas_lon.flatten()))
        values = swe_values.flatten()
    
        # Remove any NaN values
        valid_indices = ~np.isnan(values)
        valid_points = points[valid_indices]
        valid_values = values[valid_indices]
    
        # Perform interpolation to CaPA grid (using 'linear' method for upscaling)
        upscaled_values = griddata(
        valid_points, 
        valid_values, 
        (capa_lat, capa_lon), 
        method='linear'
        )
    
        # Store the upscaled values
        upscaled_swe[t] = upscaled_values

    upscaled_swe_da = xr.DataArray(
        data=upscaled_swe,
        dims=['time', 'latitude', 'longitude'],
        coords={
            'time': SNODAS_SWE['time'],
            'latitude': CaPA_lat_range,
            'longitude': CaPA_lon_range
        },
        name='swe_upscaled'
    )

    upscaled_snodas = xr.Dataset({'swe_upscaled': upscaled_swe_da})

    return upscaled_snodas, CaPA




