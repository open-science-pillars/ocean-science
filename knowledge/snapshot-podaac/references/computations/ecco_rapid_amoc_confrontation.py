# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4"]
# ///
"""Attested confrontation of the ECCO V4r4 overturning at 26.5 north
with the RAPID-MOCHA-WBTS observed overturning, month by month over
the overlap.

WHAT IT CONSUMES
  the model side: a receipt of the sanctioned overturning computation
      (ecco_amoc_26n.py beside this file, named by hash; scope
      "atlantic", convention "mass-balanced"; the receipt's own hash
      and its verified-tree stamp travel into this receipt);
  the observed side: moc_transports.nc from a verified RAPID tree
      (RECORD.json stamp copied in, file hashed live), variable
      moc_mar_hc10, twelve-hourly ten-day low-passed overturning in
      Sverdrups; the file's version and DOI attributes are read and
      recorded, never typed.

COLOCATION
  RAPID is averaged to calendar months over the samples it has; a
  month enters when at least --min-valid-fraction of its expected
  twelve-hourly samples are valid (default 0.5, so April 2004 with 48
  valid of 60 enters as the array's first month). ECCO is the monthly
  mean already. The overlap is the run of months both sides have, and
  it must be consecutive: the intervals below rest on lag-1
  autocorrelation, which has no meaning across a gap.

SKILL SCORES, EACH WITH AN INTERVAL FROM THE ATTESTED UNCERTAINTY
METHOD (ecco_trend_ci.py, imported from beside this file and named by
hash): the same chain the trend intervals use, lag-1 autocorrelation
of the series in hand, effective sample size n(1-r1)/(1+r1) capped at
n, Student's t on the effective degrees of freedom, 95 percent.
  bias: mean of d = ECCO minus RAPID; interval on the mean of d with
      n_eff from r1 of d, dof n_eff - 1;
  rmsd: square root of the mean of d squared; the interval is the
      chain applied to the series d squared, then the square root of
      both ends (clipped at zero);
  correlation: Pearson r of the two monthly series; Fisher z, with
      n_eff = n(1 - r1a r1b)/(1 + r1a r1b) (Bretherton et al. 1999)
      capped at n, dof n_eff - 3, transformed back;
  anomaly correlation: the same after removing each series' own
      monthly climatology over the overlap, so the seasonal cycle the
      two share is not counted as skill.
Descriptive, beside the scores and not scores: each series' mean,
standard deviation and trend block from the sanctioned trend method
(165 months is not a whole number of years, so the method fits with
deseasonalize "none" and says so).

RECEIPT: both series in full with the RAPID sample counts, a digest
of each series (sha256 of canonical JSON of months and values), every
score with its interval and the numbers that made it, the model
receipt's identity, the observation's record, version, DOI, citation,
acknowledgement and licence, and the published measurement
uncertainty the scores must be read against (RMS 1.5 Sv on ten-day
values, 0.9 Sv annual, McCarthy et al. 2015 via the programme's
README_ERROR). The attester recomputes every score from the series
in the receipt.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import re
import sys
import uuid
from pathlib import Path

import netCDF4
import numpy as np

HERE = Path(__file__).resolve().parent
AMOC_FILE = HERE / "ecco_amoc_26n.py"
METHOD_FILE = HERE / "ecco_trend_ci.py"
OBS_FILE = "moc_transports.nc"
OBS_VARIABLE = "moc_mar_hc10"
SAMPLES_PER_DAY = 2
MIN_DOF = 1.0
PUBLISHED_UNCERTAINTY = {
    "rms_ten_day_Sv": 1.5, "rms_annual_Sv": 0.9,
    "source": "McCarthy et al. 2015, reproduced in the programme's "
              "README_ERROR.pdf; the README states the errors do not "
              "reduce substantially in annual averages"}
CITATION = ("Moat B.I.; Smeed D.; Rayner D.; Johns W.E.; Smith R.H.; "
            "Volkov D.L.; Elipot S.; Petit T.; Kajtar J.B.; Baringer M.O.; "
            "Collins J. (2026). Atlantic meridional overturning circulation "
            "observed by the RAPID-MOCHA-WBTS (RAPID-Meridional Overturning "
            "Circulation and Heatflux Array-Western Boundary Time Series) "
            "array at 26N from 2004 to 2024 (v2024.1a). NERC EDS British "
            "Oceanographic Data Centre NOC. "
            "doi:10.5285/48d0bf43-0598-ceb2-e063-7086abc062f1")
LICENCE = ("UK Open Government Licence v3, https://www.nationalarchives."
           "gov.uk/doc/open-government-licence/version/3/")


def load_method():
    spec = importlib.util.spec_from_file_location("ecco_trend_ci", METHOD_FILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def digest(months, values):
    """sha256 of canonical JSON of the series: the attester recomputes
    it from the receipt's own lists."""
    text = json.dumps({"months": list(months), "values": [float(v) for v in values]},
                      separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()


def n_effective(r1, n):
    return min(float(n), n * (1.0 - r1) / (1.0 + r1))


def mean_interval(values, m, confidence):
    """Interval on the mean of an autocorrelated monthly series by the
    attested chain: r1 of the anomalies, n_eff, Student's t on
    n_eff - 1."""
    n = len(values)
    mean = sum(values) / n
    a = [v - mean for v in values]
    r1 = m.lag1(a)
    n_eff = n_effective(r1, n)
    dof = n_eff - 1.0
    sd = math.sqrt(sum(x * x for x in a) / (n - 1))
    se = sd / math.sqrt(n_eff)
    block = {"value": mean, "n": n, "r1": r1, "n_eff": n_eff, "dof": dof,
             "sd": sd, "se": se, "confidence": confidence}
    if dof < MIN_DOF:
        block.update(stated=False, reason=f"{dof:.2f} effective degrees of "
                     f"freedom is under {MIN_DOF}")
        return block
    tq = m.t_quantile(0.5 + confidence / 2.0, dof)
    half = tq * se
    block.update(stated=True, t_quantile=tq, half_width=half,
                 ci_low=mean - half, ci_high=mean + half)
    return block


def correlation_interval(x, y, m, confidence):
    """Pearson r with a Fisher-z interval on the effective sample size
    of the pair (Bretherton et al. 1999), Student's t on n_eff - 3."""
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    ax, ay = [v - mx for v in x], [v - my for v in y]
    sxx, syy = sum(v * v for v in ax), sum(v * v for v in ay)
    sxy = sum(a * b for a, b in zip(ax, ay))
    r = sxy / math.sqrt(sxx * syy)
    r1x, r1y = m.lag1(ax), m.lag1(ay)
    n_eff = n_effective(r1x * r1y, n)
    dof = n_eff - 3.0
    block = {"value": r, "n": n, "r1_a": r1x, "r1_b": r1y, "n_eff": n_eff,
             "dof": dof, "confidence": confidence}
    if dof < MIN_DOF or abs(r) >= 1.0:
        block.update(stated=False, reason=f"{dof:.2f} effective degrees of "
                     f"freedom is under {MIN_DOF}" if dof < MIN_DOF
                     else "correlation of magnitude one has no Fisher z")
        return block
    z = math.atanh(r)
    se_z = 1.0 / math.sqrt(dof)
    tq = m.t_quantile(0.5 + confidence / 2.0, dof)
    block.update(stated=True, fisher_z=z, se_z=se_z, t_quantile=tq,
                 ci_low=math.tanh(z - tq * se_z), ci_high=math.tanh(z + tq * se_z))
    return block


def deseasonalize(months, values):
    """Remove each calendar month's mean over the series (the series'
    own climatology on the overlap)."""
    by = {}
    for mo, v in zip(months, values):
        by.setdefault(mo[5:], []).append(v)
    clim = {k: sum(v) / len(v) for k, v in by.items()}
    return [v - clim[mo[5:]] for mo, v in zip(months, values)]


def scores(months, ecco, rapid, m, confidence):
    d = [a - b for a, b in zip(ecco, rapid)]
    bias = mean_interval(d, m, confidence)
    msd = mean_interval([v * v for v in d], m, confidence)
    rmsd = {"value": math.sqrt(msd["value"]), "msd": msd,
            "stated": msd["stated"], "confidence": confidence,
            "note": "interval is the mean-of-d-squared interval's ends "
                    "under the square root, clipped at zero"}
    if msd["stated"]:
        rmsd["ci_low"] = math.sqrt(max(msd["ci_low"], 0.0))
        rmsd["ci_high"] = math.sqrt(msd["ci_high"])
    else:
        rmsd["reason"] = msd["reason"]
    corr = correlation_interval(ecco, rapid, m, confidence)
    acorr = correlation_interval(deseasonalize(months, ecco),
                                 deseasonalize(months, rapid), m, confidence)
    acorr["note"] = ("each series' own monthly climatology over the "
                     "overlap removed before correlating")
    return {"bias_Sv": bias, "rmsd_Sv": rmsd, "correlation": corr,
            "anomaly_correlation": acorr}


def read_rapid(root, min_fraction):
    root = Path(root).expanduser().resolve()
    path = root / OBS_FILE
    d = netCDF4.Dataset(str(path))
    t = d["time"]
    dates = netCDF4.num2date(t[:], t.units, getattr(t, "calendar", "standard"))
    var = d[OBS_VARIABLE]
    vals = np.ma.filled(var[:].astype(np.float64), np.nan)
    attrs = {a: d.getncattr(a) for a in d.ncattrs()}
    units = var.getncattr("units")
    fill = float(var.getncattr("_FillValue"))
    d.close()
    by = {}
    for date, v in zip(dates, vals):
        by.setdefault(f"{date.year:04d}-{date.month:02d}", []).append(float(v))
    monthly = {}
    for mo, xs in sorted(by.items()):
        y, mth = int(mo[:4]), int(mo[5:])
        days = (dt.date(y + (mth == 12), mth % 12 + 1, 1) - dt.date(y, mth, 1)).days
        expected = days * SAMPLES_PER_DAY
        valid = [x for x in xs if not math.isnan(x)]
        monthly[mo] = {"mean": sum(valid) / len(valid) if valid else None,
                       "present": len(xs), "valid": len(valid),
                       "expected": expected,
                       "enters": bool(valid) and len(valid) / expected >= min_fraction}
    doi = str(attrs.get("DOI", ""))
    doi = re.sub(r"^\s*doi:\s*", "", doi, flags=re.I).strip()
    return {
        "record": {"data_root": str(root),
                   "record": (json.loads((root / "RECORD.json").read_text())
                              if (root / "RECORD.json").exists()
                              else "unverified: no RECORD.json in this tree")},
        "file": OBS_FILE, "file_sha256": sha256_file(path),
        "variable": OBS_VARIABLE, "units": units, "fill_value": fill,
        "version": str(attrs.get("version", "")), "doi": doi,
        "creation_date": str(attrs.get("Creation_date", "")),
        "acknowledgement": str(attrs.get("Acknowledgement", "")),
        "institution": str(attrs.get("Institution", "")),
        "samples": int(len(vals)), "first_sample": str(dates[0]),
        "last_sample": str(dates[-1]),
        "cadence": "twelve-hourly", "filter": "ten-day low-pass, as distributed",
    }, monthly


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ecco-receipt", type=Path, required=True,
                    help="receipt of the sanctioned overturning computation")
    ap.add_argument("--rapid-root", type=Path,
                    default=Path.home() / "RAPID_26N" / "rapid.ac.uk-2026-09-02",
                    help="verified RAPID tree (execution plumbing)")
    ap.add_argument("--min-valid-fraction", type=float, default=0.5,
                    help="a RAPID month enters at this fraction of valid "
                         "twelve-hourly samples (declared parameter)")
    ap.add_argument("--period", default=None,
                    help="YYYY-MM:YYYY-MM to narrow the overlap (declared "
                         "parameter; default the full overlap)")
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    m = load_method()
    confidence = m.CONFIDENCE

    er = json.loads(args.ecco_receipt.read_text())
    want = sha256_file(AMOC_FILE)
    if er.get("code_sha256") != want:
        sys.exit("the model receipt was not written by the sanctioned "
                 "overturning computation beside this file; no receipt written")
    bp = er["bound_parameters"]
    if bp.get("scope") != "atlantic" or bp.get("convention") != "mass-balanced":
        sys.exit(f"model receipt scope {bp.get('scope')!r} convention "
                 f"{bp.get('convention')!r}; the array observes the Atlantic "
                 "with zero net transport, so only atlantic and mass-balanced "
                 "confront it; no receipt written")
    if not isinstance(er.get("data", {}).get("record"), dict):
        sys.exit("model receipt names no verified data tree; no receipt written")
    ecco_by = dict(zip(er["results"]["months"], er["results"]["amoc_Sv"]))

    obs, monthly = read_rapid(args.rapid_root, args.min_valid_fraction)
    both = [mo for mo in monthly if monthly[mo]["enters"] and mo in ecco_by]
    if args.period:
        mm = re.fullmatch(r"(\d{4}-\d{2}):(\d{4}-\d{2})", args.period)
        if not mm:
            sys.exit("period must be YYYY-MM:YYYY-MM")
        both = [mo for mo in both if mm.group(1) <= mo <= mm.group(2)]
    if len(both) < 24:
        sys.exit(f"overlap of {len(both)} months is under 24; no receipt written")
    if not m.consecutive(both):
        sys.exit("the overlap has a gap; the intervals rest on lag-1 "
                 "autocorrelation, which has no meaning across one; "
                 "no receipt written")
    dropped = [mo for mo in monthly if mo in ecco_by and not monthly[mo]["enters"]]
    ecco = [float(ecco_by[mo]) for mo in both]
    rapid = [float(monthly[mo]["mean"]) for mo in both]

    sc = scores(both, ecco, rapid, m, confidence)
    ecco_trend = m.interval_block(ecco, "Sv/year")
    rapid_trend = m.interval_block(rapid, "Sv/year")

    def sd(v):
        mu = sum(v) / len(v)
        return math.sqrt(sum((x - mu) ** 2 for x in v) / (len(v) - 1))

    receipt = {
        "run_id": (dt.datetime.now(dt.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]),
        "computation": "ecco-rapid-amoc-26n-confrontation",
        "code_sha256": sha256_file(__file__),
        "method_code_sha256": sha256_file(METHOD_FILE),
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model": {
            "receipt": args.ecco_receipt.name,
            "receipt_sha256": sha256_file(args.ecco_receipt),
            "run_id": er["run_id"], "computation": er.get("computation"),
            "code_sha256": er["code_sha256"],
            "section_code_sha256": er.get("section_code_sha256"),
            "data": er["data"], "scope": bp["scope"],
            "convention": bp["convention"], "period": bp["period"],
            "mask_sha256": er["resolved_section"]["mask_sha256"],
            "faces": er["resolved_section"]["faces"],
        },
        "observation": {
            "record": obs["record"]["record"],
            "data_root": obs["record"]["data_root"],
            "file": obs["file"], "file_sha256": obs["file_sha256"],
            "version": obs["version"], "doi": obs["doi"],
            "creation_date": obs["creation_date"],
            "citation": CITATION, "acknowledgement": obs["acknowledgement"],
            "licence": LICENCE, "institution": obs["institution"],
            "variable": obs["variable"], "units": obs["units"],
            "cadence": obs["cadence"], "filter": obs["filter"],
            "samples": obs["samples"], "first_sample": obs["first_sample"],
            "last_sample": obs["last_sample"],
            "published_uncertainty": PUBLISHED_UNCERTAINTY,
        },
        "bound_parameters": {
            "min_valid_fraction": args.min_valid_fraction,
            "overlap": f"{both[0]}:{both[-1]}", "months": len(both),
            "confidence": confidence,
            "colocation": "calendar-month mean of the twelve-hourly "
                          "ten-day-filtered observed series against the "
                          "model's monthly-mean-velocity streamfunction "
                          "maximum",
        },
        "series": {
            "months": both, "ecco_Sv": ecco, "rapid_Sv": rapid,
            "rapid_samples_valid": [monthly[mo]["valid"] for mo in both],
            "rapid_samples_expected": [monthly[mo]["expected"] for mo in both],
            "months_dropped": {mo: {k: monthly[mo][k] for k in ("valid", "expected")}
                               for mo in dropped},
        },
        "digests": {"ecco_series_sha256": digest(both, ecco),
                    "rapid_series_sha256": digest(both, rapid),
                    "canonical": "sha256 of json.dumps({months, values}, "
                                 "separators (',', ':'), sort_keys) of the "
                                 "series as the receipt lists it"},
        "scores": sc,
        "descriptive": {
            "ecco_mean_Sv": sum(ecco) / len(ecco), "ecco_sd_Sv": sd(ecco),
            "rapid_mean_Sv": sum(rapid) / len(rapid), "rapid_sd_Sv": sd(rapid),
            "ecco_trend": ecco_trend, "rapid_trend": rapid_trend,
            "note": "context, not scores: the trends come from the "
                    "sanctioned trend method on each series over the overlap",
        },
        "caveats": {
            "representativeness": ("the array's overturning is a "
                                   "hydrographic-plus-cable-plus-Ekman "
                                   "estimate with its own mass-balance "
                                   "constraint; the model's is the "
                                   "streamfunction maximum of a monthly-mean "
                                   "velocity field with the net removed the "
                                   "same way; the published RMS uncertainty "
                                   "of the observed series sets the floor "
                                   "below which a bias or RMSD is not "
                                   "distinguishable from measurement"),
            "intervals": ("sampling intervals on the scores, from the "
                          "series' own autocorrelation; they do not include "
                          "the observed series' measurement uncertainty"),
            "not_assimilated": ("ECCO V4r4 does not assimilate the RAPID "
                                "transports, so this is a confrontation, "
                                "not a consistency check; the recipe "
                                "concept states the distinction"),
        },
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=1) + "\n")

    print(f"run {receipt['run_id']}: {len(both)} months {both[0]} to {both[-1]}, "
          f"RAPID {obs['version']} {obs['doi']}", file=sys.stderr)
    b, r, c, a = sc["bias_Sv"], sc["rmsd_Sv"], sc["correlation"], sc["anomaly_correlation"]

    def band(blk):
        return (f"[{blk['ci_low']:+.4f}, {blk['ci_high']:+.4f}]" if blk["stated"]
                else f"no interval: {blk['reason']}")
    print(f"  bias        {b['value']:+.4f} Sv  95% {band(b)}  (r1 {b['r1']:+.3f}, "
          f"n_eff {b['n_eff']:.1f} of {b['n']})", file=sys.stderr)
    print(f"  rmsd        {r['value']:.4f} Sv  95% {band(r)}  (r1 of d2 "
          f"{r['msd']['r1']:+.3f}, n_eff {r['msd']['n_eff']:.1f})", file=sys.stderr)
    print(f"  correlation {c['value']:+.4f}     95% {band(c)}  (n_eff {c['n_eff']:.1f})",
          file=sys.stderr)
    print(f"  anomaly corr {a['value']:+.4f}    95% {band(a)}  (n_eff {a['n_eff']:.1f})",
          file=sys.stderr)
    print(f"  means: ECCO {receipt['descriptive']['ecco_mean_Sv']:.4f} "
          f"(sd {receipt['descriptive']['ecco_sd_Sv']:.4f}), RAPID "
          f"{receipt['descriptive']['rapid_mean_Sv']:.4f} "
          f"(sd {receipt['descriptive']['rapid_sd_Sv']:.4f}) Sv", file=sys.stderr)
    for name, blk in (("ECCO", ecco_trend), ("RAPID", rapid_trend)):
        print(f"  trend {name:5s} {blk['trend']:+.4f} Sv/yr 95% "
              f"[{blk['ci_low']:+.4f}, {blk['ci_high']:+.4f}] "
              f"(deseasonalize {blk['deseasonalize']}, "
              f"{'significant' if blk['significant_at_confidence'] else 'not significant'})",
              file=sys.stderr)
    if dropped:
        print(f"  dropped months: {dropped}", file=sys.stderr)
    print(f"  receipt -> {args.receipt}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
