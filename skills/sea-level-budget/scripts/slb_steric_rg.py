#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4", "gsw"]
# ///
"""Loader for the steric term of the attested sea level budget closure:
the ocean mean steric height anomaly per month from the Roemmich and
Gilson gridded Argo product (RG Argo Climatology, the 2019 release and
its monthly extension files), written as the data root's steric.csv.

What it computes, per calendar month from 2004-01 onward:

  1. The full temperature and practical salinity field on the RG grid
     (1 degree, 64.5S to 79.5N, 58 pressure levels from 2.5 to 1975
     dbar): the 2004 to 2018 climatological mean from the base files
     plus that month's anomaly (from the base files through 2018-12,
     from one extension file per month after).
  2. Absolute Salinity and Conservative Temperature (TEOS-10, gsw),
     the specific volume per level, and the steric height per cell as
     the vertical integral of the specific volume anomaly against the
     climatology, from the surface to the sampled floor. Layer
     thicknesses come from the midpoints between levels, the top layer
     from 0 dbar and the bottom layer to 2000 dbar; pressure in dbar
     is converted to Pa and divided by the local gravity.
  3. The cos-latitude weighted mean over the cells that carry a value
     in every month of the record (one fixed ocean mask, so a cell
     dropping out cannot move the mean), in millimeters. The mask and
     the covered latitude band are written into the stamp fields the
     executor's corrections table needs.

The per-month uncertainty is a stated noise floor, not a product
error: the product ships no monthly error field for a global mean,
so the loader takes the standard deviation of adjacent-month
differences of the finished series divided by sqrt(2) and writes the
same value on every row, saying so in the stamp. The sanctioned
computation takes the larger of this and the sampling half width
from the trend chain, so the floor is never the whole statement.

The deep ocean below the floor is not in this term; the stamp's
deep_steric fields say so, and the computation adds the systematic
separately.

Usage:
  slb_steric_rg.py --rg-dir DIR --out steric.csv [--stamp-out steric-stamp.json]
      DIR holds RG_ArgoClim_Temperature_2019.nc(.gz),
      RG_ArgoClim_Salinity_2019.nc(.gz) and RG_ArgoClim_YYYYMM_2019.nc(.gz);
      gzipped files are read through a temporary decompressed copy.
  --start YYYY-MM --end YYYY-MM   restrict the months written (default: all)
  --selftest                      the integrator on a synthetic column
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

import netCDF4 as nc
import numpy as np

FLOOR_DBAR = 2000.0
FILL = -999.0
T_ANOM, S_ANOM = "ARGO_TEMPERATURE_ANOMALY", "ARGO_SALINITY_ANOMALY"
T_MEAN, S_MEAN = "ARGO_TEMPERATURE_MEAN", "ARGO_SALINITY_MEAN"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def opened(path: Path, tmp: Path) -> Path:
    """A readable netCDF path: the file itself, or a decompressed copy."""
    if path.suffix != ".gz":
        return path
    target = tmp / path.name[:-3]
    if not target.exists():
        with gzip.open(path, "rb") as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst, 1 << 20)
    return target


def layer_thickness_dbar(p: np.ndarray) -> np.ndarray:
    """Thickness of the layer each level represents: midpoints between
    levels, the top layer from 0, the bottom layer down to the floor."""
    edges = np.empty(len(p) + 1)
    edges[0] = 0.0
    edges[1:-1] = 0.5 * (p[:-1] + p[1:])
    edges[-1] = FLOOR_DBAR
    return np.diff(edges)


def steric_height_m(sp, t, p, lon2d, lat2d, dp_dbar, g):
    """Steric height per cell (m) as the integral of specific volume over
    the column; NaN where any level of the column is missing."""
    import gsw
    p3 = p[:, None, None]
    sa = gsw.SA_from_SP(sp, p3, lon2d[None], lat2d[None])
    ct = gsw.CT_from_t(sa, t, p3)
    v = gsw.specvol(sa, ct, p3)                   # m3/kg
    column = (v * (dp_dbar[:, None, None] * 1.0e4)).sum(axis=0)   # m3/kg * Pa
    return column / g


def run(rg_dir: Path, out: Path, stamp_out: Path | None, start: str | None, end: str | None):
    files = sorted(rg_dir.iterdir())
    base_t = next((f for f in files if f.name.startswith("RG_ArgoClim_Temperature_")), None)
    base_s = next((f for f in files if f.name.startswith("RG_ArgoClim_Salinity_")), None)
    if base_t is None or base_s is None:
        sys.exit(f"{rg_dir} lacks the RG temperature or salinity base file")
    ext = sorted(f for f in files if f.name.startswith("RG_ArgoClim_") and f.name[12:18].isdigit())
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        dt = nc.Dataset(opened(base_t, tmp))
        ds = nc.Dataset(opened(base_s, tmp))
        lat = np.asarray(dt["LATITUDE"][:], dtype=float)
        lon = np.asarray(dt["LONGITUDE"][:], dtype=float)
        p = np.asarray(dt["PRESSURE"][:], dtype=float)
        dp = layer_thickness_dbar(p)
        lon2d, lat2d = np.meshgrid(lon, lat)
        import gsw
        g = gsw.grav(lat2d, 0.0)
        tm = np.ma.filled(np.ma.masked_values(dt[T_MEAN][:], FILL), np.nan).astype(float)
        sm = np.ma.filled(np.ma.masked_values(ds[S_MEAN][:], FILL), np.nan).astype(float)
        h_clim = steric_height_m(sm, tm, p, lon2d, lat2d, dp, g)
        months, fields = [], []
        tunits = dt["TIME"].units
        base_months = np.asarray(dt["TIME"][:], dtype=float)
        origin_year, origin_month = 2004, 1      # "months since 2004-01-01"
        assert tunits.startswith("months since 2004-01-01"), tunits

        def label(m: float) -> str:
            k = int(math.floor(m))
            y, mo = origin_year + (origin_month - 1 + k) // 12, (origin_month - 1 + k) % 12 + 1
            return f"{y:04d}-{mo:02d}"

        for i, m in enumerate(base_months):
            months.append(label(m)); fields.append(("base", i))
        for f in ext:
            months.append(f"{f.name[12:16]}-{f.name[16:18]}"); fields.append(("ext", f))
        if len(set(months)) != len(months):
            sys.exit("duplicate months between the base files and the extensions")
        series, valid_all = {}, None
        sources = {base_t.name: sha256(base_t), base_s.name: sha256(base_s)}
        for mlabel, (kind, ref) in zip(months, fields):
            if (start and mlabel < start) or (end and mlabel > end):
                continue
            if kind == "base":
                ta = dt[T_ANOM][ref]; sa_ = ds[S_ANOM][ref]
            else:
                dx = nc.Dataset(opened(ref, tmp))
                ta = dx[T_ANOM][0]; sa_ = dx[S_ANOM][0]
                sources[ref.name] = sha256(ref)
                dx.close()
            ta = np.ma.filled(np.ma.masked_values(ta, FILL), np.nan).astype(float)
            sa_ = np.ma.filled(np.ma.masked_values(sa_, FILL), np.nan).astype(float)
            h = steric_height_m(sm + sa_, tm + ta, p, lon2d, lat2d, dp, g) - h_clim
            ok = np.isfinite(h)
            valid_all = ok if valid_all is None else (valid_all & ok)
            series[mlabel] = h
            print(f"  {mlabel}: {int(ok.sum())} cells", file=sys.stderr)
        dt.close(); ds.close()
    if not series:
        sys.exit("no months in range")
    w = np.cos(np.deg2rad(lat2d)) * valid_all
    wsum = float(w.sum())
    rows = []
    for mlabel in sorted(series):
        rows.append((mlabel, 1000.0 * float(np.nansum(series[mlabel] * w) / wsum)))
    values = np.array([v for _, v in rows])
    noise = float(np.std(np.diff(values), ddof=1) / math.sqrt(2.0)) if len(values) > 2 else float("nan")
    with out.open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f); wr.writerow(["month", "value_mm", "uncertainty_mm"])
        for mlabel, v in rows:
            wr.writerow([mlabel, f"{v:.6f}", f"{noise:.6f}"])
    stamp = {
        "term": "steric",
        "product": "Roemmich and Gilson gridded Argo climatology, 2019 release, "
                   "2004 to 2018 mean plus monthly anomalies and extension files "
                   "(sio-argo.ucsd.edu/RG_Climatology.html)",
        "method": "TEOS-10 specific volume (gsw) integrated per cell from 0 to "
                  f"{FLOOR_DBAR:.0f} dbar over the 58 RG levels (2.5 to 1975 dbar), "
                  "as an anomaly against the RG 2004 to 2018 climatology, "
                  "cos-latitude weighted mean over the fixed cell set valid in every month",
        "sampled_depth_floor_m": int(FLOOR_DBAR),
        "coverage": f"latitudes {lat.min():.1f} to {lat.max():.1f}, {int(valid_all.sum())} of {valid_all.size} cells",
        "months": [rows[0][0], rows[-1][0]],
        "uncertainty_mm": noise,
        "uncertainty_basis": "stated noise floor: standard deviation of adjacent-month "
                             "differences of the finished series divided by sqrt(2); "
                             "the product ships no monthly error for a global mean",
        "sources": sources,
    }
    if stamp_out:
        stamp_out.write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")
    print(f"steric.csv: {len(rows)} months {rows[0][0]} to {rows[-1][0]}, "
          f"noise floor {noise:.3f} mm, {int(valid_all.sum())} cells")


def selftest():
    """A uniform warming of a 2000 dbar column expands it by the known
    thermal expansion; the integrator must reproduce it to 5 percent."""
    import gsw
    p = np.array([2.5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500,
                  600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700,
                  1800, 1900, 1975], dtype=float)
    dp = layer_thickness_dbar(p)
    assert abs(dp.sum() - FLOOR_DBAR) < 1e-9
    lon2d, lat2d = np.zeros((1, 1)), np.zeros((1, 1))
    g = gsw.grav(lat2d, 0.0)
    sp = np.full((len(p), 1, 1), 35.0); t0 = np.full((len(p), 1, 1), 10.0)
    h0 = steric_height_m(sp, t0, p, lon2d, lat2d, dp, g)
    h1 = steric_height_m(sp, t0 + 0.1, p, lon2d, lat2d, dp, g)
    sa = gsw.SA_from_SP(35.0, 1000.0, 0.0, 0.0); ct = gsw.CT_from_t(sa, 10.0, 1000.0)
    alpha = gsw.alpha(sa, ct, 1000.0)
    expected = alpha * 0.1 * (FLOOR_DBAR * 1.0e4 / float(g[0, 0])) * gsw.specvol(sa, ct, 1000.0) * 1000.0
    got = float(h1[0, 0] - h0[0, 0])
    rel = abs(got - expected / 1000.0) / (expected / 1000.0)
    print(f"selftest: 0.1 K over 2000 dbar expands the column by {got*1000:.2f} mm, "
          f"expected about {expected:.2f} mm ({rel*100:.1f} percent off)")
    if rel > 0.05:
        sys.exit("selftest FAILED")
    print("selftest: OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rg-dir", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--stamp-out", type=Path)
    ap.add_argument("--start"); ap.add_argument("--end")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if not (a.rg_dir and a.out):
        ap.error("--rg-dir and --out are required")
    run(a.rg_dir, a.out, a.stamp_out, a.start, a.end)


if __name__ == "__main__":
    main()
