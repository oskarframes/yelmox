#!/usr/bin/env python3
"""Plot the SMB and surface-velocity observational reference rasters used in output/cal_eval calibration scoring."""
import argparse
import os

import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LogNorm


def read_raster(path):
    with rasterio.open(path) as src:
        data = src.read(1).astype(float)
        if src.nodata is not None:
            data = np.where(data == src.nodata, np.nan, data)
        bounds = src.bounds
        extent = [bounds.left / 1e3, bounds.right / 1e3, bounds.bottom / 1e3, bounds.top / 1e3]
    return data, extent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref-dir", default="output/cal_eval/tifs_ref",
                         help="Directory containing the reference GeoTIFFs")
    parser.add_argument("--out", default="output/cal_eval/plots/observational_targets.png",
                         help="Output PNG path")
    parser.add_argument("--suffix", default="", help="Filename suffix, e.g. '_npi' for the NPI-cropped targets")
    parser.add_argument("--domain", default="", help="Domain label for the figure title, e.g. 'NPI'")
    args = parser.parse_args()

    smb, smb_extent = read_raster(os.path.join(args.ref_dir, f"smb_epsg32718_ref{args.suffix}.tif"))
    vel, vel_extent = read_raster(os.path.join(args.ref_dir, f"vel_epsg32718_ref_mouginot{args.suffix}.tif"))
    vel = np.where(vel > 0, vel, np.nan)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    fig, (ax_smb, ax_vel) = plt.subplots(1, 2, figsize=(12, 5.5))

    smb_lim = np.nanpercentile(np.abs(smb), 98)
    im_s = ax_smb.imshow(smb, origin="upper", extent=smb_extent, cmap="RdBu",
                          norm=TwoSlopeNorm(vcenter=0, vmin=-smb_lim, vmax=smb_lim))
    ax_smb.set_title("Reference SMB\n(1994-2023 climatology)")
    fig.colorbar(im_s, ax=ax_smb, label="SMB [m ice/yr]", shrink=0.85)

    v_pos = vel[np.isfinite(vel)]
    v_vmin = max(np.percentile(v_pos, 2), 0.1) if v_pos.size else 0.1
    v_vmax = np.percentile(v_pos, 98) if v_pos.size else 1.0
    im_v = ax_vel.imshow(vel, origin="upper", extent=vel_extent, cmap="viridis",
                          norm=LogNorm(vmin=v_vmin, vmax=v_vmax))
    ax_vel.set_title("Reference surface velocity\n(Mouginot & Rignot 2015)")
    fig.colorbar(im_v, ax=ax_vel, label="Surface velocity [m/yr]", shrink=0.85)

    for ax in (ax_smb, ax_vel):
        ax.set_xlabel("x [km] (EPSG:32718)")
        ax.set_ylabel("y [km] (EPSG:32718)")
        ax.set_aspect("equal")

    title = "Observational calibration targets (output/cal_eval)"
    if args.domain:
        title = f"{args.domain} - {title}"
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    plt.close(fig)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
