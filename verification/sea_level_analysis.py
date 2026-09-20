#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Golden for the sea-level-analysis skill's attested computations.

A computation is a skill, so each executor and its attester sit together
in skills/sea-level-analysis/scripts:

  regional sea level       ecco_regional_sea_level.py,
  partition                sea_level_partition.py
  regional steric height   ecco_steric_height.py, steric_check.py

Both embed the one sanctioned trend method beside its own skill,
skills/ecco/scripts/ecco_trend_ci.py, and name it by hash in every
interval block; both attesters recompute that block through
skills/ecco/scripts/trend_recompute.py.

The arguments are the reference runs `sea-level` and `steric` of
verification/reference_runs.yaml verbatim. Both read the stamped ECCO
2010 fixture cache, so this golden runs in the cache job; `uv run
verification/sea_level_analysis.py --paths` checks the wiring offline.
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
SCRIPTS = package_root(HERE) / "skills" / "sea-level-analysis" / "scripts"
MONTHS = [f"2010-{m:02d}" for m in range(1, 13)]

STEPS = [
    {"label": "sea-level",
     "args": ["--region", "us-northeast-coast", "--period", "2010-01:2010-12"],
     "executor": SCRIPTS / "ecco_regional_sea_level.py",
     "attester": SCRIPTS / "sea_level_partition.py"},
    {"label": "steric",
     "args": ["--region", "us-northeast-coast", "--months", *MONTHS],
     "executor": SCRIPTS / "ecco_steric_height.py",
     "attester": SCRIPTS / "steric_check.py"},
]

if __name__ == "__main__":
    sys.exit(chain("sea_level_analysis golden", HERE, STEPS))
