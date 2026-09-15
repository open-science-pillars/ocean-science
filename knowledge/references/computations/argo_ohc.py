#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Sanctioned computation for the attested Argo ocean heat content
change.

Contract: computations/argo-ohc.md. Over one stated window of calendar
months, one monthly series of open-ocean heat content anomaly in
zettajoules (1e21 J) for one layer, 0 to 700 dbar or 0 to 2000 dbar,
from the Roemmich and Gilson gridded Argo product as the loader wrote
it (an anomaly against the product's 2004 to 2018 climatology, summed
over the product's mapped open-ocean domain, never scaled to the
global ocean), each month with a stated uncertainty. The receipt
carries four terms and a residual:

  trend            the linear rate of the series over the window in
                   ZJ per year, the annual cycle removed jointly with
                   the fit as calendar-month group means, with a 95
                   percent interval under a lag-1 autocorrelated
                   residual (the effective sample size capped at the
                   sample, Student's t on n_eff minus 2) and the
                   formal error the per-month uncertainties propagate;
  change           the heat content change from the first calendar
                   year of the window to the last that the trend
                   implies: the rate times the years between the two
                   year centres, its uncertainty the interval half
                   width times the same span;
  endpoint_change  the same change read directly: the mean of the last
                   twelve months minus the mean of the first twelve,
                   its uncertainty from the per-month floor;
  deep_omission    the ocean below 2000 dbar, which the product does
                   not sample and this term does not carry: a stated
                   omission with the published rate and its source,
                   never added to the terms.

The residual is endpoint_change minus change; the combined uncertainty
is the two in quadrature; the verdict consistent_within_uncertainty
says whether the record's own endpoints agree with its linear rate.
The receipt also states the rate per unit area of the mapped domain
and per unit area of the Earth's surface (4 pi R squared with the
6371 km mean radius, the convention the published inventories use),
and, on a data root whose record carries a published anchor for the
layer, the distance of the run from that anchor.

