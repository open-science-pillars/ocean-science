#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested ECCO v4r4 wind-stress curl
and Ekman pumping check.

No LLM, stdlib only, consumer-side (OKF v0.2 §10.2). PASS (exit 0) only
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
  5. any other month: r in [0.70, 0.92], provisional;
  6. when the receipt carries a `fields` block (the run was asked for
     per-cell arrays), the .npz it names exists and hashes to the
     recorded sha256, and every array entry carries a shape and a
     sha256; a receipt whose fields file is missing or altered fails,
     so a map drawn from it can only show what the receipt vouches for.

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


def check_fields(r, receipt_path):
    """The optional per-cell fields file: when the receipt carries a
    `fields` block, the file it names must exist (beside the receipt
    if not at the recorded path) and hash to the recorded sha256, so a
    map drawn from it shows the numbers this receipt vouches for.
    Returns None when the block holds, else the failure message."""
    if "fields" not in r:
        return None
    fb = r["fields"]
    if (not isinstance(fb, dict) or not fb.get("path")
            or not isinstance(fb.get("sha256"), str)
            or len(fb["sha256"]) != 64
            or not isinstance(fb.get("arrays"), dict) or not fb["arrays"]):
        return "fields block present but malformed (needs path, sha256, arrays)"
    candidates = [Path(fb["path"]), receipt_path.parent / Path(fb["path"]).name]
    found = next((c for c in candidates if c.is_file()), None)
    if found is None:
        return (f"fields file {fb['path']} not found at its recorded path "
                "or beside the receipt: a receipt that names per-cell "
                "fields is attested with them or not at all")
    got = hashlib.sha256(found.read_bytes()).hexdigest()
    if got != fb["sha256"]:
        return (f"fields file {found} does not hash to the receipt's "
                f"sha256 ({got[:12]}... vs {fb['sha256'][:12]}...)")
    for name, spec in fb["arrays"].items():
        if (not isinstance(spec, dict) or not isinstance(spec.get("shape"), list)
                or not isinstance(spec.get("sha256"), str)
                or len(spec["sha256"]) != 64):
            return f"fields.arrays.{name} lacks shape or sha256"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--computation", type=Path,
                    default=Path(__file__).resolve().parent / "ecco_curl_ekman.py")
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

    problem = check_fields(r, args.receipt)
    if problem:
        return fail(problem)

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
