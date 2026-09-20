#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Golden for the one sanctioned trend with interval, the method every
other computation of this package embeds beside its own trends.

A computation is a skill, so the three files live together in the ecco
skill: the executor skills/ecco/scripts/ecco_trend_ci.py under the
contract knowledge/computations/ecco-trend-ci.md, the attester
skills/ecco/scripts/trend_ci_check.py, which imports the independent
recompute skills/ecco/scripts/trend_recompute.py, and the Monte Carlo
coverage calibration skills/ecco/scripts/ecco_trend_ci_calibration.py.

Nothing is downloaded and no cache is read. The source series is the
committed steric exhibit under knowledge/references/retrieval, which is
evidence rather than code, so this golden is headless and offline.

Three things are checked, in order:

  1. the reference run `trend-ci` of verification/reference_runs.yaml,
     at the new paths: the executor over the steric exhibit's monthly
     series, scaled to millimeters with no deseasonalization, attested
     PASS by trend_ci_check.py;
  2. every number of that run equal to the committed trend exhibit
     knowledge/references/retrieval/exhibit-trend-steric-2010.json,
     which the same attester also passes;
  3. the calibration's seeded coverage report, whose assertions are its
     own: the honest interval covers inside the stated band where the
     method claims to, and the naive interval collapses where it does
     not.

Exit 0 only when all three hold.

  uv run verification/trend_ci.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parent
SCRIPTS = PACKAGE_ROOT / "skills" / "ecco" / "scripts"
EXECUTOR = SCRIPTS / "ecco_trend_ci.py"
ATTESTER = SCRIPTS / "trend_ci_check.py"
RECOMPUTE = SCRIPTS / "trend_recompute.py"
CALIBRATION = SCRIPTS / "ecco_trend_ci_calibration.py"
RETRIEVAL = PACKAGE_ROOT / "knowledge" / "references" / "retrieval"
SOURCE = RETRIEVAL / "exhibit-steric-2010.json"
EXHIBIT = RETRIEVAL / "exhibit-trend-steric-2010.json"

# The reference run `trend-ci`, verbatim from verification/reference_runs.yaml.
REFERENCE_ARGS = ["--field", "steric_mean_m_by_month", "--value-units", "m",
                  "--scale", "1000", "--report-units", "mm",
                  "--deseasonalize", "none"]
TOLERANCE = 1e-9
NUMBERS = ("trend", "ci_low", "ci_high", "half_width", "naive_half_width",
           "r1", "n_eff", "dof", "se", "t_quantile")


def run(argv):
    return subprocess.run(["uv", "run", *[str(a) for a in argv]],
                          capture_output=True, text=True, cwd=PACKAGE_ROOT)


def last_line(p):
    text = (p.stdout or "").strip() or (p.stderr or "").strip()
    return text.splitlines()[-1] if text else ""


def fail(message: str) -> int:
    print(f"trend_ci golden: {message}")
    return 1


def close(got, want) -> bool:
    if got is None or want is None:
        return got is want
    return abs(float(got) - float(want)) <= TOLERANCE * max(1.0, abs(float(want)))


def main() -> int:
    for p in (EXECUTOR, ATTESTER, RECOMPUTE, CALIBRATION, SOURCE, EXHIBIT):
        if not p.is_file():
            return fail(f"no {p.name} at {p.parent}")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        receipt = work / "trend-ci-receipt.json"
        done = run([EXECUTOR, "--source", SOURCE, *REFERENCE_ARGS,
                    "--receipt", receipt])
        if done.returncode != 0:
            print((done.stdout or "").strip())
            print((done.stderr or "").strip())
            return fail(f"the reference run exited {done.returncode}, not 0")
        verdict = run([ATTESTER, receipt])
        print(last_line(verdict))
        if verdict.returncode != 0 or not (verdict.stdout or "").startswith("PASS"):
            print((verdict.stdout or "").strip())
            return fail("the reference run did not attest PASS")
        got = json.loads(receipt.read_text(encoding="utf-8"))["results"]

    want = json.loads(EXHIBIT.read_text(encoding="utf-8"))["results"]
    for name in NUMBERS:
        if not close(got.get(name), want.get(name)):
            return fail(f"{name} is {got.get(name)}, not the {want.get(name)} "
                        f"{EXHIBIT.name} records; a reference value that moved "
                        "is a finding, not a number to update here")
    if got.get("n") != want.get("n"):
        return fail(f"{got.get('n')} months, not the {want.get('n')} recorded")

    verdict = run([ATTESTER, EXHIBIT])
    print(last_line(verdict))
    if verdict.returncode != 0 or not (verdict.stdout or "").startswith("PASS"):
        print((verdict.stdout or "").strip())
        return fail(f"the committed exhibit {EXHIBIT.name} did not attest PASS")

    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "trend-ci-coverage.json"
        done = run([CALIBRATION, "--out", report])
        print(last_line(done))
        if done.returncode != 0:
            print((done.stdout or "").strip())
            print((done.stderr or "").strip())
            return fail(f"the coverage calibration exited {done.returncode}, not 0")

    print(f"trend_ci golden: the reference run reproduces {EXHIBIT.name} to "
          f"{TOLERANCE:g} relative on every number, both receipts attest PASS "
          "through trend_recompute.py, and the seeded coverage calibration "
          "holds its own assertions (executor, attester and calibration from "
          "the ecco skill)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
