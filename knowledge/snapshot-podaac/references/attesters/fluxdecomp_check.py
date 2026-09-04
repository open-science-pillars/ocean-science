#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested ECCO v4r4 flux
decomposition.

No LLM, stdlib only, consumer-side (spec 10.2). PASS (exit 0) only
when ALL hold, else FAIL (exit 1) naming the field:

  1. declared receipt fields present, including all four stored terms
     (all_terms_PW travels regardless of grouping, so no grouping can
     hide a term) and MUTATION EVIDENCE with both sabotages caught;
  2. code_sha256 matches the sanctioned computation file;
  3. bound parameters are the contract exactly, including the mean
     convention and both oracle bars;
  4. BOTH ORACLES hold from the receipt's own numbers: the four-term
     identity and the vanishing cross-term means, each at 1e-12
     relative;
  5. the reported terms are CONSISTENT with the stored four:
     time-mean-eddy must report mean-mean as mean-advective and
     prime-prime as eddy; anomaly must report total minus mean-mean;
     full-four-term must report all four verbatim: a receipt whose
     reported view disagrees with its stored terms fails;
  6. REFERENCE ANCHORS (southeast-atlantic-upper, 2010): 27,078 wet
     faces; total within 0.01 PW of the measured +8.97391 TWO-SIDED;
     mean-mean within 0.01 of +9.04354.

Usage: fluxdecomp_check.py RECEIPT.json [--computation PATH]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

IDENTITY_BAR = 1e-12
CROSS_BAR = 1e-12
REF_REGION = "southeast-atlantic-upper"
REF_YEAR = 2010
REF_FACES = 27078
REF_TOTAL = 8.97391
REF_MM = 9.04354
REF_TOL = 0.01
COLLECTIONS = [
    "ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4",
    "ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4",
]
MUTATIONS = {"cross-term-dropped", "stale-mean-half-window"}


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--computation", type=Path,
                    default=Path(__file__).parent.parent
                    / "computations" / "ecco_flux_decomposition.py")
    args = ap.parse_args()
    r = json.loads(args.receipt.read_text(encoding="utf-8"))

    for f in ["run_id", "code_sha256", "bound_parameters",
              "resolved_faces", "results", "mutation_evidence", "caveats"]:
        if f not in r:
            return fail(f"receipt field missing: {f}")
    res = r["results"]
    at = res.get("all_terms_PW")
    if not at or set(at) != {"mean-mean_PW", "mean-prime_PW",
                             "prime-mean_PW", "prime-prime_PW",
                             "total_PW"}:
        return fail("all four stored terms must travel in every receipt")

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
    if (bp.get("collections") != COLLECTIONS
            or bp.get("rhoConst_kg_m3") != 1029.0
            or bp.get("Cp_J_kg_K") != 3994.0
            or bp.get("identity_bar_rel") != IDENTITY_BAR
            or bp.get("cross_bar_rel") != CROSS_BAR
            or "equal-weight" not in str(bp.get("mean_convention"))):
        return fail("constants, collections, bars, or mean convention "
                    "differ from the contract")

    if res.get("identity_max_rel", 1) > IDENTITY_BAR:
        return fail(f"identity oracle failed: {res.get('identity_max_rel')}")
    if res.get("cross_term_mean_max_rel", 1) > CROSS_BAR:
        return fail("cross-term oracle failed: "
                    f"{res.get('cross_term_mean_max_rel')}")

    ev = r["mutation_evidence"]
    if {e.get("mutation") for e in ev} != MUTATIONS:
        return fail("mutation evidence must carry exactly both sabotages")
    for e in ev:
        if not e.get("caught"):
            return fail(f"sabotage {e['mutation']} uncaught")
        num = e.get("identity_rel", e.get("cross_term_rel", 0))
        if num <= max(IDENTITY_BAR, CROSS_BAR):
            return fail(f"sabotage {e['mutation']} marked caught but its "
                        "number trips no oracle")

    g = bp.get("grouping")
    rep = res.get("reported_terms", {})
    tol = 1e-9

    def close(x, y):
        return abs(x - y) <= tol

    if g == "full-four-term":
        ok = all(close(rep.get(k, 1e9), at[k]) for k in at)
    elif g == "time-mean-eddy":
        ok = (close(rep.get("mean-advective_PW", 1e9), at["mean-mean_PW"])
              and close(rep.get("eddy_PW", 1e9), at["prime-prime_PW"])
              and close(rep.get("total_PW", 1e9), at["total_PW"]))
    elif g == "anomaly":
        ok = (close(rep.get("anomaly-total_PW", 1e9),
                    at["total_PW"] - at["mean-mean_PW"])
              and close(rep.get("prime-prime_PW", 1e9),
                        at["prime-prime_PW"]))
    else:
        return fail(f"unknown grouping {g!r}")
    if not ok:
        return fail(f"reported terms disagree with the stored four for "
                    f"grouping {g}: the view cannot contradict the data")

    if bp.get("region") == REF_REGION and bp.get("year") == REF_YEAR:
        if r["resolved_faces"]["faces_wet"] != REF_FACES:
            return fail(f"reference faces {r['resolved_faces']['faces_wet']} "
                        f"!= {REF_FACES}")
        if abs(at["total_PW"] - REF_TOTAL) > REF_TOL:
            return fail(f"reference total {at['total_PW']} not within "
                        f"{REF_TOL} of the measured {REF_TOTAL} (two-sided)")
        if abs(at["mean-mean_PW"] - REF_MM) > REF_TOL:
            return fail(f"reference mean-mean {at['mean-mean_PW']} off "
                        f"the measured {REF_MM}")
        print(f"PASS run {r['run_id']}: sanctioned code, both oracles, "
              f"view consistent with stored terms ({g}), reference "
              f"anchors hold (total {at['total_PW']:+.5f} PW)")
        return 0

    print(f"PASS run {r['run_id']}: sanctioned code, both oracles, view "
          f"consistent with stored terms ({g})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
