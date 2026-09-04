#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Sanctioned computation: a linear trend with an honest interval.

A trend without an error bar is arithmetic, not a claim. This file
fixes ONE method for turning a monthly series into a trend and a
two-sided 95 percent confidence interval that accounts for the serial
correlation every geophysical monthly series carries:

  1. deseasonalize by monthly climatology, JOINTLY with the trend:
     the mean of each calendar month is subtracted from the series
     and from the time index alike, so the slope that follows is the
     least-squares estimate of trend and climatology fitted together
     (the Frisch-Waugh-Lovell identity: identical to the thirteen
     parameter regression). The two are not orthogonal, even over
     complete years: the calendar-month means of time form a sawtooth
     carrying 143/(144Y^2-1) of any trend, a quarter of it at two
     years, and subtracting the climatology from the series alone
     hands that fraction to the climatology. Complete years (n a
     multiple of 12, at least 24 months) are required so every
     calendar month is estimated from the same number of years;
     otherwise "none", and the receipt says which;
  2. ordinary least squares trend against time in months;
  3. lag-1 autocorrelation r1 of the OLS residuals;
  4. effective sample size n_eff = n (1 - r1) / (1 + r1), capped at
     n: a sample cannot be more effective than itself, and r1
     estimated from a short residual series is biased negative, so
     the uncapped formula would hand a short series an interval
     NARROWER than the independent-samples one (measured: 24 months
     of white noise estimated n_eff 33; capping lifts coverage there
     from 78 to 86 percent and from 86 to 95 at twelve months);
  5. residual variance with n_eff - 2 degrees of freedom and the
     standard error of the slope from it;
  6. the two-sided 95 percent interval from Student's t on n_eff - 2
     degrees of freedom (fractional, evaluated exactly); below one
     degree of freedom the tool refuses to state an interval at all.

This is the treatment of Santer et al. (2008), the standard for
trend significance in climate series. Every intermediate (the series
after deseasonalization, slope, r1, n_eff, standard error, the t
quantile) is in the receipt, so the attester recomputes the whole
chain from the series itself rather than sampling it. Changing the
method is a new computation, not an edit to this file.

Other sanctioned computations that report a trend of their own
(steric height, the sea-level partition) do not reimplement any of
this: they call interval_block() from this file and embed its result
beside their trend, and the block carries this file's hash so their
attesters can bind the interval to the one sanctioned method and
recompute it from the series in that receipt.

Input is a JSON file: either a receipt from another sanctioned
computation with a monthly field named by --field (a mapping of
YYYY-MM to value), or a bare {"YYYY-MM": value} mapping. The receipt
records the source file, its sha256, and, when the source is a
receipt, that receipt's run id, code hash, and verified-tree stamp,
so a trend inherits its data provenance from the series it was fit
to. Months must be consecutive.

Usage:
  ecco_trend_ci.py --source steric_receipt.json --field steric_mean_m_by_month \
      --value-units m --scale 1000 --report-units mm \
      [--deseasonalize climatology|none] [--receipt trend_receipt.json]
