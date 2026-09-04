# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4", "xarray", "dask"]
# ///
"""Representativeness at the western boundary of the 26.5N section:
what the array measures with a cable across the Florida Straits, and
what the llc90 grid has there instead.

Enumerates the Atlantic section faces the sanctioned overturning
computation uses (same machinery, same basin codes), lists the
westernmost faces with their longitude, wet levels and depth, and
integrates the full-depth transport through each over the RAPID
overlap; beside them, the monthly means of the array's cable
(t_gs10), Ekman (t_ek10) and upper mid-ocean (t_umo10) components
from the same release. Writes a JSON summary the recipe cites.

Usage: ecco_western_boundary_26n.py --out SUMMARY.json
       [--data-root ~/ECCO_V4r4_record] [--rapid-root TREE]
       [--first 2004-04] [--last 2017-12]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import netCDF4
import numpy as np

HERE = Path(__file__).resolve().parent
SECTION_FILE = HERE.parent / "computations" / "ecco_section_transport.py"
BASIN_NPZ = HERE.parent / "masks" / "llc90_basin_codes.npz"
BASIN_JSON = HERE.parent / "masks" / "llc90_basin_codes.json"
VOLF = "ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4"
GEOM = "geometry/GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"
LATITUDE = 26.5
N_WEST = 8


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-root", type=Path, default=Path.home() / "ECCO_V4r4_record")
    ap.add_argument("--rapid-root", type=Path,
                    default=Path.home() / "RAPID_26N" / "rapid.ac.uk-2026-09-02")
    ap.add_argument("--first", default="2004-04")
    ap.add_argument("--last", default="2017-12")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    spec = importlib.util.spec_from_file_location("ecco_section_transport", SECTION_FILE)
    sect = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sect)
    side = json.loads(BASIN_JSON.read_text())
    codes = np.load(BASIN_NPZ)["codes"]
    if hashlib.sha256(codes.tobytes()).hexdigest() != side["codes_sha256"]:
        sys.exit("basin codes do not hash to the derived value")
    atl = codes == side["names"].index("atl") + 1

    root = args.data_root.expanduser().resolve()
    g = netCDF4.Dataset(str(root / GEOM))
    YC, XC = g["YC"][:].filled(np.nan), g["XC"][:].filled(np.nan)
    drF = g["drF"][:].filled(0).astype(float)
    dxG, dyG = g["dxG"][:].filled(0).astype(float), g["dyG"][:].filled(0).astype(float)
    hFacW, hFacS = g["hFacW"][:].filled(0), g["hFacS"][:].filled(0)
    Zu = g["Zu"][:].filled(0)
    g.close()
    C = (YC >= LATITUDE).astype(np.int8)
    mW, mS = sect.face_masks(C)
    mW, mS = np.where(atl, mW, 0), np.where(atl, mS, 0)
    faces = []
    for kind, mask, hfac in (("W", mW, hFacW), ("S", mS, hFacS)):
        for t, j, i in np.argwhere(mask != 0):
            nwet = int((hfac[:, t, j, i] > 0).sum())
            faces.append({"lon": float(XC[t, j, i]), "lat": float(YC[t, j, i]),
                          "kind": kind, "tile": int(t), "j": int(j), "i": int(i),
                          "wet_levels": nwet,
                          "depth_m": float(-Zu[nwet - 1]) if nwet else 0.0,
                          "sign": int(mask[t, j, i])})
    faces.sort(key=lambda f: f["lon"])
    west = faces[:N_WEST]
    tiles = sorted({f["tile"] for f in faces})

    files = {}
    for p in (root / VOLF).glob("*.nc"):
        m = re.search(r"_(\d{4}-\d{2})_", p.name)
        if m:
            files[m.group(1)] = p
    months = [m for m in sorted(files) if args.first <= m <= args.last]
    weights = []
    for f in west:
        w = np.zeros((13, 90, 90))
        w[f["tile"], f["j"], f["i"]] = f["sign"]
        horiz = dyG if f["kind"] == "W" else dxG
        weights.append((drF[:, None, None, None] * horiz[None] * w[None])[:, tiles])
    per = [[] for _ in west]
    for mo in months:
        d = netCDF4.Dataset(str(files[mo]))
        u = d["UVELMASS"][0][:, tiles].filled(0).astype(float)
        v = d["VVELMASS"][0][:, tiles].filled(0).astype(float)
        d.close()
        for k, f in enumerate(west):
            field = u if f["kind"] == "W" else v
            per[k].append(float((field * weights[k]).sum() / 1e6))
    for k, f in enumerate(west):
        vals = np.asarray(per[k])
        f["mean_Sv"] = float(vals.mean())
        f["sd_Sv"] = float(vals.std(ddof=1))
    shelf = [f for f in west if f["depth_m"] < 1000.0]
    shelf_tot = np.sum([np.asarray(per[k]) for k, f in enumerate(west)
                        if f["depth_m"] < 1000.0], axis=0)

    tr = netCDF4.Dataset(str(args.rapid_root.expanduser() / "moc_transports.nc"))
    t = tr["time"]
    dates = netCDF4.num2date(t[:], t.units)
    comp = {k: np.ma.filled(tr[k][:].astype(float), np.nan)
            for k in ("t_gs10", "t_ek10", "t_umo10")}
    tr.close()
    by = {k: {} for k in comp}
    for idx, date in enumerate(dates):
        mo = f"{date.year:04d}-{date.month:02d}"
        for k in comp:
            if not np.isnan(comp[k][idx]):
                by[k].setdefault(mo, []).append(comp[k][idx])
    obs = {}
    for k in comp:
        series = np.asarray([np.mean(by[k][mo]) for mo in months])
        obs[k] = {"mean_Sv": float(series.mean()), "sd_Sv": float(series.std(ddof=1))}
    cable = np.asarray([np.mean(by["t_gs10"][mo]) for mo in months])
    a, b = shelf_tot - shelf_tot.mean(), cable - cable.mean()
    out = {
        "overlap": [months[0], months[-1]], "months": len(months),
        "section_faces": len(faces), "tiles": tiles,
        "westernmost_faces": [{k: (round(v, 3) if isinstance(v, float) else v)
                               for k, v in f.items()} for f in west],
        "model_shelf": {
            "faces": [round(f["lon"], 1) for f in shelf],
            "depth_m": sorted({round(f["depth_m"]) for f in shelf}),
            "note": "the contiguous westernmost faces shallower than 1000 m: "
                    "the grid's stand-in for the Florida Straits and the "
                    "Bahama Banks together",
            "total_mean_Sv": float(shelf_tot.mean()),
            "total_sd_Sv": float(shelf_tot.std(ddof=1)),
            "correlation_with_cable_monthly": float(
                (a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum())),
        },
        "array_components_monthly_over_overlap": obs,
    }
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("model_shelf", "array_components_monthly_over_overlap")},
                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
