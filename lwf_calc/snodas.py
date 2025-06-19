import numpy as np
import xarray as xr
import pandas as pd
import os
import tarfile
import gzip
import shutil
from pathlib import Path
import subprocess
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
#from snodas_postprocess import run_postprocessing

# Get current date
now = datetime.now()
#now = datetime(2025, 5, 1)  # For testing purposes, set a fixed date
year = now.year
month_num = now.strftime("%m")     # e.g., "05"
month_name = now.strftime("%b")    # e.g., "May"

# Construct the BASE_URL
BASE_URL = f"https://noaadata.apps.nsidc.org/NOAA/G02158/unmasked/{year}/{month_num}_{month_name}/"

# Get the directory where this script lives
SCRIPT_DIR = Path(__file__).parent.absolute()
DOWNLOAD_DIR = SCRIPT_DIR / "snodas_data"

# Create local download folder if not exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_file_list():
    """Scrape list of files on the server."""
    #headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(BASE_URL)  # , headers=headers)
    #if response.status_code != 200:
        #raise Exception(f"Failed to fetch file list from {BASE_URL}. Status code: {response.status_code}")
    soup = BeautifulSoup(response.text, 'html.parser')
    return [a['href'] for a in soup.find_all('a') if a['href'].endswith('.tar')]

