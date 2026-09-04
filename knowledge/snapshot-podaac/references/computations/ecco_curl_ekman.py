# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4"]
# ///
"""Attested wind-stress curl and Ekman pumping on the ECCO V4r4 native
llc90 grid, validated against the model's own vertical velocity.

WHAT IT COMPUTES
1. WIND-STRESS CURL at tracer points, in each tile's LOCAL grid frame:
   curl(tau) = d(tau_y)/dx - d(tau_x)/dy. The curl of a horizontal
   vector field is invariant under a local orthogonal rotation of the
   frame, so computing it entirely in the stored tile frame NEEDS NO
   ROTATION AT ALL. This sidesteps the trap the curl gotcha records
   (vector components rotated once for one purpose, then differenced in
   a frame they no longer match): we never mix frames, so there is no
   second rotation to forget. The staggered ocean-surface stresses
   oceTAUX (west faces) and oceTAUY (south faces) are averaged to cell
   centers before differencing.

2. EKMAN PUMPING: w_ek = (1/rho0) * [d(tau_y/f)/dx - d(tau_x/f)/dy],
   the vertical velocity the wind curl demands at the base of the Ekman
   layer. Compared against the model's actual WVEL at the interface
   nearest --wvel-depth-m (default 70 m, below the surface layer),
   over the open-ocean interior (10 <= |lat| <= 55 degrees, seafloor
   deeper than 3000 m; the equatorial band is excluded because f -> 0
   makes w_ek blow up, and shelf seas are excluded because coastal
   upwelling there is not wind-curl driven at the grid scale).
   Reported: Pearson correlation and median absolute difference.
   The model's WVEL contains everything (eddies, mixing, topographic
   steering), not only Ekman pumping, so the expected agreement is
   MODERATE by construction: the comparison validates sign and pattern,
   not equality.

INPUTS (local files only; retrieval is a separate, credentialed step)
  ECCO_L4_STRESS_LLC0090GRID_MONTHLY_V4R4      oceTAUX, oceTAUY
  ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4   WVEL (interface levels)
  geometry GRID_GEOMETRY_ECCO_V4r4_native      dxC, dyC, Depth, YC, Z l

Emits a JSON receipt: run_id, code sha256, bound parameters, measured
correlations and medians, cells evaluated.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import uuid
from pathlib import Path

import numpy as np
import netCDF4

RHO0 = 1029.0
OMEGA = 7.2921e-5
STRESS = "ECCO_L4_STRESS_LLC0090GRID_MONTHLY_V4R4"
VEL = "ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4"
GEOM = "geometry/GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"


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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path,
                    default=Path.home() / "ECCO_V4r4")
    ap.add_argument("--month", default="2009-12")
    ap.add_argument("--wvel-depth-m", type=float, default=70.0)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()

    grid = netCDF4.Dataset(args.data_root / GEOM)
    yc = np.asarray(grid["YC"][:])
    dxC = np.asarray(grid["dxC"][:])
    dyC = np.asarray(grid["dyC"][:])
    depth = np.asarray(grid["Depth"][:])
    maskC = np.asarray(grid["maskC"][0])   # surface wet mask
    f = 2.0 * OMEGA * np.sin(np.deg2rad(yc))

    st = netCDF4.Dataset(
        args.data_root / STRESS /
        f"OCEAN_AND_ICE_SURFACE_STRESS_mon_mean_{args.month}"
        "_ECCO_V4r4_native_llc0090.nc")
    taux_w = np.asarray(st["oceTAUX"][0])   # at west faces (i_g)
    tauy_s = np.asarray(st["oceTAUY"][0])   # at south faces (j_g)

    vds = netCDF4.Dataset(
        args.data_root / VEL /
        f"OCEAN_VELOCITY_mon_mean_{args.month}_ECCO_V4r4_native_llc0090.nc")
    Zl = np.asarray(vds["Zl"][:])
    kw = int(np.argmin(np.abs(Zl + args.wvel_depth_m)))
    wvel = np.asarray(vds["WVEL"][0][kw])

    # Staggered stresses to cell centers (local frame throughout).
    taux = np.full_like(yc, np.nan)
    taux[:, :, :-1] = 0.5 * (taux_w[:, :, :-1] + taux_w[:, :, 1:])
    tauy = np.full_like(yc, np.nan)
    tauy[:, :-1, :] = 0.5 * (tauy_s[:, :-1, :] + tauy_s[:, 1:, :])
    dry = maskC == 0
    taux[dry] = np.nan
    tauy[dry] = np.nan

    def ddx(a: np.ndarray) -> np.ndarray:
        out = np.full_like(a, np.nan)
        out[:, :, 1:-1] = (a[:, :, 2:] - a[:, :, :-2]) / (2 * dxC[:, :, 1:-1])
        return out

    def ddy(a: np.ndarray) -> np.ndarray:
        out = np.full_like(a, np.nan)
        out[:, 1:-1, :] = (a[:, 2:, :] - a[:, :-2, :]) / (2 * dyC[:, 1:-1, :])
        return out

    curl = ddx(tauy) - ddy(taux)                     # N m-3
    with np.errstate(all="ignore"):
        w_ek = (ddx(tauy / f) - ddy(taux / f)) / RHO0   # m s-1

    margin = np.zeros_like(yc, dtype=bool)
    margin[:, 3:-3, 3:-3] = True
    valid = (margin & (np.abs(yc) >= 10.0) & (np.abs(yc) <= 55.0)
             & (depth > 3000.0) & np.isfinite(w_ek) & np.isfinite(wvel)
             & np.isfinite(curl))
    r_ek = float(np.corrcoef(w_ek[valid], wvel[valid])[0, 1])
    med = float(np.median(np.abs(w_ek[valid] - wvel[valid])))
    curl_abs_med = float(np.median(np.abs(curl[valid])))

    code = Path(__file__).read_bytes()
    receipt = {
        "run_id": (dt.datetime.now(dt.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ")
                   + "-" + uuid.uuid4().hex[:8]),
        "computation": "ecco-wind-stress-curl-ekman",
        "code_sha256": hashlib.sha256(code).hexdigest(),
        "data": data_identity(args.data_root),
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "bound_parameters": {
            "month": args.month,
            "stress_collection": STRESS,
            "velocity_collection": VEL,
            "rho0_kg_m3": RHO0,
            "wvel_interface_m": float(-Zl[kw]),
            "validation_domain":
                "10-55 deg latitude, seafloor deeper than 3000 m",
        },
        "results": {
            "r_ekman_vs_wvel": r_ek,
            "median_abs_diff_m_s": med,
            "median_abs_curl_N_m3": curl_abs_med,
            "n_points": int(valid.sum()),
        },
        "method_caveat": (
            "curl computed entirely in each tile's local grid frame; "
            "curl is rotation-invariant so no component rotation is "
            "performed or needed. WVEL contains all vertical motion, "
            "not only Ekman pumping, so r validates sign and pattern, "
            "not equality."),
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"run {receipt['run_id']}: month {args.month}")
    print(f"  Ekman pumping vs model WVEL at {-Zl[kw]:.0f} m, open-ocean "
          f"interior: r = {r_ek:.4f}, median |diff| = {med:.2e} m/s, "
          f"n = {valid.sum():,}")
    print(f"  median |curl| = {curl_abs_med:.2e} N m-3")
    print(f"  receipt -> {args.receipt}")


if __name__ == "__main__":
    main()
