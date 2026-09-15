# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.23.13",
# ]
# ///
# Golden notebook for the attested Argo ocean heat content change (the
# golden-notebook requirement: one fixture-backed asserting script per
# attested computation): the sanctioned executor under
# knowledge/references/computations/argo_ohc.py and its attester go
# through the fixture chain (a known change planted and recovered),
# the refusal (a window that leaves the coverage exits 3 and attests
# as a refusal), the loader's and the data-root tool's selftests, the
# committed data root's record check, and the record run on the
# committed root for both layers, whose numbers are asserted against
# the values recorded in knowledge/computations/argo-ohc.md. Headless
# green via `uv run verification/argo_ohc.py`; no network, no
# credential. Reference numbers measured at record creation on
# 2026-09-15.

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import json
    import subprocess
    import tempfile
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    refs = root / "knowledge" / "references"
    executor = refs / "computations" / "argo_ohc.py"
    attester = refs / "attesters" / "argo_ohc_check.py"
    loader = refs / "loaders" / "ohc_rg_loader.py"
    data_root_tool = refs / "loaders" / "ohc_data_root.py"
    data_root = refs / "retrieval" / "argo-ohc-root"
    tmp = Path(tempfile.mkdtemp(prefix="argo_ohc_"))

    def compute(window, depth, name, fixture=True, seed=7):
        # The executor as the skill runs it, from the repository root so
        # the receipt's bundle block names this package.
        out = tmp / f"{name}.json"
        cmd = ["uv", "run", str(executor), "--window", window, "--depth", str(depth),
               "--runtime", "golden", "--receipt", str(out)]
        cmd += ["--fixture", "--seed", str(seed)] if fixture else ["--data-root", str(data_root)]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
        receipt = json.loads(out.read_text()) if out.is_file() else None
        return p.returncode, p.stdout, p.stderr, receipt, out

    def attest(receipt_path):
        att = tmp / (receipt_path.stem + "-attestation.json")
        p = subprocess.run(["uv", "run", str(attester), str(receipt_path), "--out", str(att)],
                           capture_output=True, text=True, cwd=root)
        doc = json.loads(att.read_text()) if att.is_file() else {}
        return p.returncode, p.stdout, p.stderr, doc

    def run_tool(script, *args):
        p = subprocess.run(["uv", "run", str(script), *args], capture_output=True, text=True, cwd=root)
        return p.returncode, p.stdout, p.stderr

    return attest, attester, compute, data_root, data_root_tool, json, loader, run_tool


@app.cell
def _(attest, compute):
    # 1. The fixture chain: a planted rate of 10 ZJ per year over
    #    2005-01 through 2016-12 in the 0 to 2000 dbar layer is recovered
    #    inside the interval, the planted change lies within the change's
    #    uncertainty, and the receipt attests PASS with every check.
    _code, _out, _err, fx, fx_path = compute("2005-01:2016-12", 2000, "fixture-2000")
    assert _code == 0, _err
    assert fx["refused"] is False and fx["data"]["mode"] == "fixture"
    _kt = fx["known_truth"]
    assert _kt["planted_rate_ZJ_yr"] == 10.0 and abs(_kt["planted_change_ZJ"] - 110.0) < 1e-9
    assert _kt["rate_inside_interval"] is True and _kt["change_within_uncertainty"] is True
    assert abs(fx["terms"]["trend"]["value"] - 10.0594) < 0.001
    assert abs(fx["terms"]["change"]["value"] - 110.6532) < 0.001
    assert abs(fx["terms"]["endpoint_change"]["value"] - 110.4110) < 0.001
    assert fx["verdict"]["consistent_within_uncertainty"] is True
    assert fx["terms"]["deep_omission"]["omitted"] is True and fx["terms"]["deep_omission"]["value"] is None
    _rc, _o, _e, _doc = attest(fx_path)
    assert _rc == 0, _o + _e
    assert _doc["verdict"] == "PASS" and _doc["refusal"] is False
    assert {c["name"] for c in _doc["checks"]} == {"fields", "code", "release", "runtime", "data",
                                                     "series", "recompute", "bookkeeping", "plausible"}
    assert all(c["ok"] for c in _doc["checks"])
    assert "PASS run" in _o and "FAIL" not in _o
    return (fx_path,)


@app.cell
def _(attest, compute):
    # 2. The refusal: a window that leaves the fixture's coverage exits 3,
    #    computes nothing, and attests PASS as a refusal.
    _code, _out, _err, rf, rf_path = compute("2001-01:2016-12", 700, "refusal")
    assert _code == 3, (_code, _err)
    assert rf["refused"] is True and rf["reason_code"] == "window-outside-coverage"
    assert "terms" not in rf and "series" not in rf
    assert "REFUSED" in _out
    _rc, _o, _e, _doc = attest(rf_path)
    assert _rc == 0, _o + _e
    assert _doc["verdict"] == "PASS" and _doc["refusal"] is True
    assert "PASS refusal" in _o
    return