"""

import argparse
import datetime as dt
import hashlib
import json
import math
import uuid
from pathlib import Path

CONFIDENCE = 0.95
MIN_MONTHS = 6
CLIM_MIN_YEARS = 2
MIN_DOF = 1.0  # below one degree of freedom no finite interval is honest


# ---- the numeric core. Plain Python floats on purpose: no numpy, no
# ---- scipy, so the attester's stdlib recompute is the same arithmetic

def ols(t, y):
    n = len(y)
    tbar = sum(t) / n
    ybar = sum(y) / n
    sxx = sum((a - tbar) ** 2 for a in t)
    sxy = sum((a - tbar) * (b - ybar) for a, b in zip(t, y))
    slope = sxy / sxx
    intercept = ybar - slope * tbar
    resid = [b - (intercept + slope * a) for a, b in zip(t, y)]
    return slope, intercept, resid, sxx


def lag1(resid):
    num = sum(a * b for a, b in zip(resid[:-1], resid[1:]))
    den = sum(a * a for a in resid)
    return num / den


def betacf(a, b, x, max_iter=500, eps=1e-15):
    """Continued fraction for the incomplete beta (modified Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / (c if abs(c) > tiny else tiny)
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / (c if abs(c) > tiny else tiny)
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            return h
    raise ArithmeticError("incomplete beta did not converge")


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * betacf(a, b, x) / a
    return 1.0 - front * betacf(b, a, 1.0 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1.0 - tail if t >= 0 else tail


def t_quantile(p, df):
    """Inverse of Student's t CDF by bisection, exact to 1e-13."""
    lo, hi = 0.0, 1.0
    while t_cdf(hi, df) < p:
        hi *= 2.0
        if hi > 1e12:
            raise ArithmeticError("t quantile out of range")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13 * max(1.0, hi):
            break
    return 0.5 * (lo + hi)


def fit(values, deseasonalize):
    """The least-squares half of the chain: the trend itself, stated
    for any series of at least three months. values: consecutive
    monthly values (any units). With climatology the calendar-month
    means come off the series AND the time index, so the slope is the
    joint estimate of trend and climatology. The slope is per month."""
    y = [float(v) for v in values]
    n = len(y)
    if n < 3:
        raise ValueError(f"need at least 3 months for a slope, got {n}")
    t = [float(i) for i in range(n)]
    if deseasonalize == "climatology":
        if n % 12 or n < 12 * CLIM_MIN_YEARS:
            raise ValueError("climatology deseasonalization needs complete "
                             f"years and at least {CLIM_MIN_YEARS} of them; "
                             f"got {n} months. Declare --deseasonalize none")
        years = n // 12
        clim = [sum(y[k::12]) / years for k in range(12)]
        y = [v - clim[i % 12] for i, v in enumerate(y)]
        tclim = [sum(t[k::12]) / years for k in range(12)]
        t = [v - tclim[i % 12] for i, v in enumerate(t)]
    elif deseasonalize != "none":
        raise ValueError(f"unknown deseasonalization {deseasonalize!r}")
    slope, intercept, resid, sxx = ols(t, y)
    return {"n": n, "series_fit": y, "time_fit": t,
            "slope_per_month": slope, "intercept": intercept,
            "residuals": resid, "sxx": sxx}


def trend_ci(values, deseasonalize):
    """The whole chain: the fit, then the interval. Returns every
    intermediate; the trend is per month."""
    f = fit(values, deseasonalize)
    n = f["n"]
    if n < MIN_MONTHS:
        raise ValueError(f"an interval needs at least {MIN_MONTHS} months, "
                         f"got {n}")
    slope, intercept, resid, sxx = (f["slope_per_month"], f["intercept"],
                                    f["residuals"], f["sxx"])
    y = f["series_fit"]
    r1 = lag1(resid)
    n_eff = min(float(n), n * (1.0 - r1) / (1.0 + r1))
    dof = n_eff - 2.0
    if dof < MIN_DOF:
        raise ValueError(f"effective sample size {n_eff:.2f} leaves "
                         f"{dof:.2f} degrees of freedom, below {MIN_DOF}; "
                         "the series is too short or too autocorrelated "
                         "for a finite interval, and none is stated")
    s2 = sum(e * e for e in resid) / dof
    se = math.sqrt(s2 / sxx)
    tq = t_quantile(0.5 + CONFIDENCE / 2.0, dof)
    naive_se = math.sqrt(sum(e * e for e in resid) / (n - 2) / sxx)
    return {
        "n": n, "series_fit": y, "slope_per_month": slope,
        "intercept": intercept, "residuals": resid, "sxx": sxx,
        "r1": r1, "n_eff": n_eff, "dof": dof,
        "se_per_month": se, "t_quantile": tq,
        "half_width_per_month": tq * se,
        "naive_se_per_month": naive_se,
    }


def default_deseasonalize(n):
    """The one policy for a series of n months: climatology over
    complete years when there are at least two of them, otherwise
    none. Embedded blocks must follow it; the attesters check."""
    return ("climatology" if n % 12 == 0 and n >= 12 * CLIM_MIN_YEARS
            else "none")


def interval_block(values, units_per_year):
    """The trend and interval another sanctioned computation embeds
    as its own. values: the consecutive monthly series in the units
    the caller reports (scaled already); trend and interval come back
    per year in units_per_year. The trend is this file's fit (joint
    with the climatology over complete years), so no computation in
    the bundle states a trend by any other arithmetic. When the chain
    refuses an interval (fewer than six months, or under one degree
    of freedom) the block says so with stated false and the reason,
    and no interval is invented; the trend stays if a slope exists."""
    block = {
        "method": "trend-ci",
        "method_code_sha256":
            hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "confidence": CONFIDENCE,
        "units": units_per_year,
        "n": len(values),
        "deseasonalize": default_deseasonalize(len(values)),
    }
    try:
        block["trend"] = (fit(values, block["deseasonalize"])["slope_per_month"]
                          * 12.0)
        c = trend_ci(values, block["deseasonalize"])
    except ValueError as e:
        block.update({"stated": False, "reason": str(e)})
        return block
    trend = c["slope_per_month"] * 12.0
    half = c["half_width_per_month"] * 12.0
    naive_half = (t_quantile(0.5 + CONFIDENCE / 2.0, c["n"] - 2)
                  * c["naive_se_per_month"] * 12.0)
    block.update({
        "stated": True,
        "trend": trend, "ci_low": trend - half, "ci_high": trend + half,
        "half_width": half, "naive_half_width": naive_half,
        "r1": c["r1"], "n_eff": c["n_eff"], "dof": c["dof"],
        "se": c["se_per_month"] * 12.0, "t_quantile": c["t_quantile"],
        "significant_at_confidence": bool((trend - half) * (trend + half) > 0),
    })
    return block


# ---- executor plumbing

def consecutive(dates):
    ym = []
    for d in dates:
        y, m = d.split("-")[:2]
        ym.append(int(y) * 12 + int(m) - 1)
    return all(b - a == 1 for a, b in zip(ym[:-1], ym[1:]))


def load_series(path, field):
    doc = json.loads(path.read_text(encoding="utf-8"))
    src = {"source": str(path), "source_sha256":
           hashlib.sha256(path.read_bytes()).hexdigest()}
    if "run_id" in doc and "code_sha256" in doc:
        if not field or field not in doc:
            raise SystemExit(f"--field must name a monthly field of the "
                             f"source receipt (have: {sorted(doc)})")
        series = doc[field]
        src["source_receipt"] = {
            "run_id": doc["run_id"], "code_sha256": doc["code_sha256"],
            "field": field}
        data = doc.get("data") or {}
        src["record"] = data.get("record",
                                 "unverified: source receipt carries no "
                                 "data block")
    else:
        series = doc if field is None else doc[field]
        src["record"] = "unverified: source is not a receipt from a " \
                        "verified tree"
    if not isinstance(series, dict) or not series:
        raise SystemExit("series must be a non-empty {YYYY-MM: value} mapping")
    dates = list(series)
    if dates != sorted(dates):
        raise SystemExit("series months are not in order")
    if not consecutive(dates):
        raise SystemExit("series months are not consecutive")
    return dates, [float(series[d]) for d in dates], src


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--field", default=None)
    ap.add_argument("--value-units", required=True,
                    help="units of the series values as stored, e.g. m")
    ap.add_argument("--scale", type=float, default=1.0,
                    help="multiply values by this before fitting")
    ap.add_argument("--report-units", default=None,
                    help="units after scaling, e.g. mm; default value-units")
    ap.add_argument("--deseasonalize", choices=["climatology", "none"],
                    default="climatology")
    ap.add_argument("--receipt", type=Path, default=Path("trend_receipt.json"))
    args = ap.parse_args()

    dates, values, src = load_series(args.source, args.field)
    scaled = [v * args.scale for v in values]
    try:
        c = trend_ci(scaled, args.deseasonalize)
    except ValueError as e:
        raise SystemExit(f"refused: {e}")
    units = args.report_units or args.value_units
    per_year = 12.0
    trend = c["slope_per_month"] * per_year
    half = c["half_width_per_month"] * per_year
    naive_half = (t_quantile(0.5 + CONFIDENCE / 2.0, c["n"] - 2)
                  * c["naive_se_per_month"] * per_year)
    receipt = {
        "run_id": dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                  + "-" + str(uuid.uuid4())[:8],
        "computation": "trend-ci",
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "data": src,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "bound_parameters": {
            "field": args.field, "value_units": args.value_units,
            "scale": args.scale, "report_units": units,
            "deseasonalize": args.deseasonalize,
            "confidence": CONFIDENCE, "time_unit": "month",
            "trend_per": "year", "months_per_year": per_year,
            "method": "OLS slope, jointly with the monthly climatology "
                      "when one is removed (calendar-month means off the "
                      "series and the time index); lag-1 autocorrelation "
                      "of residuals; n_eff = n(1-r1)/(1+r1) capped at n; residual "
                      "variance on n_eff-2 dof; two-sided interval from "
                      "Student's t on n_eff-2 dof (Santer et al. 2008)",
        },
        "series": {"dates": dates, "values": values,
                   "units": args.value_units},
        "intermediates": {
            "n": c["n"], "series_fit": c["series_fit"],
            "slope_per_month": c["slope_per_month"],
            "intercept": c["intercept"], "sxx": c["sxx"],
            "r1": c["r1"], "n_eff": c["n_eff"], "dof": c["dof"],
            "se_per_month": c["se_per_month"],
            "t_quantile": c["t_quantile"],
            "naive_se_per_month": c["naive_se_per_month"],
        },
        "results": {
            "trend": trend, "ci_low": trend - half, "ci_high": trend + half,
            "half_width": half, "units": f"{units}/year",
            "n": c["n"], "n_eff": c["n_eff"], "r1": c["r1"],
            "naive_half_width": naive_half,
            "significant_at_confidence": bool(
                (trend - half) * (trend + half) > 0),
        },
        "caveats": {
            "deseasonalize": (
                "monthly climatology removed over complete years"
                if args.deseasonalize == "climatology" else
                "no deseasonalization: the seasonal cycle is in the "
                "residuals and inflates r1 and the interval; with fewer "
                "than two complete years no climatology can be formed"),
            "interval": "the interval is a statement about sampling "
                        "under an AR(1) residual model, not about model "
                        "or observational error in the series",
        },
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n",
                            encoding="utf-8")
    r = receipt["results"]
    print(f"run {receipt['run_id']}: {c['n']} months, "
          f"deseasonalize {args.deseasonalize}")
    print(f"  trend {r['trend']:+.4f} {r['units']}, 95% interval "
          f"[{r['ci_low']:+.4f}, {r['ci_high']:+.4f}] (half width "
          f"{r['half_width']:.4f}); naive half width {r['naive_half_width']:.4f}")
    print(f"  r1 {c['r1']:+.4f}, n_eff {c['n_eff']:.2f} of {c['n']}, "
          f"t {c['t_quantile']:.4f} on {c['dof']:.2f} dof; "
          f"{'significant' if r['significant_at_confidence'] else 'NOT significant'} "
          f"at {CONFIDENCE:.0%}")
    print(f"  receipt -> {args.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
