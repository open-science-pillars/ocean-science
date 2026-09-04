#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4"]
# ///
"""Sanctioned computation: steric height anomaly from ECCO v4r4 density.

steric_h(column) = -(1/rho0) * sum_k( RHOAnoma * hFacC * drF )   [m]

The model's own density anomaly integrated over depth with partial-cell
weighting, the same steric formulation the attested regional sea level
partition uses, which is exactly the point: for the registered
reference region and period, this computation must reproduce the
steric trend that the sea-level partition's signed receipt already
carries. Area means are rA-weighted over wet surface cells. The trend and its
interval come from the one sanctioned trend method (ecco_trend_ci.py,
imported from beside this file and named by hash in the receipt's
interval block): a least-squares slope across the requested months,
jointly with the monthly climatology over complete years, per month
scaled to mm/yr, so no consumer meets the trend without the interval
and the attester recomputes both from the series in the receipt.

Regions are the registry the sea-level computation uses; "global" adds
the whole-ocean mean, and any global-mean steric statement carries the
Boussinesq caveat (a Boussinesq model conserves volume, so global-mean
steric change is a diagnostic overlay, not a modeled sea-surface rise).

Usage:
  ecco_steric_height.py --region us-northeast-coast --months 2010-01 ... 2010-12
      [--data-root ~/ECCO_V4r4] [--receipt steric_receipt.json]
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import uuid
from pathlib import Path

import netCDF4
import numpy as np

RHO0 = 1029.0
COLLECTION = "ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4"
GEOMETRY = "geometry/GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"
REGIONS = {
    # Boxes are KEYED, not positional. Two sanctioned computations once
    # stored these as bare tuples in opposite orders, so the same region
    # names resolved to different water (gulf-of-mexico differed by 8
    # percent in area, north-sea by 18.5). Keys make that class of error
    # impossible to reintroduce silently.
    "us-northeast-coast": {"lat": (35.0, 45.0), "lon": (-75.0, -65.0)},
    "gulf-of-mexico": {"lat": (18.0, 31.0), "lon": (-98.0, -81.0)},
    "north-sea": {"lat": (51.0, 60.0), "lon": (-2.0, 9.0)},
    "global": None,
}


def trend_interval_mm_yr(series):
    """The trend and its interval, from the one sanctioned method."""
    path = Path(__file__).with_name("ecco_trend_ci.py")
    spec = importlib.util.spec_from_file_location("ecco_trend_ci", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.interval_block([s * 1000.0 for s in series], "mm/year")


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
    ap.add_argument("--region", choices=sorted(REGIONS), required=True)
    ap.add_argument("--months", nargs="+", required=True)
    ap.add_argument("--data-root", type=Path, default=Path.home() / "ECCO_V4r4")
    ap.add_argument("--receipt", type=Path, default=Path("steric_receipt.json"))
    args = ap.parse_args()

    g = netCDF4.Dataset(args.data_root / GEOMETRY)
    rA = np.asarray(g["rA"][:])
    drF = np.asarray(g["drF"][:])
    hFacC = np.asarray(g["hFacC"][:])
    maskC0 = np.asarray(g["maskC"][0]).astype(bool)
    yc = np.asarray(g["YC"][:]); xc = np.asarray(g["XC"][:])

    box = REGIONS[args.region]
    if box is None:
        inbox = maskC0
    else:
        lat0, lat1 = box["lat"]
        lon0, lon1 = box["lon"]
        inbox = ((yc >= lat0) & (yc <= lat1)
                 & (xc >= lon0) & (xc <= lon1) & maskC0)
    w = rA * inbox
    wsum = float(w.sum())
    assert wsum > 0, "region selects no wet cells"
    hfac_drf = hFacC * drF[:, None, None, None]

    series = []
    for month in args.months:
        fn = (args.data_root / COLLECTION /
              f"OCEAN_DENS_STRAT_PRESS_mon_mean_{month}_ECCO_V4r4_native_llc0090.nc")
        ds = netCDF4.Dataset(fn)
        rho = np.nan_to_num(np.asarray(ds["RHOAnoma"][0]))  # (50,13,90,90)
        steric_col = -(rho * hfac_drf).sum(axis=0) / RHO0   # (13,90,90) m
        series.append(float((steric_col * w).sum() / wsum))
        ds.close()

    anom = [s - float(np.mean(series)) for s in series]
    receipt = {
        "run_id": (datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + str(uuid.uuid4())[:8]),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "data": data_identity(args.data_root),
        "bound_parameters": {
            "region": args.region,
            "months": list(args.months),
            "collection": COLLECTION,
            "rho0_kg_m3": RHO0,
        },
        "steric_mean_m_by_month": {m: s for m, s in zip(args.months, series)},
        "steric_anomaly_m_by_month": {m: a for m, a in zip(args.months, anom)},
        "cells_in_region": int(inbox.sum()),
        "generated_at": (datetime.datetime.now(datetime.timezone.utc)
                         .strftime("%Y-%m-%dT%H:%M:%SZ")),
    }
    if len(series) >= 3:
        receipt["steric_trend_interval"] = trend_interval_mm_yr(series)
        receipt["steric_trend_mm_yr"] = receipt["steric_trend_interval"]["trend"]
    if args.region == "global":
        receipt["boussinesq_caveat"] = (
            "a Boussinesq model conserves volume, so a global-mean steric "
            "change is a diagnostic overlay, not a modeled sea-surface rise")

    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n",
                            encoding="utf-8")
    print(f"run {receipt['run_id']}: region {args.region}, "
          f"{len(series)} months, {receipt['cells_in_region']} cells")
    for m, s in zip(args.months, series):
        print(f"  {m}: area-mean steric height {s:+.6f} m")
    if "steric_trend_mm_yr" in receipt:
        print(f"  steric trend: {receipt['steric_trend_mm_yr']:+.4f} mm/yr")
        iv = receipt["steric_trend_interval"]
        if iv["stated"]:
            print(f"  95% interval: [{iv['ci_low']:+.4f}, {iv['ci_high']:+.4f}] "
                  f"mm/yr (r1 {iv['r1']:+.4f}, n_eff {iv['n_eff']:.2f} of "
                  f"{iv['n']}, deseasonalize {iv['deseasonalize']}; "
                  f"{'significant' if iv['significant_at_confidence'] else 'NOT significant'})")
        else:
            print(f"  no interval stated: {iv['reason']}")
    print(f"  receipt -> {args.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
