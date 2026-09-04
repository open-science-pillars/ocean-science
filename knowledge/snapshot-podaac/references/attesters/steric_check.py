#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested ECCO v4r4 steric height.

No LLM, stdlib only, consumer-side (spec 10.2). PASS (exit 0) only
when ALL hold, else FAIL (exit 1) naming the field:

  1. declared receipt fields present (run_id, code_sha256,
     bound_parameters, steric_mean_m_by_month, cells_in_region);
  2. code_sha256 matches the sanctioned computation file;
  3. bound parameters are the contract exactly: a registered region,
     months as YYYY-MM strings, rho0 1029.0, the density collection;
  4. THE CROSS-COMPUTATION ANCHOR: when the run is the reference
     configuration (region us-northeast-coast, months 2010-01 through
     2010-12), steric_trend_mm_yr must match the steric trend the
     attested sea-level partition's receipt records, +135.7772 mm/yr,
     within 0.05 mm/yr (measured agreement 2026-09-01: identical to
     four decimals), and cells_in_region must be exactly 102, the
     registered box's wet-cell count; the same anchor holds over the
     full record (1992-01 through 2017-12), where the partition's
     receipt records +2.7999 mm/yr (measured agreement 2026-09-02:
     the two interval blocks agree to every digit). The anchor is
     on the central value; the interval travels beside it;
  5. sanity everywhere: every area-mean steric height within -60 to 0
     m (measured: -19.6 regional, -30.9 global);
  6. a global run must carry the Boussinesq caveat field, so no
     consumer can quote a global-mean steric change as modeled
     sea-surface rise;
  7. THE TREND AND ITS INTERVAL: any run of three months or more
     carries steric_trend_interval, the block the sanctioned trend
     method embeds (named by that file's hash), and steric_trend_mm_yr
     is that block's trend; the block is recomputed here from the
     monthly series in the receipt by the shared chain in
     trend_recompute.py (joint fit with the climatology over complete
     years, lag-1 autocorrelation, effective sample size, Student's t),
     every number within 1e-9 relative, or the refusal of an interval
     is one the recompute reproduces. The 2010 reference interval is
     [-701.5, +973.1] mm/yr around +135.8: twelve months cannot tell
     that trend from zero, and the receipt says so beside the anchor.

Usage: steric_check.py RECEIPT.json [--computation PATH]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from trend_recompute import DEFAULT_METHOD, check_block, close

REF_REGION = "us-northeast-coast"
REF_MONTHS = [f"2010-{m:02d}" for m in range(1, 13)]
REF_TREND = 135.7772
REF_RECORD_MONTHS = [f"{y}-{m:02d}" for y in range(1992, 2018)
                     for m in range(1, 13)]
REF_RECORD_TREND = 2.7999
REF_TREND_TOL = 0.05
REF_CELLS = 102
RHO0 = 1029.0
COLLECTION = "ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4"
REGIONS = {"us-northeast-coast", "gulf-of-mexico", "north-sea", "global"}
FIELDS = ["run_id", "code_sha256", "bound_parameters",
          "steric_mean_m_by_month", "cells_in_region"]


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--computation", type=Path,
                    default=Path(__file__).parent.parent
                    / "computations" / "ecco_steric_height.py")
    ap.add_argument("--method", type=Path, default=DEFAULT_METHOD,
                    help="the sanctioned trend method the interval block "
                         "must name by hash")
    args = ap.parse_args()
    r = json.loads(args.receipt.read_text(encoding="utf-8"))

    for f in FIELDS:
        if f not in r:
            return fail(f"receipt field missing: {f}")
    want = hashlib.sha256(args.computation.read_bytes()).hexdigest()
    if r["code_sha256"] != want:
        return fail("code_sha256 does not match the sanctioned computation")

    data = r.get("data")
    if (not isinstance(data, dict)
            or not isinstance(data.get("record"), dict)):
        return fail("receipt names no verified data tree: data.record must "
                    "be the RECORD.json stamp the verify tool leaves in "
                    "a tree checked against its manifest; nothing is "
                    "attested against unmanifested data")

    bp = r["bound_parameters"]
    if bp.get("region") not in REGIONS:
        return fail(f"region {bp.get('region')!r} is not registered")
    months = bp.get("months")
    if (not isinstance(months, list) or not months
            or not all(isinstance(m, str) and len(m) == 7 and m[4] == "-"
                       for m in months)):
        return fail("months is not a list of YYYY-MM")
    if bp.get("rho0_kg_m3") != RHO0 or bp.get("collection") != COLLECTION:
        return fail("constants or collection differ from the contract")

    for m, s in r["steric_mean_m_by_month"].items():
        if not (-60.0 <= s <= 0.0):
            return fail(f"steric mean {s} m outside [-60, 0] for {m}")
    if list(r["steric_mean_m_by_month"]) != months:
        return fail("steric_mean_m_by_month does not cover the bound months "
                    "in order")

    if len(months) >= 3:
        block = r.get("steric_trend_interval")
        series_mm = [float(v) * 1000.0
                     for v in r["steric_mean_m_by_month"].values()]
        err = check_block(block, series_mm, args.method)
        if err:
            return fail(f"steric_trend_interval: {err}")
        t = r.get("steric_trend_mm_yr")
        if not isinstance(t, (int, float)) or not close(t, block["trend"]):
            return fail(f"steric_trend_mm_yr {t} is not the sanctioned "
                        f"method's trend {block['trend']}")
        iv = (f"; trend {block['trend']:+.4f} mm/yr, 95% interval "
              f"[{block['ci_low']:+.4f}, {block['ci_high']:+.4f}] recomputed"
              if block["stated"] else
              f"; trend {block['trend']:+.4f} mm/yr, no interval "
              f"(recompute agrees: {block['reason']})")
    else:
        iv = ""

    anchors = {tuple(REF_MONTHS): REF_TREND,
               tuple(REF_RECORD_MONTHS): REF_RECORD_TREND}
    if bp["region"] == REF_REGION and tuple(months) in anchors:
        ref = anchors[tuple(months)]
        t = r.get("steric_trend_mm_yr")
        if t is None or abs(t - ref) > REF_TREND_TOL:
            return fail(f"reference trend {t} mm/yr not within "
                        f"{REF_TREND_TOL} of the sea-level partition's "
                        f"{ref} over these {len(months)} months")
        if r["cells_in_region"] != REF_CELLS:
            return fail(f"cells_in_region {r['cells_in_region']} != {REF_CELLS}")
        print(f"PASS run {r['run_id']}: sanctioned code, contract "
              f"parameters, and the cross-computation anchor holds "
              f"(steric trend {t:+.4f} mm/yr vs the partition's "
              f"{ref:+.4f} over {len(months)} months{iv})")
        return 0

    if bp["region"] == "global" and "boussinesq_caveat" not in r:
        return fail("global run without the Boussinesq caveat field")

    print(f"PASS run {r['run_id']}: sanctioned code, contract parameters, "
          f"and sanity bounds hold ({bp['region']}, {len(months)} months{iv})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
