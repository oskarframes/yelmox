#!/usr/bin/env python3
"""Build NPI-cropped observational reference rasters (SMB, velocity), mirroring the existing SPI cal_eval targets."""
import os

import numpy as np
import xarray as xr
import rioxarray  # noqa: F401  (registers the .rio accessor)
import rasterio
from rasterio.windows import from_bounds

# NPI ice extent within the combined Mouginot mosaic, +15 km buffer (EPSG:32718)
NPI_BOUNDS = (554370.0, 4718930.0, 656550.0, 4868870.0)  # left, bottom, right, top

REPO = "/home/saturn/gwgi/gwgi026h/RESPONSE/yelmo/patagonia_dev/yelmox"
MAR_SMB_PATH = f"{REPO}/input/INPUT-NPI/raw/climatology-MAR/smb.1940-2023.MAR3v14.PAT.0.5km.MM.nc"
VEL_SRC_PATH = f"{REPO}/output/cal_eval/tifs_ref/VEL_SPI_Mouginot.tif"
OUT_DIR = f"{REPO}/output/cal_eval/tifs_ref"


def build_smb_target():
    ds = xr.open_dataset(MAR_SMB_PATH)
    clim = ds["smb_rec"].sel(time=slice("1994-01-01", "2023-12-31"))
    smb = clim.groupby("time.month").mean("time").mean("month")
    smb = smb.rio.write_crs("EPSG:32718", inplace=True)
    smb = (smb * 12) * (1 / 1000) * (1000 / 900)  # mm/month -> m ice/yr, same conversion as SPI reference

    left, bottom, right, top = NPI_BOUNDS
    smb = smb.rio.clip_box(minx=left, miny=bottom, maxx=right, maxy=top)

    out_path = f"{OUT_DIR}/smb_epsg32718_ref_npi.tif"
    smb.rio.to_raster(out_path)
    print(f"Wrote {out_path}")


def build_vel_target():
    with rasterio.open(VEL_SRC_PATH) as src:
        window = from_bounds(*NPI_BOUNDS, transform=src.transform)
        data = src.read(1, window=window)
        transform = src.window_transform(window)
        profile = src.profile.copy()
        profile.update(height=data.shape[0], width=data.shape[1], transform=transform)

    out_path = f"{OUT_DIR}/vel_epsg32718_ref_mouginot_npi.tif"
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(data, 1)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    build_smb_target()
    build_vel_target()
