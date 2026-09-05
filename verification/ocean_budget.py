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
knowledge/podaac/references/computations/ecco_heat_budget.py,
whose contract is
knowledge/podaac/computations/ecco-heat-budget.md: the attested
computation owns the pass bar (absolute residual, max <= 1e-10 and
p99.9 <= 1e-11 degC/s, pointwise on the interior wet cells of one
tile), and the attester
knowledge/podaac/references/attesters/budget_residual.py hashes
the computation file, so editing it breaks attestation by construction.
This script does what the executor instructions
(knowledge/podaac/references/skills/run-golden.md) prescribe:
stage the 2010 fixture cache, run the computation for a receipt, attest
the receipt, and fail unless the verdict is PASS.

The bundle paths above are resolved the way the consult-knowledge
convention resolves them: the PO.DAAC bundle is installed with the
nasa-daac-knowledge dependency, and its root is read from the
installer's record (`claude plugin list --json`, the entry's
installPath), never from a remembered path. A checkout of the provider
repository can stand in for the install by setting
NASA_DAAC_KNOWLEDGE to its root.

One requirement beyond the cache: the attester refuses a receipt from a
tree without a RECORD.json stamp, and that stamp is written by the
provider repository's verify tool (tools/science_record_verify.py
--stamp, shipped in the same plugin) against the fixture manifest at
knowledge/podaac/references/retrieval/fixtures-2010-manifest.json.
Run it once after the first fetch. Headless green via
`uv run verification/ocean_budget.py`.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROVIDER_PLUGIN = "nasa-daac-knowledge"
YEAR = 2010


def provider_root() -> Path:
    """The installed provider plugin's root, from the installer's record."""
    override = os.environ.get("NASA_DAAC_KNOWLEDGE")
    if override:
        return Path(override).expanduser().resolve()
    claude = shutil.which("claude")
    if claude is None:
        sys.exit("no `claude` on PATH to read the installed-plugin record; "
                 "set NASA_DAAC_KNOWLEDGE to a checkout of the provider "
                 "repository instead")
    rec = subprocess.run([claude, "plugin", "list", "--json"],
                         capture_output=True, text=True)
    if rec.returncode != 0:
        sys.exit(f"`claude plugin list --json` failed: {rec.stderr.strip()}")
    for entry in json.loads(rec.stdout):
        if entry.get("id", "").split("@")[0] != PROVIDER_PLUGIN:
            continue
        if not entry.get("enabled", True) or entry.get("errors"):
            sys.exit(f"{entry['id']} is installed but not usable: "
                     f"{entry.get('errors') or 'disabled'}")
        return Path(entry["installPath"])
    sys.exit(f"{PROVIDER_PLUGIN} is not installed; it arrives with this "
             "plugin's dependencies (`claude plugin install "
             "ocean-science@open-science-pillars`), or set "
             "NASA_DAAC_KNOWLEDGE to a checkout of the provider repository")


REFERENCES = provider_root() / "knowledge" / "podaac" / "references"
COMPUTATION = REFERENCES / "computations" / "ecco_heat_budget.py"
ATTESTER = REFERENCES / "attesters" / "budget_residual.py"


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
          "pass bar (executor and attester from the installed bundle)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
