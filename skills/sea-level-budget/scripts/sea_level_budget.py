#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Sanctioned computation for the attested sea level budget closure.

Contract: knowledge/computations/sea-level-budget.md. Over one stated
period, three monthly global-mean series in millimeters, each with a
per-month uncertainty: altimetric sea level (NASA-SSH), steric sea level
from Argo-era hydrography (the sampled depth floor stated), and ocean
mass from the GRACE-FO mascons (the product's formal uncertainty). The
budget is altimetry = mass + steric + deep steric, and the receipt
carries the monthly residual (altimetry minus mass minus steric), the
trend of every term and of the residual with the interval the bundle's
one sanctioned trend method states for it, the combined uncertainty
(the three term uncertainties in quadrature, the deep-steric
systematic stated separately beside it), the verdict
closed_within_uncertainty, and the corrections table the closure
convention demands as a bookkeeping block.

Two input modes. --data-root DIR reads three CSV files (altimetry.csv,
steric.csv, mass.csv: month, value_mm, uncertainty_mm) and the
RECORD.json stamp that names the tree and carries the corrections
table; the layout is documented in the run procedure of the
sea-level-budget skill beside this file.
--fixture [--seed N] [--fixture-offset MM] generates a synthetic record
deterministically (a hash-based Gaussian stream, so the digest does not
depend on any numeric library's release): monthly series 2005-01
through 2022-12 with a known closure (altimetry equals mass plus steric
plus a stated deep-steric trend plus noise consistent with the stated
uncertainties), an annual cycle in mass and steric of opposite phase,
an interannual AR(1) component in each, and the mass months the real
record lacks removed (the 2017-07 through 2018-05 inter-mission gap and
earlier battery-management months). --fixture-offset injects an
inter-mission offset into the mass series after the gap, zero by
default, so a bridged run across the gap has something to fail on.

The matching-period rule is applied at the month: a month with no mass
solution is dropped from every term (a hole, never interpolated), and
the four trends are fitted over the same epochs. Where the period has
no hole the trend and interval are the sanctioned chain verbatim
(ecco_trend_ci.interval_block, imported from beside this file and named
by hash in each block); where it has holes, the same method statement
is applied on the calendar epochs (climatology removed jointly with the
trend as group means over the existing months, lag-1 autocorrelation
over adjacent-epoch residual pairs), which reduces to the chain
exactly when no month is missing. The attester recomputes both.

Refusals, exit 3 with a refusal receipt and never a number: a period
that crosses the inter-mission gap with no --bridge (a citation of the
independent continuity evidence), a term with fewer than 24 months in
the period, a period outside the record, or a term whose interval the
chain refuses to state.

Consumers bind values for the declared parameters and MUST NOT edit
this file; the attester hashes it, regenerates the fixture at the
receipt's seed, and recomputes every trend, interval, uncertainty and
the verdict from the series in the receipt.

  sea_level_budget.py --period YYYY-MM:YYYY-MM --runtime NAME
      (--fixture [--seed N] [--fixture-offset MM] | --data-root DIR)
      [--bridge TEXT] [--runtime-version V] [--receipt PATH]
      [--capability-root DIR]
"""

import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent.parent
COMPUTATION = "skills/sea-level-budget/scripts/sea_level_budget.py"
# The one sanctioned trend method, in the ecco skill; a copy beside
# this file wins, which is how the attester sandboxes a tampered run.
METHOD = (HERE / "ecco_trend_ci.py" if (HERE / "ecco_trend_ci.py").is_file()
          else SKILLS / "ecco" / "scripts" / "ecco_trend_ci.py")

FIXTURE_SPAN = ("2005-01", "2022-12")
GAP = ("2017-07", "2018-05")          # no mass solution: the inter-mission gap
# Battery-management and instrument months the fixture removes from the
# mass record, patterned on the public month list of the mascon
# product; the pattern is the point, not a verified copy of the list.
BATTERY_MONTHS = ("2011-01", "2011-06", "2012-05", "2012-10", "2013-03",
                  "2013-08", "2013-09", "2014-02", "2014-07", "2014-12",
                  "2015-06", "2015-10", "2015-11", "2016-04", "2016-09",
                  "2016-10", "2017-02", "2018-08", "2018-09")
MIN_MONTHS_PER_TERM = 24
Z95 = 1.959963984540054              # two-sided 95 percent normal quantile
DEEP_STERIC_MM_YR = {
    "value": 0.1, "uncertainty": 0.1,
    "basis": "the steric contribution below the Argo sampling floor is "
             "not measured by Argo-era hydrography and is not zero; the "
             "value here is the order the WCRP 2018 budget quotes for the "
             "ocean below 2000 m and is a stated assumption until a "
             "real-data run states its own from the source it cites"}
TRUTH = {                             # what the fixture imposes, mm per year
    "altimetry_mm_yr": 3.5, "mass_mm_yr": 2.1, "steric_mm_yr": 1.3,
    "deep_steric_mm_yr": 0.1, "residual_mm_yr": 0.1,
    "annual_amplitude_mass_mm": 8.5, "annual_peak_mass_month": 10,
    "annual_amplitude_steric_mm": 4.0, "annual_peak_steric_month": 3,
    "noise_sigma_altimetry_mm": 1.2,
    "noise_sigma_mass_mm": "1.5 to 1.9, an annual pattern",
    "noise_sigma_steric_mm": "2.2 in 2005 falling to 1.6 by 2010",
    "interannual_ar1": {"phi": 0.9, "sigma_mass_mm": 0.6, "sigma_steric_mm": 0.7},
    "baseline_offsets_mm": {"altimetry": 12.3, "mass": -4.1, "steric": 7.7},
}
FIXTURE_BOOKKEEPING = {
    "gia": {"altimetry": "synthetic: no GIA signal generated, consistent "
                         "with the mass term by construction; a real run "
                         "names the altimetry GIA convention",
            "mass": "synthetic: none; a real run names the GIA model the "
                    "mascon product applied (grace-gia-correction)"},
    "inverse_barometer": {"altimetry": "synthetic: no atmospheric loading "
                                       "generated; a real run states the "
                                       "dynamic atmospheric correction",
                          "mass": "synthetic: none; a real run states how "
                                  "atmospheric pressure over the ocean was "
                                  "restored or removed in the mass term"},
    "reference_frame": {"altimetry": "synthetic: one frame by construction; "
                                     "a real run names the altimetry frame",
                        "mass": "synthetic: one frame; a real run names the "
                                "degree-1 series the product applied"},
    "effective_smoothing": {"altimetry": "synthetic global mean: no spatial "
                                         "footprint",
                            "mass": "synthetic global mean: no mascon "
                                    "footprint; a real run states the "
                                    "mascon scale and the ocean mask"},
    "low_degree": {"mass": "synthetic: none; a real run names the degree-1 "
                           "and C20/C30 series as applied by the product, "
                           "nothing re-applied (grace-low-degree-replacements)"},
    "deep_steric": {"sampled_depth_floor_m": 2000,
                    "steric_source": "synthetic upper-ocean steric series, "
                                     "standing in for a gridded Argo estimate"},
}
REQUIRED_BOOKKEEPING = (
    ("gia", "altimetry"), ("gia", "mass"),
    ("inverse_barometer", "altimetry"), ("inverse_barometer", "mass"),
    ("reference_frame", "altimetry"), ("reference_frame", "mass"),
    ("effective_smoothing", "altimetry"), ("effective_smoothing", "mass"),
    ("low_degree", "mass"),
    ("deep_steric", "sampled_depth_floor_m"), ("deep_steric", "steric_source"),
)
REASONS = ("gap-without-bridge", "too-few-months", "period-outside-record",
           "interval-not-stated")


# ---- months

def ym(date: str) -> int:
    return int(date[:4]) * 12 + int(date[5:7]) - 1


def label(k: int) -> str:
    return f"{k // 12:04d}-{k % 12 + 1:02d}"


def parse_period(period: str):
    m = re.fullmatch(r"(\d{4}-\d{2}):(\d{4}-\d{2})", period or "")
    if not m or not (1 <= int(m.group(1)[5:]) <= 12 and 1 <= int(m.group(2)[5:]) <= 12) \
            or ym(m.group(1)) > ym(m.group(2)):
        raise SystemExit(f"period must be YYYY-MM:YYYY-MM, got {period!r}")
    return m.group(1), m.group(2)


def crosses_gap(start: str, end: str) -> bool:
    """Mass months on both sides of the inter-mission gap."""
    return ym(start) < ym(GAP[0]) and ym(end) > ym(GAP[1])


# ---- the fixture

def normals(seed: int, stream: str, n: int):
    """A deterministic standard-normal stream: SHA-256 in counter mode
    for the uniforms, Box-Muller for the pair. Stdlib only, so the
    fixture digest is the same on every platform and library release."""
    out, counter = [], 0
    scale = 2.0 ** 64 + 2.0
    while len(out) < n:
        h = hashlib.sha256(f"{seed}:{stream}:{counter}".encode()).digest()
        u1 = (int.from_bytes(h[:8], "big") + 1) / scale
        u2 = (int.from_bytes(h[8:16], "big") + 1) / scale
        r = math.sqrt(-2.0 * math.log(u1))
        out.append(r * math.cos(2.0 * math.pi * u2))
        out.append(r * math.sin(2.0 * math.pi * u2))
        counter += 1
    return out[:n]


def ar1(seed: int, stream: str, n: int, phi: float, sigma: float):
    e = normals(seed, stream, n)
    x = [e[0] * sigma / math.sqrt(1.0 - phi * phi)]
    for i in range(1, n):
        x.append(phi * x[-1] + sigma * e[i])
    return x


def make_fixture(seed: int, offset_mm: float = 0.0) -> dict:
    """The synthetic record: three terms, each dates, value_mm and
    uncertainty_mm, the mass term with the real record's holes."""
    k0, k1 = ym(FIXTURE_SPAN[0]), ym(FIXTURE_SPAN[1])
    n = k1 - k0 + 1
    dates = [label(k) for k in range(k0, k1 + 1)]
    t = TRUTH
    e_alt, e_mass, e_ster = (normals(seed, "altimetry", n),
                             normals(seed, "mass", n), normals(seed, "steric", n))
    ar_mass = ar1(seed, "mass-interannual", n, t["interannual_ar1"]["phi"],
                  t["interannual_ar1"]["sigma_mass_mm"])
    ar_ster = ar1(seed, "steric-interannual", n, t["interannual_ar1"]["phi"],
                  t["interannual_ar1"]["sigma_steric_mm"])
    alt, mass, ster = ([], [], []), ([], [], []), ([], [], [])
    missing = set(BATTERY_MONTHS) | {label(k) for k in range(ym(GAP[0]), ym(GAP[1]) + 1)}
    for i, d in enumerate(dates):
        month = i % 12 + 1
        mass_true = (t["mass_mm_yr"] / 12.0 * i
                     + t["annual_amplitude_mass_mm"]
                     * math.cos(2.0 * math.pi * (month - t["annual_peak_mass_month"]) / 12.0)
                     + ar_mass[i])
        ster_true = (t["steric_mm_yr"] / 12.0 * i
                     + t["annual_amplitude_steric_mm"]
                     * math.cos(2.0 * math.pi * (month - t["annual_peak_steric_month"]) / 12.0)
                     + ar_ster[i])
        deep = t["deep_steric_mm_yr"] / 12.0 * i
        s_alt = t["noise_sigma_altimetry_mm"]
        s_mass = 1.5 + 0.4 * (1.0 + math.cos(2.0 * math.pi * (month - 1) / 12.0)) / 2.0
        s_ster = 1.6 + 0.6 * max(0.0, 1.0 - i / 60.0)
        alt[0].append(d)
        alt[1].append(t["baseline_offsets_mm"]["altimetry"] + mass_true + ster_true + deep + s_alt * e_alt[i])
        alt[2].append(s_alt)
        ster[0].append(d)
        ster[1].append(t["baseline_offsets_mm"]["steric"] + ster_true + s_ster * e_ster[i])
        ster[2].append(s_ster)
        if d in missing:
            continue
        shift = offset_mm if ym(d) > ym(GAP[1]) else 0.0
        mass[0].append(d)
        mass[1].append(t["baseline_offsets_mm"]["mass"] + mass_true + s_mass * e_mass[i] + shift)
        mass[2].append(s_mass)
    term = lambda x: {"dates": x[0], "value_mm": x[1], "uncertainty_mm": x[2]}
    return {"seed": seed, "fixture_offset_mm": float(offset_mm),
            "span": list(FIXTURE_SPAN),
            "terms": {"altimetry": term(alt), "steric": term(ster), "mass": term(mass)}}


def fixture_digest(fx: dict) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(fx, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


# ---- a data root

def read_csv_term(path: Path):
    dates, values, uncs = [], [], []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            dates.append(row["month"].strip())
            values.append(float(row["value_mm"]))
            uncs.append(float(row["uncertainty_mm"]))
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise SystemExit(f"{path.name}: months must be unique and in order")
    return {"dates": dates, "value_mm": values, "uncertainty_mm": uncs}


def read_data_root(root: Path) -> dict:
    root = root.expanduser().resolve()
    stamp = root / "RECORD.json"
    if not stamp.is_file():
        raise SystemExit(f"{root} carries no RECORD.json stamp; nothing is "
                         "computed on an unrecorded tree")
    record = json.loads(stamp.read_text(encoding="utf-8"))
    book = record.get("bookkeeping")
    if not isinstance(book, dict):
        raise SystemExit("RECORD.json carries no bookkeeping table")
    for section, key in REQUIRED_BOOKKEEPING:
        if not (isinstance(book.get(section), dict) and book[section].get(key) not in (None, "")):
            raise SystemExit(f"RECORD.json bookkeeping lacks {section}.{key}")
    terms, files = {}, {}
    for name in ("altimetry", "steric", "mass"):
        path = root / f"{name}.csv"
        if not path.is_file():
            raise SystemExit(f"{root} lacks {name}.csv")
        terms[name] = read_csv_term(path)
        files[path.name] = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return {"terms": terms, "record": record, "files": files, "data_root": str(root)}


# ---- the trend on calendar epochs

def method():
    spec = importlib.util.spec_from_file_location("ecco_trend_ci", METHOD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def epoch_fit(t_cal, y, uncertainty, deseasonalize, tc):
    """The sanctioned method statement on calendar epochs t_cal (month
    indices, increasing, holes allowed). Returns the chain's
    intermediates, the fit weights of the slope and the formal error
    propagated from the per-month uncertainties."""
    n = len(y)
    t = [float(v) for v in t_cal]
    y = [float(v) for v in y]
    if deseasonalize == "climatology":
        groups = {}
        for i, k in enumerate(t_cal):
            groups.setdefault(k % 12, []).append(i)
        for idx in groups.values():
            ybar_g = sum(y[i] for i in idx) / len(idx)
            tbar_g = sum(t[i] for i in idx) / len(idx)
            for i in idx:
                y[i] -= ybar_g
                t[i] -= tbar_g
    tbar = sum(t) / n
    ybar = sum(y) / n
    sxx = sum((a - tbar) ** 2 for a in t)
    sxy = sum((a - tbar) * (b - ybar) for a, b in zip(t, y))
    slope = sxy / sxx
    intercept = ybar - slope * tbar
    e = [b - (intercept + slope * a) for a, b in zip(t, y)]
    ss = sum(v * v for v in e)
    weights = [(a - tbar) / sxx for a in t]
    formal_se = math.sqrt(sum((w * s) ** 2 for w, s in zip(weights, uncertainty)))
    out = {"n": n, "slope_per_month": slope, "sxx": sxx, "ss": ss,
           "formal_se_per_month": formal_se, "interval": False}
    if n < tc.MIN_MONTHS:
        out["reason"] = f"an interval needs at least {tc.MIN_MONTHS} months, got {n}"
        return out
    num = sum(e[i] * e[i + 1] for i in range(n - 1) if t_cal[i + 1] - t_cal[i] == 1)
    r1 = num / ss
    n_eff = min(float(n), n * (1.0 - r1) / (1.0 + r1))
    dof = n_eff - 2.0
    out.update({"r1": r1, "n_eff": n_eff, "dof": dof})
    if dof < tc.MIN_DOF:
        out["reason"] = (f"effective sample size {n_eff:.2f} leaves {dof:.2f} degrees "
                         f"of freedom, below {tc.MIN_DOF}; no interval is stated")
        return out
    se = math.sqrt(ss / dof / sxx)
    out.update({"interval": True, "se_per_month": se,
                "t_quantile": tc.t_quantile(0.5 + tc.CONFIDENCE / 2.0, dof),
                "naive_se_per_month": math.sqrt(ss / (n - 2) / sxx),
                "naive_t_quantile": tc.t_quantile(0.5 + tc.CONFIDENCE / 2.0, n - 2)})
    return out


def trend_block(t_cal, y, uncertainty, n_calendar, tc) -> dict:
    """The interval block a term carries: the sanctioned chain verbatim
    where the epochs are the period's consecutive months, the same
    method on the calendar epochs otherwise; plus the epochs it was
    fitted on and the formal error from the per-month uncertainties."""
    n = len(y)
    holes = n != n_calendar
    des = tc.default_deseasonalize(n_calendar)
    f = epoch_fit(t_cal, y, uncertainty, des, tc)
    block = {"method": "trend-ci",
             "method_code_sha256": hashlib.sha256(METHOD.read_bytes()).hexdigest(),
             "confidence": tc.CONFIDENCE, "units": "mm/year", "n": n,
             "deseasonalize": des, "trend": f["slope_per_month"] * 12.0}
    if f["interval"]:
        trend = block["trend"]
        half = f["t_quantile"] * f["se_per_month"] * 12.0
        block.update({"stated": True, "ci_low": trend - half, "ci_high": trend + half,
                      "half_width": half,
                      "naive_half_width": f["naive_t_quantile"] * f["naive_se_per_month"] * 12.0,
                      "r1": f["r1"], "n_eff": f["n_eff"], "dof": f["dof"],
                      "se": f["se_per_month"] * 12.0, "t_quantile": f["t_quantile"],
                      "significant_at_confidence": bool((trend - half) * (trend + half) > 0)})
    else:
        block.update({"stated": False, "reason": f["reason"]})
    if not holes:
        # The chain itself, so a hole-free block is the sanctioned
        # numbers to the last digit and the shared attester chain binds it.
        verbatim = tc.interval_block(y, "mm/year")
        for k, v in verbatim.items():
            if isinstance(v, float) and not math.isclose(v, block[k], rel_tol=1e-12, abs_tol=1e-12):
                raise SystemExit(f"epoch fit disagrees with the sanctioned chain on {k}: "
                                 f"{block[k]} vs {v}")
        block = verbatim
    block["epochs"] = {"n_calendar": n_calendar, "n_used": n,
                       "n_missing": n_calendar - n, "holes": holes,
                       "policy": "the sanctioned chain verbatim on a hole-free "
                                 "period; the same method on the calendar epochs "
                                 "when months are missing (climatology as group "
                                 "means over the existing months, lag-1 "
                                 "autocorrelation over adjacent epochs)"}
    block["formal_95_mm_yr"] = Z95 * f["formal_se_per_month"] * 12.0
    return block


# ---- identity and plumbing

def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def value_digest(value) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def package_root(start: Path):
    for p in (start, *start.parents):
        if (p / ".osp" / "package.yaml").is_file():
            return p
    return None


def package_identity(root) -> dict:
    """name, version and release lock digest of a package tree, the way
    core's capability_identity and this bundle's receipt_identity read
    them; null throughout where no package tree is found."""
    if root is None:
        return {"name": None, "version": None, "release_lock": None}
    text = (root / ".osp" / "package.yaml").read_text(encoding="utf-8")
    block = text.split("package:", 1)[1]
    name = re.search(r"^\s+name:\s*['\"]?([A-Za-z0-9._-]+)", block, re.M)
    version = re.search(r"^\s+version:\s*['\"]?([0-9][0-9.]*)", block, re.M)
    lock_path = root / ".osp" / "release-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.is_file() else None
    return {"name": name.group(1) if name else None,
            "version": version.group(1) if version else None,
            "release_lock": value_digest(lock) if lock is not None else None}


def bundle_root():
    return package_root(HERE)


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


# ---- the computation

def compute(terms: dict, start: str, end: str, bridge, bookkeeping: dict, tc):
    """(receipt body, None) or (None, (reason_code, reason)) over the
    period start..end on the three terms."""
    k0, k1 = ym(start), ym(end)
    calendar = [label(k) for k in range(k0, k1 + 1)]
    n_calendar = len(calendar)
    by_term = {}
    for name, term in terms.items():
        by_term[name] = {d: (v, u) for d, v, u in
                         zip(term["dates"], term["value_mm"], term["uncertainty_mm"])}
    have = {name: [d for d in calendar if d in by_term[name]] for name in terms}
    for name in ("altimetry", "steric", "mass"):
        if len(have[name]) < MIN_MONTHS_PER_TERM:
            return None, ("too-few-months",
                          f"the {name} term has {len(have[name])} months in "
                          f"{start}:{end}; the budget needs at least "
                          f"{MIN_MONTHS_PER_TERM} in every term")
    if crosses_gap(start, end) and not bridge:
        return None, ("gap-without-bridge",
                      f"the period {start}:{end} crosses the GRACE to GRACE-FO gap "
                      f"({GAP[0]} through {GAP[1]}); a trend across it needs "
                      "--bridge, a citation of the independent continuity "
                      "evidence, and none was given")
    used = [d for d in calendar if all(d in by_term[n] for n in terms)]
    missing = [d for d in calendar if d not in used]
    if len(used) < MIN_MONTHS_PER_TERM:
        return None, ("too-few-months",
                      f"only {len(used)} months of {start}:{end} carry all three "
                      f"terms; the budget needs at least {MIN_MONTHS_PER_TERM}")
    t_cal = [ym(d) - k0 for d in used]
    series = {"dates": used}
    for name in ("altimetry", "steric", "mass"):
        series[f"{name}_mm"] = [by_term[name][d][0] for d in used]
        series[f"{name}_uncertainty_mm"] = [by_term[name][d][1] for d in used]
    series["residual_mm"] = [a - m - s for a, m, s in zip(
        series["altimetry_mm"], series["mass_mm"], series["steric_mm"])]
    blocks = {}
    for name in ("altimetry", "mass", "steric"):
        blocks[name] = trend_block(t_cal, series[f"{name}_mm"],
                                   series[f"{name}_uncertainty_mm"], n_calendar, tc)
    resid_unc = [math.sqrt(a * a + m * m + s * s) for a, m, s in zip(
        series["altimetry_uncertainty_mm"], series["mass_uncertainty_mm"],
        series["steric_uncertainty_mm"])]
    blocks["residual"] = trend_block(t_cal, series["residual_mm"], resid_unc, n_calendar, tc)
    for name in ("altimetry", "mass", "steric"):
        if not blocks[name]["stated"]:
            return None, ("interval-not-stated",
                          f"the {name} trend carries no interval ({blocks[name]['reason']}); "
                          "a combined uncertainty cannot be formed")
    term_unc = {name: max(blocks[name]["half_width"], blocks[name]["formal_95_mm_yr"])
                for name in ("altimetry", "mass", "steric")}
    quadrature = math.sqrt(sum(v * v for v in term_unc.values()))
    bar = quadrature + DEEP_STERIC_MM_YR["uncertainty"]
    gap = blocks["residual"]["trend"] - DEEP_STERIC_MM_YR["value"]
    closed = abs(gap) <= bar
    book = json.loads(json.dumps(bookkeeping))
    book["deep_steric"]["systematic_mm_yr"] = dict(DEEP_STERIC_MM_YR)
    book["gap_handling"] = {
        "rule": "a month with no solution in any term is a hole: dropped from "
                "every term (the matching-period rule at the month), never "
                "interpolated; the trends are fitted on the calendar epochs "
                "that remain",
        "months_missing": missing,
        "crosses_intermission_gap": crosses_gap(start, end),
        "bridge": bridge or None,
    }
    body = {
        "months": {"period": [start, end], "n_calendar": n_calendar,
                   "n_used": len(used), "used": used, "missing": missing,
                   "missing_by_term": {name: [d for d in calendar if d not in by_term[name]]
                                       for name in ("altimetry", "steric", "mass")}},
        "series": series,
        "trend_altimetry_mm_yr": round(blocks["altimetry"]["trend"], 4),
        "trend_mass_mm_yr": round(blocks["mass"]["trend"], 4),
        "trend_steric_mm_yr": round(blocks["steric"]["trend"], 4),
        "trend_residual_mm_yr": round(blocks["residual"]["trend"], 4),
        "trends": blocks,
        "combined_uncertainty": {
            "rule": "each term's uncertainty is the larger of its sampling half "
                    "width (the sanctioned chain, 95 percent) and the formal "
                    "error propagated from its per-month uncertainties at the "
                    "same confidence; the three combine in quadrature; the "
                    "deep-steric systematic is stated separately and its "
                    "uncertainty is added to the bar, not folded in",
            "terms_mm_yr": term_unc,
            "quadrature_mm_yr": quadrature,
            "deep_steric_systematic_mm_yr": dict(DEEP_STERIC_MM_YR),
            "bar_mm_yr": bar,
        },
        "verdict": {
            "closed_within_uncertainty": closed,
            "rule": "closed when the residual trend minus the stated deep-steric "
                    "value lies within the quadrature of the three term "
                    "uncertainties plus the deep-steric uncertainty",
            "closure_gap_mm_yr": gap,
            "bar_mm_yr": bar,
        },
        "bookkeeping": book,
    }
    return body, None


def receipt_head(args, capability, bundle, data) -> dict:
    return {
        "computation": COMPUTATION,
        "code_sha256": sha256_file(Path(__file__).resolve()),
        "capability": capability,
        "bundle": bundle,
        "runtime": {"name": args.runtime, "version": args.runtime_version},
        "generated_utc": now_utc(),
        "data": data,
        "bound_parameters": {"period": args.period, "bridge": args.bridge or None},
    }


def finish(receipt: dict) -> dict:
    receipt["run_id"] = value_digest({k: v for k, v in receipt.items()
                                      if k != "generated_utc"})[:23]
    return receipt


def write(receipt: dict, path) -> None:
    text = json.dumps(receipt, indent=2) + "\n"
    if path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"receipt written: {path}", file=sys.stderr)
    else:
        print(text)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--period", required=True, help="YYYY-MM:YYYY-MM (declared parameter)")
    ap.add_argument("--bridge", default=None,
                    help="citation of the independent continuity evidence; required "
                         "for a period that crosses the inter-mission gap (declared parameter)")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", action="store_true", help="the synthetic record")
    mode.add_argument("--data-root", type=Path, help="a recorded tree (execution plumbing)")
    ap.add_argument("--seed", type=int, default=7, help="fixture seed (default 7)")
    ap.add_argument("--fixture-offset", type=float, default=0.0,
                    help="inter-mission offset injected into the fixture's mass "
                         "series after the gap, mm (default 0)")
    ap.add_argument("--runtime", required=True,
                    help="the runtime that ran this (claude-code, claude-cowork, "
                         "openai-codex, a gate's name, ...)")
    ap.add_argument("--runtime-version", default=None)
    ap.add_argument("--receipt", type=Path, default=None)
    ap.add_argument("--capability-root", type=Path, default=None,
                    help="the package tree this run is evidence for (default: the "
                         "bundle this executor ships in)")
    args = ap.parse_args(argv)

    start, end = parse_period(args.period)
    tc = method()
    bundle = package_identity(bundle_root())
    capability = (package_identity(package_root(args.capability_root.expanduser().resolve()))
                  if args.capability_root else bundle)
    if args.fixture:
        fx = make_fixture(args.seed, args.fixture_offset)
        data = {"mode": "fixture", "seed": args.seed,
                "fixture_offset_mm": float(args.fixture_offset),
                "span": list(FIXTURE_SPAN), "digest": fixture_digest(fx),
                "generator": COMPUTATION + " (make_fixture)",
                "generator_sha256": sha256_file(Path(__file__).resolve()),
                "truth": TRUTH}
        terms, bookkeeping, span = fx["terms"], FIXTURE_BOOKKEEPING, FIXTURE_SPAN
    else:
        tree = read_data_root(args.data_root)
        data = {"mode": "data-root", "data_root": tree["data_root"],
                "record": tree["record"], "files": tree["files"]}
        terms, bookkeeping = tree["terms"], tree["record"]["bookkeeping"]
        span = (min(min(t["dates"]) for t in terms.values()),
                max(max(t["dates"]) for t in terms.values()))
    head = receipt_head(args, capability, bundle, data)

    refusal = None
    if not (ym(span[0]) <= ym(start) and ym(end) <= ym(span[1])):
        refusal = ("period-outside-record",
                   f"the period {start}:{end} lies outside the record "
                   f"{span[0]} through {span[1]}")
    else:
        body, refusal = compute(terms, start, end, args.bridge, bookkeeping, tc)
    if refusal:
        receipt = finish({**head, "refused": True, "reason_code": refusal[0],
                          "reason": refusal[1]})
        print(f"REFUSED ({refusal[0]}): {refusal[1]}")
        write(receipt, args.receipt)
        return 3

    receipt = finish({**head, "refused": False, **body,
                      "caveats": [
                          ("a fixture run proves the chain, not the ocean; the real-data "
                           "anchor is the stamped data root run the concept records")
                          if args.fixture else
                          ("a real-data run on a stamped record: each term loader's stamp "
                           "in the data root states the product, the mask, the GIA "
                           "convention and the uncertainty basis, and the residual carries "
                           "the coverage mismatch between the terms"),
                          "the series and the residual travel at full precision so "
                          "every trend, interval and the verdict are recomputable "
                          "from the receipt",
                          "the interval is a statement about sampling under an AR(1) "
                          "residual model on the epochs used; product systematics "
                          "enter through the bookkeeping table and the deep-steric term",
                      ]})
    v = receipt["verdict"]
    where = (f"fixture seed {args.seed}" + (f" offset {args.fixture_offset} mm"
                                             if args.fixture_offset else "")
             if args.fixture else f"data root {data['data_root']}")
    for name in ("altimetry", "mass", "steric", "residual"):
        b = receipt["trends"][name]
        band = (f"95% [{b['ci_low']:+.4f}, {b['ci_high']:+.4f}] (r1 {b['r1']:+.4f}, "
                f"n_eff {b['n_eff']:.2f} of {b['n']})" if b["stated"]
                else f"no interval: {b['reason']}")
        print(f"trend {name} {b['trend']:+.4f} mm/yr, {band}", file=sys.stderr)
    print(f"sea level budget {start}:{end} on {where}: {receipt['months']['n_used']} of "
          f"{receipt['months']['n_calendar']} months used; residual trend "
          f"{receipt['trends']['residual']['trend']:+.4f} mm/yr, closure gap "
          f"{v['closure_gap_mm_yr']:+.4f} against a bar of {v['bar_mm_yr']:.4f} "
          f"(quadrature {receipt['combined_uncertainty']['quadrature_mm_yr']:.4f} plus "
          f"deep steric {DEEP_STERIC_MM_YR['uncertainty']}); "
          f"closed_within_uncertainty {str(v['closed_within_uncertainty']).lower()}; "
          f"run {receipt['run_id']}")
    write(receipt, args.receipt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
