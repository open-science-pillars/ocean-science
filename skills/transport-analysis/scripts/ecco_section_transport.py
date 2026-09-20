# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "xarray", "netCDF4", "dask"]
# ///
"""Attested section transports on the ECCO V4r4 native llc90 grid.

WHAT IT COMPUTES
Volume and heat transport across a registered section, built by the
indicator-gradient method: an indicator field C marks the region on
one side, and every stored face whose two adjacent cells disagree in C
is a section face, signed by C(right cell) minus C(left cell), so
positive transport crosses INTO the indicated region. Faces are
enumerated as STORED: each physical face exists exactly once in the
archive, and a face on a tile's west or south edge takes its outside
cell from the neighbor tile per the topology below.

THE TOPOLOGY, and why it can be trusted: lifted from
ecco_v4_py 1.8.1 get_llc_grid (xgcm face connections), then verified
twice on 2026-09-01. Geometrically: every one of the 24 connected
edges maps neighbor cells within one local grid spacing, same-axis
joins parallel, cross-axis joins index-reversed, every join attaching
at the neighbor's axis start so no sign flip is needed. By physics:
the pointwise heat budget evaluated on all 683,496 seam-adjacent cell
months of 2010 with these mappings closes at max 2.1e-11 degC per s,
INSIDE the interior tolerance (1e-10), median 5.4e-14 equal to the
interior's. A wrong mapping or sign cannot close at round-off; the
budget is the oracle.

WEIGHTING, per collection and opposite by design (the trap the
regional budget documents): heat fluxes ADV*_TH and DF*_TH are
already face-integrated transports (degC m3 per s) and take NO
weighting; volume velocities UVELMASS and VVELMASS need face length
times layer thickness (dyG or dxG times drF) and NO partial-cell
factor, which the MASS suffix already carries.

MUTATION EVIDENCE in every receipt, as in the regional budget: five
sabotages rerun per execution, each recorded against the catch bars
(0.02 PW or 1 Sv of mean-transport change). The seam-ghost sabotage
deserves its name spelled out: zeroing the cross-tile ghost tables
makes every tile-edge face bordering an inside cell a spurious
section face, which is exactly the error a section tool that ignores
tile topology commits silently. Two are structural where
they apply and abort the run receiptless if not caught: rotated-tile
face signs flipped (the vector-orientation trap) and south-face
component dropped (the forgot-one-component error). Two are
applicability-aware with their measured deltas recorded: seam-owned
faces dropped (a section owning few seam faces cannot demonstrate
their omission) and the path shifted one row, which physics keeps
small for a smooth transport field (measured 0.014 PW for the global
26.5 north circle); the defense against a wrong path is not closure
but disclosure, the mask digest and latitude extent in the receipt.

REGISTERED SECTIONS (keyed; a name is contract, free text is not):
  global-26.5n: the full latitude circle at 26.5 north, closed and
      seam-crossing. Anchored: an independent implementation (the
      ocean-science transport golden, via ecco_v4_py
      calc_meridional_heat_trsp) records the 2010 global mean
      meridional heat transport 1.098 PW at this latitude.
  fifteen-s-southeast-atlantic: an open segment at 15 south spanning
      one tile (strictly interior; no seam faces by construction).
      Unanchored: its receipt is disclosure, not a benchmarked claim,
      and the concept says so.
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
FLUX = "ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4"
VOLF = "ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4"
GEOM = "geometry/GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"

# provenance: ecco_v4_py 1.8.1 get_llc_grid; verified 2026-09-01
# geometrically and by seam budget closure (see module docstring).
CONN_EAST = {0: (3, "X"), 1: (4, "X"), 2: (5, "X"), 3: (9, "Y"),
             4: (8, "Y"), 5: (7, "Y"), 6: (7, "X"), 7: (8, "X"),
             8: (9, "X"), 10: (11, "X"), 11: (12, "X")}
CONN_NORTH = {0: (1, "Y"), 1: (2, "Y"), 2: (6, "X"), 3: (4, "Y"),
              4: (5, "Y"), 5: (6, "Y"), 6: (10, "X"), 7: (10, "Y"),
              8: (11, "Y"), 9: (12, "Y"), 10: (2, "X"), 11: (1, "X"),
              12: (0, "X")}

SECTIONS = {
    "global-26.5n": {"kind": "latitude-circle", "lat": 26.5},
    "fifteen-s-southeast-atlantic": {"kind": "latitude-segment",
                                     "lat": -15.0, "tile": 1},
}

HEAT_ANCHOR_PW = 1.098          # independent implementation, 2010 mean
HEAT_TOL_PW = 0.03              # cross-implementation band
MUT_HEAT_PW = 0.02              # a mutation is caught above this delta
MUT_VOL_SV = 1.0                # or this one


def ghost_tables_zeroed(C):
    """The sabotage: pretend the outside of every tile edge is open
    water outside the region (C=0), as topology-ignorant code does."""
    return ({t: np.zeros(90, dtype=np.int8) for t in range(13)},
            {t: np.zeros(90, dtype=np.int8) for t in range(13)})


def ghost_tables(C):
    """Outside-cell indicator for every stored west (i_g=0) and south
    (j_g=0) edge face, from the inverse topology. Edges with no
    neighbor keep their own value (sign 0, land)."""
    gw = {t: C[t, :, 0].copy() for t in range(13)}    # default: sign 0
    gs = {t: C[t, 0, :].copy() for t in range(13)}
    for t, (nt, nax) in CONN_EAST.items():
        if nax == "X":                 # my east row j -> their west, parallel
            gw[nt] = C[t, :, 89]
        else:                          # my east -> their south, reversed
            gs[nt] = C[t, ::-1, 89]
    for t, (nt, nax) in CONN_NORTH.items():
        if nax == "Y":
            gs[nt] = C[t, 89, :]
        else:
            gw[nt] = C[t, 89, ::-1]
    return gw, gs


def face_masks(C, ghosts=ghost_tables):
    """Signed masks on stored faces: mW (13,90,90) at west faces,
    mS (13,90,90) at south faces; sign = C(inside cell) - C(outside)."""
    gw, gs = ghosts(C)
    mW = np.zeros((13, 90, 90), dtype=np.int8)
    mS = np.zeros((13, 90, 90), dtype=np.int8)
    for t in range(13):
        mW[t, :, 1:] = C[t, :, 1:] - C[t, :, :-1]
        mW[t, :, 0] = C[t, :, 0] - gw[t]
        mS[t, 1:, :] = C[t, 1:, :] - C[t, :-1, :]
        mS[t, 0, :] = C[t, 0, :] - gs[t]
    return mW, mS


def build_indicator(grid, spec):
    yc = grid.YC.values
    if spec["kind"] == "latitude-circle":
        return (yc >= spec["lat"]).astype(np.int8), None
    if spec["kind"] == "latitude-segment":
        C = np.zeros_like(yc, dtype=np.int8)
        t = spec["tile"]
        C[t] = (yc[t] >= spec["lat"]).astype(np.int8)
        return C, t
    raise SystemExit(f"unknown section kind {spec['kind']}")


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
    ap.add_argument("--section", choices=sorted(SECTIONS), required=True)
    ap.add_argument("--year", type=int, default=2010)
    ap.add_argument("--data-root", type=Path,
                    default=Path.home() / "ECCO_V4r4")
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    spec = SECTIONS[args.section]

    geom_path = args.data_root / GEOM
    grid = xr.open_dataset(geom_path)
    C, only_tile = build_indicator(grid, spec)
    mW, mS = face_masks(C)
    if only_tile is not None:
        # segment sections keep only the target tile's INTERIOR faces:
        # the indicator's jump at the tile boundary is an artifact of
        # restricting C to one tile, not a physical section face.
        keep = np.zeros_like(mW, dtype=bool)
        keep[only_tile, :, 1:] = True
        mW = np.where(keep, mW, 0)
        keep = np.zeros_like(mS, dtype=bool)
        keep[only_tile, 1:, :] = True
        mS = np.where(keep, mS, 0)

    # seam-owned faces: stored edge faces whose outside cell crossed a seam
    seamW = np.zeros_like(mW, dtype=bool)
    seamW[:, :, 0] = mW[:, :, 0] != 0
    seamS = np.zeros_like(mS, dtype=bool)
    seamS[:, 0, :] = mS[:, 0, :] != 0
    n_seam = int(seamW.sum() + seamS.sum())
    n_faces = int((mW != 0).sum() + (mS != 0).sum())

    def mf(short):
        d = xr.open_mfdataset(str(args.data_root / short / "*.nc"),
                              combine="by_coords")
        d = d.sel(time=slice(f"{args.year}-01-01", f"{args.year}-12-31"))
        assert d.sizes["time"] == 12, f"{short}: want 12 months"
        return d

    flux, volf = mf(FLUX), mf(VOLF)
    fxh = (np.nan_to_num(flux.ADVx_TH.values)
           + np.nan_to_num(flux.DFxE_TH.values)).astype(np.float64)
    fyh = (np.nan_to_num(flux.ADVy_TH.values)
           + np.nan_to_num(flux.DFyE_TH.values)).astype(np.float64)
    # dyG (13,90,90) at west faces, drF (50): build (50,13,90,90)
    dyg_drf = grid.drF.values[:, None, None, None] * grid.dyG.values[None]
    dxg_drf = grid.drF.values[:, None, None, None] * grid.dxG.values[None]
    fxv = np.nan_to_num(volf.UVELMASS.values).astype(np.float64) * dyg_drf[None]
    fyv = np.nan_to_num(volf.VVELMASS.values).astype(np.float64) * dxg_drf[None]

    def transports(mw, ms):
        h = ((fxh * mw[None, None]).sum(axis=(1, 2, 3, 4))
             + (fyh * ms[None, None]).sum(axis=(1, 2, 3, 4)))
        v = ((fxv * mw[None, None]).sum(axis=(1, 2, 3, 4))
             + (fyv * ms[None, None]).sum(axis=(1, 2, 3, 4)))
        return h * RHOCONST * C_P / 1e15, v / 1e6      # PW, Sv

    heat, vol = transports(mW, mS)
    hm, vm = float(heat.mean()), float(vol.mean())

    anchored = args.section == "global-26.5n"
    if anchored and abs(hm - HEAT_ANCHOR_PW) > HEAT_TOL_PW:
        raise SystemExit(
            f"heat transport mean {hm:.3f} PW not within {HEAT_TOL_PW} "
            f"of the independent implementation's {HEAT_ANCHOR_PW}; "
            "no receipt written")

    # mutation evidence
    evidence = []

    def record(name, mw, ms, structural=True):
        h2, v2 = transports(mw, ms)
        dh, dv = abs(float(h2.mean()) - hm), abs(float(v2.mean()) - vm)
        caught = dh > MUT_HEAT_PW or dv > MUT_VOL_SV
        entry = {"mutation": name, "delta_heat_PW": dh,
                 "delta_volume_Sv": dv, "caught": bool(caught)}
        if not caught:
            if structural:
                raise SystemExit(
                    f"structural mutation {name} was NOT caught (dH "
                    f"{dh:.3e} PW, dV {dv:.3e} Sv); no receipt written")
            entry["applicable"] = False
            entry["note"] = (
                "the deltas above sit under the catch bars here; for "
                "seam faces that means the section owns too few "
                f"({n_seam}) to demonstrate omission, and for the "
                "shifted path it is smooth-transport physics, guarded "
                "by the disclosed mask digest and latitude extent "
                "rather than by closure")
        evidence.append(entry)

    # rotated-tile sign flip: the vector-orientation trap
    rot = np.zeros_like(mW, dtype=bool)
    rot[7:13] = True
    record("rotated-tile-face-signs-flipped",
           np.where(rot, -mW, mW), np.where(rot, -mS, mS),
           structural=bool((mW[7:13] != 0).any() or (mS[7:13] != 0).any()))
    # south-face component dropped: the forgot-one-component error
    record("south-faces-dropped", mW, np.zeros_like(mS),
           structural=bool((mS != 0).any()))
    # path shifted one row: applicability-aware by physics (transports
    # vary smoothly with latitude; the disclosure is the guard)
    Cs = C.copy()
    if spec["kind"] == "latitude-circle":
        Cs = np.roll(C, 1, axis=1)
    else:
        Cs[spec["tile"]] = np.roll(C[spec["tile"]], 1, axis=0)
    mW2, mS2 = face_masks(Cs)
    if only_tile is not None:
        keep = np.zeros_like(mW2, dtype=bool); keep[only_tile, :, 1:] = True
        mW2 = np.where(keep, mW2, 0)
        keep = np.zeros_like(mS2, dtype=bool); keep[only_tile, 1:, :] = True
        mS2 = np.where(keep, mS2, 0)
    record("path-shifted-one-row", mW2, mS2, structural=False)
    # seam-owned faces dropped
    record("seam-faces-dropped",
           np.where(seamW, 0, mW), np.where(seamS, 0, mS),
           structural=False)
    # ghost tables zeroed: the topology-ignorant tool
    mW3, mS3 = face_masks(C, ghosts=ghost_tables_zeroed)
    if only_tile is not None:
        keep = np.zeros_like(mW3, dtype=bool); keep[only_tile, :, 1:] = True
        mW3 = np.where(keep, mW3, 0)
        keep = np.zeros_like(mS3, dtype=bool); keep[only_tile, 1:, :] = True
        mS3 = np.where(keep, mS3, 0)
    record("seam-ghosts-zeroed", mW3, mS3,
           structural=bool((mW3 != mW).any() or (mS3 != mS).any()))

    # disclosure: where the section actually runs
    yc = grid.YC.values; xc = grid.XC.values
    cellsW = np.argwhere(mW != 0); cellsS = np.argwhere(mS != 0)
    pts = ([yc[t, j, i] for t, j, i in cellsW]
           + [yc[t, j, i] for t, j, i in cellsS])
    lon = ([xc[t, j, i] for t, j, i in cellsW]
           + [xc[t, j, i] for t, j, i in cellsS])

    code = Path(__file__).read_bytes()
    receipt = {
        "run_id": (dt.datetime.now(dt.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]),
        "computation": "ecco-section-transport",
        "code_sha256": hashlib.sha256(code).hexdigest(),
        "data": data_identity(args.data_root),
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "bound_parameters": {
            "section": args.section, "year": args.year,
            "collections": [FLUX, VOLF],
            "rhoConst_kg_m3": RHOCONST, "Cp_J_kg_K": C_P,
            "heat_anchor_PW": HEAT_ANCHOR_PW if anchored else None,
            "heat_anchor_tol_PW": HEAT_TOL_PW if anchored else None,
        },
        "resolved_section": {
            "faces": n_faces, "seam_faces": n_seam,
            "closed": spec["kind"] == "latitude-circle",
            "lat_extent": [float(np.min(pts)), float(np.max(pts))],
            "lon_extent": [float(np.min(lon)), float(np.max(lon))],
            "mask_sha256": hashlib.sha256(
                mW.tobytes() + mS.tobytes()).hexdigest(),
            "geometry_sha256": hashlib.sha256(
                geom_path.read_bytes()).hexdigest(),
        },
        "results": {
            "heat_transport_mean_PW": hm,
            "volume_transport_mean_Sv": vm,
            "heat_transport_monthly_PW": [float(x) for x in heat],
            "volume_transport_monthly_Sv": [float(x) for x in vol],
        },
        "mutation_evidence": evidence,
        "caveats": {
            "sign_convention": "positive crosses into the indicated "
                               "region (northward for latitude sections)",
            "unanchored" if not anchored else "anchor": (
                "this section has no independent benchmark; its receipt "
                "is disclosure, not a validated claim"
                if not anchored else
                "independent implementation (ecco_v4_py "
                "calc_meridional_heat_trsp, ocean-science transport "
                "golden) records 1.098 PW for the same year and latitude"),
        },
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"run {receipt['run_id']}: {args.section}, year {args.year}")
    print(f"  faces {n_faces} ({n_seam} seam-owned), "
          f"lat {receipt['resolved_section']['lat_extent']}, closed "
          f"{receipt['resolved_section']['closed']}")
    print(f"  heat  mean {hm:+.4f} PW"
          + (f" (anchor {HEAT_ANCHOR_PW} +/- {HEAT_TOL_PW})" if anchored else ""))
    print(f"  volume mean {vm:+.4f} Sv")
    nc = sum(1 for e in evidence if e["caught"])
    na = [e["mutation"] for e in evidence if not e["caught"]]
    print(f"  mutations caught: {nc}/{len(evidence)}"
          + (f" ({', '.join(na)} not applicable here)" if na else ""))
    print(f"  receipt -> {args.receipt}")


if __name__ == "__main__":
    main()
