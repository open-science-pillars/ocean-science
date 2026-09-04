#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy"]
# ///
"""Calibration with teeth for the attested trend interval.

A confidence interval is a promise about coverage: over many series
whose true trend is known, the 95 percent interval should contain
that trend about 95 percent of the time. This file tests the promise
on the sanctioned code itself (it imports trend_ci from
ecco_trend_ci.py, so the code under test is the code that ships):

  1. synthetic monthly series y_t = a + b t + season_t + e_t with e_t
     a stationary AR(1) process of known lag-1 coefficient phi and
     unit variance, for a grid of lengths n and coefficients phi;
  2. for each, the sanctioned interval's empirical coverage of the
     true trend b over a fixed number of seeded trials;
  3. THE ASSERTION: in the regime the bundle uses the method (n at
     least 120 months, phi at most 0.8) coverage must lie within the
     stated band; the run exits 1 otherwise;
  4. THE NEGATIVE CONTROL: the same trials scored with the naive
     interval (n - 2 degrees of freedom, no effective-sample-size
     correction, which is what a bare polyfit trend with a textbook
     standard error would give). Its coverage must collapse below
     the collapse bar at phi 0.8, and the measured collapse is
     recorded, so a reader can see what the correction is worth.

The band is set from measurement, not from hope. The correction is
known to under-cover: the lag-1 coefficient estimated from OLS
residuals is biased toward zero, so n_eff is overestimated and the
interval is a little too narrow, more so for short or strongly
autocorrelated series (measured 2026-09-02, 2000 trials: 92.0 to
95.0 percent in the asserted regime; 90 to 92 percent at 60 months;
82 to 86 percent at 12 or 24 months, where the tool also declines
to state an interval in up to 7 percent of trials because fewer
than one degree of freedom remains). Two variants that charge the
climatology's parameters to the degrees of freedom were tried and
gained under one point at phi 0 and nothing at phi 0.8, so the
method stands as stated. Short series are measured and reported,
not asserted; those rows are the numerical content of the
naked-trend gotcha.

The report (JSON) carries every configuration's coverage, mean
estimated n_eff against the true n_eff = n(1-phi)/(1+phi), and the
seed, so the run is reproducible to the last trial.

Usage: ecco_trend_ci_calibration.py --out REPORT.json [--trials 2000]
"""

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
SEED = 20260902
TRUE_TREND_PER_MONTH = 0.02
SEASON_AMPLITUDE = 1.0
GRID = [(n, phi) for n in (12, 24, 60, 120, 312) for phi in (0.0, 0.5, 0.8)]
ASSERT_MIN_N = 120
ASSERT_MAX_PHI = 0.8
COVERAGE_BAND = (0.90, 0.975)
COLLAPSE_BAR = 0.80
COLLAPSE_PHI = 0.8


def load_sanctioned():
    path = HERE / "ecco_trend_ci.py"
    spec = importlib.util.spec_from_file_location("ecco_trend_ci", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, hashlib.sha256(path.read_bytes()).hexdigest()


def ar1(rng, n, phi, trials):
    """Stationary AR(1) with unit marginal variance, trials x n."""
    e = np.empty((trials, n))
    e[:, 0] = rng.standard_normal(trials)
    sd = math.sqrt(1.0 - phi * phi)
    for t in range(1, n):
        e[:, t] = phi * e[:, t - 1] + sd * rng.standard_normal(trials)
    return e


def run(mod, trials):
    rng = np.random.default_rng(SEED)
    rows = []
    for n, phi in GRID:
        t = np.arange(n)
        season = SEASON_AMPLITUDE * np.sin(2 * np.pi * t / 12.0)
        deseasonalize = "climatology" if n >= 24 else "none"
        noise = ar1(rng, n, phi, trials)
        y = 3.0 + TRUE_TREND_PER_MONTH * t + (season if n >= 24 else 0) + noise
        hit = naive_hit = 0
        n_eff_sum = 0.0
        skipped = 0
        tq_naive = mod.t_quantile(0.5 + mod.CONFIDENCE / 2.0, n - 2)
        for k in range(trials):
            try:
                c = mod.trend_ci(y[k].tolist(), deseasonalize)
            except ValueError:
                skipped += 1  # n_eff left no degrees of freedom
                continue
            half = c["half_width_per_month"]
            lo, hi = c["slope_per_month"] - half, c["slope_per_month"] + half
            hit += lo <= TRUE_TREND_PER_MONTH <= hi
            nh = tq_naive * c["naive_se_per_month"]
            naive_hit += (c["slope_per_month"] - nh <= TRUE_TREND_PER_MONTH
                          <= c["slope_per_month"] + nh)
            n_eff_sum += c["n_eff"]
        done = trials - skipped
        rows.append({
            "n": n, "phi": phi, "deseasonalize": deseasonalize,
            "trials": trials, "no_interval": skipped,
            "coverage": hit / done, "naive_coverage": naive_hit / done,
            "n_eff_true": n * (1 - phi) / (1 + phi),
            "n_eff_mean_estimated": n_eff_sum / done,
        })
        r = rows[-1]
        print(f"n {n:4d} phi {phi:.1f} {deseasonalize:11s} coverage "
              f"{r['coverage']:.3f}  naive {r['naive_coverage']:.3f}  "
              f"n_eff true {r['n_eff_true']:6.1f} est "
              f"{r['n_eff_mean_estimated']:6.1f}"
              f"{'  no-interval ' + str(skipped) if skipped else ''}")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--trials", type=int, default=2000)
    args = ap.parse_args()
    mod, code_sha = load_sanctioned()
    rows = run(mod, args.trials)

    failures = []
    asserted = [r for r in rows
                if r["n"] >= ASSERT_MIN_N and r["phi"] <= ASSERT_MAX_PHI]
    for r in asserted:
        if not COVERAGE_BAND[0] <= r["coverage"] <= COVERAGE_BAND[1]:
            failures.append(f"coverage {r['coverage']:.3f} outside "
                            f"{COVERAGE_BAND} at n {r['n']} phi {r['phi']}")
    control = [r for r in asserted if r["phi"] == COLLAPSE_PHI]
    for r in control:
        if r["naive_coverage"] >= COLLAPSE_BAR:
            failures.append(f"negative control did not collapse: naive "
                            f"coverage {r['naive_coverage']:.3f} at n "
                            f"{r['n']} phi {r['phi']} is not below "
                            f"{COLLAPSE_BAR}")
    report = {
        "computation": "trend-ci", "code_sha256": code_sha,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "seed": SEED, "trials_per_configuration": args.trials,
        "true_trend_per_month": TRUE_TREND_PER_MONTH,
        "season_amplitude": SEASON_AMPLITUDE, "noise_variance": 1.0,
        "assertion": {"regime": f"n >= {ASSERT_MIN_N} and phi <= "
                                f"{ASSERT_MAX_PHI}",
                      "coverage_band": list(COVERAGE_BAND),
                      "negative_control": f"naive coverage below "
                                          f"{COLLAPSE_BAR} at phi "
                                          f"{COLLAPSE_PHI}"},
        "rows": rows, "failures": failures,
        "verdict": "PASS" if not failures else "FAIL",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    worst = min(r["naive_coverage"] for r in control)
    print(f"{report['verdict']}: {len(asserted)} asserted configurations, "
          f"naive coverage at phi {COLLAPSE_PHI} collapses to {worst:.3f}; "
          f"report -> {args.out}")
    for f in failures:
        print(f"  {f}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
