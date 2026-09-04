#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4"]
# ///
"""Attested comparison of the ECCO V4r4 regional sea level with the
NASA-SSH gridded altimetry record, month by month over the overlap, on
the registered box of the attested sea level partition.

WHAT IT CONSUMES
  the model side: a receipt of the sanctioned sea level partition
      (ecco_regional_sea_level.py beside this file, named by hash),
      whose total_anomaly_m series is the area-mean monthly anomaly of
      the SSH variant (dynamic sea surface height, inverse-barometer
      corrected, with the global-mean steric correction) over the
      registered region; the receipt's own hash, region, period and
      verified-tree stamp travel into this receipt;
  the observed side: every 0.5 degree grid of NASA_SSH_REF_SIMPLE_GRID
      in a verified tree (RECORD.json stamp copied in, every file
      hashed live into one digest), variable ssha in metres relative
      to the DTU21 mean sea surface, dynamic atmospheric correction
      applied, so the two sides share the inverse-barometer
      convention; the product's version, DOI, mean sea surface and
      licence are read from the files' attributes and recorded, never
      typed.

COLOCATION
  Each weekly grid (ten days of reference-mission passes, 100 km
  Gaussian smoothing) is reduced to one number: the cos-latitude
  weighted mean of ssha over the grid cells whose centres lie in the
  registered box and that carry a value. Grids are assigned to the
  calendar month of their centre date (the file's time variable), and
  a month enters when at least --min-grids grids fall in it (default
  4, so a month with one edge grid does not enter). The model side is
  the monthly mean already. Both series are then taken as anomalies
  about their own mean over the overlap, so the mean difference is
  zero by construction and is not a score: an altimetric anomaly about
  a mean sea surface and a model's dynamic height have no common
  level. The overlap must be consecutive, as for every score built on
  lag-1 autocorrelation. The two footprints differ (the model's 1
  degree class wet cells against 0.5 degree smoothed altimetry cells)
  and the receipt records both cell counts.

SKILL SCORES, EACH WITH AN INTERVAL FROM THE ATTESTED UNCERTAINTY
METHOD, computed by the same functions the overturning confrontation
uses (ecco_rapid_amoc_confrontation.py beside this file, imported by
path and named by hash, so one definition of each score serves every
confrontation in the bundle):
  rmsd: root mean square of d = ECCO minus altimetry, interval from
      the chain applied to d squared;
  correlation and anomaly correlation: Pearson r with Fisher z on the
      Bretherton effective sample size, the second after removing each
      series' own monthly climatology over the overlap;
  trend difference: the sanctioned trend method's interval block on d,
      in mm per year; the score that bears on a trend claim. Beside
      it, descriptive and not scores, each series' own trend block
      over the overlap.

INDEPENDENCE, STATED. ECCO V4r4 was fitted to along-track sea surface
height from the same reference missions this product regrids, at or
close to a specified noise level, so this record is not one the
estimate never saw. The receipt carries that statement, what the
agreement can therefore show (that the fit reached this box at these
scales) and what it cannot (that the model's sea level is right for
reasons other than having been fitted to it). The bundle's doctrine
concept is the authority on the label; this docstring is not.

RECEIPT: both series in full with the grids per month, digests of
each series, every score with its interval and the numbers that made
it, the model receipt's identity, the observation's record, version,
DOI, citation, licence, the product's published quality statements
and the published regional trend uncertainty of gridded altimetry the
trend score must be read against, and the independence statement. The
attester recomputes every score from the series in the receipt.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import importlib.util
import json
import math
import re
import sys
import uuid
from pathlib import Path

import netCDF4 as nc
import numpy as np

HERE = Path(__file__).resolve().parent
PARTITION_FILE = HERE / "ecco_regional_sea_level.py"
METHOD_FILE = HERE / "ecco_trend_ci.py"
SCORING_FILE = HERE / "ecco_rapid_amoc_confrontation.py"
OBS_SHORT_NAME = "NASA_SSH_REF_SIMPLE_GRID_V11"
OBS_VARIABLE = "ssha"
MIN_MONTHS = 24

CITATION = ("Willis, J. K., S. Fournier, K. Marlis, E. Killett and J. Sanchez "
            "(2026). NASA-SSH: JPL Sea Surface Height Anomalies, Version 1.1. "
            "Ver. 1.1. PO.DAAC, CA, USA. https://doi.org/10.5067/NSREF-SG0V11")
USER_GUIDE = ("https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/"
              "web-misc/nasa-ssh/NASA-SSH_V1_1_UserGuide.pdf")
PUBLISHED_UNCERTAINTY = {
    "product_statement": (
        "The NASA-SSH V1.1 User Guide publishes no uncertainty for the "
        "gridded fields. For the along-track source it states that the "
        "orbit error reduction lowers the RMS variability of crossovers "
        "by a variance of about 2.3 cm, and that a pass is removed when "
        "its crossover mean exceeds 0.1 m or its crossover RMS exceeds "
        "0.27 m; the gridded ssha is a 100 km Gaussian-weighted average "
        "of ten days of those passes, produced every seven days, so "
        "adjacent grids share data."),
    "product_statement_source": USER_GUIDE,
    "regional_trend_uncertainty_mm_yr": 0.83,
    "regional_trend_uncertainty_range_mm_yr": [0.78, 1.22],
    "regional_trend_uncertainty_confidence": 0.90,
    "regional_trend_uncertainty_source": (
        "Prandi et al. 2021, Local sea level trends, accelerations and "
        "uncertainties over 1993-2019, Scientific Data 8, 1, "
        "doi:10.1038/s41597-020-00786-7: the average local sea level "
        "trend uncertainty from a local altimetry error budget for a "
        "gridded multi-mission product over 1993-2019, at the 90 percent "
        "confidence level. Cited as the order a gridded-altimetry "
        "regional trend is held to; it is not this product's own figure"),
}
INDEPENDENCE = {
    "degree": "low for this record",
    "constraint": (
        "ECCO V4r4 is a least-squares fit of the MITgcm to the modern "
        "observing system over 1992-2017; its baseline solution 'fits "
        "altimetry (Forget and Ponte, 2015), SST (Buckley et al., 2014), "
        "and subsurface hydrography data at or close to the specified "
        "noise level' (Forget et al. 2015, quoted by the bundle's "
        "large-scale statistics validity domain). The along-track sea "
        "surface height it was fitted to comes from the same reference "
        "missions (TOPEX/Poseidon and the Jason series) that NASA-SSH "
        "V1.1 regrids with its own orbits, corrections and mean sea "
        "surface."),
    "overlap": (
        "The observed side is a reprocessing of measurements the "
        "estimate was constrained by. Where the two agree, the agreement "
        "is in part the fit: it shows the constraint reached this box at "
        "these scales, not that the model's sea level is right for "
        "independent reasons. Where they disagree, the disagreement is "
        "a fit residual the estimate could not remove, and stands."),
    "what_it_can_show": (
        "that the model's box-mean sea level anomaly follows the "
        "altimetric one in phase, amplitude and trend to the measured "
        "degree; and any departure, which the fit did not close"),
    "what_it_cannot_show": (
        "that the partition of that sea level into steric and manometric "
        "parts is right (no observation here bears on the partition), or "
        "that the agreement would survive against a record the estimate "
        "never saw, such as tide gauges"),
    "unfitted_records_in_scope": (
        "coastal tide gauges (relative sea level, inverse-barometer "
        "uncorrected, with vertical land motion) were not among the "
        "V4r4 constraints and are the un-fitted sea level record for this "
        "box; a confrontation against them is a different computation"),
}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def registered_regions(path: Path) -> dict:
    """The partition's region registry, read from its source without
    importing it (the partition carries xarray and dask for the native
    grid; this comparison needs only the box it was defined on)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "REGIONS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit(f"{path.name} declares no REGIONS registry")


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def box_mean(ds, box) -> tuple[float, int]:
    """cos-latitude weighted mean of ssha over the cells whose centres
    lie in the box and that carry a value; and the cell count."""
    lat = np.asarray(ds.variables["latitude"][:], dtype=float)
    lon = np.asarray(ds.variables["longitude"][:], dtype=float)
    lon = ((lon + 180.0) % 360.0) - 180.0                # 0..360 to -180..180
    ilat = np.where((lat >= box["lat"][0]) & (lat <= box["lat"][1]))[0]
    ilon = np.where((lon >= box["lon"][0]) & (lon <= box["lon"][1]))[0]
    sub = ds.variables[OBS_VARIABLE][ilat.min():ilat.max() + 1,
                                     ilon.min():ilon.max() + 1]
    sub = np.ma.masked_invalid(np.ma.asarray(sub, dtype=float))
    valid = ~np.ma.getmaskarray(sub)
    w = np.cos(np.deg2rad(lat[ilat]))[:, None] * np.ones((1, len(ilon)))
    wsum = float((w * valid).sum())
    if wsum <= 0.0:
        return float("nan"), 0
    return float((sub.filled(0.0) * w * valid).sum() / wsum), int(valid.sum())


