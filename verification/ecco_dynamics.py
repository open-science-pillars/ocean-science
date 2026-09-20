#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Golden for the ecco skill's attested computations of the state
estimate's own dynamics and its global heat content.

A computation is a skill, so each executor and its attester sit together
in skills/ecco/scripts, and the concept each answers to is under
knowledge/computations:

  geostrophic balance      ecco_geostrophy.py, geos_check.py
  wind-stress curl         ecco_curl_ekman.py, curl_check.py
  thermal-wind             ecco_thermal_wind_reconstruction.py,
                           thermal_wind_check.py
  global ocean heat        ecco_ohc.py, ohc_check.py

The arguments are the reference runs of verification/reference_runs.yaml
verbatim (geostrophy, curl-ekman, thermal-wind and ohc). Each executor
reads the stamped ECCO 2010 fixture cache, so this golden runs in the
cache job, which stages it; `uv run verification/ecco_dynamics.py
--paths` checks the wiring offline and stages nothing.
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
SCRIPTS = package_root(HERE) / "skills" / "ecco" / "scripts"

STEPS = [
    {"label": "geostrophy", "args": ["--month", "2009-12"],
     "executor": SCRIPTS / "ecco_geostrophy.py", "attester": SCRIPTS / "geos_check.py"},
    {"label": "curl-ekman", "args": ["--month", "2009-12"],
     "executor": SCRIPTS / "ecco_curl_ekman.py", "attester": SCRIPTS / "curl_check.py"},
    {"label": "thermal-wind", "args": ["--month", "2009-12"],
     "executor": SCRIPTS / "ecco_thermal_wind_reconstruction.py",
     "attester": SCRIPTS / "thermal_wind_check.py"},
    {"label": "ohc", "args": ["--months", "2010-01", "2010-12"],
     "executor": SCRIPTS / "ecco_ohc.py", "attester": SCRIPTS / "ohc_check.py"},
]

if __name__ == "__main__":
    sys.exit(chain("ecco_dynamics golden", HERE, STEPS))
