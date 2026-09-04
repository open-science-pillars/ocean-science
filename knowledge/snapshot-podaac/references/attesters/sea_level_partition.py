#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested regional sea level partition.

Stdlib only, consumer-side. Checks A1 through A6 from the contract
(podaac/computations/ecco-regional-sea-level.md). Exit 0 PASS, 1 FAIL
with the failing check named.

A4's tolerance is MEASURED, never assumed: TOLERANCE_M below is set from
the first sanctioned fixture run and recorded in the concept in the same
change; while it is None, every run fails A4 by design.

A6 is the recompute: the receipt carries the three monthly anomaly
series, so the residual series and its maximum, each trend, and each
trend's interval block are rebuilt here from those series (the shared
chain in trend_recompute.py, the one every attester in this bundle
runs) rather than read and believed. Before the series travelled in
the receipt, A4 could only check that the stated residual was small,
not that it was the residual.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from trend_recompute import (DEFAULT_METHOD, REL_TOL, check_block, close,
                             consecutive)

RECEIPT_FIELDS = ("run_id", "code_sha256", "bound_parameters", "ssh_variant",
                  "months", "cells_evaluated", "trend_total_mm_yr",
                  "trend_mass_mm_yr", "trend_steric_mm_yr",
                  "trend_total_interval", "trend_mass_interval",
                  "trend_steric_interval", "partition_residual_max",
                  "series_by_month")
SERIES = ("total_anomaly_m", "mass_anomaly_m", "steric_anomaly_m")
REGIONS = {"us-northeast-coast", "gulf-of-mexico", "north-sea"}
SPAN = ("1992-01", "2017-12")
TOLERANCE_M = 1.0e-3   # m; measured 2026-08-30 on us-northeast-coast
# 2010-01:2010-12 over 102 cells: max monthly area-mean residual
# 5.061e-04 m once the anomaly means are formed in double precision
# (the first measurement read 5.085e-04 m; its series were float32 end
# to end, and at a steric mean of -19.5 m the float32 quantum is 2e-6 m,
# which sat in every residual as a constant offset). The full record
# 1992-01:2017-12 measures 8.282e-04 m, inside the same bar. Recorded
# with headroom over the fixture run, per the measured-not-assumed rule.
ROUNDING = 5.0e-5      # the receipt rounds trends to four decimals
DEFAULT_COMPUTATION = (Path(__file__).resolve().parent.parent
                       / "computations" / "ecco_regional_sea_level.py")


