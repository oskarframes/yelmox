#!/usr/bin/env python3
"""Render a thickness/velocity/volume/velocity-evolution frame per yelmo2D.nc timestep and animate them into a GIF."""
import argparse
import os

import numpy as np
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from PIL import Image

COLOR_VOLUME   = "#0072B2"   # Okabe-Ito blue
COLOR_VELOCITY = "#D55E00"   # Okabe-Ito vermillion


def map_limits(ds2d):
    """Fixed color-scale limits for H_ice and uxy_s, shared across all frames."""

    H_ice = ds2d["H_ice"].values
    uxy_s = np.where(H_ice > 0, ds2d["uxy_s"].values, np.nan)
    H_ice_masked = np.where(H_ice > 0, H_ice, np.nan)

    h_vmax = np.nanpercentile(H_ice_masked, 98) if np.isfinite(H_ice_masked).any() else 1.0
    v_pos = uxy_s[np.isfinite(uxy_s) & (uxy_s > 0)]
    v_vmin = max(np.percentile(v_pos, 2), 0.1) if v_pos.size else 0.1
    v_vmax = np.percentile(v_pos, 98) if v_pos.size else 1.0

    return h_vmax, v_vmin, v_vmax


def line_limits(ds1d, varname):
    y = ds1d[varname].values
    pad = 0.05 * (np.nanmax(y) - np.nanmin(y) or 1.0)
    return np.nanmin(y) - pad, np.nanmax(y) + pad


def plot_frame(ds1d, ds2d, time_idx, out_path, h_vmax, v_vmin, v_vmax,
                t_range, vol_range, vel_range, domain, grid_name):
    """One 2x2 frame: thickness map, velocity map, volume-over-time, velocity-over-time."""

    frame = ds2d.isel(time=time_idx)
    t_cur = float(frame["time"].values)

    H_ice = frame["H_ice"].values
    uxy_s_map = np.where(H_ice > 0, frame["uxy_s"].values, np.nan)
    H_ice_masked = np.where(H_ice > 0, H_ice, np.nan)

    xc, yc = ds2d["xc"].values, ds2d["yc"].values
    extent = [xc.min(), xc.max(), yc.min(), yc.max()]

    t1d = ds1d["time"].values
    sel = t1d <= t_cur

    fig, ((ax_h, ax_v), (ax_vol, ax_vel)) = plt.subplots(2, 2, figsize=(11, 10))

    im_h = ax_h.imshow(H_ice_masked, origin="lower", extent=extent,
                        cmap="Blues", vmin=0, vmax=h_vmax)
    ax_h.set_title("Ice thickness")
    fig.colorbar(im_h, ax=ax_h, label="Ice thickness [m]", shrink=0.85)

    im_v = ax_v.imshow(uxy_s_map, origin="lower", extent=extent, cmap="viridis",
                        norm=LogNorm(vmin=v_vmin, vmax=v_vmax))
    ax_v.set_title("Surface velocity")
    fig.colorbar(im_v, ax=ax_v, label="Surface velocity [m/yr]", shrink=0.85)

    for ax in (ax_h, ax_v):
        ax.set_xlabel("x [km]")
        ax.set_ylabel("y [km]")
        ax.set_aspect("equal")

    ax_vol.plot(t1d[sel], ds1d["V_ice"].values[sel], color=COLOR_VOLUME, lw=2)
    if sel.any():
        ax_vol.plot(t1d[sel][-1], ds1d["V_ice"].values[sel][-1], "o", color=COLOR_VOLUME)
    ax_vol.set_xlim(*t_range)
    ax_vol.set_ylim(*vol_range)
    ax_vol.set_xlabel("Time [years]")
    ax_vol.set_ylabel("Ice volume [1e6 km$^3$]")
    ax_vol.set_title("Volume evolution")
    ax_vol.grid(True, color="0.85", lw=0.8)
    ax_vol.spines[["top", "right"]].set_visible(False)

    ax_vel.plot(t1d[sel], ds1d["uxy_s"].values[sel], color=COLOR_VELOCITY, lw=2)
    if sel.any():
        ax_vel.plot(t1d[sel][-1], ds1d["uxy_s"].values[sel][-1], "o", color=COLOR_VELOCITY)
    ax_vel.set_xlim(*t_range)
    ax_vel.set_ylim(*vel_range)
    ax_vel.set_xlabel("Time [years]")
    ax_vel.set_ylabel("Mean surface velocity [m/yr]")
    ax_vel.set_title("Velocity evolution")
    ax_vel.grid(True, color="0.85", lw=0.8)
    ax_vel.spines[["top", "right"]].set_visible(False)

    fig.suptitle(f"{domain} {grid_name} - t = {t_cur:.0f} yr".strip())
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def make_gif(frame_paths, out_path, duration_ms):
    frames = [Image.open(p) for p in frame_paths]
    frames[0].save(out_path, save_all=True, append_images=frames[1:],
                    duration=duration_ms, loop=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rundir", help="Path to a yelmox run directory (containing yelmo1D.nc, yelmo2D.nc)")
    parser.add_argument("--out", default=None, help="Output directory for plots (default: <rundir>/plots)")
    parser.add_argument("--fps", type=float, default=2.0, help="GIF frames per second (default: 2)")
    args = parser.parse_args()

    path_1d = os.path.join(args.rundir, "yelmo1D.nc")
    path_2d = os.path.join(args.rundir, "yelmo2D.nc")
    for p in (path_1d, path_2d):
        if not os.path.isfile(p):
            raise FileNotFoundError(f"Expected output file not found: {p}")

    out_dir = args.out or os.path.join(args.rundir, "plots")
    frames_dir = os.path.join(out_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    with xr.open_dataset(path_1d) as ds1d, xr.open_dataset(path_2d) as ds2d:

        h_vmax, v_vmin, v_vmax = map_limits(ds2d)
        t_range = (float(ds1d["time"].min()), float(ds1d["time"].max()))
        vol_range = line_limits(ds1d, "V_ice")
        vel_range = line_limits(ds1d, "uxy_s")
        domain = ds2d.attrs.get("domain", "")
        grid_name = ds2d.attrs.get("grid_name", "")

        n_frames = ds2d.sizes["time"]
        frame_paths = []
        for i in range(n_frames):
            frame_path = os.path.join(frames_dir, f"frame_{i:03d}.png")
            plot_frame(ds1d, ds2d, i, frame_path, h_vmax, v_vmin, v_vmax,
                       t_range, vol_range, vel_range, domain, grid_name)
            frame_paths.append(frame_path)
            print(f"Wrote {frame_path}")

    gif_path = os.path.join(out_dir, "evolution.gif")
    make_gif(frame_paths, gif_path, duration_ms=int(1000 / args.fps))
    print(f"Wrote {gif_path}")


if __name__ == "__main__":
    main()
