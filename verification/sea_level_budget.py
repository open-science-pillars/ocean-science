#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Golden and PROVE wrapper for the attested sea level budget closure:
the sanctioned executor and attester in the PO.DAAC bundle, run on the
bundle's synthetic fixture, so the chain is proven headless with no
data download and no NASA host reachable.

The computation lives in the provider bundle,
knowledge/podaac/references/computations/sea_level_budget.py, under
the contract knowledge/podaac/computations/sea-level-budget.md; the
attester is knowledge/podaac/references/attesters/sea_level_budget_check.py.
Nothing scientific is reimplemented here. The bundle root is resolved
the way ocean_budget.py resolves it: NASA_DAAC_KNOWLEDGE names a
checkout of the provider repository, else the installer's record
(`claude plugin list --json`, the entry's installPath) names the
installed plugin.

Three modes:

  (no flags)                 the golden: run the fixture computation for
                             2005-01:2016-12 into a temporary receipt,
                             attest it (PASS required); then run the
                             gap-crossing case 2016-01:2019-12 with no
                             bridge and require exit 3 and an attestation
                             that passes it as a refusal. Exit 0 only when
                             both hold.
  --runtime NAME --out R     the PROVE step: run the fixture computation
                             and write the receipt at R, the capability
                             block naming this package (ocean-science)
                             and the bundle block naming the provider
                             bundle.
  --attest R --out A         run the bundle attester on receipt R and
                             write the attestation at A: a top-level
                             verdict PASS or FAIL, the refusal flag, and
                             the capability, bundle and runtime blocks
                             copied from the receipt (the shape core's
                             trend_attester.py writes). Exit 0 on PASS.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parent
PROVIDER_PLUGIN = "nasa-daac-knowledge"
PERIOD = "2005-01:2016-12"
REFUSAL_PERIOD = "2016-01:2019-12"
SEED = 7


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


def bundle_paths():
    refs = provider_root() / "knowledge" / "podaac" / "references"
    computation = refs / "computations" / "sea_level_budget.py"
    attester = refs / "attesters" / "sea_level_budget_check.py"
    for p in (computation, attester):
        if not p.is_file():
            sys.exit(f"the provider bundle carries no {p.name} at {p.parent}; "
                     "the sea level budget closure needs nasa-daac-knowledge "
                     "at a release that ships it")
    return computation, attester


def run_computation(computation: Path, period: str, receipt: Path, runtime: str,
                    runtime_version=None, bridge=None) -> subprocess.CompletedProcess:
    cmd = ["uv", "run", str(computation), "--fixture", "--seed", str(SEED),
           "--period", period, "--runtime", runtime,
           "--capability-root", str(PACKAGE_ROOT), "--receipt", str(receipt)]
    if runtime_version:
        cmd += ["--runtime-version", runtime_version]
    if bridge:
        cmd += ["--bridge", bridge]
    return subprocess.run(cmd, capture_output=True, text=True)


def run_attester(attester: Path, receipt: Path, out: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["uv", "run", str(attester), str(receipt), "--out", str(out)],
                          capture_output=True, text=True)


def last_line(p: subprocess.CompletedProcess) -> str:
    text = (p.stdout or "").strip() or (p.stderr or "").strip()
    return text.splitlines()[-1] if text else ""


def golden(computation: Path, attester: Path) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        receipt, attestation = work / "receipt.json", work / "attestation.json"
        run = run_computation(computation, PERIOD, receipt, "golden")
        print(last_line(run))
        if run.returncode != 0:
            print(run.stderr.strip())
            print("sea_level_budget golden: the sanctioned computation FAILED")
            return 1
        verdict = run_attester(attester, receipt, attestation)
        print(last_line(verdict))
        att = json.loads(attestation.read_text(encoding="utf-8")) if attestation.is_file() else {}
        if verdict.returncode != 0 or att.get("verdict") != "PASS" or att.get("refusal") is not False:
            print(verdict.stdout.strip())
            print("sea_level_budget golden: attestation FAILED")
            return 1

        refusal, r_att = work / "refusal.json", work / "refusal-attestation.json"
        run = run_computation(computation, REFUSAL_PERIOD, refusal, "golden")
        print(last_line(run))
        if run.returncode != 3:
            print(f"sea_level_budget golden: the gap-crossing period {REFUSAL_PERIOD} with no "
                  f"bridge exited {run.returncode}, not 3; a number where a refusal was due")
            return 1
        verdict = run_attester(attester, refusal, r_att)
        print(last_line(verdict))
        att = json.loads(r_att.read_text(encoding="utf-8")) if r_att.is_file() else {}
        if (verdict.returncode != 0 or att.get("verdict") != "PASS" or att.get("refusal") is not True
                or "refusal" not in (verdict.stdout or "")):
            print(verdict.stdout.strip())
            print("sea_level_budget golden: the refusal did not attest as a refusal")
            return 1
    print(f"sea_level_budget golden: the fixture budget {PERIOD} closes within its "
          f"uncertainty and attests PASS; the gap-crossing period {REFUSAL_PERIOD} "
          "refuses without a bridge and attests as a refusal (executor and attester "
          "from the installed bundle)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runtime", default=None, help="PROVE: the runtime that ran this")
    ap.add_argument("--runtime-version", default=None)
    ap.add_argument("--attest", type=Path, default=None, help="a receipt to attest")
    ap.add_argument("--out", type=Path, default=None, help="where the receipt or the attestation goes")
    args = ap.parse_args()
    computation, attester = bundle_paths()

    if args.attest:
        if not args.out:
            ap.error("--attest needs --out ATTESTATION")
        verdict = run_attester(attester, args.attest, args.out)
        print((verdict.stdout or "").strip())
        if verdict.stderr.strip():
            print(verdict.stderr.strip(), file=sys.stderr)
        return 0 if verdict.returncode == 0 and args.out.is_file() else 1
    if args.runtime:
        if not args.out:
            ap.error("--runtime needs --out RECEIPT")
        run = run_computation(computation, PERIOD, args.out, args.runtime, args.runtime_version)
        print((run.stdout or "").strip())
        if run.stderr.strip():
            print(run.stderr.strip(), file=sys.stderr)
        return run.returncode
    return golden(computation, attester)


if __name__ == "__main__":
    sys.exit(main())
