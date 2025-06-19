import xarray as xr
import os
from datetime import datetime

def load_SNODAS(start_date, end_date, variable='SWE', lat=None, lon=None):
    """
    Load SNODAS data for a specific date range and location.
    
    Parameters:
    -----------
    start_date : str or datetime
        Start date in format 'YYYY-MM-DD' or datetime object
    end_date : str or datetime
        End date in format 'YYYY-MM-DD' or datetime object
    variable : str
        Either 'SWE' or 'SD' (Snow Water Equivalent or Snow Depth)
    lat : float, optional
        Latitude of interest. If None, returns all latitudes
    lon : float, optional
        Longitude of interest. If None, returns all longitudes
    
    Returns:
    --------
    xarray.Dataset
        Dataset containing the requested SNODAS data
    """
    # Convert string dates to datetime if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get list of files in Archive directory
    archive_dir = os.path.join(os.path.dirname(__file__), "Archive")
    files = [f for f in os.listdir(archive_dir) if f.endswith(f"{variable}_final.nc")]
    
    # Filter files for date range
    date_files = []
    for file in files:
        # Extract date from filename (assuming format contains YYYYMMDD)
        date_str = file.split('_')[0]  # Adjust this based on your filename format
        file_date = datetime.strptime(date_str, '%Y%m%d')
        if start_date <= file_date <= end_date:
            date_files.append(file)
    
    if not date_files:
        raise ValueError(f"No {variable} files found for the specified date range")
    
    # Sort files by date
    date_files.sort()
    
    # Load and concatenate data
    data_list = []
    for file in date_files:
        ds = xr.open_dataset(os.path.join(archive_dir, file))
        data_list.append(ds)
    
    # Concatenate all data
    combined_data = xr.concat(data_list, dim='time')
    
    # Select specific location if provided
    if lat is not None and lon is not None:
        combined_data = combined_data.sel(lat=lat, lon=lon, method='nearest')
    
    return combined_data

def load_CaPA(start_date, end_date, lat=None, lon=None):
    """
    Load CaPA data for a specific date range and location from the concatenated file.
    
    Parameters:
    -----------
    start_date : str or datetime
        Start date in format 'YYYY-MM-DD' or datetime object
    end_date : str or datetime
        End date in format 'YYYY-MM-DD' or datetime object
    lat : float, optional
        Latitude of interest. If None, returns all latitudes
    lon : float, optional
        Longitude of interest. If None, returns all longitudes
    
    Returns:
    --------
    xarray.Dataset
        Dataset containing the requested CaPA data
    """
    # Convert string dates to datetime if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Load the concatenated CaPA file
    archive_dir = os.path.join(os.path.dirname(__file__), "Archive_CaPA")
    nc_file = [f for f in os.listdir(archive_dir) if f.endswith(".nc")]
    capa_file = os.path.join(archive_dir, nc_file[0])
    
    # Load the dataset
    ds = xr.open_dataset(capa_file)
    
    # Select the date range
    data = ds.sel(time=slice(start_date, end_date))
    
    # Select specific location if provided
    if lat is not None and lon is not None:
        data = data.sel(lat=lat, lon=lon, method='nearest')
    
    return data