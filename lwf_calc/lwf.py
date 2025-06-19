import xarray as xr
import pandas as pd
import numpy as np

# Calculate Liquid Water Flux (LWF) using the formula: LWF(t) = SWE(t-1) - SWE(t) + P(t)
# Where SWE is from SNODAS and P is from CaPA

def calculate_lwf(SNODAS_SWE, CaPA):

    # Extract the SWE data from upscaled SNODAS
    swe = SNODAS_SWE.swe_upscaled

    # Extract precipitation data from CaPA
    precip = CaPA.accum_precip

    # Create a new dataset with the same dimensions as the input datasets
    lwf_data = xr.DataArray(
        data=np.zeros((len(swe.time)-1, len(swe.latitude), len(swe.longitude))),
        dims=["time", "latitude", "longitude"],
        coords={
            "time": swe.time[1:],  # Start from the second day
            "latitude": swe.latitude,
            "longitude": swe.longitude
        }
    )

    # Calculate LWF for each time step (starting from the second day)
    for t in range(1, len(swe.time)):
        current_date = swe.time[t].values
        previous_date = swe.time[t-1].values
        
        # Get SWE for current and previous day
        swe_current = swe.sel(time=current_date)
        swe_previous = swe.sel(time=previous_date)
        
        # Get precipitation for current day
        precip_current = precip.sel(time=current_date)
        
        # Calculate LWF: LWF(t) = SWE(t-1) - SWE(t) + P(t)
        lwf = swe_previous - swe_current + precip_current
        
        # Convert negative values to zero
        lwf = xr.where(lwf < 0, 0, lwf)

        # convert to m/sec
        lwf = lwf / (86400 * 1000)
        
        # Add to the data array
        lwf_data[t-1, :, :] = lwf

    # Create the final dataset
    lwf_dataset = xr.Dataset(
        data_vars={
            "lwf": lwf_data
        },
        attrs={
            "description": "Liquid Water Flux calculated as LWF(t) = SWE(t-1) - SWE(t) + P(t)",
            "units": "m/s",
            "negative_values": "converted to zero"
        }
    )

    lwf_dataset_mm_day = xr.Dataset(
        data_vars={
            "lwf": lwf_data * 86400 * 1000
        },
        attrs={
            "description": "Liquid Water Flux calculated as LWF(t) = SWE(t-1) - SWE(t) + P(t)",
            "units": "mm/day",
            "negative_values": "converted to zero"
        }
    )

    return lwf_dataset, lwf_dataset_mm_day