def read_altimetry(root: Path, box, min_grids: int) -> tuple[dict, dict]:
    stamp = root / "RECORD.json"
    if not stamp.exists():
        sys.exit(f"{root} carries no RECORD.json stamp: the tree has not "
                 "been verified against its manifest; no receipt written")
    record = json.loads(stamp.read_text())
    files = sorted(p for p in root.glob("*.nc"))
    if not files:
        sys.exit(f"{root} holds no netCDF grids")
    grids, ident, lines = [], {}, []
    for p in files:
        lines.append(f"{p.name} {sha256_file(p)}")
        ds = nc.Dataset(p)
        attrs = {a: str(getattr(ds, a)).strip() for a in ds.ncattrs()}
        this = {"version": attrs.get("product_version"), "doi": attrs.get("id"),
                "short_name": attrs.get("product_short_name"),
                "mean_sea_surface": attrs.get("mean_sea_surface"),
                "license": attrs.get("license"), "title": attrs.get("title"),
                "institution": attrs.get("institution"),
                "units": str(getattr(ds.variables[OBS_VARIABLE], "units", "")),
                "gridding_method": attrs.get("gridding_method"),
                "source_along_track_doi": attrs.get("references")}
        if ident and this != ident:
            sys.exit(f"{p.name} identifies a different release or convention "
                     f"than the first grid: {this} vs {ident}; no receipt written")
        ident = this
        t = ds.variables["time"]
        centre = nc.num2date(np.atleast_1d(t[:])[0], t.units,
                             getattr(t, "calendar", "standard"))
        mean, cells = box_mean(ds, box)
        grids.append({"file": p.name, "centre": f"{centre.year:04d}-{centre.month:02d}-{centre.day:02d}",
                      "window": [attrs.get("time_coverage_start"),
                                 attrs.get("time_coverage_end")],
                      "box_mean_m": mean, "cells": cells})
        ds.close()
    if ident["short_name"] != OBS_SHORT_NAME:
        sys.exit(f"the tree holds {ident['short_name']}, not {OBS_SHORT_NAME}")
    if not ident["version"] or not ident["doi"]:
        sys.exit("the grids carry no product_version or DOI attribute; an "
                 "unidentified observation is refused")
    by_month: dict[str, dict] = {}
    empty = []                      # grids with no value in the box
    for g in grids:
        if math.isnan(g["box_mean_m"]):
            empty.append(g["centre"])
            continue
        by_month.setdefault(g["centre"][:7], []).append(g)
    monthly = {}
    for mo, gs in sorted(by_month.items()):
        monthly[mo] = {"mean_m": sum(x["box_mean_m"] for x in gs) / len(gs),
                       "grids": len(gs),
                       "cells_mean": sum(x["cells"] for x in gs) / len(gs),
                       "enters": len(gs) >= min_grids}
    obs = {"record": record, "data_root": str(root), **ident,
           "grids": len(grids), "grids_sha256": hashlib.sha256(
               ("\n".join(lines) + "\n").encode()).hexdigest(),
           "grids_digest_rule": "sha256 of the lines 'NAME SHA256' of every "
                                "*.nc in the tree, sorted by name, newline "
                                "terminated",
           "empty_in_box": empty,
           "first_grid": grids[0]["centre"], "last_grid": grids[-1]["centre"],
           "first_window": grids[0]["window"], "last_window": grids[-1]["window"],
           "box_cells": {"min": min(g["cells"] for g in grids),
                         "max": max(g["cells"] for g in grids)}}
    return obs, monthly


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--partition-receipt", type=Path, required=True,
                    help="receipt of the sanctioned sea level partition")
    ap.add_argument("--obs-root", type=Path,
                    default=Path.home() / "NASA_SSH" / "podaac-2026-09-02",
                    help="verified NASA-SSH tree (execution plumbing)")
    ap.add_argument("--min-grids", type=int, default=4,
                    help="grids whose centre falls in a month for the month "
                         "to enter (declared parameter)")
    ap.add_argument("--period", default=None,
                    help="YYYY-MM:YYYY-MM to narrow the overlap (declared "
                         "parameter; default the whole overlap)")
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    m = load_module(METHOD_FILE, "ecco_trend_ci")
    S = load_module(SCORING_FILE, "ecco_rapid_amoc_confrontation")
    regions = registered_regions(PARTITION_FILE)
    confidence = m.CONFIDENCE

    pr = json.loads(args.partition_receipt.read_text())
    if pr.get("code_sha256") != sha256_file(PARTITION_FILE):
        sys.exit("the model receipt was not written by the sanctioned sea "
                 "level partition beside this file; no receipt written")
    bp = pr["bound_parameters"]
    region = bp.get("region")
    if region not in regions:
        sys.exit(f"model receipt region {region!r} is not registered; no receipt written")
    if pr.get("ssh_variant") != "SSH":
        sys.exit(f"model receipt variant {pr.get('ssh_variant')!r}: only the "
                 "inverse-barometer corrected SSH variant shares the "
                 "altimetry's convention; no receipt written")
    if not isinstance(pr.get("data", {}).get("record"), dict):
        sys.exit("model receipt names no verified data tree; no receipt written")
    box = regions[region]
    ecco_by = dict(zip(pr["series_by_month"]["dates"],
                       pr["series_by_month"]["total_anomaly_m"]))

    obs, monthly = read_altimetry(args.obs_root, box, args.min_grids)
    both = [mo for mo in monthly if monthly[mo]["enters"] and mo in ecco_by]
    if args.period:
        mm = re.fullmatch(r"(\d{4}-\d{2}):(\d{4}-\d{2})", args.period)
        if not mm:
            sys.exit("period must be YYYY-MM:YYYY-MM")
        both = [mo for mo in both if mm.group(1) <= mo <= mm.group(2)]
    if len(both) < MIN_MONTHS:
        sys.exit(f"overlap of {len(both)} months is under {MIN_MONTHS}; no receipt written")
    if not m.consecutive(both):
        sys.exit("the overlap has a gap; the intervals rest on lag-1 "
                 "autocorrelation, which has no meaning across one; "
                 "no receipt written")
    dropped = {mo: monthly[mo]["grids"] for mo in monthly
               if mo in ecco_by and not monthly[mo]["enters"]}

    def anomalies_mm(values):
        mu = sum(values) / len(values)
        return [(v - mu) * 1000.0 for v in values]

    ecco = anomalies_mm([float(ecco_by[mo]) for mo in both])
    alt = anomalies_mm([float(monthly[mo]["mean_m"]) for mo in both])
    d = [a - b for a, b in zip(ecco, alt)]

    msd = S.mean_interval([v * v for v in d], m, confidence)
    rmsd = {"value": math.sqrt(msd["value"]), "msd": msd, "stated": msd["stated"],
            "confidence": confidence,
            "note": "interval is the mean-of-d-squared interval's ends under "
                    "the square root, clipped at zero"}
    if msd["stated"]:
        rmsd["ci_low"] = math.sqrt(max(msd["ci_low"], 0.0))
        rmsd["ci_high"] = math.sqrt(msd["ci_high"])
    else:
        rmsd["reason"] = msd["reason"]
    corr = S.correlation_interval(ecco, alt, m, confidence)
    acorr = S.correlation_interval(S.deseasonalize(both, ecco),
                                   S.deseasonalize(both, alt), m, confidence)
    acorr["note"] = ("each series' own monthly climatology over the overlap "
                     "removed before correlating")
    trend_diff = m.interval_block(d, "mm/year")
    trend_diff["note"] = ("the sanctioned trend method on d = ECCO minus "
                          "altimetry; an interval that excludes zero is a "
                          "trend disagreement of the stated size")
    ecco_trend = m.interval_block(ecco, "mm/year")
    alt_trend = m.interval_block(alt, "mm/year")

    def sd(v):
        mu = sum(v) / len(v)
        return math.sqrt(sum((x - mu) ** 2 for x in v) / (len(v) - 1))

    receipt = {
        "run_id": (dt.datetime.now(dt.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]),
        "computation": "ecco-ssh-vs-altimetry",
        "code_sha256": sha256_file(__file__),
        "method_code_sha256": sha256_file(METHOD_FILE),
        "scoring_code_sha256": sha256_file(SCORING_FILE),
        "partition_code_sha256": sha256_file(PARTITION_FILE),
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model": {
            "receipt": args.partition_receipt.name,
            "receipt_sha256": sha256_file(args.partition_receipt),
            "run_id": pr["run_id"], "code_sha256": pr["code_sha256"],
            "data": pr["data"], "region": region,
            "box": {"lat": list(box["lat"]), "lon": list(box["lon"])},
            "period": bp["period"], "ssh_variant": pr["ssh_variant"],
            "cells_evaluated": pr["cells_evaluated"],
            "series_field": "series_by_month.total_anomaly_m",
        },
        "observation": {
            **obs, "variable": OBS_VARIABLE,
            "convention": "sea surface height anomaly relative to the mean "
                          "sea surface named above, dynamic atmospheric "
                          "correction applied (inverse barometer included), "
                          "per the product's User Guide",
            "cadence": "one grid every 7 days from 10 days of passes",
            "citation": CITATION, "user_guide": USER_GUIDE,
            "published_uncertainty": PUBLISHED_UNCERTAINTY,
            "independence": INDEPENDENCE,
        },
        "bound_parameters": {
            "min_grids": args.min_grids,
            "overlap": f"{both[0]}:{both[-1]}", "months": len(both),
            "confidence": confidence,
            "colocation": "cos-latitude weighted mean of ssha over the box's "
                          "valued cells for each grid, grids assigned to the "
                          "calendar month of their centre date and averaged, "
                          "against the partition receipt's area-mean monthly "
                          "SSH anomaly; both taken as anomalies about their "
                          "own overlap mean, in mm",
        },
        "series": {
            "months": both, "ecco_mm": ecco, "altimetry_mm": alt,
            "difference_mm": d,
            "grids_per_month": [monthly[mo]["grids"] for mo in both],
            "cells_per_grid_mean": [monthly[mo]["cells_mean"] for mo in both],
            "months_dropped": dropped,
        },
        "digests": {"ecco_series_sha256": S.digest(both, ecco),
                    "altimetry_series_sha256": S.digest(both, alt),
                    "canonical": "sha256 of json.dumps({months, values}, "
                                 "separators (',', ':'), sort_keys) of the "
                                 "series as the receipt lists it"},
        "scores": {"rmsd_mm": rmsd, "correlation": corr,
                   "anomaly_correlation": acorr,
                   "trend_difference_mm_yr": trend_diff},
        "descriptive": {
            "ecco_sd_mm": sd(ecco), "altimetry_sd_mm": sd(alt),
            "ecco_trend": ecco_trend, "altimetry_trend": alt_trend,
            "note": "context, not scores: each series' own trend block from "
                    "the sanctioned trend method over the overlap",
        },
        "caveats": {
            "level": "both series are anomalies about their own overlap "
                     "mean, so no bias is scored; the model's dynamic height "
                     "and an anomaly about a mean sea surface share no level",
            "footprint": "the model averages its wet cells of the 1 degree "
                         "class in the box; the altimetry averages 0.5 degree "
                         "cells each already smoothed over 100 km from passes "
                         "up to 600 km away, so coastal cells carry offshore "
                         "information; the counts are in the receipt",
            "intervals": "sampling intervals on the scores, from the series' "
                         "own autocorrelation; they do not include the "
                         "altimetry's measurement uncertainty, which the "
                         "published block states",
            "fitted": "the estimate was fitted to along-track sea surface "
                      "height from these missions; see observation.independence",
        },
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=1) + "\n")

    def band(blk):
        return (f"[{blk['ci_low']:+.4f}, {blk['ci_high']:+.4f}]" if blk["stated"]
                else f"no interval: {blk['reason']}")
    print(f"run {receipt['run_id']}: {len(both)} months {both[0]} to {both[-1]}, "
          f"{obs['short_name']} {obs['version']} {obs['doi']}, {obs['grids']} grids, "
          f"box cells {obs['box_cells']}", file=sys.stderr)
    print(f"  rmsd         {rmsd['value']:.4f} mm  95% {band(rmsd)}", file=sys.stderr)
    print(f"  correlation  {corr['value']:+.4f}    95% {band(corr)}  (n_eff {corr['n_eff']:.1f})",
          file=sys.stderr)
    print(f"  anomaly corr {acorr['value']:+.4f}    95% {band(acorr)}  (n_eff {acorr['n_eff']:.1f})",
          file=sys.stderr)
    for name, blk in (("ECCO", ecco_trend), ("altimetry", alt_trend),
                      ("difference", trend_diff)):
        print(f"  trend {name:10s} {blk['trend']:+.4f} mm/yr 95% {band(blk)} "
              f"(deseasonalize {blk['deseasonalize']}, n_eff {blk['n_eff']:.1f}, "
              f"{'significant' if blk['significant_at_confidence'] else 'not significant'})",
              file=sys.stderr)
    print(f"  sd: ECCO {receipt['descriptive']['ecco_sd_mm']:.2f} mm, altimetry "
          f"{receipt['descriptive']['altimetry_sd_mm']:.2f} mm", file=sys.stderr)
    if dropped:
        print(f"  dropped months (grids): {dropped}", file=sys.stderr)
    print(f"  receipt -> {args.receipt}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
