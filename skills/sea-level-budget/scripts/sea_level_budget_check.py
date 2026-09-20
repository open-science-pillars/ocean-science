#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Deterministic attester for the attested sea level budget closure
(sea_level_budget.py). Stdlib only, consumer side, no language model.

A receipt from any runtime attests PASS (exit 0) only when ALL hold,
else FAIL (exit 1) naming the check:

  fields       every declared receipt field is present;
  code         the receipt's code_sha256 is the sanctioned executor
               beside this file (or the one --computation names), so an
               edited computation invalidates every earlier receipt;
  release      the receipt's bundle block names this bundle's package
               name, version and release lock digest (null where the
               tree carries none), and its capability block, the
               package the run is evidence for, is well formed;
  runtime      the receipt names the runtime that produced it;
  data         a fixture regenerated here at the receipt's seed and
               offset hashes to the receipt's digest, and the generator
               (the executor itself) to the receipt's generator digest;
               for a data root, the RECORD.json stamp is present and
               names the tree;
  series       the three series, their uncertainties and the months used
               and missing are what the regenerated fixture yields over
               the period (1e-9), and the residual is altimetry minus
               mass minus steric;
  recompute    every trend, interval, formal error, the combined
               uncertainty and the verdict recomputed here from the
               series match the receipt (1e-9 relative): an independent
               epoch fit of the sanctioned method statement, and on a
               hole-free period the shared attester chain
               (trend_recompute.check_block) binds each block to the
               sanctioned trend method by hash;
  bookkeeping  every field of the convention's corrections table is
               present, the deep-steric systematic is stated, the gap
               handling lists exactly the months missing, and a period
               that crosses the inter-mission gap carries a bridge;
  plausible    on the fixture with no injected offset, the known truth:
               the closure gap lies within the bar, the verdict says
               closed, and each term's trend is within 1 mm per year of
               the imposed one.

A refusal receipt (refused true) attests PASS only as a refusal: the
identity checks hold, the reason code is one the executor issues, and
the refusal is reproduced here (the period does cross the gap with no
bridge bound, a term does have fewer than 24 months, the period does
lie outside the record, or the executor's own compute refuses the same
way). The verdict line then carries the word refusal, and the exit is 0.

--out writes the attestation: the verdict, whether it is a refusal, the
attester's and the computation's digests, the receipt's digest and run
id, the capability, bundle and runtime blocks copied from the receipt,
and every check, so a qualification record can cite it.

  sea_level_budget_check.py RECEIPT.json [--computation PATH] [--out ATTESTATION.json]
  sea_level_budget_check.py --selftest
