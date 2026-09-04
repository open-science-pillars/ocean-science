#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy",
#     "xarray",
#     "netcdf4",
#     "ecco_v4_py",
# ]
# ///
"""Sanctioned computation for the attested ECCO v4r4 heat budget.

EXTRACTED 2026-08-30 from the ocean-science golden notebook
(verification/ocean_budget.py); the four-term formulation is exactly as
skills/ecco/references/budget-formulation.md records it (tutorial-quoted,
verified line by line 2026-07-04). The numerics below are the golden's
cells verbatim; this file adds only parameter binding (year, region),
data-cache path resolution, and receipt emission.

Contract: podaac/computations/ecco-heat-budget.md (type: Attested
Computation). Consumers bind values for the declared parameters and MUST
NOT edit this file; the attester (references/attesters/budget_residual.py)
hashes it, so any edit fails attestation by construction (spec 10.3).

Receipt (JSON to stdout, or --receipt PATH): run_id, code_sha256,
bound_parameters, residual_max, residual_p999, cells_evaluated.
"""

import argparse
import datetime
import hashlib
import json
import sys
import uuid
from pathlib import Path

import ecco_v4_py as ecco
import numpy as np
import xarray as xr

# Tutorial constants (budget-formulation.md, "Constants and the volume
# element") and the fixture region geometry.
RHOCONST, C_P = 1029.0, 3994.0
R_SW, ZETA1, ZETA2 = 0.62, 0.6, 20.0
REGIONS = {
    # region name -> (tile index, interior slice bound). tile1-interior is
    # the fixture-verified subset (South Atlantic tile; interior j,i in
    # 0..88 needs no tile-seam operators; pointwise closure holds on any
    # spatial subset per the recipe's domain caveat).
    "tile1-interior": (1, 89),
}