def process_tar_file(tar_file_path):
    """Process a SNODAS tar file and convert its contents to NetCDF format."""
    if not tar_file_path:
        print("No .tar file provided.")
        return False

    # Get the directory where this script lives
    script_dir = Path(__file__).parent.absolute()
    
    # Create output and log folders
    output_dir = script_dir / "netcdf_output"
    output_dir.mkdir(exist_ok=True)
    log_file = script_dir / "conversion_log.txt"

    # Create temporary directory for extraction
    temp_dir = Path(f"extracted_{Path(tar_file_path).stem}")
    temp_dir.mkdir(exist_ok=True)

    try:
        # Extract contents
        with tarfile.open(tar_file_path) as tar:
            tar.extractall(path=temp_dir)

        # Keep only selected files (5th to 8th)
        files = sorted(os.listdir(temp_dir))
        if len(files) >= 8:
            keep_files = files[4:8]
            for file in files:
                if file not in keep_files:
                    os.remove(temp_dir / file)
            #for file in keep_files:
                #shutil.move(temp_dir / file, Path(tar_file_path).parent)

        # Unzip all .gz files in current directory
        for gz_file in temp_dir.glob("*.gz"):
            with gzip.open(gz_file, 'rb') as f_in:
                with open(temp_dir / gz_file.stem, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(gz_file)

        # Create .hdr files
        for dat_file in temp_dir.glob("*.dat"):
            header = dat_file.stem
            hdr_file = (dat_file.with_suffix('.hdr'))
            
            with open(hdr_file, 'w') as f:
                f.write("ENVI\nsamples = 8192\nlines = 4096\nbands = 1\nheader offset = 0\nfile type = ENVI Standard\ndata type = 2\ninterleave = bsq\nbyte order = 1\n")

        # Convert to NetCDF and clean up
        for dat_file in temp_dir.glob("*.dat"):
            # Extract date part from filename
            date_part = dat_file.stem.split("ssmv1")[-1].split("05HP001")[0]
            output_file = temp_dir / f"output_{date_part}.nc"

            print(f"Processing: {dat_file} → {output_file}")

            # Set GDAL_DATA environment variable
            os.environ['GDAL_DATA'] = r"C:\_LOCALdata\Anaconda\envs\forecast\Library\share\gdal"

            # Define the path to gdal_translate
            GDAL_TRANSLATE = r"C:\_LOCALdata\Anaconda\envs\forecast\Library\bin\gdal_translate.exe"

            # Then your subprocess.run call remains the same
            result = subprocess.run([
                GDAL_TRANSLATE,
                "-of", "NetCDF",
                "-a_srs", "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs",
                "-a_nodata", "-9999",
                "-a_ullr", "-130.51666666666667", "58.23333333333333", "-62.25000000000000", "24.10000000000000",
                str(dat_file),
                str(output_file)
            ], capture_output=True, text=True)

            if result.returncode == 0:
                # Log success
                with open(log_file, 'a') as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Converted {dat_file} -> {output_dir}\n")
                
                # Move output file to netcdf_output directory
                shutil.move(output_file, output_dir / output_file.name)

                # Cleanup
                os.remove(dat_file)
                os.remove(dat_file.with_suffix('.hdr'))
                os.remove(dat_file.with_suffix('.txt'))
            else:
                # Log failure
                with open(log_file, 'a') as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Failed to convert {dat_file}\n")
                print(f"Error converting {dat_file}: {result.stderr}")

        return True

    except Exception as e:
        print(f"Error processing file: {e}")
        return False
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def run_postprocessing():
    """
    This function processes SNODAS NetCDF files, filtering them for a specific area,
    renaming variables, and saving the cleaned datasets.
    """
    # Define area of interest
    area_alberta_extended = [63.5, -129, 46, -101]  # Alberta, Saskatchewan, BC

    # Set folder path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path_SNODAS = os.path.join(script_dir, "netcdf_output")

    # Get list of NetCDF files excluding final ones
    nc_files_SNODAS = sorted([
        os.path.join(folder_path_SNODAS, f)
        for f in os.listdir(folder_path_SNODAS)
        if not f.endswith("Alberta.nc")
    ])

    # Prepare cleaned names
    cleaned_names = []
    for fpath in nc_files_SNODAS:
        fname = os.path.basename(fpath)
        date_part = fname.split("NATS")[-1].split(".")[0]
        var_type = "SWE" if "1034" in fname else "SD" if "1036" in fname else "UNKNOWN"
        cleaned_names.append((fpath, f"{date_part}_{var_type}", var_type, date_part))

    # Process each file
    for fpath, new_name, var_type, date_part in cleaned_names:
        with xr.open_dataset(fpath) as ds:
            ds_filtered = ds.where(
                (ds['lon'] >= area_alberta_extended[1]) & (ds['lon'] <= area_alberta_extended[3]) &
                (ds['lat'] >= area_alberta_extended[2]),
                drop=True
            )

            time_index = pd.to_datetime(date_part, format="%Y%m%d")
            ds_time = ds_filtered.expand_dims(dim={"time": [time_index]})
            ds_dropped = ds_time.drop_vars('crs', errors='ignore')

            if var_type == "SWE":
                ds_final = ds_dropped.rename({'Band1': 'SWE'})
                ds_final['SWE'].attrs["units"] = 'mm'
            elif var_type == "SD":
                ds_final = ds_dropped.rename({'Band1': 'SD'})
                ds_final['SD'] = ds_final['SD'] / 1000
                ds_final['SD'].attrs['units'] = 'm'
            else:
                continue
            # Save the final dataset
            ds_final.to_netcdf(os.path.join(folder_path_SNODAS, new_name + "_final.nc"))
        
def download_new_files():
    print(f"[{datetime.now()}] Checking for new SNODAS files...")

    files_online = get_file_list()
    files_local = os.listdir(DOWNLOAD_DIR)

    new_files = [f for f in files_online if f not in files_local]

    if not new_files:
        print("No new files found.")
        return
    
    for file in new_files:
        file_url = urljoin(BASE_URL, file)
        local_path = os.path.join(DOWNLOAD_DIR, file)
        print(f"Downloading {file}...")
        with requests.get(file_url, stream=True) as r:
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded: {file}")

        # Process the downloaded file
        try:
            if process_tar_file(local_path):
                print(f"Processed: {file}")
            else:
                print(f"Processing failed for {file}")
        except Exception as e:
            print(f"Processing failed for {file}: {e}")

    # Run the postprocessing script
    run_postprocessing()
    print("Postprocessing completed.")
    print("All new files downloaded and processed.")


    ### ARCHIVE FINAL FILES AND CLEANUP ###
    output_dir = os.path.join(os.path.dirname(__file__), "netcdf_output")
    archive_dir = os.path.join(os.path.dirname(__file__), "Archive")

    os.makedirs(archive_dir, exist_ok=True)

    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)

        # Move only SWE/SD .final files to Archive
        if filename.endswith("final.nc") and ("SWE" in filename or "SD" in filename):
            archive_path = os.path.join(archive_dir, filename)
            os.rename(file_path, archive_path)
            print(f"Archived: {filename}")

    # Now clear the rest of the netcdf_output directory
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            os.remove(file_path)
            print(f"Deleted: {filename}")
        except Exception as e:
            print(f"Failed to delete {filename}: {e}")



if __name__ == "__main__":
    download_new_files()
