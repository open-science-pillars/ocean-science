#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for attested ECCO v4r4 section transports.

No LLM, stdlib only, consumer-side (spec 10.2). PASS (exit 0) only
when ALL hold, else FAIL (exit 1) naming the field:

  1. declared receipt fields present, including the DISCLOSURE set
     (resolved section with face counts, extent, mask digest, geometry
     digest) and MUTATION EVIDENCE carrying exactly the five named
     sabotages;
  2. code_sha256 matches the sanctioned computation file;
  3. bound parameters are the contract exactly;
  4. every mutation's caught flag is consistent with its own numbers
     against the catch bars (0.02 PW, 1 Sv): a caught entry must trip
     a bar, an uncaught entry must be marked not applicable and sit
     under both;
  5. an UNANCHORED section's receipt must say so in its caveats: a
     receipt that presents a benchmark-free transport without that
     statement fails, whatever its numbers;
  6. ANCHORED REFERENCE (global-26.5n, year 2010): heat mean within
     the cross-implementation band (1.098 plus or minus 0.03 PW, the
     independent implementation's number) AND within 0.005 PW of the
     measured 1.0963 TWO-SIDED, so a receipt doctored toward the
     anchor fails the same as a broken one; volume mean within 0.3 Sv
     of the measured -0.4274; exactly 360 faces, closed. The interior
     segment (fifteen-s-southeast-atlantic) pins its face count (90)
     and carries no transport anchor by design.

Usage: section_transport_check.py RECEIPT.json [--computation PATH]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

MUT_HEAT_PW = 0.02
MUT_VOL_SV = 1.0
ANCHOR_PW = 1.098
ANCHOR_TOL = 0.03
REF_HEAT = 1.0963
REF_HEAT_TOL = 0.005
REF_VOL = -0.4274
REF_VOL_TOL = 0.3
REF_FACES = {"global-26.5n": 360, "fifteen-s-southeast-atlantic": 90}
COLLECTIONS = [
    "ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4",
    "ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4",
]
MUTATIONS = {"rotated-tile-face-signs-flipped", "south-faces-dropped",
             "path-shifted-one-row", "seam-faces-dropped",
             "seam-ghosts-zeroed"}


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--computation", type=Path,
                    default=Path(__file__).parent.parent
                    / "computations" / "ecco_section_transport.py")
    args = ap.parse_args()
    r = json.loads(args.receipt.read_text(encoding="utf-8"))

    for f in ["run_id", "code_sha256", "bound_parameters",
              "resolved_section", "results", "mutation_evidence",
              "caveats"]:
        if f not in r:
            return fail(f"receipt field missing: {f}")
    rs = r["resolved_section"]
    for f in ["faces", "seam_faces", "closed", "lat_extent", "lon_extent",
              "mask_sha256", "geometry_sha256"]:
        if f not in rs:
            return fail(f"disclosure field missing: resolved_section.{f}")

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
            or bp.get("Cp_J_kg_K") != 3994.0):
        return fail("constants or collections differ from the contract")

    ev = r["mutation_evidence"]
    if {e.get("mutation") for e in ev} != MUTATIONS:
        return fail("mutation evidence must carry exactly the five "
                    "named sabotages")
    for e in ev:
        tripped = (e.get("delta_heat_PW", 0) > MUT_HEAT_PW
                   or e.get("delta_volume_Sv", 0) > MUT_VOL_SV)
        if e.get("caught") and not tripped:
            return fail(f"mutation {e['mutation']} marked caught but its "
                        "numbers trip no bar")
        if not e.get("caught"):
            if e.get("applicable") is not False:
                return fail(f"mutation {e['mutation']} uncaught yet not "
                            "marked inapplicable")
            if tripped:
                return fail(f"mutation {e['mutation']} marked "
                            "inapplicable but its numbers trip a bar")

    res = r["results"]
    hm, vm = res.get("heat_transport_mean_PW"), res.get("volume_transport_mean_Sv")
    if hm is None or vm is None:
        return fail("results missing transport means")

    section = bp.get("section")
    if rs["faces"] != REF_FACES.get(section):
        return fail(f"faces {rs['faces']} != the registered "
                    f"{REF_FACES.get(section)} for {section}")

    if section == "global-26.5n" and bp.get("year") == 2010:
        if not rs["closed"]:
            return fail("global-26.5n must be a closed circle")
        if abs(hm - ANCHOR_PW) > ANCHOR_TOL:
            return fail(f"heat mean {hm} outside the independent "
                        f"implementation's {ANCHOR_PW} +/- {ANCHOR_TOL}")
        if abs(hm - REF_HEAT) > REF_HEAT_TOL:
            return fail(f"heat mean {hm} not within {REF_HEAT_TOL} of the "
                        f"measured {REF_HEAT} (two-sided: a receipt "
                        "doctored toward the anchor fails too)")
        if abs(vm - REF_VOL) > REF_VOL_TOL:
            return fail(f"volume mean {vm} not within {REF_VOL_TOL} of "
                        f"the measured {REF_VOL}")
        print(f"PASS run {r['run_id']}: sanctioned code, evidence "
              f"consistent, anchored reference holds (heat {hm:+.4f} PW "
              f"vs independent {ANCHOR_PW}, measured {REF_HEAT})")
        return 0

    if "unanchored" not in r["caveats"]:
        return fail("an unanchored section's receipt must say so in its "
                    "caveats; a benchmark-free transport presented "
                    "without that statement fails")
    print(f"PASS run {r['run_id']}: sanctioned code, evidence consistent, "
          f"disclosure complete ({section}, unanchored by design)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