def compute(year: int, region: str, data_root: Path) -> dict:
    tile, interior = REGIONS[region]

    grid = xr.open_dataset(
        data_root / "geometry" / "GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"
    ).isel(tile=tile)

    def monthly(short_name):
        ds = xr.open_mfdataset(
            str(data_root / short_name / "*.nc"), combine="by_coords"
        ).isel(tile=tile)
        ds = ds.sel(time=slice(f"{year}-01-01", f"{year}-12-31"))
        assert ds.sizes["time"] == 12, (
            f"{short_name}: want 12 monthly means for {year}, "
            f"got {ds.sizes['time']}")
        return ds

    def snapshots(short_name):
        ds = xr.open_mfdataset(
            str(data_root / short_name / "*.nc"), combine="by_coords"
        ).isel(tile=tile)
        ds = ds.sel(time=slice(f"{year}-01-01", f"{year + 1}-01-01T23:59"))
        assert ds.sizes["time"] == 13, (
            f"{short_name}: want 13 month-boundary snapshots bracketing "
            f"{year}, got {ds.sizes['time']}")
        return ds

    flux = monthly("ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4")
    hf = monthly("ECCO_L4_HEAT_FLUX_LLC0090GRID_MONTHLY_V4R4")
    snp_ts = snapshots("ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4")
    snp_ssh = snapshots("ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4")
    assert "ETAN" in snp_ssh, (
        f"ETAN missing from SSH snapshots: {sorted(snp_ssh.data_vars)}")

    dt = (snp_ts.time.values[1:] - snp_ts.time.values[:-1]) / np.timedelta64(1, "s")
    dt = dt.astype(np.float64)                     # seconds per month, (12,)

    # TERM 1: tendency with the z* scale factor (formulation term 1).
    depth = grid.Depth.values                       # (90, 90)
    theta_snp = snp_ts.THETA.values                 # (13, 50, 90, 90)
    etan_snp = snp_ssh.ETAN.values                  # (13, 90, 90)
    with np.errstate(divide="ignore", invalid="ignore"):
        sfac = np.where(depth > 0, 1.0 + etan_snp / depth, 1.0)   # (13, 90, 90)
    stheta = theta_snp * sfac[:, None, :, :]
    g_total = (stheta[1:] - stheta[:-1]) / dt[:, None, None, None]  # (12, 50, 90, 90)

    # Volume element (partial cells IN) and the within-tile convergences.
    vol = (grid.rA.values[None, :, :] * grid.drF.values[:, None, None]
           * grid.hFacC.values)                     # (50, 90, 90)

    hfacc = grid.hFacC.values
    ax = np.nan_to_num(flux.ADVx_TH.values)         # (12, 50, 90, 90) at i_g
    ay = np.nan_to_num(flux.ADVy_TH.values)         # at j_g
    dx = np.nan_to_num(flux.DFxE_TH.values)
    dy = np.nan_to_num(flux.DFyE_TH.values)

    def h_conv(fx_, fy_):
        # convergence for interior cells i,j in 0..interior-1: -(d/dx + d/dy)
        return -((fx_[:, :, :interior, 1:interior + 1] - fx_[:, :, :interior, 0:interior])
                 + (fy_[:, :, 1:interior + 1, 0:interior] - fy_[:, :, 0:interior, 0:interior]))

    def v_conv(fr):                                 # fr at k_l, (12, 50, 90, 90)
        fr = np.nan_to_num(fr)
        fr = np.where(hfacc[None] > 0, fr, 0.0)     # dry-cell garbage out
        frp = np.concatenate([fr, np.zeros_like(fr[:, :1])], axis=1)  # pad bottom
        return (frp[:, 1:] - frp[:, :-1])           # (12, 50, 90, 90)

    adv_h = h_conv(ax, ay)
    dif_h = h_conv(dx, dy)
    adv_v = v_conv(flux.ADVr_TH.values)[:, :, :interior, :interior]
    dif_v = v_conv(flux.DFrE_TH.values + flux.DFrI_TH.values)[:, :, :interior, :interior]

    vol_i = vol[:, :interior, :interior]
    with np.errstate(divide="ignore", invalid="ignore"):
        g_adv = np.where(vol_i > 0, (adv_h + adv_v) / vol_i, 0.0)
        g_dif = np.where(vol_i > 0, (dif_h + dif_v) / vol_i, 0.0)

    # TERM 4: forcing with shortwave penetration and geothermal.
    Z = grid.Z.values                                # (50,) cell centers
    RF = np.concatenate([grid.Zp1.values[:-1], [np.nan]])  # upper faces + pad
    q1 = R_SW * np.exp(RF[:-1] / ZETA1) + (1 - R_SW) * np.exp(RF[:-1] / ZETA2)
    q2 = R_SW * np.exp(RF[1:] / ZETA1) + (1 - R_SW) * np.exp(RF[1:] / ZETA2)
    zcut = int(np.where(Z < -200)[0][0])
    q1[zcut:] = 0
    q2[zcut - 1:] = 0

    mskc = (grid.hFacC.values > 0).astype(np.float64)         # (50, 90, 90)
    mskc_dn = np.concatenate([mskc[1:], np.zeros_like(mskc[:1])], axis=0)

    tflux = np.nan_to_num(hf.TFLUX.values)           # (12, 90, 90)
    qsw = np.nan_to_num(hf.oceQsw.values)

    forc_sub = (q1[None, :, None, None] * (mskc[None] == 1)
                - q2[None, :, None, None] * (mskc_dn[None] == 1)) * qsw[:, None]
    forc_surf = (tflux - (1 - (q1[0] - q2[0])) * qsw) * mskc[0][None]
    forch = np.concatenate([forc_surf[:, None], forc_sub[:, 1:]], axis=1)

    geoflx = ecco.read_llc_to_tiles(str(data_root), "geothermalFlux.bin",
                                    less_output=True)
    geo_tile = np.asarray(geoflx)[tile]              # (90, 90)
    mskb = mskc - mskc_dn                            # bottom wet cell = 1
    geo3d = geo_tile[None, None] * mskb[None]        # (1, 50, 90, 90)

    hfac_drf = grid.hFacC.values * grid.drF.values[:, None, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        g_forc = np.where(hfac_drf[None] > 0,
                          ((forch + geo3d) / (RHOCONST * C_P)) / hfac_drf[None],
                          0.0)

    # Pointwise absolute residual on interior wet cells.
    gt = g_total[:, :, :interior, :interior]
    gf = g_forc[:, :, :interior, :interior]
    wet = grid.hFacC.values[:, :interior, :interior] > 0

    res = np.abs((gt - (g_adv + g_dif + gf))[np.broadcast_to(wet[None], gt.shape)])
    return {
        "residual_max": float(res.max()),
        "residual_p999": float(np.percentile(res, 99.9)),
        "residual_median": float(np.median(res)),
        "cells_evaluated": int(res.size),
    }


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
    ap.add_argument("--year", type=int, required=True,
                    help="calendar year the budget closes over (declared parameter)")
    ap.add_argument("--region", type=str, default="tile1-interior",
                    choices=sorted(REGIONS),
                    help="named spatial subset (declared parameter, optional)")
    ap.add_argument("--data-root", type=Path, default=Path.home() / "ECCO_V4r4",
                    help="fixture cache root (execution plumbing, not a parameter)")
    ap.add_argument("--receipt", type=Path, default=None,
                    help="write the receipt JSON here instead of stdout")
    args = ap.parse_args()

    stats = compute(args.year, args.region, args.data_root)
    med = stats.pop("residual_median")
    print(f"cells checked: {stats['cells_evaluated']} "
          f"(12 months x interior wet cells)", file=sys.stderr)
    print(f"absolute residual (degC/s): max {stats['residual_max']:.2e}, "
          f"p99.9 {stats['residual_p999']:.2e}, median {med:.2e}",
          file=sys.stderr)

    receipt = {
        "run_id": (datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "data": data_identity(args.data_root),
        "bound_parameters": {"year": args.year, "region": args.region},
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
