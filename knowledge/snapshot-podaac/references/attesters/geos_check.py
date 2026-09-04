#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested ECCO v4r4 geostrophic
balance and thermal wind check.

No LLM, stdlib only, consumer-side (spec 10.2). PASS (exit 0) only
when ALL hold, else FAIL (exit 1) naming the field:

  1. declared receipt fields present, including the DISCLOSURE fields
     (full-band and polar-band figures): a receipt that quotes only
     the favorable open-ocean interior correlation and drops the
     weaker bands fails attestation outright;
  2. code_sha256 matches the sanctioned computation file;
  3. bound parameters are the contract exactly (collections, rho0
     1029.0, the stated validation domain);
  4. REFERENCE-MONTH ANCHOR (month 2009-12): r_velocity within 0.02
     of the measured 0.9242 TWO-SIDED, so a doctored receipt claiming
     a flattering 0.99 fails the same as a broken 0.5; n_points
     exactly 20,771 (deterministic given data and masks); thermal
     wind r within 0.05 of the measured 0.6102;
  5. any other month: r_velocity in [0.85, 0.98] and thermal wind r
     in [0.45, 0.85], provisional bands to be tightened as months
     accumulate.

Usage: geos_check.py RECEIPT.json [--computation PATH]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REF_MONTH = "2009-12"
REF_R = 0.9242
REF_R_TOL = 0.02
REF_N = 20771
REF_TW_R = 0.6102
REF_TW_TOL = 0.05
RHO0 = 1029.0
DENS = "ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4"
VEL = "ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4"
SSH = "ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4"
DOMAIN = "10-55 deg latitude, seafloor deeper than 3000 m"
GEO_FIELDS = ["r_velocity", "median_abs_diff_m_s", "n_points",
              "r_velocity_full_band", "n_points_full_band",
              "r_velocity_polar_band", "n_points_polar"]


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--computation", type=Path,
                    default=Path(__file__).parent.parent
                    / "computations" / "ecco_geostrophy.py")
    args = ap.parse_args()
    r = json.loads(args.receipt.read_text(encoding="utf-8"))

    for f in ["run_id", "code_sha256", "bound_parameters",
              "geostrophic", "thermal_wind"]:
        if f not in r:
            return fail(f"receipt field missing: {f}")
    geo = r["geostrophic"]
    for f in GEO_FIELDS:
        if f not in geo:
            return fail(f"disclosure field missing from receipt: {f} "
                        "(the full-band and polar figures are part of "
                        "the contract, not optional)")

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
            or sorted(bp.get("collections", [])) != sorted([DENS, VEL, SSH])):
        return fail("constants or collections differ from the contract")
    if geo.get("validation_domain") != DOMAIN:
        return fail("validation domain differs from the contract")

    rv = geo["r_velocity"]
    tw = r["thermal_wind"].get("r_shear")
    if tw is None:
        return fail("thermal_wind.r_shear missing")

    if bp.get("month") == REF_MONTH:
        if abs(rv - REF_R) > REF_R_TOL:
            return fail(f"reference-month r_velocity {rv} not within "
                        f"{REF_R_TOL} of the measured {REF_R} "
                        "(two-sided: inflated claims fail too)")
        if geo["n_points"] != REF_N:
            return fail(f"n_points {geo['n_points']} != {REF_N}")
        if abs(tw - REF_TW_R) > REF_TW_TOL:
            return fail(f"reference-month thermal wind r {tw} not within "
                        f"{REF_TW_TOL} of the measured {REF_TW_R}")
        print(f"PASS run {r['run_id']}: sanctioned code, contract "
              f"parameters, disclosure fields present, and the "
              f"reference-month anchors hold (r {rv:.4f} vs measured "
              f"{REF_R}, thermal wind {tw:.4f} vs {REF_TW_R})")
        return 0

    if not (0.85 <= rv <= 0.98):
        return fail(f"r_velocity {rv} outside the provisional [0.85, 0.98]")
    if not (0.45 <= tw <= 0.85):
        return fail(f"thermal wind r {tw} outside the provisional "
                    "[0.45, 0.85]")
    print(f"PASS run {r['run_id']}: sanctioned code, contract parameters, "
          f"disclosure fields present, provisional bands hold "
          f"({bp.get('month')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