@app.cell
def _(attest, fx_path, json):
    # 3. A doctored receipt fails on its check: the attester recomputes
    #    from the series and does not take the receipt's word.
    _r = json.loads(fx_path.read_text())
    _r["terms"]["trend"]["value"] += 0.5
    _doctored = fx_path.with_name("doctored.json")
    _doctored.write_text(json.dumps(_r, indent=2) + "\n")
    _rc, _o, _e, _doc = attest(_doctored)
    assert _rc == 1 and "FAIL recompute" in _o, _o
    return


@app.cell
def _(attester, data_root, data_root_tool, loader, run_tool):
    # 4. The loader's selftest on a synthetic grid, the data-root tool's
    #    selftest, the attester's selftest, and the committed root's
    #    record check, all offline.
    _rc, _o, _e = run_tool(loader, "--selftest")
    assert _rc == 0 and "selftest: OK" in _o, _o + _e
    _rc, _o, _e = run_tool(data_root_tool, "--selftest")
    assert _rc == 0 and "ohc_data_root selftest: ok" in _o, _o + _e
    _rc, _o, _e = run_tool(attester, "--selftest")
    assert _rc == 0 and "argo_ohc_check selftest: ok" in _o, _o + _e
    _rc, _o, _e = run_tool(data_root_tool, "--root", str(data_root), "--check")
    assert _rc == 0 and "RECORD.json matches the files" in _o, _o + _e
    return


@app.cell
def _(attest, compute, data_root, json):
    # 5. The record run on the committed root, 0 to 2000 dbar over
    #    2006-01 through 2020-12: the numbers the concept records, the
    #    anchor distance, and a PASS attestation.
    _rec = json.loads((data_root / "RECORD.json").read_text())
    assert _rec["record"] == "argo-ohc-root-2026-09-15"
    _code, _out, _err, r2000, r2000_path = compute("2006-01:2020-12", 2000, "record-2000", fixture=False)
    assert _code == 0, _err
    assert r2000["data"]["mode"] == "data-root" and r2000["data"]["record"] == _rec["record"]
    assert r2000["months"]["n_used"] == 180 and r2000["months"]["missing"] == []
    assert abs(r2000["terms"]["trend"]["value"] - 9.6664) < 0.001
    assert abs(r2000["terms"]["trend"]["interval"]["half_width"] - 1.2118) < 0.001
    assert abs(r2000["terms"]["change"]["value"] - 135.33) < 0.001
    assert abs(r2000["terms"]["endpoint_change"]["value"] - 110.0473) < 0.001
    assert abs(r2000["residual"]["value"] - -25.2827) < 0.001
    assert r2000["verdict"]["consistent_within_uncertainty"] is False
    assert abs(r2000["terms"]["trend"]["per_area"]["W_m2_of_earth_surface"] - 0.60053) < 0.0001
    assert abs(r2000["anchor"]["distance_W_m2_of_earth_surface"] - -0.01947) < 0.0001
    assert r2000["known_truth"] is None
    _rc, _o, _e, _doc = attest(r2000_path)
    assert _rc == 0 and _doc["verdict"] == "PASS" and _doc["refusal"] is False, _o + _e
    return


@app.cell
def _(attest, compute):
    # 6. The same window for 0 to 700 dbar, and the record's refusal of
    #    a window past its coverage.
    _code, _out, _err, r700, r700_path = compute("2006-01:2020-12", 700, "record-700", fixture=False)
    assert _code == 0, _err
    assert abs(r700["terms"]["trend"]["value"] - 5.9498) < 0.001
    assert abs(r700["terms"]["trend"]["interval"]["half_width"] - 0.9582) < 0.001
    assert abs(r700["terms"]["change"]["value"] - 83.2973) < 0.001
    assert abs(r700["anchor"]["distance_W_m2_of_earth_surface"] - -0.02036) < 0.0001
    _rc, _o, _e, _doc = attest(r700_path)
    assert _rc == 0 and _doc["verdict"] == "PASS", _o + _e
    _code, _out, _err, rr, rr_path = compute("2010-01:2030-12", 700, "record-refusal", fixture=False)
    assert _code == 3 and rr["reason_code"] == "window-outside-coverage", _err
    _rc, _o, _e, _doc = attest(rr_path)
    assert _rc == 0 and _doc["refusal"] is True and "PASS refusal" in _o
    return


if __name__ == "__main__":
    app.run()
