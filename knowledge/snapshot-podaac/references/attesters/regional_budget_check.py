#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested ECCO v4r4 regional budgets
(heat, salt, volume) over a control volume.

No LLM, stdlib only, consumer-side (spec 10.2). PASS (exit 0) only
when ALL hold, else FAIL (exit 1) naming the field:

  1. declared receipt fields present, including the DISCLOSURE set
     (resolved volume with mask and geometry digests, wet and bottom
     cell counts) and the MUTATION EVIDENCE carrying exactly the
     budget's named sabotage set;
  2. code_sha256 matches the sanctioned computation file;
  3. bound parameters are the budget's contract exactly (collections,
     constants, the two bars);
  4. BOTH BARS hold, recomputed from the receipt's results;
  5. every mutation's caught flag is consistent with its own numbers;
     structural sabotages must trip a bar, applicability-aware ones
     (geothermal for heat, the surface salt flux and salt plume for
     salt) may instead be marked not applicable with numbers under
     both bars; the volume budget's spurious-freshwater sabotage is
     ALWAYS structural, because the demonstrated double-count must be
     caught, not merely documented;
  6. REFERENCE ANCHORS (southeast-atlantic-upper, 2010): wet_cells
     exactly 27,921, volume within 0.1 percent of 4.1351e15 m3, and
     the residual per volume within a factor of three TWO-SIDED of
     the measured value for the budget (heat 1.352e-14, salt
     3.056e-14, volume 1.068e-15), so flattering receipts fail too.

Usage: regional_budget_check.py RECEIPT.json [--computation PATH]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

FLUX = "ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4"
HF = "ECCO_L4_HEAT_FLUX_LLC0090GRID_MONTHLY_V4R4"
SFLX = "ECCO_L4_OCEAN_3D_SALINITY_FLUX_LLC0090GRID_MONTHLY_V4R4"
FF = "ECCO_L4_FRESH_FLUX_LLC0090GRID_MONTHLY_V4R4"
VOLF = "ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4"
SNP_TS = "ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4"
SNP_SSH = "ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4"

CONTRACT = {
    "heat": {"bars": (1e-10, 1e-6), "units": "degC/s",
             "collections": [FLUX, HF, SNP_TS, SNP_SSH],
             "mutations": {"geothermal-omitted", "rim-west-face-shifted",
                           "vertical-face-sign-flipped",
                           "vertical-faces-omitted"},
             "aware": {"geothermal-omitted"},
             "ref_residual": 1.352e-14},
    "salt": {"bars": (1.5e-10, 1e-6), "units": "g/kg/s",
             "collections": [SFLX, FF, SNP_TS, SNP_SSH],
             "mutations": {"surface-sflux-omitted", "salt-plume-omitted",
                           "rim-west-face-shifted",
                           "vertical-face-sign-flipped",
                           "vertical-faces-omitted"},
             "aware": {"surface-sflux-omitted", "salt-plume-omitted"},
             "ref_residual": 3.056e-14},
    "volume": {"bars": (1e-11, 1e-6), "units": "1/s",
               "collections": [VOLF, SNP_TS, SNP_SSH],
               "mutations": {"spurious-freshwater-forcing-added",
                             "rim-west-face-shifted",
                             "vertical-face-sign-flipped",
                             "vertical-faces-omitted"},
               "aware": set(),
               "ref_residual": 1.068e-15},
}
REF_REGION = "southeast-atlantic-upper"
REF_YEAR = 2010
REF_FACTOR = 3.0
REF_CELLS = 27921
REF_VOLUME = 4.1351e15


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--computation", type=Path,
                    default=Path(__file__).parent.parent
                    / "computations" / "ecco_regional_budget.py")
    args = ap.parse_args()
    r = json.loads(args.receipt.read_text(encoding="utf-8"))

    for f in ["run_id", "code_sha256", "bound_parameters",
              "resolved_volume", "results", "mutation_evidence",
              "caveats"]:
        if f not in r:
            return fail(f"receipt field missing: {f}")
    rv = r["resolved_volume"]
    for f in ["tile", "j", "i", "k_cells", "depth_face_m", "lat_extent",
              "lon_extent", "wet_cells", "bottom_cells", "volume_m3",
              "mask_sha256", "geometry_sha256"]:
        if f not in rv:
            return fail(f"disclosure field missing: resolved_volume.{f}")

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
    budget = bp.get("budget")
    if budget not in CONTRACT:
        return fail(f"unknown budget {budget!r}")
    c = CONTRACT[budget]
    abs_bar, rel_bar = c["bars"]
    if (bp.get("collections") != c["collections"]
            or bp.get("rhoConst_kg_m3") != 1029.0
            or bp.get("Cp_J_kg_K") != 3994.0
            or bp.get("abs_bar") != abs_bar
            or bp.get("abs_bar_units") != c["units"]
            or bp.get("rel_bar") != rel_bar):
        return fail("constants, collections, bars, or bar units differ "
                    f"from the {budget} contract")

    res = r["results"]
    a = res.get("residual_per_volume_max")
    rel = res.get("residual_relative_max")
    if a is None or rel is None:
        return fail("results missing the two bar figures")
    if (res.get("units") or {}).get("residual_per_volume") != c["units"]:
        return fail(f"results must state residual units {c['units']!r} "
                    f"for the {budget} budget")
    if a > abs_bar:
        return fail(f"absolute bar failed: {a} > {abs_bar}")
    if rel > rel_bar:
        return fail(f"relative bar failed: {rel} > {rel_bar}")

    ev = r["mutation_evidence"]
    if {e.get("mutation") for e in ev} != c["mutations"]:
        return fail(f"{budget} mutation evidence must carry exactly "
                    f"{sorted(c['mutations'])}")
    for e in ev:
        tripped = (e.get("residual_per_volume", 0) > abs_bar
                   or e.get("residual_relative", 0) > rel_bar)
        if e.get("caught") and not tripped:
            return fail(f"mutation {e['mutation']} marked caught but its "
                        "numbers trip no bar")
        if not e.get("caught"):
            if e.get("mutation") not in c["aware"]:
                return fail(f"structural mutation {e['mutation']} uncaught")
            if e.get("applicable") is not False or tripped:
                return fail(f"mutation {e['mutation']} inconsistently "
                            "marked inapplicable")

    if (bp.get("mode") == "registered" and bp.get("region") == REF_REGION
            and bp.get("year") == REF_YEAR):
        if rv["wet_cells"] != REF_CELLS:
            return fail(f"reference wet_cells {rv['wet_cells']} != {REF_CELLS}")
        if abs(rv["volume_m3"] - REF_VOLUME) / REF_VOLUME > 0.001:
            return fail(f"reference volume {rv['volume_m3']} off")
        ref = c["ref_residual"]
        if not (ref / REF_FACTOR <= a <= ref * REF_FACTOR):
            return fail(f"reference residual {a} outside a factor of "
                        f"{REF_FACTOR} of the measured {ref} "
                        "(two-sided: flattering claims fail too)")
        print(f"PASS run {r['run_id']}: {budget} budget, sanctioned code, "
              f"both bars, evidence consistent, reference anchors hold "
              f"(residual {a:.3e} vs measured {ref:.3e})")
        return 0

    print(f"PASS run {r['run_id']}: {budget} budget, sanctioned code, "
          f"both bars, evidence consistent "
          f"({bp.get('region') or 'explicit box'}, year {bp.get('year')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