"""

import argparse
import contextlib
import datetime as dt
import hashlib
import importlib.util
import io
import json
import math
import re
import sys
import tempfile
from pathlib import Path

# The attester side of the sanctioned trend with interval is one file for
# every attester that meets one, so a defect in the recompute shows up in
# all of them at once rather than hiding in a copy. It lives beside the
# trend computation, in the ecco skill, and is loaded by path rather than
# by name: a bare import would need a copy beside every attester. A copy
# beside this file still wins, which is how a sandboxed run resolves it.
def _load_beside(name: str):
    here = Path(__file__).resolve().parent
    path = here / f"{name}.py"
    if not path.is_file():
        path = here.parent.parent / "ecco" / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_trend_recompute = _load_beside("trend_recompute")
CONFIDENCE = _trend_recompute.CONFIDENCE
MIN_DOF = _trend_recompute.MIN_DOF
MIN_MONTHS = _trend_recompute.MIN_MONTHS
REL_TOL = _trend_recompute.REL_TOL
check_block = _trend_recompute.check_block
close = _trend_recompute.close
default_deseasonalize = _trend_recompute.default_deseasonalize
t_quantile = _trend_recompute.t_quantile

HERE = Path(__file__).resolve().parent
DEFAULT_COMPUTATION = HERE / "sea_level_budget.py"
SKILLS = HERE.parent.parent
METHOD = SKILLS / "ecco" / "scripts" / "ecco_trend_ci.py"


def method_beside(computation: Path) -> Path:
    """The sanctioned trend method the computation imports: a copy beside
    it when there is one (the sandbox this attester builds), else the one
    file, in the ecco skill."""
    beside = computation.resolve().parent / "ecco_trend_ci.py"
    return beside if beside.is_file() else METHOD
FIELDS = ("run_id", "computation", "code_sha256", "capability", "bundle", "runtime",
          "generated_utc", "data", "bound_parameters", "refused", "months", "series",
          "trend_altimetry_mm_yr", "trend_mass_mm_yr", "trend_steric_mm_yr",
          "trend_residual_mm_yr", "trends", "combined_uncertainty", "verdict",
          "bookkeeping", "caveats")
REFUSAL_FIELDS = ("run_id", "computation", "code_sha256", "capability", "bundle",
                  "runtime", "generated_utc", "data", "bound_parameters", "refused",
                  "reason_code", "reason")
TERMS = ("altimetry", "mass", "steric")
ROUNDING = 5.0e-5
TRUTH_BAND_MM_YR = 1.0


def load(path: Path):
    spec = importlib.util.spec_from_file_location("sea_level_budget", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def ym(d: str) -> int:
    return int(d[:4]) * 12 + int(d[5:7]) - 1


def label(k: int) -> str:
    return f"{k // 12:04d}-{k % 12 + 1:02d}"


def numbers(v, n=None):
    return (isinstance(v, list) and (n is None or len(v) == n)
            and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                    and math.isfinite(x) for x in v))


# ---- the independent recompute of the method statement on epochs

def epoch_recompute(t_cal, y, unc, deseasonalize):
    """Written from the method statement, not copied from the executor:
    group means over the existing months of each calendar month, off
    the series and the time index; least squares; lag-1 autocorrelation
    over adjacent-epoch residual pairs; n_eff capped at n; Student's t
    on n_eff - 2; the slope's weights carry the per-month uncertainties
    into a formal error."""
    n = len(y)
    if n < 3:
        return None
    tt = [float(k) for k in t_cal]
    yy = [float(v) for v in y]
    if deseasonalize == "climatology":
        by_month = {}
        for i, k in enumerate(t_cal):
            by_month.setdefault(k % 12, []).append(i)
        for idx in by_month.values():
            my = sum(yy[i] for i in idx) / len(idx)
            mt = sum(tt[i] for i in idx) / len(idx)
            for i in idx:
                yy[i] = yy[i] - my
                tt[i] = tt[i] - mt
    tbar, ybar = sum(tt) / n, sum(yy) / n
    sxx = sum((a - tbar) ** 2 for a in tt)
    slope = sum((a - tbar) * (b - ybar) for a, b in zip(tt, yy)) / sxx
    icpt = ybar - slope * tbar
    e = [b - icpt - slope * a for a, b in zip(tt, yy)]
    ss = sum(v * v for v in e)
    formal = math.sqrt(sum(((a - tbar) / sxx * s) ** 2 for a, s in zip(tt, unc)))
    out = {"n": n, "trend": slope * 12.0, "formal_95": 1.959963984540054 * formal * 12.0,
           "interval": False}
    if n < MIN_MONTHS:
        return out
    r1 = sum(e[i] * e[i + 1] for i in range(n - 1) if t_cal[i + 1] - t_cal[i] == 1) / ss
    n_eff = min(float(n), n * (1.0 - r1) / (1.0 + r1))
    dof = n_eff - 2.0
    out.update({"r1": r1, "n_eff": n_eff, "dof": dof})
    if dof < MIN_DOF:
        return out
    se = math.sqrt(ss / dof / sxx)
    tq = t_quantile(0.5 + CONFIDENCE / 2.0, dof)
    half = tq * se * 12.0
    out.update({"interval": True, "se": se * 12.0, "t_quantile": tq, "half_width": half,
                "ci_low": out["trend"] - half, "ci_high": out["trend"] + half,
                "naive_half_width": t_quantile(0.5 + CONFIDENCE / 2.0, n - 2)
                * math.sqrt(ss / (n - 2) / sxx) * 12.0})
    return out


def check_trend_block(block, t_cal, y, unc, n_calendar, method_path):
    """None when the block recomputes, else why not."""
    if not isinstance(block, dict):
        return "missing or not an object"
    n = len(y)
    if block.get("method") != "trend-ci":
        return f"method {block.get('method')!r} is not trend-ci"
    if not method_path.is_file():
        return f"no sanctioned trend method beside the computation ({method_path.name} missing)"
    if block.get("method_code_sha256") != hashlib.sha256(method_path.read_bytes()).hexdigest():
        return "method_code_sha256 does not name the sanctioned trend method beside the computation"
    if block.get("confidence") != CONFIDENCE or block.get("n") != n:
        return f"confidence {block.get('confidence')} or n {block.get('n')} (series has {n})"
    des = default_deseasonalize(n_calendar)
    if block.get("deseasonalize") != des:
        return f"deseasonalize {block.get('deseasonalize')!r} is not the policy for a {n_calendar}-month period ({des})"
    ep = block.get("epochs")
    if (not isinstance(ep, dict) or ep.get("n_calendar") != n_calendar or ep.get("n_used") != n
            or ep.get("n_missing") != n_calendar - n or ep.get("holes") is not (n != n_calendar)):
        return "epochs block disagrees with the months used and the period"
    c = epoch_recompute(t_cal, y, unc, des)
    if c is None or not isinstance(block.get("trend"), (int, float)) or not close(block["trend"], c["trend"]):
        return f"trend {block.get('trend')} does not recompute ({c and c['trend']})"
    f = block.get("formal_95_mm_yr")
    if not isinstance(f, (int, float)) or not close(f, c["formal_95"]):
        return f"formal_95_mm_yr {f} does not recompute ({c['formal_95']})"
    if block.get("stated") is False:
        if c["interval"]:
            return "block refuses an interval the recompute states"
        return None if isinstance(block.get("reason"), str) and block["reason"] else "refused interval carries no reason"
    if block.get("stated") is not True:
        return "stated must be true or false"
    if not c["interval"]:
        return "block states an interval the recompute refuses"
    for k in ("ci_low", "ci_high", "half_width", "naive_half_width", "r1", "n_eff", "dof", "se", "t_quantile"):
        v = block.get(k)
        if not isinstance(v, (int, float)) or not close(v, c[k]):
            return f"{k} {v} does not recompute ({c[k]})"
    if block.get("significant_at_confidence") is not (c["ci_low"] * c["ci_high"] > 0):
        return "significance flag disagrees with the interval"
    if n == n_calendar:
        err = check_block(block, y, method_path)
        if err:
            return f"shared chain: {err}"
    return None


# ---- the attestation

def attest(receipt_path: Path, computation: Path):
    """(verdict, refusal, checks, receipt) for one receipt."""
    checks = []

    def check(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
        return bool(ok)

    try:
        r = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert isinstance(r, dict)
    except (OSError, ValueError, AssertionError) as e:
        check("fields", False, f"unreadable or not a JSON object: {e}")
        return "FAIL", False, checks, {}
    mod = load(computation)
    refusal = r.get("refused") is True
    fields = REFUSAL_FIELDS if refusal else FIELDS
    missing = [f for f in fields if f not in r]
    check("fields", not missing, "all present" if not missing else f"missing {missing}")

    sanctioned = sha256_file(computation)
    check("code", r.get("code_sha256") == sanctioned,
          f"receipt {r.get('code_sha256')} vs sanctioned {sanctioned}")

    identity = mod.package_identity(mod.package_root(computation.parent))
    bundle = r.get("bundle") or {}
    cap = r.get("capability") or {}
    cap_ok = (isinstance(cap, dict) and isinstance(cap.get("name"), str) and cap["name"]
              and isinstance(cap.get("version"), str) and cap["version"]
              and "release_lock" in cap
              and (cap["release_lock"] is None
                   or re.fullmatch(r"sha256:[0-9a-f]{64}", str(cap["release_lock"]))))
    check("release", bundle == identity and bool(identity.get("name")) and cap_ok,
          f"bundle {bundle} vs this tree {identity}; capability {cap} "
          f"{'well formed' if cap_ok else 'malformed'}")
    rt = r.get("runtime") or {}
    check("runtime", isinstance(rt, dict) and isinstance(rt.get("name"), str) and bool(rt.get("name")),
          f"runtime {rt.get('name')!r} {rt.get('version') or ''}".strip())

    data = r.get("data") or {}
    bound = r.get("bound_parameters") or {}
    period = str(bound.get("period", ""))
    m = re.fullmatch(r"(\d{4}-\d{2}):(\d{4}-\d{2})", period)
    start, end = (m.group(1), m.group(2)) if m else (None, None)
    fx = None
    if data.get("mode") == "fixture":
        seed, offset = data.get("seed"), data.get("fixture_offset_mm", 0.0)
        ok = isinstance(seed, int) and isinstance(offset, (int, float))
        if ok:
            fx = mod.make_fixture(seed, float(offset))
            digest = mod.fixture_digest(fx)
            ok = (data.get("digest") == digest and data.get("generator_sha256") == sanctioned
                  and data.get("span") == list(mod.FIXTURE_SPAN))
            detail = (f"regenerated fixture at seed {seed} offset {offset}: {digest}; receipt "
                      f"{data.get('digest')}; generator match {data.get('generator_sha256') == sanctioned}")
        else:
            detail = "fixture seed or offset missing"
        check("data", ok, detail)
    elif data.get("mode") == "data-root":
        rec = data.get("record")
        ok = (isinstance(rec, dict) and isinstance(rec.get("record"), str) and rec.get("record")
              and isinstance(rec.get("manifest_sha256"), str)
              and isinstance(rec.get("bookkeeping"), dict)
              and isinstance(data.get("files"), dict)
              and set(data["files"]) == {"altimetry.csv", "steric.csv", "mass.csv"})
        check("data", ok, f"data root {data.get('data_root')} stamped "
                          f"{rec.get('record') if isinstance(rec, dict) else None}")
    else:
        check("data", False, f"data mode {data.get('mode')!r} is neither fixture nor data-root")

    if refusal:
        code = r.get("reason_code")
        recognized = code in mod.REASONS
        reproduced, why = False, "reason not reproduced"
        if recognized and start:
            span = mod.FIXTURE_SPAN if fx else None
            if code == "period-outside-record":
                if span:
                    reproduced = not (ym(span[0]) <= ym(start) and ym(end) <= ym(span[1]))
                    why = f"the period {period} is outside {span[0]}..{span[1]}: {reproduced}"
                else:
                    reproduced, why = True, "a data-root refusal is taken on the executor's word for the span"
            elif code == "gap-without-bridge":
                reproduced = mod.crosses_gap(start, end) and not bound.get("bridge")
                why = f"the period {period} crosses the gap {mod.GAP} with no bridge bound: {reproduced}"
            elif code == "too-few-months" and fx:
                cal = [label(k) for k in range(ym(start), ym(end) + 1)]
                counts = {t: sum(d in set(fx["terms"][t]["dates"]) for d in cal) for t in TERMS}
                used = sum(all(d in set(fx["terms"][t]["dates"]) for t in TERMS) for d in cal)
                reproduced = min(counts.values()) < mod.MIN_MONTHS_PER_TERM or used < mod.MIN_MONTHS_PER_TERM
                why = f"months per term {counts}, all three {used}, floor {mod.MIN_MONTHS_PER_TERM}: {reproduced}"
            elif code == "interval-not-stated" and fx:
                body, again = mod.compute(fx["terms"], start, end, bound.get("bridge"),
                                          mod.FIXTURE_BOOKKEEPING, mod.method())
                reproduced = body is None and again[0] == code
                why = f"the executor's compute refuses the same way: {reproduced}"
            else:
                why = "a data-root refusal cannot be reproduced without the tree"
                reproduced = code in ("too-few-months", "interval-not-stated")
        check("refusal", recognized and reproduced,
              f"reason_code {code!r} {'recognized' if recognized else 'unknown'}; {why}")
        verdict = "PASS" if all(c["ok"] for c in checks) else "FAIL"
        return verdict, True, checks, r

    # months and series
    months = r.get("months") or {}
    used = months.get("used") or []
    miss = months.get("missing") or []
    cal = [label(k) for k in range(ym(start), ym(end) + 1)] if start else []
    n_cal = len(cal)
    months_ok = (bool(start) and months.get("period") == [start, end]
                 and months.get("n_calendar") == n_cal and months.get("n_used") == len(used)
                 and sorted(used + miss) == cal and len(set(used)) == len(used)
                 and len(used) >= mod.MIN_MONTHS_PER_TERM)
    s = r.get("series") or {}
    series_ok = months_ok and s.get("dates") == used
    for t in TERMS:
        series_ok = series_ok and numbers(s.get(f"{t}_mm"), len(used)) \
            and numbers(s.get(f"{t}_uncertainty_mm"), len(used))
    series_ok = series_ok and numbers(s.get("residual_mm"), len(used))
    detail = "months and series well formed" if series_ok else "months or series malformed"
    if series_ok:
        resid = [a - mm - st for a, mm, st in zip(s["altimetry_mm"], s["mass_mm"], s["steric_mm"])]
        dev = max(abs(x - y) for x, y in zip(resid, s["residual_mm"]))
        series_ok = dev <= REL_TOL * max(1.0, max(abs(x) for x in resid))
        detail = f"residual is altimetry minus mass minus steric (max deviation {dev:.2e})"
    if series_ok and fx:
        maxdev = 0.0
        by = {t: {d: (v, u) for d, v, u in zip(fx["terms"][t]["dates"], fx["terms"][t]["value_mm"],
                                               fx["terms"][t]["uncertainty_mm"])} for t in TERMS}
        expect_used = [d for d in cal if all(d in by[t] for t in TERMS)]
        expect_by_term = {t: [d for d in cal if d not in by[t]] for t in TERMS}
        series_ok = used == expect_used and months.get("missing_by_term") == expect_by_term
        for t in TERMS:
            for i, d in enumerate(used):
                if d in by[t]:
                    maxdev = max(maxdev, abs(by[t][d][0] - s[f"{t}_mm"][i]),
                                 abs(by[t][d][1] - s[f"{t}_uncertainty_mm"][i]))
        series_ok = series_ok and maxdev <= 1e-9
        detail += (f"; {len(used)} of {n_cal} months used, {len(miss)} missing, as the regenerated "
                   f"fixture yields (max deviation {maxdev:.2e})")
    check("series", series_ok, detail)

    # recompute
    rec_ok, rec_detail = False, "series not checkable"
    if series_ok:
        t_cal = [ym(d) - ym(start) for d in used]
        trends = r.get("trends") or {}
        method_path = method_beside(computation)
        problems = []
        resid_unc = [math.sqrt(a * a + b * b + c * c) for a, b, c in zip(
            s["altimetry_uncertainty_mm"], s["mass_uncertainty_mm"], s["steric_uncertainty_mm"])]
        for name in (*TERMS, "residual"):
            y = s[f"{name}_mm"]
            unc = resid_unc if name == "residual" else s[f"{name}_uncertainty_mm"]
            err = check_trend_block(trends.get(name), t_cal, y, unc, n_cal, method_path)
            if err:
                problems.append(f"trends.{name}: {err}")
                continue
            v = r.get(f"trend_{name}_mm_yr")
            if not isinstance(v, (int, float)) or abs(v - trends[name]["trend"]) > ROUNDING + 1e-9:
                problems.append(f"trend_{name}_mm_yr {v} is not the block's trend rounded")
        if not problems:
            deep = dict(mod.DEEP_STERIC_MM_YR)
            cu = r.get("combined_uncertainty") or {}
            terms_unc = {t: max(trends[t]["half_width"], trends[t]["formal_95_mm_yr"]) for t in TERMS}
            quad = math.sqrt(sum(v * v for v in terms_unc.values()))
            bar = quad + deep["uncertainty"]
            stated_terms = cu.get("terms_mm_yr") or {}
            if not all(isinstance(stated_terms.get(t), (int, float)) and close(stated_terms[t], terms_unc[t])
                       for t in TERMS):
                problems.append(f"combined_uncertainty.terms_mm_yr {stated_terms} do not recompute ({terms_unc})")
            for k, want in (("quadrature_mm_yr", quad), ("bar_mm_yr", bar)):
                v = cu.get(k)
                if not isinstance(v, (int, float)) or not close(v, want):
                    problems.append(f"combined_uncertainty.{k} {v} does not recompute ({want})")
            if cu.get("deep_steric_systematic_mm_yr") != deep:
                problems.append("deep_steric_systematic_mm_yr is not the sanctioned statement")
            vd = r.get("verdict") or {}
            gap = trends["residual"]["trend"] - deep["value"]
            closed = abs(gap) <= bar
            if (not isinstance(vd.get("closure_gap_mm_yr"), (int, float)) or not close(vd["closure_gap_mm_yr"], gap)
                    or not isinstance(vd.get("bar_mm_yr"), (int, float)) or not close(vd["bar_mm_yr"], bar)
                    or vd.get("closed_within_uncertainty") is not closed):
                problems.append(f"verdict {vd.get('closed_within_uncertainty')} gap {vd.get('closure_gap_mm_yr')} "
                                f"bar {vd.get('bar_mm_yr')} does not recompute (closed {closed}, gap {gap}, bar {bar})")
        rec_ok = not problems
        rec_detail = ("; ".join(problems) if problems else
                      "four trends with intervals, formal errors, the combined uncertainty and the verdict "
                      "recompute" + ("; hole-free period bound to the shared attester chain"
                                     if len(used) == n_cal else f"; {len(miss)} holes, epoch fit"))
    check("recompute", rec_ok, rec_detail)

    # bookkeeping
    book = r.get("bookkeeping") or {}
    lacking = [f"{sec}.{key}" for sec, key in mod.REQUIRED_BOOKKEEPING
               if not (isinstance(book.get(sec), dict) and book[sec].get(key) not in (None, ""))]
    gh = book.get("gap_handling") if isinstance(book.get("gap_handling"), dict) else {}
    crosses = bool(start) and mod.crosses_gap(start, end)
    bridge = gh.get("bridge")
    book_ok = (not lacking
               and isinstance(book.get("deep_steric"), dict)
               and book["deep_steric"].get("systematic_mm_yr") == dict(mod.DEEP_STERIC_MM_YR)
               and isinstance(gh.get("rule"), str) and gh.get("rule")
               and gh.get("months_missing") == miss
               and gh.get("crosses_intermission_gap") is crosses
               and bridge == bound.get("bridge")
               and (not crosses or (isinstance(bridge, str) and bridge.strip())))
    check("bookkeeping", book_ok,
          (f"lacks {lacking}; " if lacking else "corrections table complete; ")
          + f"gap handling lists {len(miss)} missing months; crosses the gap {crosses}, bridge {bridge!r}")

    # plausibility
    if fx is not None and rec_ok:
        offset = float(data.get("fixture_offset_mm", 0.0))
        vd, trends, truth = r["verdict"], r["trends"], mod.TRUTH
        near = {t: abs(trends[t]["trend"] - truth[f"{t}_mm_yr"]) for t in TERMS}
        if offset == 0.0:
            ok = (vd.get("closed_within_uncertainty") is True
                  and abs(vd["closure_gap_mm_yr"]) <= vd["bar_mm_yr"]
                  and all(v <= TRUTH_BAND_MM_YR for v in near.values()))
            detail = (f"known truth: closure gap {vd['closure_gap_mm_yr']:+.4f} within bar {vd['bar_mm_yr']:.4f}, "
                      f"verdict closed {vd.get('closed_within_uncertainty')}; term trends within "
                      f"{TRUTH_BAND_MM_YR} mm/yr of the imposed ones: {all(v <= TRUTH_BAND_MM_YR for v in near.values())}")
        else:
            ok = True
            detail = (f"offset {offset} mm injected after the gap: no closure requirement; the verdict "
                      f"({vd.get('closed_within_uncertainty')}) stands on the recompute")
        check("plausible", ok, detail)
    elif fx is not None:
        check("plausible", False, "not checkable: the recompute failed")
    else:
        check("plausible", True, "a data root carries no known truth; the verdict stands on the recompute")

    verdict = "PASS" if all(c["ok"] for c in checks) else "FAIL"
    return verdict, False, checks, r


def attestation_doc(verdict, refusal, checks, r, receipt_path, computation):
    return {
        "verdict": verdict,
        "refusal": refusal,
        "attester": "skills/sea-level-budget/scripts/sea_level_budget_check.py",
        "attester_sha256": sha256_file(Path(__file__).resolve()),
        "computation_sha256": sha256_file(computation),
        "receipt": receipt_path.name,
        "receipt_sha256": sha256_file(receipt_path),
        "run_id": r.get("run_id"),
        "capability": r.get("capability") or {},
        "bundle": r.get("bundle") or {},
        "runtime": r.get("runtime") or {},
        "attested_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "checks": checks,
    }


def report(verdict, refusal, checks, r) -> str:
    lines = [f"  {'ok  ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}" for c in checks]
    bound = r.get("bound_parameters") or {}
    if verdict != "PASS":
        first = next(c for c in checks if not c["ok"])
        lines.append(f"FAIL {first['name']}: {first['detail']}")
    elif refusal:
        lines.append(f"PASS refusal ({r.get('reason_code')}) run {r.get('run_id')}: period "
                     f"{bound.get('period')} refused, {r.get('reason')}")
    else:
        v, t = r["verdict"], r["trends"]
        lines.append(f"PASS run {r.get('run_id')}: period {bound.get('period')}, "
                     f"{r['months']['n_used']} of {r['months']['n_calendar']} months, residual trend "
                     f"{t['residual']['trend']:+.4f} mm/yr [{t['residual']['ci_low']:+.4f}, "
                     f"{t['residual']['ci_high']:+.4f}], closure gap {v['closure_gap_mm_yr']:+.4f} against "
                     f"bar {v['bar_mm_yr']:.4f}, closed_within_uncertainty "
                     f"{str(v['closed_within_uncertainty']).lower()} (recomputed)")
    return "\n".join(lines)


# ---- selftest

def selftest(computation: Path) -> int:
    mod = load(computation)

    def run(argv, path):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main([*argv, "--runtime", "selftest", "--receipt", str(path)])
        return rc

    def verdict_of(path, comp=None):
        v, refusal, checks, _ = attest(path, comp or computation)
        failed = [c["name"] for c in checks if not c["ok"]]
        return v, refusal, failed

    def first_fail(path, comp=None):
        """The check the verdict line names: the first that fails (a
        later check that depends on it is named too, so only the first
        is the tamper's own)."""
        v, _, failed = verdict_of(path, comp)
        return failed[0] if v == "FAIL" and failed else None

    def tampered(src: Path, dst: Path, edit):
        doc = json.loads(src.read_text(encoding="utf-8"))
        edit(doc)
        dst.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        return dst

    with tempfile.TemporaryDirectory() as d:
        w = Path(d)
        ref = w / "ref.json"
        assert run(["--fixture", "--seed", "7", "--period", "2005-01:2016-12"], ref) == 0
        assert verdict_of(ref) == ("PASS", False, []), verdict_of(ref)

        # a hole-free period is bound to the shared chain as well
        hf = w / "holefree.json"
        assert run(["--fixture", "--seed", "7", "--period", "2005-01:2010-12"], hf) == 0
        v, refusal, checks, _ = attest(hf, computation)
        assert v == "PASS" and "shared attester chain" in checks[6]["detail"], checks

        # tampers, each failing on its check
        t1 = tampered(ref, w / "t1.json", lambda r: r["series"]["mass_mm"].__setitem__(3, r["series"]["mass_mm"][3] + 1e-6))
        assert first_fail(t1) == "series", verdict_of(t1)
        t2 = tampered(ref, w / "t2.json", lambda r: r["trends"]["mass"].__setitem__("trend", r["trends"]["mass"]["trend"] * 1.001))
        assert first_fail(t2) == "recompute", verdict_of(t2)
        t3 = tampered(ref, w / "t3.json", lambda r: r["verdict"].__setitem__("closed_within_uncertainty", False))
        assert first_fail(t3) == "recompute", verdict_of(t3)
        t4 = tampered(ref, w / "t4.json", lambda r: r["trends"]["altimetry"].__setitem__("half_width", r["trends"]["altimetry"]["half_width"] / 2))
        assert first_fail(t4) == "recompute", verdict_of(t4)
        t5 = tampered(ref, w / "t5.json", lambda r: r["bookkeeping"]["gia"].pop("mass"))
        assert verdict_of(t5)[2] == ["bookkeeping"], verdict_of(t5)
        t6 = tampered(ref, w / "t6.json", lambda r: r["runtime"].__setitem__("name", ""))
        assert verdict_of(t6)[2] == ["runtime"], verdict_of(t6)
        t7 = tampered(ref, w / "t7.json", lambda r: r["data"].__setitem__("seed", 8))
        assert first_fail(t7) == "data", verdict_of(t7)

        # wrong release: the bundle block names another version, or the
        # capability block is malformed
        w1 = tampered(ref, w / "w1.json", lambda r: r["bundle"].__setitem__("version", "0.0.0"))
        assert verdict_of(w1)[2] == ["release"], verdict_of(w1)
        w2 = tampered(ref, w / "w2.json", lambda r: r["capability"].__setitem__("name", ""))
        assert verdict_of(w2)[2] == ["release"], verdict_of(w2)

        # a tampered computation fails code and the generator digest
        bad = w / "sea_level_budget.py"
        bad.write_bytes(computation.read_bytes() + b"\n")
        (w / "ecco_trend_ci.py").write_bytes(method_beside(computation).read_bytes())
        v, _, failed = verdict_of(ref, bad)
        assert v == "FAIL" and "code" in failed and "data" in failed, failed

        # a refusal attests PASS as a refusal, exit 3 from the executor
        rf = w / "refused.json"
        assert run(["--fixture", "--seed", "7", "--period", "2016-01:2019-12"], rf) == 3
        v, refusal, checks, r = attest(rf, computation)
        assert (v, refusal) == ("PASS", True) and r["reason_code"] == "gap-without-bridge", checks
        assert "refusal" in report(v, refusal, checks, r)
        too_few = w / "toofew.json"
        assert run(["--fixture", "--seed", "7", "--period", "2017-01:2018-12"], too_few) == 3
        assert verdict_of(too_few) == ("PASS", True, []), verdict_of(too_few)
        outside = w / "outside.json"
        assert run(["--fixture", "--seed", "7", "--period", "2001-01:2010-12"], outside) == 3
        assert verdict_of(outside) == ("PASS", True, []), verdict_of(outside)
        # a forged refusal is not reproduced
        forged = tampered(rf, w / "forged.json", lambda r: r["bound_parameters"].__setitem__("period", "2005-01:2016-12"))
        assert verdict_of(forged)[2] == ["refusal"], verdict_of(forged)

        # across the gap: bridged it computes; with the bridge stripped it fails bookkeeping
        br = w / "bridged.json"
        assert run(["--fixture", "--seed", "7", "--period", "2016-01:2019-12",
                    "--bridge", "selftest: a continuity citation"], br) == 0
        assert verdict_of(br) == ("PASS", False, []), verdict_of(br)
        nb = tampered(br, w / "nobridge.json", lambda r: (r["bookkeeping"]["gap_handling"].__setitem__("bridge", None),
                                                          r["bound_parameters"].__setitem__("bridge", None)))
        assert verdict_of(nb)[2] == ["bookkeeping"], verdict_of(nb)
        # and an injected offset across the bridged gap fails to close, on the recompute's word
        off = w / "offset.json"
        assert run(["--fixture", "--seed", "7", "--fixture-offset", "8", "--period", "2016-01:2019-12",
                    "--bridge", "selftest: a continuity citation"], off) == 0
        v, refusal, checks, r = attest(off, computation)
        assert v == "PASS" and r["verdict"]["closed_within_uncertainty"] is False, checks

        # the attestation document carries the verdict and the identity blocks
        doc = attestation_doc(*attest(ref, computation), ref, computation)
        assert doc["verdict"] == "PASS" and doc["capability"]["name"] and doc["runtime"]["name"] == "selftest"
        assert {c["name"] for c in doc["checks"]} == {"fields", "code", "release", "runtime", "data",
                                                       "series", "recompute", "bookkeeping", "plausible"}
    print("sea_level_budget_check selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("receipt", nargs="?", type=Path)
    ap.add_argument("--computation", type=Path, default=DEFAULT_COMPUTATION)
    ap.add_argument("--out", type=Path, default=None, help="write the attestation JSON here")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    computation = args.computation.resolve()
    if args.selftest:
        return selftest(computation)
    if not args.receipt:
        ap.error("give a receipt, or --selftest")
    verdict, refusal, checks, r = attest(args.receipt, computation)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(attestation_doc(verdict, refusal, checks, r, args.receipt,
                                                       computation), indent=2) + "\n",
                            encoding="utf-8")
    print(report(verdict, refusal, checks, r) + (f"; attestation {args.out}" if args.out else ""))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
