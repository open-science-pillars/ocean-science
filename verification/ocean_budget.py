# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "earthaccess",
#     "ecco_access",
# ]
# ///
"""Smoke test for the ocean-budget workflow: the attested heat budget,
run through its sanctioned executor and attester.

The four-term formulation no longer lives in this file. It was extracted
into the sanctioned computation
knowledge/snapshot-podaac/references/computations/ecco_heat_budget.py,
whose contract is
knowledge/snapshot-podaac/computations/ecco-heat-budget.md: the attested
computation owns the pass bar (absolute residual, max <= 1e-10 and
p99.9 <= 1e-11 degC/s, pointwise on the interior wet cells of one
tile), and the attester
knowledge/snapshot-podaac/references/attesters/budget_residual.py hashes
the computation file, so editing it breaks attestation by construction.
This script does what the executor instructions
(knowledge/snapshot-podaac/references/skills/run-golden.md) prescribe:
stage the 2010 fixture cache, run the computation for a receipt, attest
the receipt, and fail unless the verdict is PASS.

One requirement beyond the cache: the attester refuses a receipt from a
tree without a RECORD.json stamp, and that stamp is written by the
canonical repository's verify tool (nasa-daac-knowledge,
tools/science_record_verify.py --stamp) against the fixture manifest,
which the pinned copy carries at
knowledge/snapshot-podaac/references/retrieval/fixtures-2010-manifest.json.
Run it once after the first fetch. Headless green via
`uv run verification/ocean_budget.py`.
"""

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REFERENCES = HERE.parent / "knowledge" / "snapshot-podaac" / "references"
COMPUTATION = REFERENCES / "computations" / "ecco_heat_budget.py"
ATTESTER = REFERENCES / "attesters" / "budget_residual.py"
YEAR = 2010


def stage() -> Path:
    """Populate the fixture cache and confirm it carries the stamp."""
    spec = importlib.util.spec_from_file_location(
        "fetch_ecco_2010", HERE / "fixtures" / "fetch_ecco_2010.py")
    fx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fx)
    root = fx.ensure_cache()["root"]
    if not (root / "RECORD.json").exists():
        sys.exit(f"{root} carries no RECORD.json stamp; the attester refuses "
                 "receipts from an unstamped tree. Stamp it with the "
                 "canonical repository's verify tool (module docstring) "
                 "and rerun.")
    return root


def main() -> int:
    root = stage()
    with tempfile.TemporaryDirectory() as tmp:
        receipt = Path(tmp) / "heat-budget-receipt.json"
        run = subprocess.run(
            ["uv", "run", str(COMPUTATION), "--year", str(YEAR),
             "--data-root", str(root), "--receipt", str(receipt)],
            text=True)
        if run.returncode != 0:
            print("ocean_budget smoke: the sanctioned computation FAILED")
            return 1
        verdict = subprocess.run(
            ["uv", "run", str(ATTESTER), str(receipt)],
            capture_output=True, text=True)
    print(verdict.stdout.strip())
    if verdict.returncode != 0 or not verdict.stdout.startswith("PASS"):
        print("ocean_budget smoke: attestation FAILED")
        return 1
    print(f"ocean_budget smoke: the {YEAR} heat budget closes at the attested "
          "pass bar (executor and attester from the pinned copy)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
