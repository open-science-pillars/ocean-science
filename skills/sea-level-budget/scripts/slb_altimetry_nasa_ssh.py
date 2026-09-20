#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4"]
# ///
"""Loader for the altimetry term of the attested sea level budget
closure: the global mean sea surface height anomaly per calendar month
from the NASA-SSH simple gridded product (reference missions only),
written as the data root's altimetry.csv.

What it computes:

  1. For every grid in the tree (one every seven days), the
     cos-latitude weighted mean of ssha over the cells that carry a
     value, in millimeters, the way the bundle's confrontation
     computation reads the same grids; the identity attributes of every
     grid must agree (one release, one mean sea surface), or the loader
     refuses.
  2. The calendar month of each grid from its time coordinate (the
     centre of its window), and the month's value as the mean of its
     grids; the grids share passes, so the month is the sample. A grid
     with no cell carrying a value (an outage week) is not a sample and
     is skipped; the stamp lists it. A month with fewer than --min-grids
     grids (default 3) is left out, never filled.
  3. The GIA convention of the global budget: a linear +0.3 mm per year
     (Peltier 2004, the correction the 2018 WCRP budget applies to
     altimetric global mean sea level) added to the series, referenced
     to its first month, so that the altimetry term is the change in
     ocean water volume rather than the change in sea surface height
     over a subsiding basin. --no-gia leaves the series as measured;
     the stamp says which.
  4. The per-month uncertainty as a stated noise floor: the standard
     deviation of adjacent-month differences of the finished series
     divided by sqrt(2), written on every row and named in the stamp;
     the product ships no error field. The sanctioned computation takes
     the larger of this and the sampling half width.

The dynamic atmospheric correction is applied by the product (the
dataset concept and the user guide); nothing is added here. The
latitude coverage the reference missions give (about 66 degrees) is
read from the grids and written into the stamp as the smoothing and
coverage statement.

Usage:
  slb_altimetry_nasa_ssh.py --grid-dir DIR --out altimetry.csv
      [--stamp-out altimetry-stamp.json] [--start YYYY-MM] [--end YYYY-MM]
      [--min-grids 3] [--no-gia]
  --selftest   two synthetic months with known means
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import netCDF4 as nc
import numpy as np

OBS_VARIABLE = "ssha"
GIA_MM_PER_YEAR = 0.3
IDENTITY = ("product_version", "id", "product_short_name", "mean_sea_surface", "title",
            "institution", "gridding_method", "references")


def identity_value(v: str | None) -> str | None:
    """A DOI spelled with or without a resolver prefix is the same
    identity: the 2026 grids write references as https://doi.org/... where
    the earlier grids write the bare DOI."""
    if v is None:
        return None
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
        if v.lower().startswith(prefix):
            return v[len(prefix):]
    return v


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def global_mean_m(ds) -> tuple[float, int, float, float]:
    lat = np.asarray(ds.variables["latitude"][:], dtype=float)
    field = ds.variables[OBS_VARIABLE][:]
    field = np.ma.masked_invalid(np.ma.asarray(field, dtype=float))
    if field.ndim == 3:
        field = field[0]
    valid = ~np.ma.getmaskarray(field)
    w = np.cos(np.deg2rad(lat))[:, None] * np.ones((1, field.shape[1]))
    wsum = float((w * valid).sum())
    if wsum <= 0.0:
        return float("nan"), 0, float("nan"), float("nan")
    rows = np.where(valid.any(axis=1))[0]
    return (float((field.filled(0.0) * w * valid).sum() / wsum), int(valid.sum()),
            float(lat[rows].min()), float(lat[rows].max()))


def run(grid_dir: Path, out: Path, stamp_out: Path | None, start, end, min_grids: int, gia: bool):
    files = sorted(grid_dir.glob("*.nc"))
    if not files:
        sys.exit(f"{grid_dir} holds no netCDF grids")
    ident, per_month, lat_range, units, n_grids = None, defaultdict(list), [90.0, -90.0], None, 0
    manifest, empty = {}, []
    for p in files:
        ds = nc.Dataset(p)
        attrs = {a: str(getattr(ds, a)).strip() for a in ds.ncattrs()}
        this = {k: identity_value(attrs.get(k)) for k in IDENTITY}
        if ident and this != ident:
            sys.exit(f"{p.name} identifies a different release or convention than the first "
                     f"grid: {this} vs {ident}")
        ident = this
        units = str(getattr(ds.variables[OBS_VARIABLE], "units", ""))
        t = ds.variables["time"]
        centre = nc.num2date(np.atleast_1d(t[:])[0], t.units, getattr(t, "calendar", "standard"))
        label = f"{centre.year:04d}-{centre.month:02d}"
        ds_mean, cells, lo, hi = global_mean_m(ds)
        ds.close()
        if (start and label < start) or (end and label > end):
            continue
        if cells == 0:
            empty.append(p.name)       # no cell carries a value: not a sample of its month
            continue
        manifest[p.name] = sha256(p)
        n_grids += 1
        lat_range = [min(lat_range[0], lo), max(lat_range[1], hi)]
        per_month[label].append((ds_mean, cells))
    if units not in ("m", "meter", "meters", "metre", "metres"):
        sys.exit(f"ssha units are {units!r}, not metres; the loader converts metres to mm")
    rows, dropped = [], []
    for label in sorted(per_month):
        grids = per_month[label]
        if len(grids) < min_grids:
            dropped.append((label, len(grids))); continue
        rows.append([label, 1000.0 * float(np.mean([g[0] for g in grids])), len(grids)])
    if not rows:
        sys.exit("no month has enough grids")
    if gia:
        y0, m0 = map(int, rows[0][0].split("-"))
        for r in rows:
            y, m = map(int, r[0].split("-"))
            r[1] += GIA_MM_PER_YEAR * ((y - y0) + (m - m0) / 12.0)
    values = np.array([r[1] for r in rows])
    noise = float(np.std(np.diff(values), ddof=1) / math.sqrt(2.0)) if len(values) > 2 else float("nan")
    with out.open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f); wr.writerow(["month", "value_mm", "uncertainty_mm"])
        for label, v, _ in rows:
            wr.writerow([label, f"{v:.6f}", f"{noise:.6f}"])
    stamp = {
        "term": "altimetry",
        "product": ident.get("title"), "doi": ident.get("id"),
        "product_version": ident.get("product_version"),
        "short_name": ident.get("product_short_name"),
        "mean_sea_surface": ident.get("mean_sea_surface"),
        "gridding_method": ident.get("gridding_method"),
        "grids": n_grids, "months": [rows[0][0], rows[-1][0]],
        "grids_per_month": {r[0]: r[2] for r in rows},
        "dropped_months": dropped,
        "empty_grids": empty,
        "latitude_coverage": lat_range,
        "method": "cos-latitude weighted global mean of ssha per grid over the cells that "
                  "carry a value, metres to mm; months as the mean of their grids",
        "gia": (f"linear +{GIA_MM_PER_YEAR} mm per year added, referenced to {rows[0][0]} "
                "(Peltier 2004; the correction the 2018 WCRP budget applies to altimetric "
                "global mean sea level)") if gia else "none applied; the series is as measured",
        "dynamic_atmospheric_correction": "applied by the product",
        "uncertainty_mm": noise,
        "uncertainty_basis": "stated noise floor: standard deviation of adjacent-month "
                             "differences of the finished series divided by sqrt(2); "
                             "the product ships no error field",
        "sources": manifest,
    }
    if stamp_out:
        stamp_out.write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")
    print(f"altimetry.csv: {len(rows)} months {rows[0][0]} to {rows[-1][0]} from {n_grids} grids, "
          f"noise floor {noise:.3f} mm, {len(dropped)} months dropped, {len(empty)} empty grids skipped")


def selftest():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for i, (day, value) in enumerate([(3, 0.010), (10, 0.020), (17, 0.030), (24, 0.040),
                                          (34, 0.100), (41, 0.100), (48, 0.100)]):
            ds = nc.Dataset(d / f"g{i}.nc", "w")
            ds.createDimension("latitude", 3); ds.createDimension("longitude", 2); ds.createDimension("time", 1)
            ds.product_version = "toy"; ds.id = "10.5067/TOY"; ds.title = "toy grids"
            lat = ds.createVariable("latitude", "f8", ("latitude",)); lat[:] = [-60.0, 0.0, 60.0]
            lon = ds.createVariable("longitude", "f8", ("longitude",)); lon[:] = [0.0, 180.0]
            t = ds.createVariable("time", "f8", ("time",)); t.units = "days since 2005-01-01"; t[:] = [day]
            v = ds.createVariable(OBS_VARIABLE, "f8", ("time", "latitude", "longitude"), fill_value=-9999.0)
            v.units = "m"; v[:] = value; v[0, 1, 0] = -9999.0          # one hole
            ds.close()
        out = d / "alt.csv"; run(d, out, d / "s.json", None, None, 3, True)
        rows = list(csv.DictReader(out.open()))
        assert [r["month"] for r in rows] == ["2005-01", "2005-02"], rows
        jan, feb = float(rows[0]["value_mm"]), float(rows[1]["value_mm"])
        assert abs(jan - 25.0) < 1e-9, jan                       # mean of 10,20,30,40 mm
        assert abs(feb - (100.0 + 0.3 / 12)) < 1e-9, feb        # one month of GIA
        print(f"selftest: January {jan:.3f} mm, February {feb:.4f} mm (GIA +{0.3/12:.4f}); OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--grid-dir", type=Path); ap.add_argument("--out", type=Path)
    ap.add_argument("--stamp-out", type=Path); ap.add_argument("--start"); ap.add_argument("--end")
    ap.add_argument("--min-grids", type=int, default=3)
    ap.add_argument("--no-gia", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if not (a.grid_dir and a.out):
        ap.error("--grid-dir and --out are required")
    run(a.grid_dir, a.out, a.stamp_out, a.start, a.end, a.min_grids, not a.no_gia)


if __name__ == "__main__":
    main()
