#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Golden for the sweep skill: a fixture sweep over the sea level budget
executor's declared period, tabled from receipts the computation's own
attester passed, checked against the expectations committed beside this
file.

The sweep runs the sanctioned executor of this package
(skills/sea-level-budget/scripts/sea_level_budget.py, under the contract
knowledge/computations/sea-level-budget.md) once per window, attests
every receipt with skills/sea-level-budget/scripts/sea_level_budget_check.py
and writes the table. Nothing scientific is reimplemented here and
nothing is downloaded: the executor's synthetic fixture is generated at
run time from the seed the expectations file names, so this golden is
headless and offline with no NASA host reachable. The sweep script
resolves the three paths from CLAUDE_PLUGIN_ROOT where the runtime sets
it, else from the tree it sits in.

Three things are checked, in order:

  1. the sweep script's own selftest, which exercises every refusal it
     enforces on the fixture;
  2. the fixture sweep: every row attested, every refused row carrying
     its reason code and no number, and every cell equal to the cell
     recorded in verification/fixtures/sweep-sea-level-budget-fixture.json
     (a field of a receipt, measured when that file was written);
  3. the aggregate a reader asks for first, the overall trend across the
     rows, refused with its reason code rather than computed.

Exit 0 only when all three hold.

  uv run verification/sweep.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parent
SCRIPT = PACKAGE_ROOT / "skills" / "sweep" / "scripts" / "sweep.py"
EXPECTATIONS = HERE / "fixtures" / "sweep-sea-level-budget-fixture.json"
TOLERANCE = 1e-9


def run(args, work=None):
    return subprocess.run(["uv", "run", str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=PACKAGE_ROOT)


def same(got, want) -> bool:
    if isinstance(want, float) or isinstance(got, float):
        if got is None or want is None:
            return got is want
        return abs(float(got) - float(want)) <= TOLERANCE * max(1.0, abs(float(want)))
    return got == want


def fail(message: str) -> int:
    print(f"sweep golden: {message}")
    return 1


def main() -> int:
    if not SCRIPT.is_file():
        return fail(f"no sweep script at {SCRIPT}")
    expect = json.loads(EXPECTATIONS.read_text(encoding="utf-8"))
    spec, counts = expect["sweep"], expect["expect"]

    selftest = run(["--selftest"])
    print((selftest.stdout or "").strip() or (selftest.stderr or "").strip())
    if selftest.returncode != 0 or "sweep selftest: ok" not in selftest.stdout:
        print((selftest.stderr or "").strip())
        return fail("the sweep script's selftest FAILED")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        common = ["--computation", spec["computation"],
                  "--parameter", spec["parameter"],
                  "--windows", spec["windows"], "--span", spec["span"],
                  *[f"--fixed={name}={value}" for name, value in spec["fixed"].items()],
                  "--input", "fixture", "--seed", str(spec["input"]["seed"]),
                  "--runtime", "golden", "--capability-root", str(PACKAGE_ROOT)]
        done = run([*common, "--out-dir", str(work / "table")])
        if done.returncode != 0:
            print((done.stdout or "").strip())
            print((done.stderr or "").strip())
            return fail(f"the fixture sweep exited {done.returncode}; every row "
                        "of this sweep attests, so anything but 0 is a finding")
        doc = json.loads((work / "table" / "sweep.json").read_text(encoding="utf-8"))

        if doc["code_sha256"] != spec["code_sha256"]:
            return fail(f"the executor in the installed bundle is "
                        f"{doc['code_sha256']}, not the {spec['code_sha256']} "
                        "these expectations were measured with; the table is a "
                        "different method, so re-measure "
                        f"{EXPECTATIONS.relative_to(PACKAGE_ROOT)} and record "
                        "the new digest rather than loosening this check")
        if doc["input"]["digest"] != spec["input"]["digest"]:
            return fail("the regenerated fixture does not hash to the digest "
                        "the expectations were measured on")
        got_columns = [column["name"] for column in doc["columns"]]
        want_columns = [column["name"] for column in expect["columns"]]
        if got_columns != want_columns:
            return fail(f"the columns are {got_columns}, not {want_columns}")

        rows = doc["rows"]
        if len(rows) != counts["rows"]:
            return fail(f"{len(rows)} rows, not the {counts['rows']} the "
                        "expectations record")
        for got, want in zip(rows, expect["rows"]):
            where = f"{spec['parameter']} {want['period']}"
            if got["value"] != want["period"]:
                return fail(f"row {rows.index(got)} is {got['value']}, not "
                            f"{want['period']}")
            if not got["attested"]:
                return fail(f"the receipt at {where} did not attest: "
                            f"{got['attestation']}")
            if got["status"] != want["status"]:
                return fail(f"{where} is {got['status']}, not {want['status']}")
            if got["reason_code"] != want["reason_code"]:
                return fail(f"{where} refused with {got['reason_code']}, not "
                            f"{want['reason_code']}")
            if not got["run_id"]:
                return fail(f"{where} carries no run id to follow back")
            if got["status"] == "refused":
                numbers = [name for name, cell in got["cells"].items()
                           if isinstance(cell, (int, float)) and not isinstance(cell, bool)]
                if numbers:
                    return fail(f"the refused row {where} carries numbers "
                                f"({', '.join(numbers)}); a refusal is never a number")
            for name in want_columns:
                if not same(got["cells"].get(name), want["cells"].get(name)):
                    return fail(f"{where}, column {name}: "
                                f"{got['cells'].get(name)} is not the recorded "
                                f"{want['cells'].get(name)}")
        computed = sum(1 for row in rows if row["status"] == "computed")
        refused = sum(1 for row in rows if row["status"] == "refused")
        if (computed, refused) != (counts["computed"], counts["refused"]):
            return fail(f"{computed} computed and {refused} refused rows, not "
                        f"the {counts['computed']} and {counts['refused']} "
                        "the expectations record")

        aggregate = run([*common, "--out-dir", str(work / "aggregate"),
                         "--aggregate", "the overall sea level trend across the windows"])
        line = (aggregate.stdout or "").strip()
        print(line.splitlines()[0] if line else "")
        if aggregate.returncode != 4 or counts["aggregate_refusal_code"] not in line:
            return fail("the sweep did not refuse the aggregate across its "
                        f"rows (exit {aggregate.returncode}); that number is "
                        "one no concept owns")
        if (work / "aggregate" / "sweep.csv").is_file():
            return fail("the refused aggregate still wrote a table; a refusal "
                        "leaves no partial output")

    print(f"sweep golden: {len(rows)} rows over {spec['parameter']} on the "
          f"fixture at seed {spec['input']['seed']}, {computed} computed and "
          f"{refused} refused by the executor, every receipt attested and every "
          f"cell equal to {EXPECTATIONS.relative_to(PACKAGE_ROOT)}; the "
          "aggregate across the rows is refused "
          f"({counts['aggregate_refusal_code']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
