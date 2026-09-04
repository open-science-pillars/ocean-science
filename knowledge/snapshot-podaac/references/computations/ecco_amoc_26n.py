# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4", "xarray", "dask"]
# ///
"""Attested Atlantic overturning at 26.5 north on the ECCO V4r4 native
grid, month by month across the record.

WHAT IT COMPUTES
The meridional overturning across the Atlantic at 26.5N, the quantity
the RAPID-MOCHA-WBTS array observes: the zonal integral of meridional
volume transport per model level, cumulative in depth, maximum over
depth. Section faces come from the sanctioned section machinery
(ecco_section_transport.py, imported from beside this file and named
by hash in the receipt): the closed 26.5N latitude circle by the
indicator-gradient method over the budget-verified tile topology,
then restricted to the Atlantic by the basin code of the cell owning
each stored face. The basin codes are ECCO's own (ECCOv4-py
binary_data/basins.data, pinned and hashed; see
derivations/llc90_basin_codes.py); "atl" alone is the array's section,
Florida to Africa. The Gulf of Mexico, which the 26.5N circle also
crosses and the array does not observe, is a registered second scope
and a recorded sabotage, never a silent inclusion.

Weighting as the section computation states it: UVELMASS times dyG
times drF and VVELMASS times dxG times drF, no partial-cell factor
(the MASS suffix carries it).

THREE CONVENTIONS, ONE PRIMARY, ALL IN THE RECEIPT
The streamfunction's maximum depends on where the integral starts,
because the model's net transport across the section is not zero
(about one Sverdrup southward, the Bering Strait throughflow and
Arctic storage), whereas the array enforces zero net transport by
construction. The receipt carries the per-level transports for every
month, so all three are recomputable from it:
  mass-balanced (PRIMARY): the net transport is removed uniformly
      over the section's open area (the array's own mass-balance
      constraint applied to the model), then integrated from the
      surface and maximised over depth;
  surface-down: integrated from the surface, no balance;
  bottom-up: integrated from the bottom and negated (ecco_v4_py's
      default), which equals surface-down shifted by the net.
The primary series is what a confrontation consumes; the other two
travel beside it so the convention's effect is a number, not a
footnote.

ANCHOR. An independent implementation (ecco_v4_py 1.8.1
calc_meridional_stf, basin "atl", xgcm 0.8) gives, for 2010 on the
same granules, a monthly mean of 11.7709 Sv surface-down and 12.8615
Sv bottom-up. Any run covering 2010 must reproduce both within 0.01
Sv or it writes no receipt.

MUTATION EVIDENCE in every receipt, as the section computation keeps
it: rotated-tile face signs flipped and south-face component dropped
are structural (the Atlantic section has faces on both a rotated and
an unrotated tile) and abort the run receiptless if not caught above
1 Sv of mean change; the Gulf of Mexico included and the path shifted
one row north are recorded with their measured deltas as disclosure.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import re
import sys
import uuid
from pathlib import Path

import netCDF4
import numpy as np

VOLF = "ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4"
GEOM = "geometry/GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"
LATITUDE = 26.5
SHIFT_LATITUDE = 27.0     # one llc90 row north, for the disclosure mutation
SPAN = ("1992-01", "2017-12")
SCOPES = {
    "atlantic": ["atl"],
    "atlantic-with-gulf-of-mexico": ["atl", "mexico"],
}
CONVENTIONS = ("mass-balanced", "surface-down", "bottom-up")
PRIMARY = "mass-balanced"
ANCHOR = {"year": 2010, "surface-down": 11.7709, "bottom-up": 12.8615,
          "tol_Sv": 0.01,
          "source": "ecco_v4_py 1.8.1 calc_meridional_stf, lat_vals 26.5, "
                    "basin_name atl, doFlip False and True, xgcm 0.8, "
                    "same granules, 2026-09-02"}
MUT_SV = 1.0
HERE = Path(__file__).resolve().parent
SECTION_FILE = HERE / "ecco_section_transport.py"
BASIN_NPZ = HERE.parent / "masks" / "llc90_basin_codes.npz"
BASIN_JSON = HERE.parent / "masks" / "llc90_basin_codes.json"


def load_section_machinery():
    spec = importlib.util.spec_from_file_location("ecco_section_transport",
                                                  SECTION_FILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_basins():
    side = json.loads(BASIN_JSON.read_text())
    codes = np.load(BASIN_NPZ)["codes"]
    got = hashlib.sha256(codes.tobytes()).hexdigest()
    if got != side["codes_sha256"]:
        sys.exit(f"basin codes hash {got[:16]} is not the derived "
                 f"{side['codes_sha256'][:16]}; no receipt written")
    return codes, side


def parse_period(period):
    m = re.fullmatch(r"(\d{4}-\d{2}):(\d{4}-\d{2})", period)
    if not m or not (SPAN[0] <= m.group(1) <= m.group(2) <= SPAN[1]):
        sys.exit(f"period must be YYYY-MM:YYYY-MM within {SPAN}, got {period!r}")
    return m.group(1), m.group(2)


def months_between(a, b):
    y, m = int(a[:4]), int(a[5:])
    out = []
    while f"{y:04d}-{m:02d}" <= b:
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def data_identity(root):
    """Which tree fed this run: the root and the RECORD.json stamp the
    verify tool leaves in a tree checked against its manifest. A tree
    with no stamp is recorded as unverified, never invented."""
    root = Path(root).expanduser().resolve()
    stamp = root / "RECORD.json"
    return {"data_root": str(root),
            "record": json.loads(stamp.read_text()) if stamp.exists()
            else "unverified: no RECORD.json in this tree"}


def conventions_from_levels(T, area, area_total):
    """The three maxima from one month's per-level transports T (50,)
    in Sv and the open-area profile (50,) in m2. Returns a dict of
    convention -> (amoc, k_max) plus the net."""
    net = float(T.sum())
    psi_sd = np.cumsum(T)
    psi_bu = -np.cumsum(T[::-1])[::-1]
    Tb = T - net * area / area_total
    psi_mb = np.cumsum(Tb)
    out = {}
    for name, psi in (("mass-balanced", psi_mb), ("surface-down", psi_sd),
                      ("bottom-up", psi_bu)):
        k = int(np.argmax(psi))
        out[name] = (float(psi[k]), k)
    return out, net


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--period", default=f"{SPAN[0]}:{SPAN[1]}",
                    help="YYYY-MM:YYYY-MM within the record (declared parameter)")
    ap.add_argument("--scope", choices=sorted(SCOPES), default="atlantic",
                    help="registered basin scope (declared parameter)")
    ap.add_argument("--data-root", type=Path,
                    default=Path.home() / "ECCO_V4r4_record",
                    help="tree root (execution plumbing, not a parameter)")
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    a, b = parse_period(args.period)
    months = months_between(a, b)

    sect = load_section_machinery()
    codes, side = load_basins()
    names = side["names"]
    scope_codes = [names.index(n) + 1 for n in SCOPES[args.scope]]

    root = args.data_root.expanduser().resolve()
    geom_path = root / GEOM
    g = netCDF4.Dataset(str(geom_path))
    YC = g["YC"][:].filled(np.nan)
    XC = g["XC"][:].filled(np.nan)
    drF = g["drF"][:].filled(0).astype(np.float64)
    dxG = g["dxG"][:].filled(0).astype(np.float64)
    dyG = g["dyG"][:].filled(0).astype(np.float64)
    hFacW = g["hFacW"][:].filled(0).astype(np.float64)
    hFacS = g["hFacS"][:].filled(0).astype(np.float64)
    Zu = g["Zu"][:].filled(0).astype(np.float64)
    g.close()

    # the signed latitude-circle faces, then the basin restriction by
    # the owning cell's code (ecco_v4_py's convention for basin masks
    # on velocity points)
    C = (YC >= LATITUDE).astype(np.int8)
    mW_all, mS_all = sect.face_masks(C)

    def restrict(mw, ms, code_list):
        inb = np.isin(codes, code_list)
        return np.where(inb, mw, 0), np.where(inb, ms, 0)

    mW, mS = restrict(mW_all, mS_all, scope_codes)
    cellsW, cellsS = np.argwhere(mW != 0), np.argwhere(mS != 0)
    n_faces = len(cellsW) + len(cellsS)
    if n_faces == 0:
        sys.exit("scope selects no section faces; no receipt written")
    n_seam = int((mW[:, :, 0] != 0).sum() + (mS[:, 0, :] != 0).sum())
    tiles = sorted({int(t) for t in cellsW[:, 0]} | {int(t) for t in cellsS[:, 0]})
    lats = [float(YC[t, j, i]) for t, j, i in cellsW] + \
           [float(YC[t, j, i]) for t, j, i in cellsS]
    lons = [float(XC[t, j, i]) for t, j, i in cellsW] + \
           [float(XC[t, j, i]) for t, j, i in cellsS]

    # face weights (50, ntile, 90, 90) restricted to the tiles in play
    wW = (drF[:, None, None, None] * dyG[None])[:, tiles]
    wS = (drF[:, None, None, None] * dxG[None])[:, tiles]
    open_area = ((wW * hFacW[:, tiles] * (mW[tiles] != 0)[None]).sum(axis=(1, 2, 3))
                 + (wS * hFacS[:, tiles] * (mS[tiles] != 0)[None]).sum(axis=(1, 2, 3)))
    area_total = float(open_area.sum())

    # mutation masks
    rot = np.zeros((13, 90, 90), dtype=bool)
    rot[7:13] = True
    variants = {
        "primary": (mW, mS),
        "rotated-tile-face-signs-flipped": (np.where(rot, -mW, mW),
                                            np.where(rot, -mS, mS)),
        "south-faces-dropped": (mW, np.zeros_like(mS)),
        "gulf-of-mexico-included": restrict(mW_all, mS_all,
                                            [names.index(n) + 1 for n in
                                             SCOPES["atlantic-with-gulf-of-mexico"]]),
    }
    # llc90 rows are 0.9 degrees apart at this latitude (26.578 then
    # 27.473 north); the shifted threshold selects the next row up on
    # both the unrotated and the rotated tile
    Cs = (YC >= SHIFT_LATITUDE).astype(np.int8)
    mW2, mS2 = sect.face_masks(Cs)
    variants["path-shifted-one-row-north"] = restrict(mW2, mS2, scope_codes)
    structural = {"rotated-tile-face-signs-flipped":
                  bool((mW[7:13] != 0).any() or (mS[7:13] != 0).any()),
                  "south-faces-dropped": bool((mS != 0).any()),
                  "gulf-of-mexico-included": False,
                  "path-shifted-one-row-north": False}
    # every variant's faces must lie inside the tiles read below
    for name, (vw, vs) in variants.items():
        extra = sorted({int(t) for t in np.argwhere(vw != 0)[:, 0]}
                       | {int(t) for t in np.argwhere(vs != 0)[:, 0]})
        tiles = sorted(set(tiles) | set(extra))
    wW = (drF[:, None, None, None] * dyG[None])[:, tiles]
    wS = (drF[:, None, None, None] * dxG[None])[:, tiles]
    vweights = {name: ((vw[tiles] * wW).astype(np.float64),
                       (vs[tiles] * wS).astype(np.float64))
                for name, (vw, vs) in variants.items()}

    files = {}
    for p in (root / VOLF).glob("*.nc"):
        m = re.search(r"_(\d{4}-\d{2})_", p.name)
        if m:
            files[m.group(1)] = p
    missing = [m for m in months if m not in files]
    if missing:
        sys.exit(f"{len(missing)} months absent from the tree, first "
                 f"{missing[0]}; no receipt written")

    per_level = []                       # primary, (n, 50) Sv
    series = {c: [] for c in CONVENTIONS}
    kmax = {c: [] for c in CONVENTIONS}
    net_series = []
    variant_series = {name: [] for name in variants if name != "primary"}
    for mo in months:
        d = netCDF4.Dataset(str(files[mo]))
        u = d["UVELMASS"][0][:, tiles].filled(0).astype(np.float64)
        v = d["VVELMASS"][0][:, tiles].filled(0).astype(np.float64)
        d.close()
        for name, (ww, ws) in vweights.items():
            T = ((u * ww).sum(axis=(1, 2, 3)) + (v * ws).sum(axis=(1, 2, 3))) / 1e6
            conv, net = conventions_from_levels(T, open_area, area_total)
            if name == "primary":
                per_level.append(T)
                net_series.append(net)
                for c in CONVENTIONS:
                    series[c].append(conv[c][0])
                    kmax[c].append(conv[c][1])
            else:
                variant_series[name].append(conv[PRIMARY][0])
    per_level = np.asarray(per_level)
    means = {c: float(np.mean(series[c])) for c in CONVENTIONS}

    # anchor: any run covering the anchor year must reproduce the
    # independent implementation
    anchor_block = None
    yr = [i for i, mo in enumerate(months) if mo.startswith(str(ANCHOR["year"]))]
    if len(yr) == 12 and args.scope == "atlantic":
        anchor_block = {"year": ANCHOR["year"], "source": ANCHOR["source"],
                        "tol_Sv": ANCHOR["tol_Sv"]}
        for c in ("surface-down", "bottom-up"):
            got = float(np.mean([series[c][i] for i in yr]))
            anchor_block[f"{c}_anchor_Sv"] = ANCHOR[c]
            anchor_block[f"{c}_measured_Sv"] = got
            if abs(got - ANCHOR[c]) > ANCHOR["tol_Sv"]:
                sys.exit(f"{c} 2010 mean {got:.4f} Sv is not within "
                         f"{ANCHOR['tol_Sv']} of the independent "
                         f"implementation's {ANCHOR[c]}; no receipt written")

    evidence = []
    for name, vals in variant_series.items():
        delta = abs(float(np.mean(vals)) - means[PRIMARY])
        caught = delta > MUT_SV
        entry = {"mutation": name, "delta_mean_amoc_Sv": delta,
                 "max_monthly_delta_Sv": float(np.max(np.abs(
                     np.asarray(vals) - np.asarray(series[PRIMARY])))),
                 "caught": bool(caught)}
        if structural[name] and not caught:
            sys.exit(f"structural mutation {name} was NOT caught "
                     f"(delta {delta:.3e} Sv); no receipt written")
        if not structural[name]:
            entry["applicable"] = False
            entry["note"] = ("disclosure, not a catch: the delta is the "
                             "measured effect of this choice on the "
                             "primary series")
        evidence.append(entry)

    code = Path(__file__).read_bytes()
    receipt = {
        "run_id": (dt.datetime.now(dt.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]),
        "computation": "ecco-amoc-26n",
        "code_sha256": hashlib.sha256(code).hexdigest(),
        "section_code_sha256": hashlib.sha256(SECTION_FILE.read_bytes()).hexdigest(),
        "basin_codes_sha256": side["codes_sha256"],
        "data": data_identity(root),
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "bound_parameters": {
            "period": args.period, "scope": args.scope,
            "basins": SCOPES[args.scope], "latitude": LATITUDE,
            "convention": PRIMARY, "collection": VOLF,
            "sign_convention": "positive northward (into the region north "
                               "of the latitude)",
        },
        "resolved_section": {
            "faces": n_faces, "west_faces": int(len(cellsW)),
            "south_faces": int(len(cellsS)), "seam_faces": n_seam,
            "tiles": tiles, "closed": False,
            "lat_extent": [min(lats), max(lats)],
            "lon_extent": [min(lons), max(lons)],
            "mask_sha256": hashlib.sha256(mW.tobytes() + mS.tobytes()).hexdigest(),
            "geometry_sha256": hashlib.sha256(geom_path.read_bytes()).hexdigest(),
            "open_area_m2_by_level": [float(x) for x in open_area],
            "open_area_total_m2": area_total,
            "level_bottom_depth_m": [float(z) for z in Zu],
        },
        "anchor": anchor_block,
        "results": {
            "months": months,
            "amoc_Sv": [float(x) for x in series[PRIMARY]],
            "depth_of_max_m": [float(Zu[k]) for k in kmax[PRIMARY]],
            "net_transport_Sv": net_series,
            "mean_amoc_Sv": means[PRIMARY],
            "by_convention": {
                c: {"amoc_Sv": [float(x) for x in series[c]],
                    "mean_amoc_Sv": means[c],
                    "mean_depth_of_max_m": float(np.mean([Zu[k] for k in kmax[c]]))}
                for c in CONVENTIONS},
            "transport_per_level_Sv_by_month": [
                [round(float(x), 6) for x in row] for row in per_level],
        },
        "mutation_evidence": evidence,
        "caveats": {
            "convention": ("three maxima from one per-level transport "
                           "profile; the primary removes the model's net "
                           "transport uniformly over the open section area "
                           "before integrating from the surface, as the "
                           "array's mass-balance constraint does; the "
                           "others are recorded so the choice is a number"),
            "monthly_mean_of_velocity": ("the maximum is taken of the "
                                         "streamfunction of the MONTHLY MEAN "
                                         "velocity field, not the monthly "
                                         "mean of an instantaneous maximum"),
            "scope": f"{args.scope}: {SCOPES[args.scope]}; the Gulf of "
                     "Mexico is included only by the registered scope "
                     "that names it",
        },
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=1) + "\n")
    print(f"run {receipt['run_id']}: {args.scope} {args.period}, "
          f"{len(months)} months, {n_faces} faces on tiles {tiles} "
          f"(lon {min(lons):.1f} to {max(lons):.1f})", file=sys.stderr)
    for c in CONVENTIONS:
        tag = " (primary)" if c == PRIMARY else ""
        print(f"  {c:13s} mean {means[c]:7.4f} Sv, depth of max "
              f"{receipt['results']['by_convention'][c]['mean_depth_of_max_m']:8.1f} m{tag}",
              file=sys.stderr)
    print(f"  net transport mean {np.mean(net_series):+.4f} Sv", file=sys.stderr)
    if anchor_block:
        print(f"  anchor 2010: surface-down {anchor_block['surface-down_measured_Sv']:.4f} "
              f"vs {ANCHOR['surface-down']}, bottom-up "
              f"{anchor_block['bottom-up_measured_Sv']:.4f} vs {ANCHOR['bottom-up']}",
              file=sys.stderr)
    for e in evidence:
        print(f"  mutation {e['mutation']}: delta mean {e['delta_mean_amoc_Sv']:.4f} Sv, "
              f"max monthly {e['max_monthly_delta_Sv']:.4f}, "
              f"{'caught' if e['caught'] else 'disclosure'}", file=sys.stderr)
    print(f"  receipt -> {args.receipt}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
