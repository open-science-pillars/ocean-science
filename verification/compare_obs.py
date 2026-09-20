#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Golden for the compare-obs skill's attested confrontations: a model
receipt set against an independent observational record.

A computation is a skill, so each executor and its attester sit together
in skills/compare-obs/scripts:

  ECCO overturning         ecco_rapid_amoc_confrontation.py,
  against RAPID at 26.5N   rapid_confrontation_check.py
  ECCO regional sea level  ecco_ssh_vs_altimetry.py,
  against NASA-SSH         altimetry_confrontation_check.py

Each reads a model receipt and a stamped observational tree. The model
side of the overturning is skills/transport-analysis/scripts/ecco_amoc_26n.py
over the ECCO science record; the model side of the altimetry
confrontation is skills/sea-level-analysis/scripts/ecco_regional_sea_level.py.
Neither observational tree is committed here: this package carries their
manifests under knowledge/references/retrieval (rapid-26n-manifest.json
and nasa-ssh-manifest.json) and a reader stages the tree against one,
which is why this golden is manual rather than part of either job.

  uv run verification/compare_obs.py --paths
      resolve every executor, attester, manifest and committed exhibit
      this golden names, and stop. Offline, stages nothing.

  ECCO_V4R4_RECORD=DIR RAPID_26N_ROOT=DIR NASA_SSH_ROOT=DIR \
      uv run verification/compare_obs.py
      the confrontations end to end: the model run, then the
      confrontation, then the attester, PASS required at each step.

Without the three directories the golden says which is missing and exits
nonzero rather than pretending.
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
COMPARE = ROOT / "skills" / "compare-obs" / "scripts"
TRANSPORT = ROOT / "skills" / "transport-analysis" / "scripts"
SEA_LEVEL = ROOT / "skills" / "sea-level-analysis" / "scripts"
RETRIEVAL = ROOT / "knowledge" / "references" / "retrieval"

OVERTURNING = TRANSPORT / "ecco_amoc_26n.py"
PARTITION = SEA_LEVEL / "ecco_regional_sea_level.py"
RAPID_CONFRONTATION = COMPARE / "ecco_rapid_amoc_confrontation.py"
RAPID_CHECK = COMPARE / "rapid_confrontation_check.py"
ALTIMETRY_CONFRONTATION = COMPARE / "ecco_ssh_vs_altimetry.py"
ALTIMETRY_CHECK = COMPARE / "altimetry_confrontation_check.py"

NAMED = (OVERTURNING, PARTITION, RAPID_CONFRONTATION, RAPID_CHECK,
         ALTIMETRY_CONFRONTATION, ALTIMETRY_CHECK,
         RETRIEVAL / "rapid-26n-manifest.json",
         RETRIEVAL / "nasa-ssh-manifest.json",
         RETRIEVAL / "exhibit-amoc-26n-record.json",
         RETRIEVAL / "exhibit-rapid-amoc-26n-confrontation.json",
         RETRIEVAL / "exhibit-ssh-vs-altimetry-record.json")

TREES = (("ECCO_V4R4_RECORD", "the ECCO science record, 1992 to 2017"),
         ("RAPID_26N_ROOT", "the stamped RAPID v2024.1a tree, rapid-26n-manifest.json"),
         ("NASA_SSH_ROOT", "the stamped NASA-SSH V1.1 tree, nasa-ssh-manifest.json"))


def fail(message: str) -> int:
    print(f"compare_obs golden: {message}")
    return 1


def last_line(done) -> str:
    text = (done.stdout or "").strip() or (done.stderr or "").strip()
    return text.splitlines()[-1] if text else ""


def run(argv):
    return subprocess.run(["uv", "run", *[str(a) for a in argv]],
                          capture_output=True, text=True, cwd=ROOT)


def step(argv, label):
    done = run(argv)
    print(last_line(done))
    if done.returncode != 0:
        print((done.stdout or "").strip())
        print((done.stderr or "").strip())
        return fail(f"{label} exited {done.returncode}, not 0")
    return 0


def attest(argv, label):
    done = run(argv)
    print(last_line(done))
    if done.returncode != 0 or not (done.stdout or "").startswith("PASS"):
        print((done.stdout or "").strip())
        return fail(f"{label} did not attest PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paths", action="store_true",
                    help="resolve everything this golden names and stop")
    args = ap.parse_args()

    missing = [str(p) for p in NAMED if not p.is_file()]
    for m in missing:
        print(f"compare_obs golden: no such file: {m}")
    if missing:
        return 1
    if args.paths:
        print("compare_obs golden: every executor, attester, manifest and "
              f"committed exhibit this golden names resolves ({len(NAMED)} files)")
        return 0

    trees = {}
    absent = []
    for name, what in TREES:
        value = os.environ.get(name)
        if not value or not Path(value).expanduser().is_dir():
            absent.append(f"{name} ({what})")
        else:
            trees[name] = Path(value).expanduser().resolve()
    if absent:
        return fail("no stamped tree at " + "; ".join(absent) +
                    ". This golden runs where those trees are staged; "
                    "--paths checks the wiring without them.")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        amoc = work / "amoc-receipt.json"
        if step([OVERTURNING, "--period", "2004-04:2017-12", "--scope", "atlantic",
                 "--data-root", trees["ECCO_V4R4_RECORD"], "--receipt", amoc],
                "the overturning model run"):
            return 1
        rapid = work / "rapid-confrontation-receipt.json"
        if step([RAPID_CONFRONTATION, "--ecco-receipt", amoc,
                 "--rapid-root", trees["RAPID_26N_ROOT"], "--receipt", rapid],
                "the RAPID confrontation"):
            return 1
        if attest([RAPID_CHECK, rapid, "--model-receipt", amoc],
                  "the RAPID confrontation"):
            return 1

        partition = work / "sea-level-receipt.json"
        if step([PARTITION, "--region", "us-northeast-coast",
                 "--period", "2010-01:2010-12",
                 "--data-root", trees["ECCO_V4R4_RECORD"], "--receipt", partition],
                "the sea level partition model run"):
            return 1
        altimetry = work / "altimetry-confrontation-receipt.json"
        if step([ALTIMETRY_CONFRONTATION, "--partition-receipt", partition,
                 "--obs-root", trees["NASA_SSH_ROOT"], "--receipt", altimetry],
                "the altimetry confrontation"):
            return 1
        if attest([ALTIMETRY_CHECK, altimetry, "--model-receipt", partition],
                  "the altimetry confrontation"):
            return 1

    print("compare_obs golden: both confrontations run from a model receipt "
          "of this package against their stamped observational trees and "
          "attest PASS (executors and attesters from the compare-obs skill)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
