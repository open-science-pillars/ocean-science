#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested ECCO v4r4 ocean heat content.

No LLM, stdlib only, consumer-side (spec 10.2). Reads a receipt JSON
produced by references/computations/ecco_ohc.py and returns PASS
(exit 0) only when ALL of the following hold, otherwise FAIL (exit 1)
naming the failing field:

  1. every declared receipt field is present (run_id, code_sha256,
     bound_parameters, anchors, months, cells_evaluated,
     ohc_baseline_caveat);
  2. code_sha256 equals the sha256 of the sanctioned computation file,
     so a rewritten or swapped computation fails mechanically;
  3. bound_parameters match the contract exactly: months (a list of
     YYYY-MM strings), the fixed collection ShortName, and the MITgcm
     constants rhoConst 1029.0 and Cp 3994.0, nothing else;
  4. the grid anchors hold: ocean surface area within 0.5 percent of
     the tutorial-published 3.58e8 km2 (measured deviation 0.003
     percent, 2026-09-01), ocean volume within 1 percent of the
     literature 1.335e18 m3 (measured deviation under 0.01 percent),
     and cells_evaluated exactly 2,406,992 (a grid-determined count);
  5. every month's volume-mean THETA lies in the provisional physical
     band [2.0, 6.0] degC (band pending oceanographer confirmation;
     measured 3.6085 and 3.6068 for 2010-01 and 2010-12);
  6. the potential-temperature baseline caveat travels in the receipt,
     so no consumer can quote an absolute OHC without it.

Usage: ohc_check.py RECEIPT.json [--computation PATH]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

AREA_KM2 = 3.58e8
AREA_RTOL = 0.005
VOLUME_M3 = 1.335e18
VOLUME_RTOL = 0.01
THETA_BAND = (2.0, 6.0)
CELLS = 2406992
CONSTANTS = {"rhoConst_kg_m3": 1029.0, "Cp_J_kg_K": 3994.0}
COLLECTION = "ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4"
FIELDS = ["run_id", "code_sha256", "bound_parameters", "anchors",
          "months", "cells_evaluated", "ohc_baseline_caveat"]


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--computation", type=Path,
                    default=Path(__file__).parent.parent
                    / "computations" / "ecco_ohc.py")
    args = ap.parse_args()
    r = json.loads(args.receipt.read_text(encoding="utf-8"))

    for f in FIELDS:
        if f not in r:
            return fail(f"receipt field missing: {f}")

    want = hashlib.sha256(args.computation.read_bytes()).hexdigest()
    if r["code_sha256"] != want:
        return fail("code_sha256 does not match the sanctioned computation "
                    f"({r['code_sha256'][:12]}... vs {want[:12]}...)")

    data = r.get("data")
    if (not isinstance(data, dict)
            or not isinstance(data.get("record"), dict)):
        return fail("receipt names no verified data tree: data.record must "
                    "be the RECORD.json stamp the verify tool leaves in "
                    "a tree checked against its manifest; nothing is "
                    "attested against unmanifested data")

    bp = r["bound_parameters"]
    months = bp.get("months")
    if (not isinstance(months, list) or not months
            or not all(isinstance(m, str) and len(m) == 7 and m[4] == "-"
                       for m in months)):
        return fail("bound_parameters.months is not a list of YYYY-MM")
    if bp.get("collection") != COLLECTION:
        return fail("bound_parameters.collection is not the contract collection")
    for k, v in CONSTANTS.items():
        if bp.get(k) != v:
            return fail(f"bound_parameters.{k} != {v}")
    extra = set(bp) - {"months", "collection", *CONSTANTS}
    if extra:
        return fail(f"undeclared bound parameters: {sorted(extra)}")

    a = r["anchors"]
    area = a.get("ocean_surface_area_km2", 0.0)
    if abs(area - AREA_KM2) / AREA_KM2 > AREA_RTOL:
        return fail(f"ocean surface area {area:.4e} km2 outside "
                    f"{AREA_RTOL:.1%} of {AREA_KM2:.3e}")
    vol = a.get("ocean_volume_m3", 0.0)
    if abs(vol - VOLUME_M3) / VOLUME_M3 > VOLUME_RTOL:
        return fail(f"ocean volume {vol:.4e} m3 outside "
                    f"{VOLUME_RTOL:.1%} of {VOLUME_M3:.3e}")
    if r["cells_evaluated"] != CELLS:
        return fail(f"cells_evaluated {r['cells_evaluated']} != {CELLS}")

    for m in r["months"]:
        t = m.get("volume_mean_theta_degC")
        if t is None or not (THETA_BAND[0] <= t <= THETA_BAND[1]):
            return fail(f"volume-mean THETA {t} degC outside "
                        f"[{THETA_BAND[0]}, {THETA_BAND[1]}] for {m.get('month')}")

    if "relative to an arbitrary 0 degC" not in r["ohc_baseline_caveat"]:
        return fail("baseline caveat missing or reworded")

    print(f"PASS run {r['run_id']}: sanctioned code, bound parameters, "
          f"grid anchors, THETA sanity, and the baseline caveat all hold "
          f"({len(r['months'])} month(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
