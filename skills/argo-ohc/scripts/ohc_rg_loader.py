#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy==2.2.6", "netCDF4==1.7.2", "gsw==3.6.19"]
# ///
"""Loader for the attested Argo ocean heat content computation: the
open-ocean heat content anomaly per month for the 0 to 700 dbar and
0 to 2000 dbar layers from the Roemmich and Gilson gridded Argo
product (the 2019 release, its 2004 to 2018 climatology and the
monthly extension files), written as the data root's ohc-700.csv and
ohc-2000.csv with one stamp beside each.

What it computes, per calendar month from 2004-01 onward:

  1. The full temperature and practical salinity field on the RG grid
     (1 degree, 64.5S to 79.5N, 58 pressure levels from 2.5 to 1975
     dbar): the 2004 to 2018 climatological mean from the base files
     plus that month's anomaly (from the base files through 2018-12,
     from one extension file per month after).
  2. Absolute Salinity, Conservative Temperature and in situ density
     (TEOS-10 through gsw), and per cell the heat content of each layer
     as cp0 times the vertical integral of rho times Conservative
     Temperature, less the same integral of the climatology, so the
     value is an anomaly against the 2004 to 2018 mean. cp0 is the
     TEOS-10 constant 3991.86795711963 J per kg per K. Layer
     thicknesses come from the midpoints between pressure levels, the
     top layer from 0 dbar and the bottom layer to the layer floor
     (700 or 2000 dbar; for the 2000 dbar layer the deepest level,
     1975 dbar, is extended down to the floor), converted to height
     with gsw.z_from_p at the cell's latitude.
  3. The sum over the cells that carry a value at all 58 levels in
     every month of the record (one fixed open-ocean mask, so a cell
     dropping out cannot move the sum; it is the set of columns mapped
     to the full 2000 dbar, which excludes the marginal seas the
     product maps to a shallower limit), each cell weighted by its
     spherical area from the grid's latitude bounds. The result is in
     zettajoules (1e21 J) over the mapped domain, whose area the stamp
     states, never scaled to the global ocean.

The per-month uncertainty is a stated noise floor, not a product
error: the product ships no error field, so the loader takes the
standard deviation of adjacent-month differences of the finished series
divided by sqrt(2) and writes the same value on every row, saying so in
the stamp. The sanctioned computation takes the larger of this and the
sampling half width from its trend, so the floor is never the whole
statement. The ocean below 2000 dbar is not in either term; the stamp
says so and the computation carries the published deep rate as a
stated omission.

Usage:
  ohc_rg_loader.py --rg-dir DIR --out-dir ROOT [--start YYYY-MM] [--end YYYY-MM]
      DIR holds RG_ArgoClim_Temperature_2019.nc.gz,
      RG_ArgoClim_Salinity_2019.nc.gz and RG_ArgoClim_YYYYMM_2019.nc.gz;
      gzipped files are read through a temporary decompressed copy.
      ROOT receives ohc-700.csv, ohc-2000.csv, ohc-700-stamp.json,
      ohc-2000-stamp.json and SOURCES.json. No product file is ever
      written under ROOT.
  --fetch [--through YYYY-MM]   download the product files that DIR lacks from
                                sio-argo.ucsd.edu, recording each in
                                DIR/downloads.json (URL, bytes, sha256, time,
                                HTTP status); with --out-dir the loader then runs
  --selftest                    the integrator on a synthetic grid with a
                                planted uniform warming
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import math
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

import gsw
import netCDF4 as nc
import numpy as np

PRODUCT_PAGE = "https://sio-argo.ucsd.edu/RG_Climatology.html"
FILE_BASE = "https://sio-argo.ucsd.edu/RG/"
BASE_FILES = ("RG_ArgoClim_Temperature_2019.nc.gz", "RG_ArgoClim_Salinity_2019.nc.gz")
FIRST_EXTENSION = "2019-01"
LAYERS = {700: 700.0, 2000: 2000.0}          # layer floors in dbar
CP0 = 3991.86795711963                        # J kg-1 K-1, TEOS-10 cp0
EARTH_RADIUS_M = 6371000.0                    # the mean radius gsw's geostrophy module carries
FILL = -999.0
T_ANOM, S_ANOM = "ARGO_TEMPERATURE_ANOMALY", "ARGO_SALINITY_ANOMALY"
T_MEAN, S_MEAN = "ARGO_TEMPERATURE_MEAN", "ARGO_SALINITY_MEAN"
ZJ = 1.0e21


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---- fetching the product files (the only place they are downloaded)

def month_labels(first: str, last: str):
    y, m = int(first[:4]), int(first[5:7])
    out = []
    while f"{y:04d}-{m:02d}" <= last:
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def fetch(rg_dir: Path, through: str | None):
    """Download the base files and the extension months DIR lacks, one
    record per file in DIR/downloads.json. The extension list is read
    from the product page, so a month the page does not list is not
    asked for; --through caps it."""
    rg_dir.mkdir(parents=True, exist_ok=True)
    log_path = rg_dir / "downloads.json"
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.is_file() else {"downloads": []}
    with urllib.request.urlopen(PRODUCT_PAGE, timeout=120) as r:
        page = r.read().decode("utf-8", "replace")
    listed = sorted({n for n in
                     __import__("re").findall(r"RG_ArgoClim_(\d{6})_2019\.nc\.gz", page)})
    wanted = list(BASE_FILES)
    for ym in listed:
        label = f"{ym[:4]}-{ym[4:]}"
        if label >= FIRST_EXTENSION and (through is None or label <= through):
            wanted.append(f"RG_ArgoClim_{ym}_2019.nc.gz")
    done = {d["file"] for d in log["downloads"] if d.get("status") == 200}
    for name in wanted:
        target = rg_dir / name
        if target.is_file() and name in done:
            continue
        url = FILE_BASE + name
        started = now_utc()
        status, nbytes = None, 0
        try:
            with urllib.request.urlopen(url, timeout=600) as r, target.open("wb") as f:
                status = r.status
                shutil.copyfileobj(r, f, 1 << 20)
            nbytes = target.stat().st_size
        except Exception as e:                       # noqa: BLE001
            status = getattr(e, "code", None) or f"error: {e}"
            if target.exists():
                target.unlink()
        rec = {"file": name, "url": url, "status": status, "bytes": nbytes,
               "retrieved_utc": started,
               "sha256": sha256(target) if status == 200 else None}
        log["downloads"] = [d for d in log["downloads"] if d["file"] != name] + [rec]
        log_path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
        print(f"  {name}: {status} {nbytes} bytes", file=sys.stderr)
    failed = [d for d in log["downloads"] if d.get("status") != 200]
    print(f"fetch: {len(wanted)} files wanted, {len(failed)} failed", file=sys.stderr)
    return log


# ---- the integrator

def opened(path: Path, tmp: Path) -> Path:
    """A readable netCDF path: the file itself, or a decompressed copy."""
    if path.suffix != ".gz":
        return path
    target = tmp / path.name[:-3]
    if not target.exists():
        with gzip.open(path, "rb") as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst, 1 << 20)
    return target


def layer_edges_dbar(p: np.ndarray, floor: float) -> np.ndarray:
    """The pressure edges of the layer each level represents: 0 at the
    top, the midpoints between levels, and the floor at the bottom;
    levels at or below the floor are cut off at it."""
    edges = np.empty(len(p) + 1)
    edges[0] = 0.0
    edges[1:-1] = 0.5 * (p[:-1] + p[1:])
    edges[-1] = max(floor, float(p[-1]))
    return np.minimum(edges, floor)


def cell_area_m2(lat: np.ndarray, dlat: float, dlon: float) -> np.ndarray:
    """Spherical cell area per latitude row (m2): R^2 dlon (sin top - sin bottom)."""
    top = np.deg2rad(lat + dlat / 2.0)
    bot = np.deg2rad(lat - dlat / 2.0)
    return EARTH_RADIUS_M ** 2 * np.deg2rad(dlon) * (np.sin(top) - np.sin(bot))


def heat_column_J_m2(sp, t, p, lon2d, lat2d, floors: dict) -> dict:
    """Per cell, the heat content of each layer (J per m2) as cp0 times
    the integral of rho times Conservative Temperature over height,
    NaN where any level of the column is missing. floors maps a layer
    name to its floor in dbar."""
    p3 = p[:, None, None]
    sa = gsw.SA_from_SP(sp, p3, lon2d[None], lat2d[None])
    ct = gsw.CT_from_t(sa, t, p3)
    rho = gsw.rho(sa, ct, p3)
    out = {}
    for name, floor in floors.items():
        edges = layer_edges_dbar(p, floor)
        z_edges = gsw.z_from_p(edges[:, None, None], lat2d[None])       # m, negative down
        dz = -(np.diff(z_edges, axis=0))                                  # positive thickness
        # a level below the floor has zero thickness and contributes nothing,
        # even where the column is unmapped there
        term = np.where(dz > 0.0, rho * ct * dz, 0.0)
        out[name] = CP0 * term.sum(axis=0)
    return out


def noise_floor_ZJ(values: np.ndarray, months: list) -> float:
    """The stated per-month floor: the standard deviation of adjacent-month
    differences of the series with its calendar-month means removed (the
    mapped domain carries a large annual cycle, which is signal, not
    noise), divided by sqrt(2)."""
    if len(values) <= 2:
        return float("nan")
    de = values.astype(float).copy()
    for m in range(1, 13):
        idx = [i for i, mm in enumerate(months) if mm == m]
        if idx:
            de[idx] -= de[idx].mean()
    return float(np.std(np.diff(de), ddof=1) / math.sqrt(2.0))


def run(rg_dir: Path, out_dir: Path, start: str | None, end: str | None, downloads: dict | None):
    files = sorted(rg_dir.iterdir())
    base_t = next((f for f in files if f.name.startswith("RG_ArgoClim_Temperature_")), None)
    base_s = next((f for f in files if f.name.startswith("RG_ArgoClim_Salinity_")), None)
    if base_t is None or base_s is None:
        sys.exit(f"{rg_dir} lacks the RG temperature or salinity base file")
    ext = sorted(f for f in files if f.name.startswith("RG_ArgoClim_") and f.name[12:18].isdigit())
    out_dir.mkdir(parents=True, exist_ok=True)
    floors = {f"ohc-{k}": v for k, v in LAYERS.items()}
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        dt_ = nc.Dataset(opened(base_t, tmp))
        ds = nc.Dataset(opened(base_s, tmp))
        lat = np.asarray(dt_["LATITUDE"][:], dtype=float)
        lon = np.asarray(dt_["LONGITUDE"][:], dtype=float)
        p = np.asarray(dt_["PRESSURE"][:], dtype=float)
        lon2d, lat2d = np.meshgrid(lon, lat)
        dlat = float(np.median(np.diff(lat)))
        dlon = float(np.median(np.diff(lon)))
        area_row = cell_area_m2(lat, dlat, dlon)
        area2d = np.repeat(area_row[:, None], len(lon), axis=1)
        tm = np.ma.filled(np.ma.masked_values(dt_[T_MEAN][:], FILL), np.nan).astype(float)
        sm = np.ma.filled(np.ma.masked_values(ds[S_MEAN][:], FILL), np.nan).astype(float)
        h_clim = heat_column_J_m2(sm, tm, p, lon2d, lat2d, floors)
        months, fields = [], []
        tunits = dt_["TIME"].units
        base_months = np.asarray(dt_["TIME"][:], dtype=float)
        assert tunits.startswith("months since 2004-01-01"), tunits

        def label(m: float) -> str:
            k = int(math.floor(m))
            y, mo = 2004 + k // 12, k % 12 + 1
            return f"{y:04d}-{mo:02d}"

        for i, m in enumerate(base_months):
            months.append(label(m)); fields.append(("base", i))
        for f in ext:
            months.append(f"{f.name[12:16]}-{f.name[16:18]}"); fields.append(("ext", f))
        if len(set(months)) != len(months):
            sys.exit("duplicate months between the base files and the extensions")
        series = {name: {} for name in floors}
        valid_all = None
        sources = {base_t.name: sha256(base_t), base_s.name: sha256(base_s)}
        for mlabel, (kind, ref) in zip(months, fields):
            if (start and mlabel < start) or (end and mlabel > end):
                continue
            if kind == "base":
                ta = dt_[T_ANOM][ref]; sa_ = ds[S_ANOM][ref]
            else:
                dx = nc.Dataset(opened(ref, tmp))
                ta = dx[T_ANOM][0]; sa_ = dx[S_ANOM][0]
                sources[ref.name] = sha256(ref)
                dx.close()
            ta = np.ma.filled(np.ma.masked_values(ta, FILL), np.nan).astype(float)
            sa_ = np.ma.filled(np.ma.masked_values(sa_, FILL), np.nan).astype(float)
            h = heat_column_J_m2(sm + sa_, tm + ta, p, lon2d, lat2d, floors)
            ok = np.isfinite(h["ohc-2000"])
            valid_all = ok if valid_all is None else (valid_all & ok)
            for name in floors:
                series[name][mlabel] = h[name] - h_clim[name]
            print(f"  {mlabel}: {int(ok.sum())} cells", file=sys.stderr)
        dt_.close(); ds.close()
    if not valid_all is not None or not series["ohc-2000"]:
        sys.exit("no months in range")
    domain_area = float((area2d * valid_all).sum())
    lat_rows = lat[valid_all.any(axis=1)]
    written = {}
    for name, floor in floors.items():
        rows = []
        for mlabel in sorted(series[name]):
            field = np.where(valid_all, series[name][mlabel], 0.0)
            rows.append((mlabel, float((field * area2d).sum() / ZJ)))
        values = np.array([v for _, v in rows])
        noise = noise_floor_ZJ(values, [int(m[5:7]) for m, _ in rows])
        out = out_dir / f"{name}.csv"
        with out.open("w", encoding="utf-8", newline="") as f:
            wr = csv.writer(f); wr.writerow(["month", "value_ZJ", "uncertainty_ZJ"])
            for mlabel, v in rows:
                wr.writerow([mlabel, f"{v:.6f}", f"{noise:.6f}"])
        stamp = {
            "term": name,
            "layer": {"top_dbar": 0.0, "floor_dbar": floor,
                      "statement": f"0 to {floor:.0f} dbar; the RG levels at or above the floor, "
                                   "each level's layer bounded by the midpoints to its neighbours, "
                                   "the top from 0 dbar, the bottom cut at the floor"
                                   + (", and the deepest level (1975 dbar) extended down to the "
                                      "2000 dbar floor" if floor > p.max() else "")},
            "product": "Roemmich and Gilson gridded Argo climatology, 2019 release, "
                       "2004 to 2018 mean plus monthly anomalies and extension files "
                       "(sio-argo.ucsd.edu/RG_Climatology.html)",
            "product_version": "2019 release (Latest Version 2019, Updated Jan 17, 2020), "
                               "monthly extension files RG_ArgoClim_YYYYMM_2019.nc.gz",
            "grid": f"1 degree, latitudes {lat.min():.1f} to {lat.max():.1f}, longitudes "
                    f"{lon.min():.1f} to {lon.max():.1f}, {len(p)} pressure levels "
                    f"{p.min():.1f} to {p.max():.1f} dbar",
            "method": "TEOS-10 through gsw: Absolute Salinity from practical salinity, "
                      "Conservative Temperature from in situ temperature, in situ density "
                      f"gsw.rho; heat content per cell as cp0 ({CP0} J/kg/K) times the "
                      "integral of rho times Conservative Temperature over the layer's "
                      "height (gsw.z_from_p at the cell latitude), as an anomaly against "
                      "the same integral of the RG 2004 to 2018 mean field; summed over the "
                      "fixed cell set with each cell's spherical area from the grid's "
                      f"latitude bounds (mean Earth radius {EARTH_RADIUS_M:.0f} m)",
            "climatology": "the RG 2004 to 2018 mean field (ARGO_TEMPERATURE_MEAN and "
                           "ARGO_SALINITY_MEAN in the base files); every month's field is "
                           "that mean plus the month's anomaly, and the heat content written "
                           "is the departure from the mean field's own heat content",
            "anomaly_convention": "value_ZJ is the heat content of the layer over the mapped "
                                  "domain minus the heat content of the 2004 to 2018 "
                                  "climatological mean field over the same domain; zero means "
                                  "the climatological state, and a difference between two "
                                  "months is a heat content change",
            "mask": "the columns that carry a value at all 58 levels in every month written "
                    "(the product's own fill marks a level as unmapped; marginal seas mapped "
                    "to a shallower limit than 2000 dbar therefore drop out), applied to "
                    "both layers so the two share one domain",
            "aggregation": "area-weighted sum over the fixed cell set, in zettajoules "
                           "(1e21 J) over the mapped domain; not scaled to the global ocean",
            "coverage": {"statement": f"latitudes {lat_rows.min():.1f} to {lat_rows.max():.1f}, "
                                      f"{int(valid_all.sum())} of {valid_all.size} cells",
                         "cells": int(valid_all.sum()), "cells_total": int(valid_all.size),
                         "domain_area_m2": domain_area,
                         "latitude_min": float(lat_rows.min()), "latitude_max": float(lat_rows.max())},
            "months": [rows[0][0], rows[-1][0]],
            "n_months": len(rows),
            "uncertainty_ZJ": noise,
            "uncertainty_basis": "stated noise floor: standard deviation of adjacent-month "
                                 "differences of the finished series with its calendar-month "
                                 "means removed, divided by sqrt(2); the product ships no "
                                 "error field",
            "deep_omission": "the ocean below 2000 dbar is not sampled by the product and is "
                             "not in this term",
            "loader": "skills/argo-ohc/scripts/ohc_rg_loader.py",
            "loader_sha256": sha256(Path(__file__).resolve()),
            "written_utc": now_utc(),
            "sources": sources,
        }
        (out_dir / f"{name}-stamp.json").write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")
        written[name] = (len(rows), rows[0][0], rows[-1][0], noise)
    write_sources(out_dir, sources, downloads)
    for name, (n, a, b, noise) in written.items():
        print(f"{name}.csv: {n} months {a} to {b}, noise floor {noise:.3f} ZJ, "
              f"{int(valid_all.sum())} cells, domain {domain_area:.4e} m2")


def write_sources(out_dir: Path, sources: dict, downloads: dict | None):
    """SOURCES.json: every product file read, its URL, hash and the time
    it was retrieved (from the fetch log when the loader fetched it)."""
    by_file = {d["file"]: d for d in (downloads or {}).get("downloads", [])}
    entries = []
    for name, digest in sources.items():
        d = by_file.get(name, {})
        entries.append({"file": name, "url": FILE_BASE + name, "sha256": digest,
                        "bytes": d.get("bytes"), "retrieved_utc": d.get("retrieved_utc"),
                        "status": d.get("status"),
                        "read_utc": now_utc()})
    doc = {"purpose": "provenance of the Roemmich and Gilson product files the ocean heat "
                      "content loader read; the files themselves are never committed",
           "product_page": PRODUCT_PAGE,
           "credentials": "none: the Scripps files are public",
           "files": entries}
    (out_dir / "SOURCES.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def normals_for_selftest(n: int) -> list:
    """A fixed standard-normal stream from SHA-256 counters (no RNG state)."""
    out, k = [], 0
    while len(out) < n:
        h = hashlib.sha256(f"selftest:{k}".encode()).digest()
        u1 = (int.from_bytes(h[:8], "big") + 1) / (2.0 ** 64 + 2.0)
        u2 = (int.from_bytes(h[8:16], "big") + 1) / (2.0 ** 64 + 2.0)
        r = math.sqrt(-2.0 * math.log(u1))
        out += [r * math.cos(2 * math.pi * u2), r * math.sin(2 * math.pi * u2)]
        k += 1
    return out[:n]


def selftest():
    """A synthetic 3 by 4 grid over the RG levels: a uniform warming of
    the whole column by 0.1 K must raise the 0 to 2000 dbar heat content
    by cp0 times rho times 0.1 times the layer's volume within 0.5
    percent (the density moves with temperature by less than that), the
    0 to 700 dbar term by the same per unit volume, and a column with a
    missing level must be excluded from the fixed mask."""
    p = np.array([2.5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150,
                  160, 170, 182.5, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400,
                  420, 440, 462.5, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000,
                  1050, 1100, 1150, 1200, 1250, 1300, 1350, 1412.5, 1500, 1600, 1700, 1800,
                  1900, 1975], dtype=float)
    assert len(p) == 58
    lat = np.array([-30.5, -29.5, -28.5]); lon = np.array([20.5, 21.5, 22.5, 23.5])
    lon2d, lat2d = np.meshgrid(lon, lat)
    area = np.repeat(cell_area_m2(lat, 1.0, 1.0)[:, None], len(lon), axis=1)
    sp = np.full((len(p), 3, 4), 35.0)
    t0 = 20.0 - 18.0 * (p / 2000.0)[:, None, None] * np.ones((1, 3, 4))   # cooling with depth
    floors = {"ohc-700": 700.0, "ohc-2000": 2000.0}
    h0 = heat_column_J_m2(sp, t0, p, lon2d, lat2d, floors)
    h1 = heat_column_J_m2(sp, t0 + 0.1, p, lon2d, lat2d, floors)
    for name, floor in floors.items():
        # expected: cp0 * mean(rho * dCT) * height, level by level
        edges = layer_edges_dbar(p, floor)
        z = gsw.z_from_p(edges[:, None, None], lat2d[None])
        dz = -np.diff(z, axis=0)
        sa = gsw.SA_from_SP(sp, p[:, None, None], lon2d[None], lat2d[None])
        ct0 = gsw.CT_from_t(sa, t0, p[:, None, None]); ct1 = gsw.CT_from_t(sa, t0 + 0.1, p[:, None, None])
        rho = gsw.rho(sa, ct0, p[:, None, None])
        expected = CP0 * (rho * (ct1 - ct0) * dz).sum(axis=0)
        got = h1[name] - h0[name]
        rel = float(np.max(np.abs(got - expected) / expected))
        total_ZJ = float(((h1[name] - h0[name]) * area).sum() / ZJ)
        print(f"selftest {name}: 0.1 K over the column raises the grid's heat content by "
              f"{total_ZJ:.4e} ZJ; per-cell integral within {rel*100:.3f} percent of the "
              f"expected rho cp0 dCT dz sum")
        if rel > 0.005:
            sys.exit(f"selftest FAILED on {name}")
        assert abs(float(dz.sum(axis=0)[0, 0]) - floor) / floor < 0.03, "height differs from dbar by more than 3 percent"
    # a missing level makes the column NaN, so a fixed mask excludes it
    t_hole = t0.copy(); t_hole[40, 1, 2] = np.nan
    h_hole = heat_column_J_m2(sp, t_hole, p, lon2d, lat2d, floors)
    assert np.isnan(h_hole["ohc-2000"][1, 2]) and np.isfinite(h_hole["ohc-700"][1, 2])
    assert np.isfinite(h_hole["ohc-2000"]).sum() == 11
    # edges: the 700 floor cuts the level list at 700 dbar exactly
    e700 = layer_edges_dbar(p, 700.0)
    assert e700.max() == 700.0 and abs(e700[0]) == 0.0
    # the area of one degree cells sums to the band it covers
    band = EARTH_RADIUS_M ** 2 * np.deg2rad(4.0) * (math.sin(math.radians(-28.0)) - math.sin(math.radians(-31.0)))
    assert abs(float(area.sum()) - band) / band < 1e-12
    # the floor sees noise, not the annual cycle: a pure cycle plus white
    # noise of sigma 1 yields a floor near 1
    rng_months = [i % 12 + 1 for i in range(240)]
    cyc = 30.0 * np.cos(2 * np.pi * (np.array(rng_months) - 3) / 12.0)
    noise = np.array(normals_for_selftest(240))
    floor = noise_floor_ZJ(cyc + noise, rng_months)
    assert 0.8 < floor < 1.25, floor
    print(f"selftest: noise floor {floor:.3f} on a 30 ZJ cycle plus unit noise")
    print("selftest: OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rg-dir", type=Path)
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--start"); ap.add_argument("--end")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--through", default=None, help="last extension month to fetch, YYYY-MM")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if not a.rg_dir:
        ap.error("--rg-dir is required")
    downloads = None
    if a.fetch:
        downloads = fetch(a.rg_dir, a.through)
    elif (a.rg_dir / "downloads.json").is_file():
        downloads = json.loads((a.rg_dir / "downloads.json").read_text(encoding="utf-8"))
    if not a.out_dir:
        if a.fetch:
            return
        ap.error("--out-dir is required")
    run(a.rg_dir, a.out_dir, a.start, a.end, downloads)


if __name__ == "__main__":
    main()
