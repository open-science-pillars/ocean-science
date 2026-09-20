#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Golden and qualification wrapper for the attested sea level budget closure:
the sanctioned executor and attester of this package, run on their
synthetic fixture and on the committed data root, so the chain is
proven headless with no data download and no NASA host reachable.

The computation is a skill: the executor is
skills/sea-level-budget/scripts/sea_level_budget.py, under the contract
knowledge/computations/sea-level-budget.md, and the attester is
skills/sea-level-budget/scripts/sea_level_budget_check.py beside it.
The stamped three-term data root is committed at
knowledge/references/retrieval/sea-level-budget-root and the stamp is
checked by skills/sea-level-budget/scripts/slb_data_root.py. Nothing
scientific is reimplemented here.

This golden carries the two chains the provider repository ran in
tools/run_checks.sh before ADR E moved the computation here
(sea_level_budget_chain and sea_level_budget_record) and the two named
reference runs of verification/reference_runs.yaml, sea-level-budget
and sea-level-budget-record.

Three modes:

  (no flags)                 the golden: the attester's selftest; the
                             fixture computation for 2005-01:2016-12 into
                             a temporary receipt, attested (PASS
                             required); the gap-crossing case
                             2016-01:2019-12 with no bridge, which must
                             exit 3 and attest as a refusal; the
                             committed data root's stamp check; and the
                             record run over 2005-01:2016-12 on that
                             root, attested. Exit 0 only when all hold.
  --runtime NAME --out R     the prove step: run the fixture computation
                             and write the receipt at R, the capability
                             block and the bundle block both naming this
                             package (ocean-science), which is where the
                             executor now ships.
  --attest R --out A         run the attester on receipt R and
                             write the attestation at A: a top-level
                             verdict PASS or FAIL, the refusal flag, and
                             the capability, bundle and runtime blocks
                             copied from the receipt (the shape core's
                             trend_attester.py writes). Exit 0 on PASS.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parent
PERIOD = "2005-01:2016-12"
REFUSAL_PERIOD = "2016-01:2019-12"
SEED = 7
SKILL = PACKAGE_ROOT / "skills" / "sea-level-budget" / "scripts"
COMPUTATION = SKILL / "sea_level_budget.py"
ATTESTER = SKILL / "sea_level_budget_check.py"
DATA_ROOT_TOOL = SKILL / "slb_data_root.py"
DATA_ROOT = PACKAGE_ROOT / "knowledge" / "references" / "retrieval" / "sea-level-budget-root"


def package_paths():
    for p in (COMPUTATION, ATTESTER, DATA_ROOT_TOOL):
        if not p.is_file():
            sys.exit(f"this package carries no {p.name} at {p.parent}; the "
                     "sea level budget closure is the sea-level-budget skill")
    if not (DATA_ROOT / "RECORD.json").is_file():
        sys.exit(f"no stamped data root at {DATA_ROOT}")
    return COMPUTATION, ATTESTER


def run_computation(computation: Path, period: str, receipt: Path, runtime: str,
                    runtime_version=None, bridge=None, data_root=None) -> subprocess.CompletedProcess:
    source = (["--data-root", str(data_root)] if data_root
              else ["--fixture", "--seed", str(SEED)])
    cmd = ["uv", "run", str(computation), *source,
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
        selftest = subprocess.run(["uv", "run", str(attester), "--selftest"],
                                  capture_output=True, text=True)
        print(last_line(selftest))
        if selftest.returncode != 0:
            print(selftest.stdout.strip())
            print("sea_level_budget golden: the attester's selftest FAILED")
            return 1
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

        # The real-data anchor: the stamped three-term root committed under
        # knowledge/references/retrieval, its stamp checked, run for the
        # reference period and attested, so the anchor the concept quotes
        # is recomputed on every change.
        stamp = subprocess.run(["uv", "run", str(DATA_ROOT_TOOL),
                                "--root", str(DATA_ROOT), "--check"],
                               capture_output=True, text=True)
        print(last_line(stamp))
        if stamp.returncode != 0:
            print(stamp.stdout.strip())
            print("sea_level_budget golden: the committed data root did not check")
            return 1
        record, rec_att = work / "record.json", work / "record-attestation.json"
        run = run_computation(computation, PERIOD, record, "golden", data_root=DATA_ROOT)
        print(last_line(run))
        if run.returncode != 0:
            print(run.stderr.strip())
            print("sea_level_budget golden: the record run FAILED")
            return 1
        verdict = run_attester(attester, record, rec_att)
        print(last_line(verdict))
        att = json.loads(rec_att.read_text(encoding="utf-8")) if rec_att.is_file() else {}
        if verdict.returncode != 0 or att.get("verdict") != "PASS" or att.get("refusal") is not False:
            print(verdict.stdout.strip())
            print("sea_level_budget golden: the record attestation FAILED")
            return 1
    print(f"sea_level_budget golden: the fixture budget {PERIOD} closes within its "
          f"uncertainty and attests PASS; the gap-crossing period {REFUSAL_PERIOD} "
          "refuses without a bridge and attests as a refusal; the committed data "
          f"root checks and its record run over {PERIOD} attests PASS (executor and "
          "attester from this package)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runtime", default=None, help="the prove step: the runtime that ran this")
    ap.add_argument("--runtime-version", default=None)
    ap.add_argument("--attest", type=Path, default=None, help="a receipt to attest")
    ap.add_argument("--out", type=Path, default=None, help="where the receipt or the attestation goes")
    args = ap.parse_args()
    computation, attester = package_paths()

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
