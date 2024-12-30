import requests
import os
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://www2.census.gov/geo/tiger/TIGER_RD18/LAYER/EDGES/tl_rd22_{fips_code}_edges.zip"
tiger_path_one_line = os.path.join(os.path.expanduser('~'), 'Desktop', 'TIGER')
OUTPUT_DIR = tiger_path_one_line

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def download_file(fips_code):
    url = BASE_URL.format(fips_code=fips_code)
    try:
        print(f"Downloading {url} ...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(os.path.join(OUTPUT_DIR, f"tl_rd22_{fips_code}_edges.zip"), 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded {fips_code} successfully.")
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            print(f"No file for FIPS code {fips_code}. Skipping.")
        else:
            print(f"Error {e.response.status_code} encountered for FIPS code {fips_code}. Skipping.")
    except Exception as e:
        print(f"Unexpected error encountered for FIPS code {fips_code}: {e}. Skipping.")

START_FIPS = "01001"
start_state_code = int(START_FIPS[:2])
start_county_code = int(START_FIPS[2:])

fips_codes = []

for state_code in range(start_state_code, 57):
    if state_code == start_state_code:
        loop_start_county_code = start_county_code
    else:
        loop_start_county_code = 1

    for county_code in range(loop_start_county_code, 1000):
        fips_code = f"{state_code:02}{county_code:03}"  
        fips_codes.append(fips_code)

MAX_WORKERS = 5  # new rdp kinda slow lol
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    executor.map(download_file, fips_codes)

print("Download complete!")
