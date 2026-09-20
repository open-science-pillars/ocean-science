#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Golden for the transport-analysis skill's attested computations.

A computation is a skill, so the executors and the attester sit in
skills/transport-analysis/scripts, beside the derivations that built the
basin mask they read:

  section transports       ecco_section_transport.py,
                           section_transport_check.py
  overturning at 26.5N     ecco_amoc_26n.py, attested by
                           skills/compare-obs/scripts/rapid_confrontation_check.py,
                           which the concept names because the
                           confrontation's attester recomputes the
                           overturning receipt it consumes

The section transport arguments are the reference run `section-transport`
of verification/reference_runs.yaml verbatim. The overturning reads the
hashed basin mask committed at
knowledge/references/retrieval/llc90_basin_codes.npz, which
skills/transport-analysis/scripts/llc90_basin_codes.py derived, and the
science record rather than the 2010 fixture cache, so it is not a step
here; the confrontation golden covers it where that record is present.

Runs in the cache job, which stages the fixture cache; `uv run
verification/section_transport.py --paths` checks the wiring offline.
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
ROOT = package_root(HERE)
SCRIPTS = ROOT / "skills" / "transport-analysis" / "scripts"

STEPS = [
    {"label": "section-transport",
     "args": ["--section", "global-26.5n", "--year", "2010"],
     "executor": SCRIPTS / "ecco_section_transport.py",
     "attester": SCRIPTS / "section_transport_check.py"},
]

if __name__ == "__main__":
    sys.exit(chain("section_transport golden", HERE, STEPS))
