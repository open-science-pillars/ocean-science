# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "xarray", "netCDF4", "dask"]
# ///
"""Attested Reynolds flux decomposition on the ECCO V4r4 native grid.

WHAT IT COMPUTES
The meridional heat flux v times T through a registered region's
interior south faces, decomposed about the declared time mean:
  v T = vbar Tbar + vbar T' + v' Tbar + v' T'
with overbar the EQUAL-WEIGHT mean of the declared months and primes
the monthly departures. The grouping question (which terms a study
should report) is a scope choice this computation deliberately does
NOT settle: the grouping travels as a declared parameter and the
receipt disclosed which convention produced the numbers, so two
results can be compared honestly.
  full-four-term   all four terms reported
  time-mean-eddy   mean flux = vbar Tbar + mean(v' T'), the two cross
                   terms vanishing under the time mean
  anomaly          the departure v T - vbar Tbar, split into its
                   three terms

TWO MATHEMATICAL ORACLES, both enforced before any receipt exists:
  identity     the four terms sum back to v T at round-off, per face
               per month (this holds for ANY split point, so alone it
               proves only algebra);
  cross-terms  the time means of vbar T' and v' Tbar vanish at
               round-off, which holds ONLY when the overbar is the
               true mean of the declared window; a stale or partial
               mean cannot pass this, and this is the oracle with
               teeth.

MUTATION EVIDENCE in every receipt: a cross term dropped from the sum
(the identity catches it) and the mean taken over half the window
(the cross-term oracle catches it). Both structural: if either
sabotage passes, no receipt is written.

Velocity is VVELMASS (mass-weighted, at south faces); temperature is
THETA averaged to the same faces, both-side wet cells only. Aggregates
are reported as face-integrated transports (times dxG times drF, no
partial-cell factor on the MASS velocity; the averaged THETA carries
none) scaled by rhoConst times Cp to petawatts.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import uuid
from pathlib import Path

import numpy as np
import xarray as xr

RHOCONST, C_P = 1029.0, 3994.0
IDENTITY_BAR = 1e-12      # relative to the field scale
CROSS_BAR = 1e-12
VOLF = "ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4"
TS = "ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4"
GEOM = "geometry/GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"

REGIONS = {
    "southeast-atlantic-upper": {"tile": 1, "j": (20, 60), "i": (20, 60),
                                 "k_cells": 20},
}
GROUPINGS = ["full-four-term", "time-mean-eddy", "anomaly"]


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
    ap.add_argument("--region", choices=sorted(REGIONS), required=True)
    ap.add_argument("--grouping", choices=GROUPINGS, required=True)
    ap.add_argument("--year", type=int, default=2010)
    ap.add_argument("--data-root", type=Path,
                    default=Path.home() / "ECCO_V4r4")
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    r = REGIONS[args.region]
    tile, (j0, j1), (i0, i1), K = r["tile"], r["j"], r["i"], r["k_cells"]

    geom_path = args.data_root / GEOM
    grid = xr.open_dataset(geom_path).isel(tile=tile)

    def monthly(s):
        d = xr.open_mfdataset(str(args.data_root / s / "*.nc"),
                              combine="by_coords").isel(tile=tile)
        d = d.sel(time=slice(f"{args.year}-01-01", f"{args.year}-12-31"))
        assert d.sizes["time"] == 12, f"{s}: want 12 months"
        return d

    v = np.nan_to_num(monthly(VOLF).VVELMASS.values).astype(np.float64)
    th = monthly(TS).THETA.values.astype(np.float64)
    hfacc = grid.hFacC.values

    # THETA to south faces, both-side wet only; faces interior to the box
    jj = slice(j0 + 1, j1)          # face j_g = j, between cells j-1 and j
    ii = slice(i0, i1)
    wet2 = (hfacc[:K, j0:j1 - 1, i0:i1] > 0) & (hfacc[:K, j0 + 1:j1, i0:i1] > 0)
    Tf = 0.5 * (np.nan_to_num(th[:, :K, j0:j1 - 1, i0:i1])
                + np.nan_to_num(th[:, :K, j0 + 1:j1, i0:i1]))
    vf = v[:, :K, jj, ii]
    Tf = np.where(wet2[None], Tf, 0.0)
    vf = np.where(wet2[None], vf, 0.0)

    F = vf * Tf
    vbar, Tbar = vf.mean(axis=0), Tf.mean(axis=0)
    vp, Tp = vf - vbar[None], Tf - Tbar[None]
    mm = np.broadcast_to((vbar * Tbar)[None], F.shape)
    mp, pm, pp = vbar[None] * Tp, vp * Tbar[None], vp * Tp

    scale = float(np.abs(F).max())
    ident = float(np.abs(F - (mm + mp + pm + pp)).max() / scale)
    cross = float(max(np.abs(mp.mean(axis=0)).max(),
                      np.abs(pm.mean(axis=0)).max()) / scale)
    if ident > IDENTITY_BAR or cross > CROSS_BAR:
        raise SystemExit(f"oracles failed on the correct computation "
                         f"(identity {ident:.1e}, cross {cross:.1e}); "
                         "no receipt written")

    # mutation evidence, both structural
    ident_dropped = float(np.abs(F - (mm + mp + pp)).max() / scale)
    if ident_dropped <= IDENTITY_BAR:
        raise SystemExit("cross-term-dropped sabotage NOT caught; "
                         "no receipt written")
    vbar6 = vf[:6].mean(axis=0)
    mp6 = vbar6[None] * (Tf - Tf[:6].mean(axis=0)[None])
    pm6 = (vf - vbar6[None]) * Tf[:6].mean(axis=0)[None]
    cross6 = float(max(np.abs(mp6.mean(axis=0)).max(),
                       np.abs(pm6.mean(axis=0)).max()) / scale)
    if cross6 <= CROSS_BAR:
        raise SystemExit("stale-mean sabotage NOT caught; no receipt written")
    evidence = [
        {"mutation": "cross-term-dropped", "identity_rel": ident_dropped,
         "caught": True},
        {"mutation": "stale-mean-half-window", "cross_term_rel": cross6,
         "caught": True},
    ]

    # aggregates: face-integrated, PW
    w = (grid.dxG.values[jj, ii][None]
         * grid.drF.values[:K, None, None])          # (K, jfaces, i)
    def agg(x):
        return float((x.mean(axis=0) * w).sum() * RHOCONST * C_P / 1e15)
    terms_all = {"mean-mean_PW": agg(mm), "mean-prime_PW": agg(mp),
                 "prime-mean_PW": agg(pm), "prime-prime_PW": agg(pp),
                 "total_PW": agg(F)}
    if args.grouping == "full-four-term":
        reported = terms_all
    elif args.grouping == "time-mean-eddy":
        reported = {"mean-advective_PW": terms_all["mean-mean_PW"],
                    "eddy_PW": terms_all["prime-prime_PW"],
                    "total_PW": terms_all["total_PW"]}
    else:
        reported = {"anomaly-total_PW":
                    terms_all["total_PW"] - terms_all["mean-mean_PW"],
                    "mean-prime_PW": terms_all["mean-prime_PW"],
                    "prime-mean_PW": terms_all["prime-mean_PW"],
                    "prime-prime_PW": terms_all["prime-prime_PW"]}

    code = Path(__file__).read_bytes()
    receipt = {
        "run_id": (dt.datetime.now(dt.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]),
        "computation": "ecco-flux-decomposition",
        "code_sha256": hashlib.sha256(code).hexdigest(),
        "data": data_identity(args.data_root),
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "bound_parameters": {
            "region": args.region, "grouping": args.grouping,
            "year": args.year, "collections": [VOLF, TS],
            "mean_convention": "equal-weight mean of the 12 declared "
                               "months; primes are monthly departures",
            "rhoConst_kg_m3": RHOCONST, "Cp_J_kg_K": C_P,
            "identity_bar_rel": IDENTITY_BAR, "cross_bar_rel": CROSS_BAR,
        },
        "resolved_faces": {
            "tile": tile, "j_faces": [j0 + 1, j1], "i": [i0, i1],
            "k_cells": K, "faces_wet": int(wet2.sum()),
            "mask_sha256": hashlib.sha256(
                wet2.astype(np.uint8).tobytes()).hexdigest(),
            "geometry_sha256": hashlib.sha256(
                geom_path.read_bytes()).hexdigest(),
        },
        "results": {
            "identity_max_rel": ident,
            "cross_term_mean_max_rel": cross,
            "reported_terms": reported,
            "all_terms_PW": terms_all,
        },
        "mutation_evidence": evidence,
        "caveats": {
            "grouping": "the grouping is a declared reporting "
                        "convention, not a physical choice; the four "
                        "stored terms are identical across groupings "
                        "and all travel in all_terms_PW",
            "faces": "interior south faces of the registered region "
                     "only; this is a within-box decomposition, not a "
                     "basin transport",
        },
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"run {receipt['run_id']}: {args.region}, {args.grouping}, "
          f"year {args.year}")
    print(f"  faces {int(wet2.sum()):,}; identity {ident:.2e}; "
          f"cross-term means {cross:.2e}")
    for k, val in reported.items():
        print(f"  {k:18s} {val:+.5f}")
    print(f"  mutations caught: 2/2")
    print(f"  receipt -> {args.receipt}")


if __name__ == "__main__":
    main()