def fail(check: str, msg: str) -> int:
    print(f"FAIL {check}: {msg}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--computation", type=Path, default=DEFAULT_COMPUTATION)
    ap.add_argument("--method", type=Path, default=DEFAULT_METHOD,
                    help="the sanctioned trend method the interval blocks "
                         "must name by hash")
    args = ap.parse_args()

    try:
        r = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return fail("receipt", f"unreadable or not JSON: {e}")
    for f in RECEIPT_FIELDS:
        if f not in r:
            return fail(f, "missing from receipt")

    want = hashlib.sha256(args.computation.read_bytes()).hexdigest()
    if r["code_sha256"] != want:
        return fail("A1", f"receipt {str(r['code_sha256'])[:12]}... does not match "
                    f"sanctioned computation {want[:12]}...")

    data = r.get("data")
    if (not isinstance(data, dict)
            or not isinstance(data.get("record"), dict)):
        return fail("A1b",
                    "receipt names no verified data tree: data.record must "
                    "be the RECORD.json stamp the verify tool leaves in "
                    "a tree checked against its manifest; nothing is "
                    "attested against unmanifested data")

    bound = r["bound_parameters"]
    if not isinstance(bound, dict) or set(bound) != {"region", "period"}:
        return fail("A2", "bound_parameters must bind exactly region and period")
    if bound["region"] not in REGIONS:
        return fail("A2", f"region '{bound['region']}' is not in the registry")
    m = re.fullmatch(r"(\d{4}-\d{2}):(\d{4}-\d{2})", str(bound["period"]))
    if not m or not (SPAN[0] <= m.group(1) <= m.group(2) <= SPAN[1]):
        return fail("A2", f"period '{bound['period']}' malformed or outside "
                    f"{SPAN[0]}..{SPAN[1]}")

    if r["ssh_variant"] != "SSH":
        return fail("A3", f"ssh_variant '{r['ssh_variant']}' is not the stated "
                    "convention (exactly SSH; one variant, never mixed)")

    if TOLERANCE_M is None:
        return fail("A4", "no tolerance recorded yet: the pass bar is measured "
                    "on the sanctioned fixture run and written into the concept "
                    "and this attester together; until then nothing attests")
    resid = float(r["partition_residual_max"])
    if resid > TOLERANCE_M:
        return fail("A4", f"partition_residual_max {resid:.3e} m exceeds the "
                    f"recorded tolerance {TOLERANCE_M:.1e} m")

    if int(r["months"]) <= 0 or int(r["cells_evaluated"]) <= 0:
        return fail("A5", "months and cells_evaluated must be positive")

    # A6: the series, and everything rebuilt from them
    sb = r["series_by_month"]
    n = int(r["months"])
    dates = sb.get("dates")
    if (not isinstance(dates, list) or len(dates) != n or n < 3
            or not all(isinstance(d, str) and re.fullmatch(r"\d{4}-\d{2}", d)
                       for d in dates)
            or not consecutive(dates)
            or (dates[0], dates[-1]) != (m.group(1), m.group(2))):
        return fail("A6", "series_by_month.dates must be the period's "
                    "consecutive months, one per counted month")
    series = {}
    for k in SERIES:
        v = sb.get(k)
        if (not isinstance(v, list) or len(v) != n
                or not all(isinstance(x, (int, float)) for x in v)):
            return fail("A6", f"series_by_month.{k} must hold {n} numbers")
        if abs(sum(v)) > REL_TOL * max(1.0, max(abs(x) for x in v)):
            return fail("A6", f"{k} is not an anomaly series (mean not zero)")
        series[k] = v
    residual = [t - a - s for t, a, s in zip(series["total_anomaly_m"],
                                             series["mass_anomaly_m"],
                                             series["steric_anomaly_m"])]
    stated_mm = sb.get("residual_mm")
    if (not isinstance(stated_mm, list) or len(stated_mm) != n
            or any(abs(x * 1000.0 - y) > ROUNDING + 1e-9
                   for x, y in zip(residual, stated_mm))):
        return fail("A6", "residual_mm is not total minus mass minus steric "
                    "from the series in the receipt")
    if not close(max(abs(x) for x in residual), resid):
        return fail("A6", f"partition_residual_max {resid:.6e} is not the "
                    "maximum of the residual series")
    for part in ("total", "mass", "steric"):
        block = r[f"trend_{part}_interval"]
        mm = [x * 1000.0 for x in series[f"{part}_anomaly_m"]]
        err = check_block(block, mm, args.method)
        if err:
            return fail("A6", f"trend_{part}_interval: {err}")
        t = r[f"trend_{part}_mm_yr"]
        if (not isinstance(t, (int, float))
                or abs(t - block["trend"]) > ROUNDING + 1e-9):
            return fail("A6", f"trend_{part}_mm_yr {t} is not the sanctioned "
                        f"method's trend {block['trend']:.4f}")

    def band(part):
        b = r[f"trend_{part}_interval"]
        return (f"{part} {b['trend']:+.4f} [{b['ci_low']:+.4f}, "
                f"{b['ci_high']:+.4f}]" if b["stated"] else
                f"{part} {b['trend']:+.4f} (no interval)")

    print(f"PASS run {r['run_id']}: region {bound['region']} period "
          f"{bound['period']}, residual_max {resid:.3e} m within "
          f"{TOLERANCE_M:.1e} (recomputed), variant {r['ssh_variant']}, "
          f"{r['months']} months, {r['cells_evaluated']} cells; trends "
          f"mm/yr with 95% intervals recomputed: {band('total')}, "
          f"{band('mass')}, {band('steric')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
