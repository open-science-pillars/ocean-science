#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Sweep one declared parameter of an attested computation and table the
receipts, computing nothing.

The concept of a computation states its boundaries in prose, often from
a handful of runs someone made by hand ("the closure is window
dependent"). This script turns that sentence into a measured table: it
runs the sanctioned executor once per value of one parameter the
concept declares, runs the attester on every receipt BEFORE reading a
field out of it, and writes the executor's own headline fields as a
CSV, a markdown table and a JSON manifest that names every receipt with
the attester's verdict line, so a reader can follow any cell back to a
receipt that passed.

Every cell of the table is a field of one receipt, read by the path the
catalog below records. The script fits nothing, averages nothing and
carries no expected value of its own. A run the executor refused is a
row carrying its reason code, never a skipped row, because a refusal is
part of the measurement. A receipt the attester did not pass is a
failed row carrying the attester's own line, and no number from that
receipt is copied into the table.

What it refuses, each with exit 4 and a reason code, and never a
partial table:

  aggregate-across-rows   any aggregate over the rows (--aggregate):
                          a mean, an overall rate, a count of closures
                          read as a rate. Those are numbers no concept
                          owns. A capability that computes a number of
                          its own is domain expansion under ADR D of
                          the marketplace decisions and waits on the
                          ablation; a sweep is a wrap, so it stops here
                          and says which single receipt a reader may
                          quote instead.
  parameter-not-declared  a parameter the concept does not declare
                          (the declared set is read from the concept's
                          Parameters in its frontmatter, not from a
                          list kept here).
  parameter-not-stated    a declared parameter that the command line
                          neither sweeps nor fixes: every run states
                          the swept parameter, its values and the fixed
                          value of every other parameter.
  mixed-method            two receipts in one sweep whose executor
                          digest (code_sha256) differs, so the table
                          would be two methods.
  mixed-input             two receipts in one sweep whose input
                          identity differs (the data root's record and
                          manifest digest, or the fixture's seed,
                          offset and digest), so the table would be two
                          roots.

The executor, the attester and the concept are reached at the installed
provider bundle's path, the way the wrapping skill reaches them: the
installer's record (`claude plugin list --json`), or a checkout named
by NASA_DAAC_KNOWLEDGE. Nothing is copied here.

Usage:
  sweep.py --computation sea-level-budget --parameter period \
      --values 2005-01:2009-12,2010-01:2014-12 --fixed bridge=unbound \
      --input fixture --seed 7 --runtime claude-code --out-dir DIR

  sweep.py --computation sea-level-budget --parameter period \
      --windows 60:12 --span 2005-01:2026-07 --fixed bridge=unbound \
      --input data-root --data-root DIR --runtime claude-code --out-dir DIR

  sweep.py --selftest
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROVIDER_PLUGIN = "nasa-daac-knowledge"
BUNDLE = "podaac"

# One entry per computation this sweep can drive. The columns are the
# receipt fields the concept's Reference run section names, each a
# dotted path into the receipt: the table is those fields and nothing
# else. Adding a computation here adds no number; it names paths.
CATALOG = {
    "sea-level-budget": {
        "concept": "computations/sea-level-budget.md",
        "executor": "references/computations/sea_level_budget.py",
        "attester": "references/attesters/sea_level_budget_check.py",
        "skill": "ocean-science/sea-level-budget",
        "columns": [
            ("period", "bound_parameters.period"),
            ("bridge", "bound_parameters.bridge"),
            ("months_used", "months.n_used"),
            ("months_calendar", "months.n_calendar"),
            ("trend_altimetry_mm_yr", "trend_altimetry_mm_yr"),
            ("trend_mass_mm_yr", "trend_mass_mm_yr"),
            ("trend_steric_mm_yr", "trend_steric_mm_yr"),
            ("trend_residual_mm_yr", "trend_residual_mm_yr"),
            ("residual_ci_low_mm_yr", "trends.residual.ci_low"),
            ("residual_ci_high_mm_yr", "trends.residual.ci_high"),
            ("closure_gap_mm_yr", "verdict.closure_gap_mm_yr"),
            ("bar_mm_yr", "verdict.bar_mm_yr"),
            ("closed_within_uncertainty", "verdict.closed_within_uncertainty"),
        ],
    },
}

# Columns the sweep owns rather than the receipt: the bookkeeping that
# says whether a cell may be read at all.
STATUS_COLUMNS = ("status", "run_id", "reason_code")
UNBOUND = "unbound"
REFUSALS = ("aggregate-across-rows", "parameter-not-declared",
            "parameter-not-stated", "mixed-method", "mixed-input")


# ---- refusing

def refuse(code: str, message: str) -> int:
    print(f"SWEEP REFUSED ({code}): {message}")
    return 4


# ---- the installed bundle

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


def bundle_paths(computation: str):
    """The concept, the executor and the attester at the installed
    bundle's path; nothing is copied into this repository."""
    spec = CATALOG[computation]
    base = provider_root() / "knowledge" / BUNDLE
    paths = {k: base / spec[k] for k in ("concept", "executor", "attester")}
    for name, p in paths.items():
        if not p.is_file():
            sys.exit(f"the provider bundle carries no {name} for {computation} "
                     f"at {p}; the sweep needs {PROVIDER_PLUGIN} at a release "
                     "that ships it")
    return paths


def declared_parameters(concept: Path):
    """The parameter names the concept declares, read from its
    frontmatter's Parameters block rather than kept in a list here."""
    text = concept.read_text(encoding="utf-8")
    if not text.startswith("---"):
        sys.exit(f"{concept} carries no frontmatter to read parameters from")
    front = text.split("---", 2)[1]
    names, inside = [], False
    for line in front.splitlines():
        if re.match(r"^parameters:\s*$", line):
            inside = True
            continue
        if inside:
            if not line.startswith((" ", "\t")) and line.strip():
                break
            found = re.search(r"\bname:\s*['\"]?([A-Za-z0-9_-]+)", line)
            if found:
                names.append(found.group(1))
    if not names:
        sys.exit(f"{concept} declares no parameters; a sweep needs one to sweep")
    return names


# ---- the values swept

def month_index(label: str) -> int:
    y, m = label.split("-")
    return int(y) * 12 + int(m) - 1


def month_label(index: int) -> str:
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def windows(span: str, length: int, step: int):
    """Every window of `length` months stepping `step` months through
    `span`. Calendar arithmetic on the stated rule, so the values are
    explicit in the manifest and in every row; no science number is
    formed here."""
    first, last = span.split(":")
    out, start = [], month_index(first)
    while start + length - 1 <= month_index(last):
        out.append(f"{month_label(start)}:{month_label(start + length - 1)}")
        start += step
    if not out:
        sys.exit(f"no window of {length} months fits in {span}")
    return out


# ---- running, attesting, reading

def run_executor(executor: Path, parameter: str, value: str, fixed: dict,
                 args, receipt: Path) -> subprocess.CompletedProcess:
    """One run of the sanctioned executor with every declared parameter
    stated: the swept one at this value, the others at their fixed
    values. Exit 3 is the executor's refusal and is a row, not a stop."""
    cmd = ["uv", "run", str(executor), f"--{parameter}", value,
           "--runtime", args.runtime, "--receipt", str(receipt)]
    for name, bound in fixed.items():
        if bound != UNBOUND:
            cmd += [f"--{name}", bound]
    if args.input == "fixture":
        cmd += ["--fixture", "--seed", str(args.seed)]
        if args.fixture_offset:
            cmd += ["--fixture-offset", str(args.fixture_offset)]
    else:
        cmd += ["--data-root", str(args.data_root)]
    if args.runtime_version:
        cmd += ["--runtime-version", args.runtime_version]
    if args.capability_root:
        cmd += ["--capability-root", str(args.capability_root)]
    return subprocess.run(cmd, capture_output=True, text=True)


def attest(attester: Path, receipt: Path, attestation: Path):
    """The attester on this receipt, before any field of it is read.
    Returns (passed, the attester's own verdict line)."""
    run = subprocess.run(["uv", "run", str(attester), str(receipt),
                          "--out", str(attestation)],
                         capture_output=True, text=True)
    text = (run.stdout or "").strip() or (run.stderr or "").strip()
    lines = [line for line in text.splitlines() if line.strip()]
    line = lines[-1] if lines else "the attester printed nothing"
    return run.returncode == 0 and line.startswith("PASS"), line


def field(receipt: dict, path: str):
    """One receipt field by its dotted path, or None where the receipt
    does not carry it (a refusal receipt carries no trend)."""
    node = receipt
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def method_identity(receipt: dict) -> str:
    return receipt.get("code_sha256") or ""


def input_identity(receipt: dict) -> dict:
    """What makes a table one root: the stamped record and its manifest
    digest for a data root, the seed, offset and digest for a fixture."""
    data = receipt.get("data") or {}
    if data.get("mode") == "data-root":
        record = data.get("record") or {}
        return {"mode": "data-root", "record": record.get("record"),
                "manifest_sha256": record.get("manifest_sha256")}
    return {"mode": data.get("mode"), "seed": data.get("seed"),
            "fixture_offset_mm": data.get("fixture_offset_mm"),
            "digest": data.get("digest")}


def one_method(rows):
    """(code, message) where two rows carry different methods or
    different inputs, else None. A sweep is one method on one root."""
    seen_method, seen_input = {}, {}
    for row in rows:
        receipt = row.get("receipt_body")
        if receipt is None:
            continue
        seen_method.setdefault(method_identity(receipt), row["value"])
        key = json.dumps(input_identity(receipt), sort_keys=True)
        seen_input.setdefault(key, row["value"])
    if len(seen_method) > 1:
        first, second = list(seen_method.items())[:2]
        return ("mixed-method",
                f"the receipts in this sweep were produced by two executors: "
                f"{first[0]} at {first[1]} and {second[0]} at {second[1]}; a "
                "table is one method, and these rows are not comparable")
    if len(seen_input) > 1:
        first, second = list(seen_input.items())[:2]
        return ("mixed-input",
                f"the receipts in this sweep read two different inputs: "
                f"{first[0]} at {first[1]} and {second[0]} at {second[1]}; a "
                "table is one root, and these rows are not comparable")
    return None


def build_row(value: str, receipt_path: Path, attestation_path: Path,
              exit_code: int, attester: Path, columns):
    """One row: the attester first, then the receipt's own fields. A
    receipt the attester did not pass is a failed row carrying the
    attester's line and no number."""
    row = {"value": value, "receipt": str(receipt_path), "cells": {},
           "attested": False, "attestation": None, "run_id": None,
           "status": "not-attested", "reason_code": None,
           "receipt_body": None, "executor_exit": exit_code}
    if not receipt_path.is_file():
        row["attestation"] = f"the executor wrote no receipt (exit {exit_code})"
        return row
    passed, line = attest(attester, receipt_path, attestation_path)
    row["attestation"] = line
    row["attested"] = passed
    if not passed:
        return row
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    row["receipt_body"] = receipt
    row["run_id"] = receipt.get("run_id")
    row["reason_code"] = receipt.get("reason_code")
    row["status"] = "refused" if receipt.get("refused") else "computed"
    row["cells"] = {name: field(receipt, path) for name, path in columns}
    return row


# ---- the table

def show(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def show_md(value) -> str:
    if isinstance(value, float):
        return f"{value:+.4f}" if value else "0.0000"
    return show(value)


def headers(columns):
    return list(STATUS_COLUMNS) + [name for name, _ in columns]


def row_cells(row, columns):
    out = {"status": row["status"], "run_id": row["run_id"] or "",
           "reason_code": row["reason_code"] or ""}
    for name, _ in columns:
        out[name] = row["cells"].get(name)
    return out


def write_csv(path: Path, rows, columns) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers(columns))
        for row in rows:
            cells = row_cells(row, columns)
            writer.writerow([show(cells[name]) for name in headers(columns)])


def write_markdown(path: Path, rows, columns, head: dict) -> None:
    names = headers(columns)
    lines = [f"# {head['computation']}: {head['parameter']} swept over "
             f"{len(rows)} values", ""]
    lines += [head["provenance"], "",
              "| " + " | ".join(names) + " |",
              "| " + " | ".join("---" for _ in names) + " |"]
    for row in rows:
        cells = row_cells(row, columns)
        lines.append("| " + " | ".join(show_md(cells[name]) for name in names) + " |")
    lines += ["", head["reading"], ""]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(path: Path, rows, columns, head: dict) -> None:
    doc = dict(head)
    doc["columns"] = [{"name": name, "receipt_field": field_path}
                      for name, field_path in columns]
    doc["rows"] = [{
        "value": row["value"],
        "status": row["status"],
        "run_id": row["run_id"],
        "reason_code": row["reason_code"],
        "receipt": row["receipt"],
        "attested": row["attested"],
        "attestation": row["attestation"],
        "cells": row["cells"],
    } for row in rows]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


# ---- the sweep

def sweep(args) -> int:
    spec = CATALOG[args.computation]
    paths = bundle_paths(args.computation)
    declared = declared_parameters(paths["concept"])

    if args.aggregate:
        return refuse(
            "aggregate-across-rows",
            f"this sweep will not emit an aggregate across its rows, and "
            f"what was asked for is one: {args.aggregate}. Each row is a "
            f"receipt the attester passed, and an aggregate over the "
            f"rows is a number no concept owns: "
            f"knowledge/{BUNDLE}/{spec['concept']} owns the trend of one "
            f"period and states its uncertainty, and nothing in the bundle "
            f"owns a trend of trends. Computing one here would be a number of "
            f"this capability's own, which is domain expansion under ADR D of "
            f"the marketplace decisions and waits on the ablation. Quote one "
            f"row instead: its receipt carries the trend, the interval, the "
            f"months used and the verdict, and its run id is in the manifest.")
    if args.parameter not in declared:
        return refuse(
            "parameter-not-declared",
            f"{args.parameter} is not a parameter "
            f"knowledge/{BUNDLE}/{spec['concept']} declares; it declares "
            f"{', '.join(declared)}. Sweeping execution plumbing (a seed, an "
            "output path) or an invented knob produces a table of runs no "
            "concept licenses.")
    fixed = {}
    for item in args.fixed:
        if "=" not in item:
            return refuse("parameter-not-stated",
                          f"--fixed takes NAME=VALUE, or NAME={UNBOUND} for a "
                          f"parameter left unbound; got {item}")
        name, bound = item.split("=", 1)
        if name not in declared:
            return refuse("parameter-not-declared",
                          f"{name} is not a parameter "
                          f"knowledge/{BUNDLE}/{spec['concept']} declares; it "
                          f"declares {', '.join(declared)}")
        if name == args.parameter:
            return refuse("parameter-not-stated",
                          f"{name} is the swept parameter and cannot also be "
                          "fixed")
        fixed[name] = bound
    unstated = [name for name in declared
                if name != args.parameter and name not in fixed]
    if unstated:
        return refuse(
            "parameter-not-stated",
            f"every declared parameter is stated on every run: "
            f"{', '.join(unstated)} is neither swept nor fixed. State it with "
            f"--fixed {unstated[0]}=VALUE, or --fixed {unstated[0]}={UNBOUND} "
            "to leave it unbound on every run, so the table says what it was.")

    if args.values:
        values = [v for v in (item.strip() for item in args.values.split(",")) if v]
    else:
        length, step = (int(part) for part in args.windows.split(":"))
        values = windows(args.span, length, step)
    if not values:
        return refuse("parameter-not-stated",
                      "the sweep has no values; state them with --values or "
                      "--windows LENGTH:STEP with --span FIRST:LAST")

    out_dir = Path(args.out_dir).expanduser().resolve()
    receipts_dir = out_dir / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for index, value in enumerate(values):
        stem = f"{index:03d}-{re.sub(r'[^A-Za-z0-9._-]', '_', value)}"
        receipt = receipts_dir / f"{stem}.json"
        attestation = receipts_dir / f"{stem}-attestation.json"
        run = run_executor(paths["executor"], args.parameter, value, fixed,
                           args, receipt)
        if run.returncode not in (0, 3):
            print((run.stderr or run.stdout or "").strip())
            return refuse("executor-failed",
                          f"the executor exited {run.returncode} at "
                          f"{args.parameter} {value}; that is neither a result "
                          "nor a refusal, so the sweep stops rather than "
                          "tabling a run it cannot read")
        rows.append(build_row(value, receipt, attestation, run.returncode,
                              paths["attester"], spec["columns"]))

    mixed = one_method(rows)
    if mixed:
        return refuse(*mixed)

    attested = [row for row in rows if row["attested"]]
    body = attested[0]["receipt_body"] if attested else {}
    head = {
        "sweep": "one declared parameter swept; every cell is a field of a "
                 "receipt this sweep attested, and no aggregate across rows "
                 "is computed here",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "computation": args.computation,
        "concept": f"knowledge/{BUNDLE}/{spec['concept']}",
        "executor": f"knowledge/{BUNDLE}/{spec['executor']}",
        "attester": f"knowledge/{BUNDLE}/{spec['attester']}",
        "wrapping_skill": spec["skill"],
        "parameter": args.parameter,
        "values": values,
        "values_rule": (f"--windows {args.windows} --span {args.span}"
                        if args.windows else "--values, stated one by one"),
        "fixed": fixed,
        "runtime": args.runtime,
        "code_sha256": method_identity(body),
        "input": input_identity(body),
        "refusals_enforced": list(REFUSALS),
        "not_computed": "the trend across the rows, the mean of any column, "
                        "and any rate read off the count of closed rows: no "
                        "concept owns them",
    }
    head["provenance"] = (
        f"Every cell is a field of a receipt the attester passed. Executor "
        f"{head['executor']} at {head['code_sha256']}; attester "
        f"{head['attester']}; concept {head['concept']}; input "
        f"{json.dumps(head['input'], sort_keys=True)}; runtime "
        f"{args.runtime}. Floats are shown to four decimals; the CSV and the "
        f"receipts carry them at full precision.")
    head["reading"] = (
        "A refused row is a measurement: the executor wrote a refusal receipt "
        "with that reason code and no number. Read one row at a time, with "
        f"the caveats {head['concept']} states beside it. This table licenses "
        "no statement about the rows together, and this sweep refuses to "
        "compute one.")

    write_csv(out_dir / "sweep.csv", rows, spec["columns"])
    write_markdown(out_dir / "sweep.md", rows, spec["columns"], head)
    write_manifest(out_dir / "sweep.json", rows, spec["columns"], head)

    computed = sum(1 for row in rows if row["status"] == "computed")
    refused = sum(1 for row in rows if row["status"] == "refused")
    failed = [row for row in rows if not row["attested"]]
    print((out_dir / "sweep.md").read_text(encoding="utf-8"))
    print(f"sweep: {len(rows)} rows over {args.parameter}, {computed} computed, "
          f"{refused} refused by the executor, {len(failed)} not attested; "
          f"{out_dir}/sweep.csv, sweep.md, sweep.json")
    for row in failed:
        print(f"  not attested at {args.parameter} {row['value']}: "
              f"{row['attestation']}")
    return 1 if failed else 0


# ---- selftest

def selftest() -> int:
    """Every refusal, on the executor's synthetic fixture."""
    paths = bundle_paths("sea-level-budget")
    columns = CATALOG["sea-level-budget"]["columns"]
    base = ["--computation", "sea-level-budget", "--input", "fixture",
            "--seed", "7", "--runtime", "selftest"]

    def run_sweep(extra, work):
        cmd = [sys.executable, str(Path(__file__).resolve()), *base,
               "--out-dir", str(work), *extra]
        return subprocess.run(cmd, capture_output=True, text=True)

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)

        # 1. The sweep itself: three windows, one of which the executor
        #    refuses for crossing the gap with no bridge. Every row is
        #    attested, the refusal is a row, and every cell is the
        #    receipt's own field.
        values = "2005-01:2009-12,2010-01:2014-12,2015-01:2019-12"
        done = run_sweep(["--parameter", "period", "--values", values,
                          "--fixed", "bridge=unbound"], work / "table")
        assert done.returncode == 0, done.stdout + done.stderr
        doc = json.loads((work / "table" / "sweep.json").read_text())
        assert [row["value"] for row in doc["rows"]] == values.split(",")
        assert all(row["attested"] for row in doc["rows"]), doc["rows"]
        assert [row["status"] for row in doc["rows"]] == ["computed", "computed", "refused"]
        assert doc["rows"][2]["reason_code"] == "gap-without-bridge"
        assert doc["rows"][2]["cells"]["trend_residual_mm_yr"] is None
        assert "PASS refusal" in doc["rows"][2]["attestation"]
        for row in doc["rows"]:
            receipt = json.loads(Path(row["receipt"]).read_text())
            for name, path in columns:
                assert row["cells"][name] == field(receipt, path), (name, row["value"])
            assert row["run_id"] == receipt["run_id"]
        assert (work / "table" / "sweep.csv").is_file()
        assert "| status |" in (work / "table" / "sweep.md").read_text()
        assert doc["fixed"] == {"bridge": "unbound"}

        # 2. The aggregate a reader asks for first is refused, and the
        #    refusal says what to quote instead.
        out = run_sweep(["--parameter", "period", "--values", values,
                         "--fixed", "bridge=unbound",
                         "--aggregate", "the overall trend"], work / "agg")
        assert out.returncode == 4 and "aggregate-across-rows" in out.stdout, out.stdout
        assert "ADR D" in out.stdout and "Quote one row instead" in out.stdout

        # 3. A parameter the concept does not declare, swept or fixed.
        out = run_sweep(["--parameter", "seed", "--values", "7,8",
                         "--fixed", "bridge=unbound"], work / "undeclared")
        assert out.returncode == 4 and "parameter-not-declared" in out.stdout, out.stdout
        out = run_sweep(["--parameter", "period", "--values", values,
                         "--fixed", "bridge=unbound", "--fixed", "seed=7"],
                        work / "undeclared2")
        assert out.returncode == 4 and "parameter-not-declared" in out.stdout, out.stdout

        # 4. A declared parameter the command line leaves unstated.
        out = run_sweep(["--parameter", "period", "--values", values],
                        work / "unstated")
        assert out.returncode == 4 and "parameter-not-stated" in out.stdout, out.stdout
        assert "bridge" in out.stdout

        # 5. Two methods or two inputs in one table, on real receipts:
        #    the same period at two fixture seeds gives two inputs, and
        #    a receipt whose executor digest differs gives two methods.
        seven = run_sweep(["--parameter", "period", "--values", "2005-01:2009-12",
                           "--fixed", "bridge=unbound"], work / "seed7")
        assert seven.returncode == 0, seven.stdout + seven.stderr
        eight = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()),
             "--computation", "sea-level-budget", "--input", "fixture",
             "--seed", "8", "--runtime", "selftest", "--parameter", "period",
             "--values", "2005-01:2009-12", "--fixed", "bridge=unbound",
             "--out-dir", str(work / "seed8")], capture_output=True, text=True)
        assert eight.returncode == 0, eight.stdout + eight.stderr
        def only_receipt(out_dir: Path):
            # by the manifest, never by a glob: the receipts directory
            # holds each attestation beside its receipt, and the order a
            # glob returns them in is the filesystem's business
            manifest = json.loads((out_dir / "sweep.json").read_text())
            return json.loads(Path(manifest["rows"][0]["receipt"]).read_text())

        first = only_receipt(work / "seed7")
        second = only_receipt(work / "seed8")
        assert first["data"]["seed"] == 7 and second["data"]["seed"] == 8
        mixed = one_method([{"value": "seed 7", "receipt_body": first},
                            {"value": "seed 8", "receipt_body": second}])
        assert mixed and mixed[0] == "mixed-input", mixed
        other = json.loads(json.dumps(first))
        other["code_sha256"] = "sha256:" + "0" * 64
        mixed = one_method([{"value": "a", "receipt_body": first},
                            {"value": "b", "receipt_body": other}])
        assert mixed and mixed[0] == "mixed-method", mixed
        assert one_method([{"value": "a", "receipt_body": first}]) is None

        # 6. A receipt the attester does not pass is a failed row with
        #    the attester's own line and no number in it.
        tampered = work / "tampered.json"
        doctored = json.loads(json.dumps(first))
        doctored["trend_residual_mm_yr"] = doctored["trend_residual_mm_yr"] + 0.5
        tampered.write_text(json.dumps(doctored, indent=2) + "\n")
        row = build_row("2005-01:2009-12", tampered, work / "tampered-att.json",
                        0, paths["attester"], columns)
        assert row["attested"] is False and row["status"] == "not-attested", row
        assert row["cells"] == {} and row["run_id"] is None
        assert row["attestation"].startswith("FAIL"), row["attestation"]

        # 7. The window rule expands to explicit values, and the values
        #    are what the rows carry.
        assert windows("2005-01:2010-12", 24, 12) == [
            "2005-01:2006-12", "2006-01:2007-12", "2007-01:2008-12",
            "2008-01:2009-12", "2009-01:2010-12"]
        out = run_sweep(["--parameter", "period", "--windows", "60:60",
                         "--span", "2005-01:2014-12", "--fixed", "bridge=unbound"],
                        work / "windows")
        assert out.returncode == 0, out.stdout + out.stderr
        doc = json.loads((work / "windows" / "sweep.json").read_text())
        assert [row["value"] for row in doc["rows"]] == ["2005-01:2009-12",
                                                          "2010-01:2014-12"]
        assert doc["values_rule"] == "--windows 60:60 --span 2005-01:2014-12"

        # 8. The declared set comes from the concept, not from here.
        assert declared_parameters(paths["concept"]) == ["period", "bridge"]

    print("sweep selftest: ok "
          f"({len(REFUSALS)} refusals exercised: {', '.join(REFUSALS)}; "
          "a tampered receipt is a failed row, not a number)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--computation", choices=sorted(CATALOG),
                    help="the attested computation to sweep")
    ap.add_argument("--parameter", help="the declared parameter swept")
    ap.add_argument("--values", help="the values, comma separated, stated explicitly")
    ap.add_argument("--windows", help="LENGTH:STEP in months, expanded over --span "
                                      "into explicit values")
    ap.add_argument("--span", help="FIRST:LAST as YYYY-MM:YYYY-MM, with --windows")
    ap.add_argument("--fixed", action="append", default=[],
                    help=f"NAME=VALUE for another declared parameter, or "
                         f"NAME={UNBOUND} to leave it unbound; every declared "
                         "parameter is stated on every run")
    ap.add_argument("--input", choices=("fixture", "data-root"),
                    help="the executor's input, one for the whole sweep")
    ap.add_argument("--data-root", type=Path, help="the stamped tree, with --input data-root")
    ap.add_argument("--seed", type=int, default=7, help="fixture seed (default 7)")
    ap.add_argument("--fixture-offset", type=float, default=0.0,
                    help="fixture inter-mission offset in mm (default 0)")
    ap.add_argument("--runtime", help="the runtime that ran this, passed to every run")
    ap.add_argument("--runtime-version", default=None)
    ap.add_argument("--capability-root", type=Path, default=None,
                    help="the package tree these runs are evidence for")
    ap.add_argument("--out-dir", help="where sweep.csv, sweep.md, sweep.json and "
                                      "the receipts go")
    ap.add_argument("--aggregate", default=None,
                    help="an aggregate across the rows; always refused, and the "
                         "refusal says which receipt to quote instead")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    missing = [name for name in ("computation", "parameter", "input", "runtime",
                                 "out_dir") if getattr(args, name) is None]
    if missing:
        ap.error("these are required for a sweep: "
                 + ", ".join("--" + name.replace("_", "-") for name in missing))
    if bool(args.values) == bool(args.windows):
        ap.error("state the values with --values, or a window rule with "
                 "--windows LENGTH:STEP and --span FIRST:LAST, not both")
    if args.windows and not args.span:
        ap.error("--windows needs --span FIRST:LAST")
    if (args.input == "data-root") != bool(args.data_root):
        ap.error("--input data-root needs --data-root DIR, and --data-root is "
                 "not read with --input fixture")
    return sweep(args)


if __name__ == "__main__":
    sys.exit(main())
