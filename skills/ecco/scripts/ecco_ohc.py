#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4"]
# ///
"""Sanctioned computation: global ocean heat content from ECCO v4r4.

OHC = rhoConst * Cp * sum_wet_cells( THETA * rA * drF * hFacC )

THETA is potential temperature (degC), so the absolute number is heat
content relative to an arbitrary 0 degC baseline; the CHANGE between
two months is the physically meaningful quantity, and the receipt
reports both with the baseline caveat attached. Volume weighting is
rA * drF * hFacC: cell area times layer thickness times the wet
fraction, with hFacC doubling as the land mask (zero on land).

Constants are the ECCO/MITgcm values the budget formulation records:
rhoConst = 1029 kg m-3, Cp = 3994 J kg-1 K-1.

Anchors computed alongside, for the attester:
- total ocean surface area, (rA * maskC[k=0]).sum(), which the ECCO
  scalar-quantities tutorial publishes as 3.58E+08 km2;
- total ocean volume, (rA * drF * hFacC).sum();
- per-month volume-mean THETA, a physical-sanity scalar.

The receipt carries the monthly OHC twice on purpose: `months`, a
list of per-month records with the volume-mean THETA beside each
value, and `ohc_J_by_month`, the same values as a {YYYY-MM: J}
mapping in month order. The mapping is the form every downstream
sanctioned computation reads (the trend-with-interval computation
takes `--field ohc_J_by_month` and copies this receipt's data stamp
forward), so a deseasonalized OHC series or trend inherits its
provenance from this receipt instead of from a hand-built file. The
attester requires both and fails a receipt whose two forms disagree.

Inputs are the cached native monthly TEMP_SALINITY granules plus the
geometry granule (the fixture layout under --data-root). Deterministic:
same inputs, same numbers.

Usage:
  ecco_ohc.py --months 2010-01 2010-12 [--data-root ~/ECCO_V4r4]
      [--receipt ohc_receipt.json]
  ecco_trend_ci.py --source ohc_receipt.json --field ohc_J_by_month \
      --value-units J --scale 1e-21 --report-units ZJ
"""

import argparse
import datetime
import hashlib
import json
import uuid
from pathlib import Path

import netCDF4
import numpy as np

RHOCONST = 1029.0   # kg m-3, Boussinesq reference density (MITgcm)
CP = 3994.0         # J kg-1 K-1, seawater heat capacity (MITgcm)
COLLECTION = "ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4"
GEOMETRY = "geometry/GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"


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
    ap.add_argument("--months", nargs="+", required=True,
                    help="YYYY-MM, one or more; change is last minus first")
    ap.add_argument("--data-root", type=Path,
                    default=Path.home() / "ECCO_V4r4")
    ap.add_argument("--receipt", type=Path, default=Path("ohc_receipt.json"))
    args = ap.parse_args()

    g = netCDF4.Dataset(args.data_root / GEOMETRY)
    rA = np.asarray(g["rA"][:])                     # (13, 90, 90) m2
    drF = np.asarray(g["drF"][:])                   # (50,) m
    hFacC = np.asarray(g["hFacC"][:])               # (50, 13, 90, 90)
    maskC = np.asarray(g["maskC"][:]).astype(bool)  # (50, 13, 90, 90)
    vol = rA[None, :, :, :] * drF[:, None, None, None] * hFacC  # m3
    total_volume = float(vol.sum())
    surface_area_km2 = float((rA * maskC[0]).sum()) / 1e6

    months_out = []
    for month in args.months:
        fn = (args.data_root / COLLECTION /
              f"OCEAN_TEMPERATURE_SALINITY_mon_mean_{month}_ECCO_V4r4_native_llc0090.nc")
        ds = netCDF4.Dataset(fn)
        theta = np.nan_to_num(np.asarray(ds["THETA"][0]))  # (50, 13, 90, 90)
        weighted = float((theta * vol).sum())
        months_out.append({
            "month": month,
            "volume_mean_theta_degC": weighted / total_volume,
            "ohc_J": RHOCONST * CP * weighted,
        })
        ds.close()

    receipt = {
        "run_id": (datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + str(uuid.uuid4())[:8]),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "data": data_identity(args.data_root),
        "bound_parameters": {
            "months": list(args.months),
            "collection": COLLECTION,
            "rhoConst_kg_m3": RHOCONST,
            "Cp_J_kg_K": CP,
        },
        "anchors": {
            "ocean_surface_area_km2": surface_area_km2,
            "ocean_volume_m3": total_volume,
        },
        "months": months_out,
        "ohc_J_by_month": {m["month"]: m["ohc_J"] for m in months_out},
        "ohc_baseline_caveat": ("THETA is potential temperature, so each "
                                "ohc_J is relative to an arbitrary 0 degC "
                                "baseline; only changes are physical"),
        "cells_evaluated": int(maskC.sum()),
        "generated_at": (datetime.datetime.now(datetime.timezone.utc)
                         .strftime("%Y-%m-%dT%H:%M:%SZ")),
    }
    if len(months_out) >= 2:
        receipt["ohc_change_J"] = months_out[-1]["ohc_J"] - months_out[0]["ohc_J"]
        receipt["ohc_change_between"] = [months_out[0]["month"],
                                         months_out[-1]["month"]]
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n",
                            encoding="utf-8")

    print(f"run {receipt['run_id']}")
    print(f"  ocean surface area: {surface_area_km2:.4e} km2")
    print(f"  ocean volume:       {total_volume:.4e} m3")
    for m in months_out:
        print(f"  {m['month']}: volume-mean THETA {m['volume_mean_theta_degC']:.4f} degC,"
              f" OHC {m['ohc_J']:.6e} J")
    if "ohc_change_J" in receipt:
        a, b = receipt["ohc_change_between"]
        print(f"  OHC change {a} -> {b}: {receipt['ohc_change_J']:+.4e} J")
    print(f"  cells evaluated: {receipt['cells_evaluated']:,}")
    print(f"  receipt -> {args.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
