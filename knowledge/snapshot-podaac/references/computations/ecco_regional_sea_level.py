#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy",
#     "xarray",
#     "netcdf4",
#     "dask",
# ]
# ///
"""Sanctioned computation for the attested regional sea level partition.

Contract: podaac/computations/ecco-regional-sea-level.md. ECCO-internal
v1 scope: over a REGISTERED region and a month period, area-mean monthly
anomaly series of total sea level (the SSH variant, stated in the
receipt), the manometric piece (OBP), and an INDEPENDENT steric piece
from the model's own density anomaly (RHOAnoma integrated over depth
with partial cells), all on the native llc90 grid. The receipt carries
the three monthly anomaly series and the residual series, the three
trends each with the interval the sanctioned trend-with-interval
method states for it (ecco_trend_ci.py, imported from beside this file
and named by hash in each block), the maximum monthly partition
residual, and the convention-bound bookkeeping fields. Months are read
one at a time, so the full record costs the memory of one month.
Consumers bind values for the declared parameters and MUST NOT edit
this file; the attester hashes it and recomputes every trend, interval
and residual from the series in the receipt.
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import re
import sys
import uuid
from pathlib import Path

import numpy as np
import xarray as xr

RHO0 = 1029.0            # kg m-3, the model's Boussinesq reference density
SSH_VARIANT = "SSH"      # one variant, stated, never mixed (ssh-ib-variants)

# The region registry: part of the sanctioned file by design, so an
# unregistered region fails attestation (A2) instead of improvising a
# mask. Bounds are (lon_min, lon_max, lat_min, lat_max), degrees east.
REGIONS = {
    # Boxes are KEYED, not positional. Two sanctioned computations once
    # stored these as bare tuples in opposite orders, so the same region
    # names resolved to different water (gulf-of-mexico differed by 8
    # percent in area, north-sea by 18.5). Keys make that class of error
    # impossible to reintroduce silently.
    "us-northeast-coast": {"lat": (35.0, 45.0), "lon": (-75.0, -65.0)},
    "gulf-of-mexico": {"lat": (18.0, 31.0), "lon": (-98.0, -81.0)},
    "north-sea": {"lat": (51.0, 60.0), "lon": (-2.0, 9.0)},
}

SPAN = ("1992-01", "2017-12")   # ECCO v4r4; briefings state this boundary


def parse_period(period: str):
    m = re.fullmatch(r"(\d{4}-\d{2}):(\d{4}-\d{2})", period)
    if not m:
        raise SystemExit(f"period must be YYYY-MM:YYYY-MM, got {period!r}")
    a, b = m.group(1), m.group(2)
    if not (SPAN[0] <= a <= b <= SPAN[1]):
        raise SystemExit(f"period {period} outside the v4r4 span {SPAN}")
    return a, b


def monthly(root: Path, short_name: str, a: str, b: str) -> xr.Dataset:
    ds = xr.open_mfdataset(str(root / short_name / "*.nc"), combine="by_coords")
    ds = ds.sel(time=slice(a, b))
    return ds


def compute(region: str, period: str, root: Path) -> dict:
    box = REGIONS[region]
    lat0, lat1 = box["lat"]
    lon0, lon1 = box["lon"]
    a, b = parse_period(period)

    grid = xr.open_dataset(root / "geometry" / "GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc")
    ssh = monthly(root, "ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4", a, b)
    obp = monthly(root, "ECCO_L4_OBP_LLC0090GRID_MONTHLY_V4R4", a, b)
    dens = monthly(root, "ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4", a, b)
    n_months = int(ssh.sizes["time"])
    assert n_months == int(obp.sizes["time"]) == int(dens.sizes["time"]), \
        "matching-period rule violated: the three inputs cover different months"
    assert n_months >= 3, "need at least three months for a slope"

    xc, yc = grid.XC.values, grid.YC.values                  # (13, 90, 90)
    wet = grid.maskC.values[0] > 0                            # surface wet
    inbox = (yc >= lat0) & (yc <= lat1) & (xc >= lon0) & (xc <= lon1) & wet
    w = grid.rA.values * inbox                                # area weights
    wsum = float(w.sum())
    assert wsum > 0, f"region {region} selects no wet cells"

    def area_mean(field2d):                                   # (13, 90, 90)
        v = np.nan_to_num(field2d)
        return float((v * w).sum() / wsum)

    # Independent steric: -(1/rho0) * integral of RHOAnoma over depth,
    # partial cells in (hFacC * drF); model-consistent density, never a
    # foreign equation of state. One month in memory at a time.
    hfac_drf = grid.hFacC.values * grid.drF.values[:, None, None, None]  # (50,13,90,90)
    total, mass, steric = [], [], []
    for i in range(n_months):
        total.append(area_mean(ssh[SSH_VARIANT].isel(time=i).values))   # m
        mass.append(area_mean(obp["OBP"].isel(time=i).values))          # m (equiv. sea level)
        rho = np.nan_to_num(dens["RHOAnoma"].isel(time=i).values)       # (50, 13, 90, 90)
        steric.append(area_mean(-(rho * hfac_drf).sum(axis=0) / RHO0))  # m
    dates = [str(np.datetime_as_string(t, unit="M"))
             for t in ssh["time"].values]
    total, mass, steric = (np.asarray(total), np.asarray(mass),
                           np.asarray(steric))

    def anom(s):
        return s - s.mean()

    ta, ma, sa = anom(total), anom(mass), anom(steric)
    resid = ta - ma - sa

    def interval(s):
        return trend_interval_mm_yr([float(v) * 1000.0 for v in s])

    blocks = {part: interval(s) for part, s in
              (("total", ta), ("mass", ma), ("steric", sa))}
    return {
        "ssh_variant": SSH_VARIANT,
        "months": n_months,
        "cells_evaluated": int(inbox.sum()),
        "trend_total_mm_yr": round(blocks["total"]["trend"], 4),
        "trend_mass_mm_yr": round(blocks["mass"]["trend"], 4),
        "trend_steric_mm_yr": round(blocks["steric"]["trend"], 4),
        "trend_total_interval": blocks["total"],
        "trend_mass_interval": blocks["mass"],
        "trend_steric_interval": blocks["steric"],
        "partition_residual_max": float(np.abs(resid).max()),
        "series_by_month": {
            "dates": dates,
            "total_anomaly_m": [float(v) for v in ta],
            "mass_anomaly_m": [float(v) for v in ma],
            "steric_anomaly_m": [float(v) for v in sa],
            "residual_mm": [round(float(r) * 1000.0, 4) for r in resid],
        },
    }


def trend_interval_mm_yr(series_mm):
    """Each trend and its interval, from the one sanctioned method."""
    path = Path(__file__).with_name("ecco_trend_ci.py")
    spec = importlib.util.spec_from_file_location("ecco_trend_ci", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.interval_block(series_mm, "mm/year")


def data_identity(root):
    """Which tree fed this run. The root, and the RECORD.json stamp the
    verify tool leaves in a tree it has checked against its manifest
    (record name, manifest sha256, verification time, report sha256).
    A tree with no stamp is recorded as unverified, never invented."""
    root = Path(root).expanduser().resolve()
    stamp = root / "RECORD.json"
    return {"data_root": str(root),
            "record": json.loads(stamp.read_text()) if stamp.exists()
            else "unverified: no RECORD.json in this tree"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--region", required=True, choices=sorted(REGIONS),
                    help="registered region name (declared parameter)")
    ap.add_argument("--period", required=True,
                    help="YYYY-MM:YYYY-MM within 1992-01..2017-12 (declared parameter)")
    ap.add_argument("--data-root", type=Path, default=Path.home() / "ECCO_V4r4",
                    help="cache root (execution plumbing, not a parameter)")
    ap.add_argument("--receipt", type=Path, default=None)
    args = ap.parse_args()

    stats = compute(args.region, args.period, args.data_root)
    print(f"region {args.region}, {stats['months']} months, "
          f"{stats['cells_evaluated']} cells", file=sys.stderr)
    for part in ("total", "mass", "steric"):
        iv = stats[f"trend_{part}_interval"]
        band = (f"95% [{iv['ci_low']:+.4f}, {iv['ci_high']:+.4f}] "
                f"(r1 {iv['r1']:+.4f}, n_eff {iv['n_eff']:.2f} of {iv['n']}, "
                f"deseasonalize {iv['deseasonalize']}; "
                f"{'significant' if iv['significant_at_confidence'] else 'NOT significant'})"
                if iv["stated"] else f"no interval stated: {iv['reason']}")
        print(f"trend {part} {stats[f'trend_{part}_mm_yr']:+.4f} mm/yr, {band}",
              file=sys.stderr)
    print(f"partition residual max {stats['partition_residual_max']:.3e} m; "
          f"monthly series (mm): {stats['series_by_month']['residual_mm']}",
          file=sys.stderr)

    receipt = {
        "run_id": (datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "data": data_identity(args.data_root),
        "bound_parameters": {"region": args.region, "period": args.period},
        **stats,
    }
    text = json.dumps(receipt, indent=2)
    if args.receipt:
        args.receipt.write_text(text + "\n", encoding="utf-8")
        print(f"receipt written: {args.receipt}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
