#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested ECCO v4r4 thermal-wind
reconstruction from a level of no motion.

No LLM, stdlib only, consumer-side (OKF v0.2 §10.2). PASS (exit 0) only
when ALL hold, else FAIL (exit 1) naming the field:

  1. declared receipt fields present, including the DISCLOSURE fields:
     every band (0-100 m, 100-1000 m, 1000 m to reference, below
     reference) with BOTH the absolute score (reconstruction against
     the model's actual current) and the relative score (against the
     model's current minus its current at the reference level), the
     model's speed at the level of no motion, and the caveat that
     names which score may be quoted as what. A receipt that keeps the
     flattering relative score and drops the absolute one, or drops
     the deep band where the absolute skill collapses, fails outright;
  2. code_sha256 matches the sanctioned computation file;
  3. bound parameters are the contract exactly (collections, rho0
     1029.0, g, omega, reference depth 3000 m, the validation domain);
  4. the domain is geometry-determined: 19,315 columns at the reference
     level in every month (10-55 deg, seafloor deeper than 3000 m, wet
     at the reference level, inside the tile margins);
  5. REFERENCE-MONTH ANCHOR (month 2009-12), all TWO-SIDED so a
     doctored receipt fails the same as a broken one: 100-1000 m
     absolute r within 0.005 of the measured 0.9900 and rms ratio within
     0.02 of 0.154; relative r within 0.002 of 0.9989; shear r within
     0.02 of 0.9757; below-reference absolute r within 0.05 of 0.152;
     model speed at the reference level median within [2.5e-3, 5e-3]
     m/s;
  6. any other month, provisional bands from the 1992-2017 record runs
     (to be tightened as months accumulate): 100-1000 m absolute r in
     [0.97, 0.995], rms ratio in [0.10, 0.25], relative r >= 0.995,
     shear r in [0.85, 0.99]; below-reference absolute r <= 0.40 and
     relative r >= 0.95; 0-100 m |shear r| < 0.30 (the surface layer
     is where the method fails, and a receipt claiming otherwise fails);
  7. when the receipt carries a `fields` block (the run was asked for
     per-cell arrays), the .npz it names exists and hashes to the
     recorded sha256, and every array entry carries a shape and a
     sha256; a receipt whose fields file is missing or altered fails,
     so a map drawn from it can only show what the receipt vouches for.

Usage: thermal_wind_check.py RECEIPT.json [--computation PATH]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REF_MONTH = "2009-12"
REF_N = 19315
REF = {  # measured on the reference month, tolerance beside each
    ("100-1000 m", "r_absolute"): (0.9900, 0.005),
    ("100-1000 m", "rms_ratio_absolute"): (0.154, 0.02),
    ("100-1000 m", "r_relative"): (0.9989, 0.002),
    ("100-1000 m", "r_shear"): (0.9757, 0.02),
    ("below reference", "r_absolute"): (0.152, 0.05),
}
REF_SPEED_BAND = (2.5e-3, 5.0e-3)
RHO0 = 1029.0
REF_DEPTH = 3000.0
DENS = "ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4"
VEL = "ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4"
DOMAIN = ("10-55 deg latitude, seafloor deeper than 3000 m, wet at the "
          "reference level")
BANDS = ["0-100 m", "100-1000 m", "1000 m to reference", "below reference"]
BAND_FIELDS = ["n_points", "r_absolute", "rms_ratio_absolute",
               "r_relative", "rms_ratio_relative", "r_shear",
               "n_points_shear"]
CAVEAT_MARKS = ["zero at the reference level", "absolute score",
                "relative score", "0-100 m"]


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
                    default=Path(__file__).resolve().parent / "ecco_thermal_wind_reconstruction.py")
    args = ap.parse_args()
    r = json.loads(args.receipt.read_text(encoding="utf-8"))

    for f in ["run_id", "code_sha256", "bound_parameters", "reference",
              "bands", "by_level", "level_of_no_motion_caveat", "frame_note"]:
        if f not in r:
            return fail(f"receipt field missing: {f}"
                        + (" (the caveat is part of the contract, not "
                           "optional)" if f == "level_of_no_motion_caveat"
                           else ""))
    bands = r["bands"]
    for b in BANDS:
        if b not in bands:
            return fail(f"disclosure band missing from receipt: {b} (every "
                        "band is part of the contract; the deep band is "
                        "where the absolute skill collapses)")
        for f in BAND_FIELDS:
            if f not in bands[b]:
                return fail(f"disclosure field missing from band {b}: {f} "
                            "(absolute and relative scores travel together)")
    ref = r["reference"]
    for f in ["depth_used_m", "n_points", "median_model_speed_m_s",
              "p90_model_speed_m_s"]:
        if f not in ref:
            return fail(f"reference field missing: {f} (the model's speed "
                        "at the level of no motion is a disclosure field)")
    caveat = r["level_of_no_motion_caveat"]
    for mark in CAVEAT_MARKS:
        if mark not in caveat:
            return fail("level-of-no-motion caveat missing or reworded "
                        f"(expected the phrase '{mark}')")

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
            or bp.get("g_m_s2") != 9.81
            or bp.get("omega_s1") != 7.2921e-05
            or bp.get("reference_depth_m") != REF_DEPTH
            or sorted(bp.get("collections", [])) != sorted([DENS, VEL])):
        return fail("constants, collections, or reference depth differ "
                    "from the contract")
    if bp.get("validation_domain") != DOMAIN:
        return fail("validation domain differs from the contract")
    if ref["n_points"] != REF_N:
        return fail(f"reference-level n_points {ref['n_points']} != {REF_N} "
                    "(the domain is geometry-determined and does not vary "
                    "by month)")

    problem = check_fields(r, args.receipt)
    if problem:
        return fail(problem)

    mid, deep, top = bands["100-1000 m"], bands["below reference"], bands["0-100 m"]
    for band in BANDS:
        for f in ["r_absolute", "r_relative"]:
            if not isinstance(bands[band][f], (int, float)):
                return fail(f"{band} {f} is not a number")

    if bp.get("month") == REF_MONTH:
        for (band, field), (val, tol) in REF.items():
            got = bands[band][field]
            if got is None or abs(got - val) > tol:
                return fail(f"reference-month {band} {field} {got} not within "
                            f"{tol} of the measured {val} (two-sided: "
                            "inflated claims fail too)")
        sp = ref["median_model_speed_m_s"]
        if not (REF_SPEED_BAND[0] <= sp <= REF_SPEED_BAND[1]):
            return fail(f"reference-month median model speed at the level "
                        f"of no motion {sp} outside {REF_SPEED_BAND}")
        print(f"PASS run {r['run_id']}: sanctioned code, contract parameters, "
              f"all bands and both scores disclosed, caveat present, and "
              f"the reference-month anchors hold (100-1000 m absolute r "
              f"{mid['r_absolute']:.4f} vs measured 0.9900, relative r "
              f"{mid['r_relative']:.4f} vs 0.9989, below-reference absolute "
              f"r {deep['r_absolute']:.3f} vs 0.152)")
        return 0

    if not (0.97 <= mid["r_absolute"] <= 0.995):
        return fail(f"100-1000 m absolute r {mid['r_absolute']} outside the "
                    "provisional [0.97, 0.995]")
    if not (0.10 <= mid["rms_ratio_absolute"] <= 0.25):
        return fail(f"100-1000 m absolute rms ratio {mid['rms_ratio_absolute']} "
                    "outside the provisional [0.10, 0.25]")
    if mid["r_relative"] < 0.995:
        return fail(f"100-1000 m relative r {mid['r_relative']} below the "
                    "provisional 0.995")
    if mid["r_shear"] is None or not (0.85 <= mid["r_shear"] <= 0.99):
        return fail(f"100-1000 m shear r {mid['r_shear']} outside the "
                    "provisional [0.85, 0.99]")
    if deep["r_absolute"] > 0.40:
        return fail(f"below-reference absolute r {deep['r_absolute']} above "
                    "the provisional 0.40: the absolute skill collapses "
                    "below the level of no motion in every measured month, "
                    "and a receipt claiming otherwise is not this method")
    if deep["r_relative"] < 0.95:
        return fail(f"below-reference relative r {deep['r_relative']} below "
                    "the provisional 0.95")
    if top["r_shear"] is None or abs(top["r_shear"]) >= 0.30:
        return fail(f"0-100 m shear r {top['r_shear']} outside the provisional "
                    "(-0.30, 0.30): thermal wind does not govern the surface "
                    "layer shear, and a receipt claiming skill there is not "
                    "this method")
    print(f"PASS run {r['run_id']}: sanctioned code, contract parameters, "
          f"all bands and both scores disclosed, caveat present, "
          f"provisional bands hold ({bp.get('month')}: 100-1000 m absolute r "
          f"{mid['r_absolute']:.4f}, below-reference absolute r "
          f"{deep['r_absolute']:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
