# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "earthaccess",
#     "ecco_access",
# ]
# ///
"""Golden for the ocean-budget skill's attested budgets on the native
grid, each run through its sanctioned executor and attester.

The four-term formulation does not live in this file. A computation is a
skill, so it lives in skills/ocean-budget/scripts/ecco_heat_budget.py,
whose contract is knowledge/computations/ecco-heat-budget.md: the
attested computation owns the pass bar (absolute residual, max <= 1e-10
and p99.9 <= 1e-11 degC/s, pointwise on the interior wet cells of one
tile), and the attester
skills/ocean-budget/scripts/budget_residual.py hashes the computation
file, so editing it breaks attestation by construction. The Reynolds
flux decomposition beside it,
skills/ocean-budget/scripts/ecco_flux_decomposition.py under
knowledge/computations/ecco-flux-decomposition.md, is attested by
skills/ocean-budget/scripts/fluxdecomp_check.py the same way.

This script does what the ocean-budget skill's attested runs prescribe:
stage the 2010 fixture cache, run each computation with the arguments
its reference run in verification/reference_runs.yaml records, attest
each receipt, and fail unless every verdict is PASS.

One requirement beyond the cache: the attesters refuse a receipt from a
tree without a RECORD.json stamp, and that stamp is written by the
provider repository's verify tool (tools/science_record_verify.py
--stamp) against the fixture manifest this package now carries at
knowledge/references/retrieval/fixtures-2010-manifest.json. Run it once
after the first fetch. Headless green via
`uv run verification/ocean_budget.py`; `--paths` checks the wiring
offline and stages nothing.
"""

import importlib.util
import sys
from pathlib import Path



# The shared plumbing for the cache goldens sits under fixtures/ so that
# nothing lists it as a golden of its own; it is loaded by path, the way
# every golden here loads fetch_ecco_2010.py.
def _load(name: str):
    path = Path(__file__).resolve().parent / "fixtures" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_attested_chain = _load("attested_chain")
chain, package_root = _attested_chain.chain, _attested_chain.package_root

HERE = Path(__file__).resolve().parent
SCRIPTS = package_root(HERE) / "skills" / "ocean-budget" / "scripts"
YEAR = 2010

# The reference runs `heat-budget` and `flux-decomposition` of
# verification/reference_runs.yaml, verbatim.
STEPS = [
    {"label": "heat-budget",
     "args": ["--year", str(YEAR), "--region", "tile1-interior"],
     "executor": SCRIPTS / "ecco_heat_budget.py",
     "attester": SCRIPTS / "budget_residual.py"},
    {"label": "flux-decomposition",
     "args": ["--region", "southeast-atlantic-upper",
              "--grouping", "full-four-term", "--year", str(YEAR)],
     "executor": SCRIPTS / "ecco_flux_decomposition.py",
     "attester": SCRIPTS / "fluxdecomp_check.py"},
]


if __name__ == "__main__":
    sys.exit(chain("ocean_budget golden", HERE, STEPS))
