#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested ECCO v4r4 wind-stress curl
and Ekman pumping check.

No LLM, stdlib only, consumer-side (spec 10.2). PASS (exit 0) only
when ALL hold, else FAIL (exit 1) naming the field:

  1. declared receipt fields present, including method_caveat (the
     statement that WVEL contains all vertical motion, so r validates
     sign and pattern, not equality): a receipt that drops the caveat
     fails, so no consumer can quote the correlation as if Ekman
     pumping explained the model's vertical velocity outright;
  2. code_sha256 matches the sanctioned computation file;
  3. bound parameters are the contract exactly (collections, rho0
     1029.0, the validation domain, WVEL interface 70 m);
  4. REFERENCE-MONTH ANCHOR (month 2009-12): r_ekman_vs_wvel within
     0.02 of the measured 0.8225 TWO-SIDED (a doctored 0.99 fails the
     same as a broken 0.4); n_points exactly 20,751; median |curl|
     within a factor of two of the measured 9.25e-8 N m-3;
  5. any other month: r in [0.70, 0.92], provisional.

Usage: curl_check.py RECEIPT.json [--computation PATH]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REF_MONTH = "2009-12"
REF_R = 0.8225
REF_R_TOL = 0.02
REF_N = 20751
REF_CURL = 9.25e-8
RHO0 = 1029.0
STRESS = "ECCO_L4_STRESS_LLC0090GRID_MONTHLY_V4R4"
VEL = "ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4"
DOMAIN = "10-55 deg latitude, seafloor deeper than 3000 m"


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--computation", type=Path,
                    default=Path(__file__).parent.parent
                    / "computations" / "ecco_curl_ekman.py")
    args = ap.parse_args()
    r = json.loads(args.receipt.read_text(encoding="utf-8"))

    for f in ["run_id", "code_sha256", "bound_parameters", "results",
              "method_caveat"]:
        if f not in r:
            return fail(f"receipt field missing: {f}"
                        + (" (the caveat is part of the contract, not "
                           "optional)" if f == "method_caveat" else ""))
    res = r["results"]
    for f in ["r_ekman_vs_wvel", "median_abs_diff_m_s",
              "median_abs_curl_N_m3", "n_points"]:
        if f not in res:
            return fail(f"results field missing: {f}")

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
    if (bp.get("rho0_kg_m3") != RHO0
            or bp.get("stress_collection") != STRESS
            or bp.get("velocity_collection") != VEL
            or bp.get("validation_domain") != DOMAIN
            or bp.get("wvel_interface_m") != 70.0):
        return fail("constants, collections, or domain differ from "
                    "the contract")

    rv = res["r_ekman_vs_wvel"]
    if bp.get("month") == REF_MONTH:
        if abs(rv - REF_R) > REF_R_TOL:
            return fail(f"reference-month r {rv} not within {REF_R_TOL} "
                        f"of the measured {REF_R} (two-sided: inflated "
                        "claims fail too)")
        if res["n_points"] != REF_N:
            return fail(f"n_points {res['n_points']} != {REF_N}")
        c = res["median_abs_curl_N_m3"]
        if not (REF_CURL / 2 <= c <= REF_CURL * 2):
            return fail(f"median |curl| {c} outside a factor of two of "
                        f"the measured {REF_CURL}")
        print(f"PASS run {r['run_id']}: sanctioned code, contract "
              f"parameters, caveat present, reference-month anchors "
              f"hold (r {rv:.4f} vs measured {REF_R})")
        return 0

    if not (0.70 <= rv <= 0.92):
        return fail(f"r {rv} outside the provisional [0.70, 0.92]")
    print(f"PASS run {r['run_id']}: sanctioned code, contract parameters, "
          f"caveat present, provisional band holds ({bp.get('month')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