Two input modes. --data-root DIR reads ohc-DEPTH.csv (month, value_ZJ,
uncertainty_ZJ), the loader's stamp ohc-DEPTH-stamp.json and the
RECORD.json the data-root tool wrote, with its bookkeeping table
(climatology, anomaly convention, coverage, deep omission, uncertainty
basis, anchor); a tree that lacks the record or any required statement
is not computed on. --fixture [--seed N] generates a synthetic record
deterministically (a hash-based Gaussian stream, so the digest does not
depend on any numeric library's release): a monthly series 2005-01
through 2024-12 with a planted rate for the layer, an annual cycle, an
interannual AR(1) component and noise at the stated per-month
uncertainty, so the receipt shows the planted change recovered.

Refusals, exit 3 with a refusal receipt and never a number: a window
that leaves the record's coverage (window-outside-coverage), fewer
than 24 months, or fewer than 12 in either end year, in the window
(too-few-months), or a trend whose interval cannot be stated
(interval-not-stated).

Consumers bind values for the declared parameters and MUST NOT edit
this file; the attester hashes it, regenerates the fixture at the
receipt's seed, and recomputes every number from the series in the
receipt.

  argo_ohc.py --window YYYY-MM:YYYY-MM --depth 700|2000 --runtime NAME
      (--fixture [--seed N] | --data-root DIR)
      [--runtime-version V] [--receipt PATH] [--capability-root DIR]
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPUTATION = "references/computations/argo_ohc.py"

DEPTHS = (700, 2000)
FIXTURE_SPAN = ("2005-01", "2024-12")
MIN_MONTHS = 24
END_MONTHS = 12
CONFIDENCE = 0.95
MIN_DOF = 1.0
Z95 = 1.959963984540054              # two-sided 95 percent normal quantile
SECONDS_PER_YEAR = 365.25 * 86400.0
EARTH_RADIUS_M = 6371000.0           # the mean radius; the loader's cell areas use the same
EARTH_AREA_M2 = 4.0 * math.pi * EARTH_RADIUS_M ** 2
ZJ = 1.0e21
FIXTURE_DOMAIN_AREA_M2 = 2.2e14      # a stated fixture parameter of the order of the RG mapped domain
DEEP_OMISSION = {
    "layer": "below 2000 m",
    "statement": "the ocean below 2000 dbar is not sampled by the Argo core array or the "
                 "Roemmich and Gilson product and is not in any term of this receipt; the "
                 "published rate is named for the reader and never added to the terms",
    "published_rate_ZJ_yr": 0.97, "published_uncertainty_ZJ_yr": 0.48,
    "published_rate_W_m2": 0.06, "published_uncertainty_W_m2": 0.03,
    "period": "1992 to 2020, a constant linear trend",
    "source": "von Schuckmann and others (2023), Earth System Science Data 15, 1675 to 1709, "
              "doi:10.5194/essd-15-1675-2023, section 2 on the deep ocean, updating Purkey and "
              "Johnson (2010), doi:10.1175/2010JCLI3682.1",
}
TRUTH = {                             # what the fixture imposes, per layer
    700: {"rate_ZJ_yr": 6.3, "annual_amplitude_ZJ": 8.0, "annual_peak_month": 3,
          "noise_sigma_ZJ": 3.0, "interannual_ar1": {"phi": 0.8, "sigma_ZJ": 2.0},
          "baseline_offset_ZJ": -15.0},
    2000: {"rate_ZJ_yr": 10.0, "annual_amplitude_ZJ": 9.0, "annual_peak_month": 3,
           "noise_sigma_ZJ": 4.0, "interannual_ar1": {"phi": 0.8, "sigma_ZJ": 2.5},
           "baseline_offset_ZJ": -25.0},
    "basis": "the rates are the order of the 2006 to 2020 rates the Earth heat inventory "
             "states for the two layers (0.39 and 0.62 W per m2 of the Earth's surface, "
             "von Schuckmann and others 2023, Table 1) converted with the Earth's area; "
             "the cycle, the interannual component and the noise are fixture parameters",
}
FIXTURE_BOOKKEEPING = {
    "climatology": {"statement": "synthetic: the series is an anomaly against a zero baseline "
                                 "by construction; a real run names the RG 2004 to 2018 mean "
                                 "field the loader subtracted",
                    "period": "synthetic"},
    "anomaly_convention": {"statement": "synthetic: value_ZJ is the planted heat content anomaly "
                                        "of the layer over a fixture domain; a difference "
                                        "between two months is a heat content change"},
    "coverage": {"statement": "synthetic: one fixture domain, no mask; a real run states the "
                              "product's mapped open-ocean domain and its cell count",
                 "domain_area_m2": FIXTURE_DOMAIN_AREA_M2,
                 "months": list(FIXTURE_SPAN)},
    "deep_omission": {"statement": "the fixture plants nothing below the layer floor, as the "
                                   "product carries nothing below 2000 dbar"},
    "uncertainty": {"basis": "synthetic: the per-month uncertainty is the noise sigma the fixture "
                             "generated the series with, written on every row"},
}
REQUIRED_BOOKKEEPING = (
    ("climatology", "statement"), ("anomaly_convention", "statement"),
    ("coverage", "statement"), ("coverage", "domain_area_m2"),
    ("deep_omission", "statement"), ("uncertainty", "basis"),
)
REASONS = ("window-outside-coverage", "too-few-months", "interval-not-stated")


# ---- months

def ym(date: str) -> int:
    return int(date[:4]) * 12 + int(date[5:7]) - 1


def label(k: int) -> str:
    return f"{k // 12:04d}-{k % 12 + 1:02d}"


def parse_window(window: str):
    m = re.fullmatch(r"(\d{4}-\d{2}):(\d{4}-\d{2})", window or "")
    if not m or not (1 <= int(m.group(1)[5:]) <= 12 and 1 <= int(m.group(2)[5:]) <= 12) \
            or ym(m.group(1)) > ym(m.group(2)):
        raise SystemExit(f"window must be YYYY-MM:YYYY-MM, got {window!r}")
    return m.group(1), m.group(2)


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


def make_fixture(seed: int, depth: int) -> dict:
    """The synthetic record for one layer: dates, value_ZJ and
    uncertainty_ZJ over the fixture span, with the planted truth."""
    t = TRUTH[depth]
    k0, k1 = ym(FIXTURE_SPAN[0]), ym(FIXTURE_SPAN[1])
    n = k1 - k0 + 1
    dates = [label(k) for k in range(k0, k1 + 1)]
    e = normals(seed, f"ohc-{depth}", n)
    inter = ar1(seed, f"ohc-{depth}-interannual", n, t["interannual_ar1"]["phi"],
                t["interannual_ar1"]["sigma_ZJ"])
    values, uncs = [], []
    for i, d in enumerate(dates):
        month = i % 12 + 1
        truth = (t["rate_ZJ_yr"] / 12.0 * i
                 + t["annual_amplitude_ZJ"]
                 * math.cos(2.0 * math.pi * (month - t["annual_peak_month"]) / 12.0)
                 + inter[i])
        values.append(t["baseline_offset_ZJ"] + truth + t["noise_sigma_ZJ"] * e[i])
        uncs.append(t["noise_sigma_ZJ"])
    return {"seed": seed, "depth": depth, "span": list(FIXTURE_SPAN),
            "series": {"dates": dates, "value_ZJ": values, "uncertainty_ZJ": uncs}}


def fixture_digest(fx: dict) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(fx, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


# ---- a data root

def read_csv_series(path: Path):
    dates, values, uncs = [], [], []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            dates.append(row["month"].strip())
            values.append(float(row["value_ZJ"]))
            uncs.append(float(row["uncertainty_ZJ"]))
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise SystemExit(f"{path.name}: months must be unique and in order")
    return {"dates": dates, "value_ZJ": values, "uncertainty_ZJ": uncs}


def read_data_root(root: Path, depth: int) -> dict:
    root = root.expanduser().resolve()
    record_path = root / "RECORD.json"
    if not record_path.is_file():
        raise SystemExit(f"{root} carries no RECORD.json; nothing is computed on an unrecorded tree")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    book = record.get("bookkeeping")
    if not isinstance(book, dict):
        raise SystemExit("RECORD.json carries no bookkeeping table")
    for section, key in REQUIRED_BOOKKEEPING:
        if not (isinstance(book.get(section), dict) and book[section].get(key) not in (None, "")):
            raise SystemExit(f"RECORD.json bookkeeping lacks {section}.{key}")
    term = f"ohc-{depth}"
    csv_path, stamp_path = root / f"{term}.csv", root / f"{term}-stamp.json"
    for p in (csv_path, stamp_path):
        if not p.is_file():
            raise SystemExit(f"{root} lacks {p.name}")
    manifest = record.get("manifest") or {}
    files = {}
    for p in (csv_path, stamp_path):
        digest = sha256_file(p)
        if manifest.get(p.name) != digest:
            raise SystemExit(f"{p.name} does not match the RECORD.json manifest; the tree was "
                             "edited after it was recorded")
        files[p.name] = digest
    stamp = json.loads(stamp_path.read_text(encoding="utf-8"))
    return {"series": read_csv_series(csv_path), "record": record, "stamp": stamp,
            "files": files, "record_sha256": sha256_file(record_path), "data_root": str(root)}


# ---- Student's t, written from the definition

def _betacf(a, b, x):
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 600):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 / (max(abs(1.0 + aa * d), tiny) * (1 if 1.0 + aa * d >= 0 else -1))
        c = 1.0 + aa / (c if abs(c) > tiny else tiny)
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        dd = 1.0 + aa * d
        d = 1.0 / (dd if abs(dd) > tiny else tiny)
        c = 1.0 + aa / (c if abs(c) > tiny else tiny)
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            return h
    raise ArithmeticError("incomplete beta did not converge")


def betainc(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                     + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1.0 - tail if t >= 0 else tail


def t_quantile(p, df):
    lo, hi = 0.0, 1.0
    while t_cdf(hi, df) < p:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13 * max(1.0, hi):
            break
    return 0.5 * (lo + hi)


# ---- the trend on calendar epochs

def trend_block(t_cal, y, uncertainty) -> dict:
    """The method statement on calendar epochs t_cal (month indices
    from the window start, increasing, holes allowed): calendar-month
    group means removed from the series and the time index, least
    squares, lag-1 autocorrelation over adjacent-epoch residual pairs,
    the effective sample size capped at n, Student's t on n_eff minus
    2; the slope's weights carry the per-month uncertainties into a
    formal error."""
    n = len(y)
    t = [float(v) for v in t_cal]
    y = [float(v) for v in y]
    groups = {}
    for i, k in enumerate(t_cal):
        groups.setdefault(k % 12, []).append(i)
    for idx in groups.values():
        ybar_g = sum(y[i] for i in idx) / len(idx)
        tbar_g = sum(t[i] for i in idx) / len(idx)
        for i in idx:
            y[i] -= ybar_g
            t[i] -= tbar_g
    tbar, ybar = sum(t) / n, sum(y) / n
    sxx = sum((a - tbar) ** 2 for a in t)
    sxy = sum((a - tbar) * (b - ybar) for a, b in zip(t, y))
    slope = sxy / sxx
    icpt = ybar - slope * tbar
    e = [b - (icpt + slope * a) for a, b in zip(t, y)]
    ss = sum(v * v for v in e)
    weights = [(a - tbar) / sxx for a in t]
    formal_se = math.sqrt(sum((w * s) ** 2 for w, s in zip(weights, uncertainty)))
    block = {"method": "least squares on calendar epochs, the annual cycle removed as "
                       "calendar-month group means, lag-1 autocorrelation over adjacent "
                       "epochs, effective sample size capped at n, Student's t on n_eff - 2",
             "confidence": CONFIDENCE, "units": "ZJ/year", "n": n,
             "deseasonalize": "climatology", "trend": slope * 12.0,
             "formal_95_ZJ_yr": Z95 * formal_se * 12.0}
    num = sum(e[i] * e[i + 1] for i in range(n - 1) if t_cal[i + 1] - t_cal[i] == 1)
    r1 = num / ss if ss > 0 else 0.0
    n_eff = min(float(n), n * (1.0 - r1) / (1.0 + r1))
    dof = n_eff - 2.0
    block.update({"r1": r1, "n_eff": n_eff, "dof": dof})
    if dof < MIN_DOF:
        block.update({"stated": False,
                      "reason": f"effective sample size {n_eff:.2f} leaves {dof:.2f} degrees of "
                                f"freedom, below {MIN_DOF}; no interval is stated"})
        return block
    se = math.sqrt(ss / dof / sxx)
    tq = t_quantile(0.5 + CONFIDENCE / 2.0, dof)
    half = tq * se * 12.0
    trend = block["trend"]
    block.update({"stated": True, "se": se * 12.0, "t_quantile": tq, "half_width": half,
                  "ci_low": trend - half, "ci_high": trend + half,
                  "significant_at_confidence": bool((trend - half) * (trend + half) > 0)})
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
    """name, version and release lock digest of a package tree; null
    throughout where no package tree is found."""
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


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


# ---- the computation

def rates_per_area(rate_ZJ_yr: float, domain_area_m2: float) -> dict:
    w = rate_ZJ_yr * ZJ / SECONDS_PER_YEAR
    return {"W_m2_of_domain": w / domain_area_m2,
            "W_m2_of_earth_surface": w / EARTH_AREA_M2,
            "domain_area_m2": domain_area_m2,
            "earth_surface_area_m2": EARTH_AREA_M2,
            "rule": "the rate in ZJ per year over the mapped domain, divided by the domain's "
                    "area and by the Earth's surface area (4 pi R squared, R the 6371 km "
                    "mean radius); the second is the convention of the published inventories, "
                    "and a domain that covers part of the ocean understates it by construction"}


def anchor_block(anchor, per_area: dict, trend: dict):
    """The distance of the run from a published anchor for the layer,
    or None where the record carries none."""
    if not isinstance(anchor, dict) or not isinstance(anchor.get("value_W_m2_global"), (int, float)):
        return None
    a = float(anchor["value_W_m2_global"])
    u = float(anchor.get("uncertainty_W_m2_global") or 0.0)
    frac = anchor.get("ocean_area_fraction")
    run_global = per_area["W_m2_of_earth_surface"]
    out = {"published": anchor,
           "run_W_m2_of_earth_surface": run_global,
           "run_W_m2_of_domain": per_area["W_m2_of_domain"],
           "run_ZJ_yr": trend["trend"],
           "anchor_ZJ_yr": a * EARTH_AREA_M2 * SECONDS_PER_YEAR / ZJ,
           "anchor_uncertainty_ZJ_yr": u * EARTH_AREA_M2 * SECONDS_PER_YEAR / ZJ,
           "distance_W_m2_of_earth_surface": run_global - a,
           "distance_over_anchor_uncertainty": (run_global - a) / u if u > 0 else None,
           "rule": "distance is the run's rate per unit Earth surface minus the published "
                   "rate, and that distance over the published uncertainty; the domain "
                   "comparison divides the published rate by the ocean-area fraction its "
                   "source states and compares with the run's rate per unit domain area"}
    if isinstance(frac, (int, float)) and frac > 0:
        out["anchor_W_m2_of_ocean"] = a / frac
        out["anchor_uncertainty_W_m2_of_ocean"] = u / frac
        out["distance_W_m2_of_ocean"] = per_area["W_m2_of_domain"] - a / frac
    return out


def compute(series: dict, start: str, end: str, depth: int, bookkeeping: dict, anchor):
    """(receipt body, None) or (None, (reason_code, reason)) over the
    window start..end on one series."""
    k0, k1 = ym(start), ym(end)
    calendar = [label(k) for k in range(k0, k1 + 1)]
    n_calendar = len(calendar)
    by = {d: (v, u) for d, v, u in zip(series["dates"], series["value_ZJ"], series["uncertainty_ZJ"])}
    used = [d for d in calendar if d in by]
    missing = [d for d in calendar if d not in by]
    if n_calendar < MIN_MONTHS or len(used) < MIN_MONTHS:
        return None, ("too-few-months",
                      f"{len(used)} of {n_calendar} months of {start}:{end} carry a value; the "
                      f"change needs at least {MIN_MONTHS}")
    first_year = [d for d in calendar[:END_MONTHS] if d in by]
    last_year = [d for d in calendar[-END_MONTHS:] if d in by]
    if len(first_year) < END_MONTHS or len(last_year) < END_MONTHS:
        return None, ("too-few-months",
                      f"the first twelve months of {start}:{end} carry {len(first_year)} values "
                      f"and the last twelve {len(last_year)}; the endpoint means need all twelve")
    t_cal = [ym(d) - k0 for d in used]
    y = [by[d][0] for d in used]
    u = [by[d][1] for d in used]
    block = trend_block(t_cal, y, u)
    if not block["stated"]:
        return None, ("interval-not-stated",
                      f"the trend carries no interval ({block['reason']}); no change is stated")
    span_years = (n_calendar - END_MONTHS) / 12.0        # between the two year centres
    trend_unc = max(block["half_width"], block["formal_95_ZJ_yr"])
    change = block["trend"] * span_years
    change_unc = trend_unc * span_years
    m_first = sum(by[d][0] for d in first_year) / END_MONTHS
    m_last = sum(by[d][0] for d in last_year) / END_MONTHS
    end_change = m_last - m_first
    end_unc = Z95 * math.sqrt(sum(by[d][1] ** 2 for d in first_year) / END_MONTHS ** 2
                              + sum(by[d][1] ** 2 for d in last_year) / END_MONTHS ** 2)
    residual = end_change - change
    combined = math.sqrt(change_unc ** 2 + end_unc ** 2)
    consistent = abs(residual) <= combined
    stamp_name = bookkeeping.get("_stamp", "fixture")
    domain_area = float(bookkeeping["coverage"]["domain_area_m2"])
    per_area = rates_per_area(block["trend"], domain_area)
    book = json.loads(json.dumps({k: v for k, v in bookkeeping.items() if not k.startswith("_")}))
    book["deep_omission"]["published"] = dict(DEEP_OMISSION)
    book["window_handling"] = {
        "rule": "a calendar month of the window with no value is a hole, dropped from the fit "
                "and never interpolated; the endpoint means need all twelve months of the "
                "first and last year of the window",
        "months_missing": missing,
    }
    body = {
        "months": {"window": [start, end], "n_calendar": n_calendar, "n_used": len(used),
                   "used": used, "missing": missing,
                   "first_year": first_year, "last_year": last_year},
        "series": {"dates": used, "value_ZJ": y, "uncertainty_ZJ": u},
        "terms": {
            "trend": {"value": block["trend"], "units": "ZJ/year", "uncertainty": trend_unc,
                      "uncertainty_basis": "the larger of the 95 percent sampling half width "
                                           "under the AR(1) residual model and the formal "
                                           "error the per-month uncertainties propagate",
                      "interval": block, "per_area": per_area, "stamp": stamp_name},
            "change": {"value": change, "units": "ZJ", "uncertainty": change_unc,
                       "span_years": span_years,
                       "uncertainty_basis": "the trend uncertainty times the span between the "
                                            "first and last year centres of the window",
                       "stamp": stamp_name},
            "endpoint_change": {"value": end_change, "units": "ZJ", "uncertainty": end_unc,
                                "first_year_mean_ZJ": m_first, "last_year_mean_ZJ": m_last,
                                "uncertainty_basis": "95 percent, the per-month uncertainties "
                                                     "of the two twelve-month means in "
                                                     "quadrature",
                                "stamp": stamp_name},
            "deep_omission": {"value": None, "units": "ZJ/year", "uncertainty": None,
                              "omitted": True, "published": dict(DEEP_OMISSION),
                              "stamp": "not measured: a stated omission with its published rate"},
        },
        "trend_ZJ_yr": round(block["trend"], 4),
        "change_ZJ": round(change, 4),
        "endpoint_change_ZJ": round(end_change, 4),
        "residual": {"value": residual, "units": "ZJ",
                     "rule": "endpoint_change minus change"},
        "combined_uncertainty": {"value": combined, "units": "ZJ",
                                 "rule": "the change uncertainty and the endpoint uncertainty "
                                         "in quadrature; the deep omission is stated beside "
                                         "the terms and never folded in"},
        "verdict": {"consistent_within_uncertainty": consistent,
                    "rule": "consistent when the residual lies within the combined uncertainty",
                    "residual_ZJ": residual, "bar_ZJ": combined},
        "anchor": anchor_block(anchor, per_area, block),
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
        "bound_parameters": {"window": args.window, "depth": args.depth},
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
    ap.add_argument("--window", required=True, help="YYYY-MM:YYYY-MM (declared parameter)")
    ap.add_argument("--depth", type=int, required=True, choices=DEPTHS,
                    help="the layer floor in dbar, 700 or 2000 (declared parameter)")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", action="store_true", help="the synthetic record")
    mode.add_argument("--data-root", type=Path, help="a recorded tree (execution plumbing)")
    ap.add_argument("--seed", type=int, default=7, help="fixture seed (default 7)")
    ap.add_argument("--runtime", required=True,
                    help="the runtime that ran this (claude-code, claude-cowork, a gate's name, ...)")
    ap.add_argument("--runtime-version", default=None)
    ap.add_argument("--receipt", type=Path, default=None)
    ap.add_argument("--capability-root", type=Path, default=None,
                    help="the package tree this run is evidence for (default: the tree this "
                         "executor ships in)")
    args = ap.parse_args(argv)

    start, end = parse_window(args.window)
    bundle = package_identity(package_root(HERE))
    capability = (package_identity(package_root(args.capability_root.expanduser().resolve()))
                  if args.capability_root else bundle)
    anchor = None
    if args.fixture:
        fx = make_fixture(args.seed, args.depth)
        truth = dict(TRUTH[args.depth])
        data = {"mode": "fixture", "seed": args.seed, "depth": args.depth,
                "span": list(FIXTURE_SPAN), "digest": fixture_digest(fx),
                "generator": COMPUTATION + " (make_fixture)",
                "generator_sha256": sha256_file(Path(__file__).resolve()),
                "truth": truth, "truth_basis": TRUTH["basis"]}
        series, bookkeeping, span = fx["series"], FIXTURE_BOOKKEEPING, FIXTURE_SPAN
    else:
        tree = read_data_root(args.data_root, args.depth)
        data = {"mode": "data-root", "data_root": tree["data_root"],
                "record": tree["record"].get("record"),
                "record_sha256": tree["record_sha256"],
                "manifest_sha256": tree["record"].get("manifest_sha256"),
                "files": tree["files"], "stamp": tree["stamp"]}
        series = tree["series"]
        bookkeeping = dict(tree["record"]["bookkeeping"])
        bookkeeping["_stamp"] = f"ohc-{args.depth}-stamp.json"
        anchor = (bookkeeping.get("anchor") or {}).get(f"ohc-{args.depth}")
        span = (series["dates"][0], series["dates"][-1])
    head = receipt_head(args, capability, bundle, data)

    refusal = None
    if not (ym(span[0]) <= ym(start) and ym(end) <= ym(span[1])):
        refusal = ("window-outside-coverage",
                   f"the window {start}:{end} leaves the record's coverage "
                   f"{span[0]} through {span[1]}")
    else:
        body, refusal = compute(series, start, end, args.depth, bookkeeping, anchor)
    if refusal:
        receipt = finish({**head, "refused": True, "reason_code": refusal[0],
                          "reason": refusal[1]})
        print(f"REFUSED ({refusal[0]}): {refusal[1]}")
        write(receipt, args.receipt)
        return 3

    if args.fixture:
        planted = TRUTH[args.depth]["rate_ZJ_yr"] * body["terms"]["change"]["span_years"]
        body["known_truth"] = {
            "planted_rate_ZJ_yr": TRUTH[args.depth]["rate_ZJ_yr"],
            "planted_change_ZJ": planted,
            "recovered_rate_ZJ_yr": body["terms"]["trend"]["value"],
            "recovered_change_ZJ": body["terms"]["change"]["value"],
            "rate_inside_interval": bool(body["terms"]["trend"]["interval"]["ci_low"]
                                         <= TRUTH[args.depth]["rate_ZJ_yr"]
                                         <= body["terms"]["trend"]["interval"]["ci_high"]),
            "change_within_uncertainty": bool(abs(planted - body["terms"]["change"]["value"])
                                              <= body["terms"]["change"]["uncertainty"]),
        }
    else:
        body["known_truth"] = None
    receipt = finish({**head, "refused": False, **body,
                      "caveats": [
                          ("a fixture run proves the chain, not the ocean; the real-data "
                           "anchor is the stamped data root run the concept records")
                          if args.fixture else
                          ("a real-data run on a stamped record: the loader's stamp in the "
                           "data root states the product, the climatology, the mask, the "
                           "domain area and the uncertainty basis, and the value is the "
                           "mapped open-ocean domain's heat content, not the global ocean's"),
                          "the series travels at full precision so every term, the residual "
                          "and the verdict are recomputable from the receipt",
                          "the ocean below 2000 dbar is a stated omission with its published "
                          "rate, never a term",
                      ]})
    v = receipt["verdict"]
    tb = receipt["terms"]["trend"]["interval"]
    where = f"fixture seed {args.seed}" if args.fixture else f"data root {data['data_root']}"
    print(f"trend {tb['trend']:+.4f} ZJ/yr, 95% [{tb['ci_low']:+.4f}, {tb['ci_high']:+.4f}] "
          f"(r1 {tb['r1']:+.4f}, n_eff {tb['n_eff']:.2f} of {tb['n']})", file=sys.stderr)
    print(f"argo ohc 0 to {args.depth} dbar {start}:{end} on {where}: "
          f"{receipt['months']['n_used']} of {receipt['months']['n_calendar']} months used; "
          f"trend {tb['trend']:+.4f} ZJ/yr, change {receipt['change_ZJ']:+.4f} ZJ over "
          f"{receipt['terms']['change']['span_years']:.2f} years, endpoint change "
          f"{receipt['endpoint_change_ZJ']:+.4f} ZJ, residual {v['residual_ZJ']:+.4f} against a "
          f"bar of {v['bar_ZJ']:.4f}; consistent_within_uncertainty "
          f"{str(v['consistent_within_uncertainty']).lower()}; run {receipt['run_id']}")
    write(receipt, args.receipt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
