#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Golden for the regional budgets over a control volume: one sanctioned
executor under three contracts.

A computation is a skill, so the executor
skills/ocean-budget/scripts/ecco_regional_budget.py and its attester
skills/ocean-budget/scripts/regional_budget_check.py live in the
ocean-budget skill, and the three concepts they answer to are
knowledge/computations/ecco-regional-heat-budget.md, its salt variant
and its volume variant.

Running the executor needs the ECCO fixture cache, which the
cache-goldens job stages; this golden proves the attester instead, on
the committed receipts the concepts cite as their measured
demonstrations, which are evidence under
knowledge/references/retrieval rather than code. It is therefore
headless and offline with nothing downloaded.

Three things are checked, for each of the heat and salt exhibits:

  1. the attester passes the committed receipt, so the receipt was
     produced by the executor at its present digest and every bar,
     mutation and mask disclosure the concept demands recomputes;
  2. the receipt's bound parameters are the ones the concept records
     for that demonstration;
  3. two doctored copies FAIL: one whose headline residual is raised
     past the attested absolute bar, and one whose code hash is edited,
     so neither the pass bar nor the sanctioned identity is taken on the
     receipt's word.

Exit 0 only when all three hold for both.

  uv run verification/regional_budget.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parent
SCRIPTS = PACKAGE_ROOT / "skills" / "ocean-budget" / "scripts"
EXECUTOR = SCRIPTS / "ecco_regional_budget.py"
ATTESTER = SCRIPTS / "regional_budget_check.py"
RETRIEVAL = PACKAGE_ROOT / "knowledge" / "references" / "retrieval"

# The committed demonstrations, with the parameters the concepts record.
EXHIBITS = (
    ("exhibit-regional-heat-2005.json", "heat", "southeast-atlantic-upper", 2005),
    ("exhibit-regional-salt-2005.json", "salt", "southeast-atlantic-upper", 2005),
)


def run(argv):
    return subprocess.run(["uv", "run", *[str(a) for a in argv]],
                          capture_output=True, text=True, cwd=PACKAGE_ROOT)


def last_line(p):
    text = (p.stdout or "").strip() or (p.stderr or "").strip()
    return text.splitlines()[-1] if text else ""


def fail(message: str) -> int:
    print(f"regional_budget golden: {message}")
    return 1


def over_the_bar(doc):
    """Raise the headline absolute residual to one degree per second, far
    past any bar the concept states."""
    doc["results"]["residual_per_volume_max"] = 1.0


def wrong_code(doc):
    """Edit the receipt's claim about which file produced it."""
    doc["code_sha256"] = "0" * 64


def main() -> int:
    for p in (EXECUTOR, ATTESTER):
        if not p.is_file():
            return fail(f"no {p.name} at {p.parent}")

    for name, budget, region, year in EXHIBITS:
        exhibit = RETRIEVAL / name
        if not exhibit.is_file():
            return fail(f"no committed receipt at {exhibit}")
        verdict = run([ATTESTER, exhibit])
        print(last_line(verdict))
        if verdict.returncode != 0 or not (verdict.stdout or "").startswith("PASS"):
            print((verdict.stdout or "").strip())
            return fail(f"{name} did not attest PASS")

        receipt = json.loads(exhibit.read_text(encoding="utf-8"))
        bound = receipt.get("bound_parameters") or {}
        if bound.get("budget") != budget:
            return fail(f"{name} is the {bound.get('budget')} budget, not {budget}")
        if bound.get("region") != region:
            return fail(f"{name} names region {bound.get('region')}, not {region}")
        if int(bound.get("year", 0)) != year:
            return fail(f"{name} names year {bound.get('year')}, not {year}")

        for label, doctor in (("residual past the bar", over_the_bar),
                              ("edited code hash", wrong_code)):
            with tempfile.TemporaryDirectory() as tmp:
                bent = Path(tmp) / name
                doc = json.loads(exhibit.read_text(encoding="utf-8"))
                doctor(doc)
                bent.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
                verdict = run([ATTESTER, bent])
                if verdict.returncode == 0:
                    print((verdict.stdout or "").strip())
                    return fail(f"{name} with a {label} still attested; the "
                                "attester is taking the receipt at its word")

    print("regional_budget golden: the committed heat and salt demonstrations "
          "attest PASS at the executor's present digest under the parameters "
          "their concepts record, and a receipt whose residual is raised past "
          "the bar or whose code hash is edited FAILS (executor and attester "
          "from the ocean-budget skill)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
