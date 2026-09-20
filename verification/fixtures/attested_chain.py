#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Shared plumbing for the goldens that read the ECCO fixture cache.

Not a golden itself: it sits under fixtures/ rather than directly under
verification/, so nothing lists it as a golden to run. Each cache golden
names its steps and calls chain(); the discipline is identical in all of
them, which is the point of keeping it in one file.

A step is one attested run: the sanctioned executor with the arguments
its concept records, then the attester the concept names on the receipt,
with PASS required. Executors and attesters are named by path under
skills/<name>/scripts/, because a computation is a skill.

Every golden built on this also takes --paths, which resolves every
executor and attester it names and exits 0 when they are all there and
nonzero when one is missing. That mode reads no data and touches no
network, so the wiring of a cache golden can be checked offline.
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


def package_root(here: Path) -> Path:
    """The package root, from the verification directory a golden sits in."""
    return here.resolve().parent


def stage(here: Path) -> Path:
    """Populate the 2010 fixture cache and confirm it carries the stamp."""
    fixtures = here.resolve() / "fixtures" / "fetch_ecco_2010.py"
    spec = importlib.util.spec_from_file_location("fetch_ecco_2010", fixtures)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = module.ensure_cache()["root"]
    if not (root / "RECORD.json").exists():
        sys.exit(f"{root} carries no RECORD.json stamp; every attester refuses "
                 "a receipt from an unstamped tree. Stamp it with the provider "
                 "repository's tools/science_record_verify.py against "
                 "knowledge/references/retrieval/fixtures-2010-manifest.json "
                 "and rerun.")
    return root


def last_line(done: subprocess.CompletedProcess) -> str:
    text = (done.stdout or "").strip() or (done.stderr or "").strip()
    return text.splitlines()[-1] if text else ""


def check_paths(name: str, steps) -> int:
    missing = [str(p) for step in steps for p in (step["executor"], step["attester"])
               if not Path(p).is_file()]
    for m in sorted(set(missing)):
        print(f"{name}: no such file: {m}")
    if missing:
        return 1
    print(f"{name}: every executor and attester this golden names resolves "
          f"({len(steps)} attested runs)")
    return 0


def chain(name: str, here: Path, steps, cache: bool = True) -> int:
    """Run every step in order; exit 0 only when all attest PASS."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paths", action="store_true",
                    help="resolve the executors and attesters and stop")
    args = ap.parse_args()
    if args.paths:
        return check_paths(name, steps)

    root = package_root(here)
    data_root = stage(here) if cache else None
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for step in steps:
            receipt = work / f"{step['label']}-receipt.json"
            argv = ["uv", "run", str(step["executor"]), *map(str, step["args"])]
            if data_root is not None and step.get("data_root", True):
                argv += ["--data-root", str(data_root)]
            argv += ["--receipt", str(receipt)]
            done = subprocess.run(argv, capture_output=True, text=True, cwd=root)
            print(last_line(done))
            if done.returncode != 0:
                print((done.stdout or "").strip())
                print((done.stderr or "").strip())
                print(f"{name}: {step['label']} exited {done.returncode}, not 0")
                return 1
            verdict = subprocess.run(
                ["uv", "run", str(step["attester"]), str(receipt),
                 *map(str, step.get("attester_args", []))],
                capture_output=True, text=True, cwd=root)
            print(last_line(verdict))
            if verdict.returncode != 0 or not (verdict.stdout or "").startswith("PASS"):
                print((verdict.stdout or "").strip())
                print(f"{name}: {step['label']} did not attest PASS")
                return 1
    print(f"{name}: {len(steps)} attested runs on the fixture cache, every "
          "receipt PASS (executors and attesters from this package's skills)")
    return 0
