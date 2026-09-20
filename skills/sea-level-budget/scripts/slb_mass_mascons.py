#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4"]
# ///
"""Loader for the mass term of the attested sea level budget closure:
the global ocean mean of the JPL GRACE/GRACE-FO mascon solution per
solution month, from the CRI-filtered grid granule, written as the data
root's mass.csv.

What it computes, per solution epoch in the granule:

  1. The ocean cells from the granule's own land_mask (0 is ocean) and
     each cell's area from its latitude bounds, so the sum runs over
     the ocean part of every mascon with true areas, as the mass recipe
     says. The CRI partition of the coastal mascons is the product's;
     no further coastal buffer is applied, and the stamp says so.
  2. The ocean mean of lwe_thickness (cm of equivalent water thickness
     against the product's 2004 to 2009 baseline) over those cells,
     which is the barystatic sea level anomaly in cm, times 10 for mm.
     The product restores the GAD de-aliasing signal over the ocean
     (the release note), so the value carries the full ocean bottom
     pressure variation; the GAD field itself is left in the granule.
  3. The formal error: the granule's uncertainty is one 1-sigma value
     per 3-degree mascon (its comment says so, not per cell), so the
     error of the ocean mean is the quadrature sum over mascons of
     (ocean area of the mascon times its sigma) divided by the ocean
     area, treating mascons as independent. That understates the true
     error where mascon errors correlate; the stamp says so, and the
     sanctioned computation takes the larger of this and the sampling
     half width.
  4. The calendar month of each solution from the midpoint of its
     time_bounds. Months the product lacks are simply absent from the
     file, never filled. When two solutions' midpoints fall in one
     calendar month (the product's April 2015 pair: one spanning
     April 1 to 30, the next April 12 to May 11), the later solution
     is assigned to the following month if its span reaches into it
     and that month is otherwise empty, which is how the product's own
     month list labels it (MAY 2015); the stamp records every such
     assignment. Any other collision is refused, never averaged.

Usage:
  slb_mass_mascons.py --granule FILE.nc --out mass.csv [--stamp-out mass-stamp.json]
  --selftest   a synthetic two-mascon world with a known ocean mean
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
import tempfile
from pathlib import Path

import netCDF4 as nc
import numpy as np

EARTH_RADIUS_KM = 6371.0


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def cell_areas_km2(lat_bounds: np.ndarray, lon_bounds: np.ndarray) -> np.ndarray:
    """Spherical cell areas from bounds: shape (nlat, nlon)."""
    s = np.sin(np.deg2rad(lat_bounds))
    dlat = np.abs(s[:, 1] - s[:, 0])                     # (nlat,)
    dlon = np.deg2rad(np.abs(lon_bounds[:, 1] - lon_bounds[:, 0]))  # (nlon,)
    return EARTH_RADIUS_KM ** 2 * dlat[:, None] * dlon[None, :]


def at_epoch(var, i: int) -> np.ndarray:
    """The field of a variable at epoch i: the product stores lat_bounds,
    lon_bounds, land_mask and mascon_ID once, without a time axis, while
    a per-epoch layout carries time first; both are read the same way."""
    if "time" in var.dimensions:
        return np.asarray(var[i], dtype=float)
    return np.asarray(var[:], dtype=float)


def next_month(label: str) -> str:
    y, m = int(label[:4]), int(label[5:])
    return f"{y + m // 12:04d}-{m % 12 + 1:02d}"


def ocean_mean_and_error(lwe, unc, mascon_id, ocean, area):
    """Ocean mean of lwe (cm) and its formal error (cm) over the ocean
    cells, with the error combined per mascon."""
    w = area * ocean
    wsum = float(w.sum())
    mean = float(np.nansum(lwe * w) / wsum)
    ids = mascon_id[ocean]
    a = w[ocean]
    sig = unc[ocean]
    order = np.argsort(ids, kind="stable")
    ids, a, sig = ids[order], a[order], sig[order]
    cuts = np.flatnonzero(np.diff(ids)) + 1
    area_per = np.add.reduceat(a, np.r_[0, cuts])
    sig_per = sig[np.r_[0, cuts]]                       # one sigma per mascon
    err = float(np.sqrt(np.sum((area_per * sig_per) ** 2)) / wsum)
    return mean, err, int(len(area_per))


def run(granule: Path, out: Path, stamp_out: Path | None):
    ds = nc.Dataset(granule)
    attrs = {a: str(getattr(ds, a)) for a in ds.ncattrs()}
    t = ds["time"]
    tb = np.asarray(ds["time_bounds"][:], dtype=float)
    units, cal = t.units, getattr(t, "calendar", "standard")
    lat_b = at_epoch(ds["lat_bounds"], 0)
    lon_b = at_epoch(ds["lon_bounds"], 0)
    area = cell_areas_km2(lat_b, lon_b)
    rows, months_seen, mascon_counts, assignments = [], {}, set(), []
    n = len(t)
    for i in range(n):
        mid = 0.5 * (tb[i, 0] + tb[i, 1])
        d = nc.num2date(mid, units, cal)
        label = f"{d.year:04d}-{d.month:02d}"
        if label in months_seen:
            end = nc.num2date(tb[i, 1], units, cal)
            end_label = f"{end.year:04d}-{end.month:02d}"
            following = next_month(label)
            if end_label == following and following not in months_seen:
                assignments.append({"epoch": i, "midpoint_month": label, "assigned": following,
                                    "span": [f"{nc.num2date(tb[i,0], units, cal):%Y-%m-%d}",
                                             f"{end:%Y-%m-%d}"],
                                    "reason": "midpoint month already taken by the previous "
                                              "solution; the span reaches into the following "
                                              "month, which the product's month list labels it"})
                label = following
            else:
                sys.exit(f"two solutions fall in {label} (epochs {months_seen[label]} and {i}) "
                         "and the later one does not reach into a free following month; "
                         "the loader does not average solutions")
        months_seen[label] = i
        lwe = np.ma.filled(np.ma.masked_invalid(ds["lwe_thickness"][i]), np.nan).astype(float)
        unc = np.ma.filled(np.ma.masked_invalid(ds["uncertainty"][i]), np.nan).astype(float)
        land = at_epoch(ds["land_mask"], i)
        mid_ = at_epoch(ds["mascon_ID"], i)
        ocean = (land == 0) & np.isfinite(lwe) & np.isfinite(unc)
        mean_cm, err_cm, nm = ocean_mean_and_error(lwe, unc, mid_, ocean, area)
        mascon_counts.add(nm)
        rows.append((label, 10.0 * mean_cm, 10.0 * err_cm,
                     f"{nc.num2date(tb[i,0], units, cal):%Y-%m-%d}",
                     f"{nc.num2date(tb[i,1], units, cal):%Y-%m-%d}"))
        print(f"  {label}: {10*mean_cm:+.3f} mm, formal {10*err_cm:.3f} mm, {nm} ocean mascons",
              file=sys.stderr)
    ds.close()
    rows.sort()
    with out.open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f); wr.writerow(["month", "value_mm", "uncertainty_mm"])
        for label, v, e, *_ in rows:
            wr.writerow([label, f"{v:.6f}", f"{e:.6f}"])
    stamp = {
        "term": "mass",
        "product": attrs.get("title", ""),
        "doi": attrs.get("id", ""),
        "granule": granule.name,
        "granule_sha256": sha256(granule),
        "time_coverage": [rows[0][3], rows[-1][4]],
        "months": [rows[0][0], rows[-1][0]],
        "n_solutions": len(rows),
        "month_assignments": assignments,
        "ocean_mascons": sorted(mascon_counts),
        "ocean_mask": "the granule's land_mask (0 is ocean), every ocean cell, no coastal "
                      "buffer; the CRI partition of the coastal mascons is the product's",
        "units": "mm of barystatic sea level: the ocean-area-weighted mean of "
                 "lwe_thickness (cm, against the product baseline) times 10",
        "gad": "restored over the ocean by the product (release note); the value carries "
               "the full ocean bottom pressure variation",
        "uncertainty_basis": "formal: the granule's one sigma per mascon, combined in "
                             "quadrature over the ocean part of each mascon weighted by its "
                             "ocean area, mascons treated as independent (a floor where "
                             "mascon errors correlate)",
        "global_attributes": {k: attrs[k] for k in ("title", "id", "time_coverage_start",
                                                    "time_coverage_end", "date_created",
                                                    "processing_level", "source")
                              if k in attrs},
    }
    if stamp_out:
        stamp_out.write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")
    print(f"mass.csv: {len(rows)} solution months {rows[0][0]} to {rows[-1][0]}")


def selftest():
    """Two mascons, one all ocean at +2 cm with sigma 1 and one half land
    at -1 cm with sigma 2: the ocean mean and its error follow by hand."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "toy.nc"
        ds = nc.Dataset(p, "w")
        ds.createDimension("time", 3); ds.createDimension("lat", 2); ds.createDimension("lon", 2); ds.createDimension("nv", 2)
        ds.title = "toy"; ds.id = "10.5067/TOY"
        t = ds.createVariable("time", "f8", ("time",)); t.units = "days since 2002-01-01T00:00:00Z"
        tb = ds.createVariable("time_bounds", "f8", ("time", "nv")); tb.units = t.units
        t[:] = [1100.0, 1130.0, 1145.0]
        tb[:] = [[1096.0, 1126.0], [1127.0, 1157.0], [1138.0, 1167.0]]   # Jan, Feb, and Feb 12 to Mar 13 2005
        lat_b = ds.createVariable("lat_bounds", "f8", ("lat", "nv")); lon_b = ds.createVariable("lon_bounds", "f8", ("lon", "nv"))
        lat_b[:] = [[0, 1], [1, 2]]; lon_b[:] = [[0, 1], [1, 2]]   # stored once, as the product does
        for name in ("lwe_thickness", "uncertainty"):
            ds.createVariable(name, "f8", ("time", "lat", "lon"))
        for name in ("land_mask", "mascon_ID"):
            ds.createVariable(name, "f8", ("lat", "lon"))
        ds["mascon_ID"][:] = [[1, 1], [2, 2]]              # mascon 1 is the first row, 2 the second
        ds["land_mask"][:] = [[0, 0], [0, 1]]              # mascon 2 has one land cell
        ds["lwe_thickness"][:] = [[[2, 2], [-1, -1]]] * 3
        ds["uncertainty"][:] = [[[1, 1], [2, 2]]] * 3
        ds.close()
        out = Path(td) / "mass.csv"; st = Path(td) / "stamp.json"
        run(p, out, st)
        rows = list(csv.DictReader(out.open()))
        area = cell_areas_km2(np.array([[0, 1], [1, 2]], float), np.array([[0, 1], [1, 2]], float))
        a1 = area[0].sum(); a2 = area[1, 0]
        mean = (2 * a1 - 1 * a2) / (a1 + a2)
        err = np.sqrt((a1 * 1) ** 2 + (a2 * 2) ** 2) / (a1 + a2)
        got = float(rows[0]["value_mm"]), float(rows[0]["uncertainty_mm"])
        print(f"selftest: mean {got[0]:.4f} mm vs {10*mean:.4f}, error {got[1]:.4f} vs {10*err:.4f}; "
              f"months {[r['month'] for r in rows]}")
        assert abs(got[0] - 10 * mean) < 1e-6 and abs(got[1] - 10 * err) < 1e-6
        assert [r["month"] for r in rows] == ["2005-01", "2005-02", "2005-03"], [r["month"] for r in rows]
        stamp = json.loads(st.read_text())
        assert stamp["month_assignments"][0]["assigned"] == "2005-03", stamp["month_assignments"]
        print("selftest: the third solution (midpoint in February, span into March) is assigned to March; OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--granule", type=Path); ap.add_argument("--out", type=Path)
    ap.add_argument("--stamp-out", type=Path); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if not (a.granule and a.out):
        ap.error("--granule and --out are required")
    run(a.granule, a.out, a.stamp_out)


if __name__ == "__main__":
    main()
