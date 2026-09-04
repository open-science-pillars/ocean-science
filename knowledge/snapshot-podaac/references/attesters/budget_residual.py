#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested ECCO v4r4 heat budget.

No LLM, stdlib only, consumer-side (spec 10.2: the attester is code that
takes a receipt and returns a verdict). Reads a receipt JSON produced per
references/skills/run-golden.md and returns PASS (exit 0) only when ALL
of the following hold, otherwise FAIL (exit 1) naming the failing field:

  1. every declared receipt field is present (run_id, code_sha256,
     bound_parameters, residual_max, residual_p999, cells_evaluated);
  2. code_sha256 equals the sha256 of the sanctioned computation file
     (references/computations/ecco_heat_budget.py), so a rewritten or
     swapped computation fails mechanically (spec 10.3);
  3. bound_parameters match the declared parameter set of the contract
     (year: integer, required; region: string, optional; nothing else);
  4. residual_max  <= 1e-10 degC/s and residual_p999 <= 1e-11 degC/s,
     the tolerances recorded by the heat-budget recipe (measured
     2026-07-04, 2x headroom over the measured max).

Usage: budget_residual.py RECEIPT.json [--computation PATH]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

RECEIPT_FIELDS = ("run_id", "code_sha256", "bound_parameters",
                  "residual_max", "residual_p999", "cells_evaluated")
TOL_MAX = 1e-10    # degC/s, absolute pointwise (recipe pass bar)
TOL_P999 = 1e-11   # degC/s (recipe pass bar)
DEFAULT_COMPUTATION = (Path(__file__).resolve().parent.parent
                       / "computations" / "ecco_heat_budget.py")


def fail(field: str, reason: str) -> int:
    print(f"FAIL {field}: {reason}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--computation", type=Path, default=DEFAULT_COMPUTATION,
                    help="sanctioned computation file to hash against")
    args = ap.parse_args()

    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return fail("receipt", f"unreadable or not JSON: {e}")

    for field in RECEIPT_FIELDS:
        if field not in receipt:
            return fail(field, "missing from receipt")

    want = hashlib.sha256(args.computation.read_bytes()).hexdigest()
    if receipt["code_sha256"] != want:
        return fail("code_sha256",
                    f"receipt {str(receipt['code_sha256'])[:12]}... does not "
                    f"match sanctioned computation {want[:12]}... "
                    f"({args.computation.name}): not the sanctioned code")

    data = receipt.get("data")
    if (not isinstance(data, dict)
            or not isinstance(data.get("record"), dict)):
        return fail("data",
                    "receipt names no verified data tree: data.record must "
                    "be the RECORD.json stamp the verify tool leaves in "
                    "a tree checked against its manifest; nothing is "
                    "attested against unmanifested data")

    bound = receipt["bound_parameters"]
    if not isinstance(bound, dict):
        return fail("bound_parameters", "not a mapping")
    if "year" not in bound:
        return fail("bound_parameters", "required parameter `year` not bound")
    if not isinstance(bound["year"], int) or isinstance(bound["year"], bool):
        return fail("bound_parameters", "`year` must bind an integer")
    if "region" in bound and not isinstance(bound["region"], str):
        return fail("bound_parameters", "`region` must bind a string")
    extra = set(bound) - {"year", "region"}
    if extra:
        return fail("bound_parameters",
                    f"undeclared parameter(s) bound: {sorted(extra)}")

    for field, tol in (("residual_max", TOL_MAX), ("residual_p999", TOL_P999)):
        value = receipt[field]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return fail(field, "not a number")
        if value > tol:
            return fail(field, f"{value:.3e} exceeds tolerance {tol:.0e} degC/s")

    print(f"PASS run_id={receipt['run_id']} "
          f"bound={json.dumps(bound, sort_keys=True)} "
          f"residual_max={receipt['residual_max']:.3e} "
          f"residual_p999={receipt['residual_p999']:.3e} "
          f"cells={receipt['cells_evaluated']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
