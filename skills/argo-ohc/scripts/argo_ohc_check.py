#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Deterministic attester for the attested Argo ocean heat content
change (argo_ohc.py). Stdlib only, consumer side, no language model.

A receipt from any runtime attests PASS (exit 0) only when ALL hold,
else FAIL (exit 1) naming the check; one line per check, `PASS name`
or `FAIL name: reason`:

  fields       every declared receipt field is present;
  code         the receipt's code_sha256 is the sanctioned executor
               beside this file (or the one --computation names), so an
               edited computation invalidates every earlier receipt;
  release      the receipt's bundle block names this tree's package
               name, version and release lock digest, and its capability
               block is well formed;
  runtime      the receipt names the runtime that produced it;
  data         a fixture regenerated here at the receipt's seed and
               depth hashes to the receipt's digest, and the generator
               (the executor itself) to the receipt's generator digest;
               for a data root, the record name, the record's digest,
               the two files read and the stamp are present, and with
               --data-root DIR the record, the CSV and the stamp in
               that tree hash to the receipt's digests (without the
               tree the check says the digests were not verified);
  series       the months used and missing partition the window, and on
               a fixture the values and uncertainties are what the
               regenerated fixture yields (1e-9);
  recompute    the trend, its interval, its formal error, the change,
               the endpoint change, the residual, the combined
               uncertainty, the verdict, the rates per unit area and
               the anchor distance recomputed here from the series
               match the receipt (1e-9 relative): an independent
               recompute of the method statement, with its own
               Student's t from the density;
  bookkeeping  every required statement is present, the deep omission
               carries the sanctioned published statement, and the
               window handling lists exactly the months missing;
  plausible    stated bounds: the trend within 40 ZJ per year of zero
               (four times the published 0 to 2000 m rate), the
               per-month uncertainty positive and below 50 ZJ, the
               domain area between 1e14 and 4e14 square meters, and on
               the fixture the known truth: the planted rate within
               1.5 ZJ per year of the recovered one and the known_truth
               block agreeing with the recompute.

A refusal receipt (refused true) attests PASS only as a refusal: the
identity checks hold, the reason code is one the executor issues, and
the refusal is reproduced here from the window and the regenerated
fixture, or from the tree --data-root names (its stamp's coverage,
its CSV's months, or the executor's own compute on its series). A
data-root refusal with no tree given is taken on the executor's word
and is not reproduced, so it FAILS. The verdict line of a reproduced
refusal reads `PASS refusal`, and the exit is 0.

--out writes the attestation: the verdict, whether it is a refusal, the
attester's and the computation's digests, the receipt's digest and run
id, the capability, bundle and runtime blocks copied from the receipt,
and every check.

  argo_ohc_check.py RECEIPT.json [--computation PATH] [--data-root DIR] [--out ATTESTATION.json]
  argo_ohc_check.py --selftest
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

HERE = Path(__file__).resolve().parent
DEFAULT_COMPUTATION = HERE / "argo_ohc.py"
FIELDS = ("run_id", "computation", "code_sha256", "capability", "bundle", "runtime",
          "generated_utc", "data", "bound_parameters", "refused", "months", "series",
          "terms", "trend_ZJ_yr", "change_ZJ", "endpoint_change_ZJ", "residual",
          "combined_uncertainty", "verdict", "anchor", "bookkeeping", "known_truth", "caveats")
REFUSAL_FIELDS = ("run_id", "computation", "code_sha256", "capability", "bundle",
                  "runtime", "generated_utc", "data", "bound_parameters", "refused",
                  "reason_code", "reason")
TERMS = ("trend", "change", "endpoint_change", "deep_omission")
REL_TOL = 1e-9
ROUNDING = 5.0e-5
TREND_BOUND_ZJ_YR = 40.0
UNCERTAINTY_BOUND_ZJ = 50.0
DOMAIN_AREA_BOUNDS_M2 = (1.0e14, 4.0e14)
TRUTH_BAND_ZJ_YR = 1.5
CONFIDENCE = 0.95
Z95 = 1.959963984540054


def load(path: Path):
    spec = importlib.util.spec_from_file_location("argo_ohc", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def ym(d: str) -> int:
    return int(d[:4]) * 12 + int(d[5:7]) - 1


def label(k: int) -> str:
    return f"{k // 12:04d}-{k % 12 + 1:02d}"


def close(a, b, tol=REL_TOL) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def numbers(v, n=None) -> bool:
    return isinstance(v, list) and (n is None or len(v) == n) and all(number(x) for x in v)


# ---- Student's t from the density, integrated: an independent route

def t_density(x, df):
    c = math.exp(math.lgamma((df + 1.0) / 2.0) - math.lgamma(df / 2.0)) / math.sqrt(df * math.pi)
    return c * (1.0 + x * x / df) ** (-(df + 1.0) / 2.0)


def t_cdf(t, df, panels=8000):
    """Composite Simpson from 0 to t, plus one half."""
    if t == 0.0:
        return 0.5
    a, b = 0.0, abs(t)
    h = (b - a) / panels
    s = t_density(a, df) + t_density(b, df)
    for i in range(1, panels):
        s += (4.0 if i % 2 else 2.0) * t_density(a + i * h, df)
    area = s * h / 3.0
    return 0.5 + area if t > 0 else 0.5 - area


def t_quantile(p, df):
    lo, hi = 0.0, 1.0
    while t_cdf(hi, df) < p:
        hi *= 2.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-14 * max(1.0, hi):
            break
    return 0.5 * (lo + hi)


# ---- the independent recompute of the method statement

def recompute_trend(t_cal, y, unc):
    """From the statement: calendar-month group means off the series
    and off the epoch index, least squares, lag-1 autocorrelation over
    adjacent epochs, n_eff capped at n, t on n_eff minus 2; the formal
    error from the slope weights and the per-month uncertainties."""
    n = len(y)
    if n < 3:
        return None
    by_month = {}
    for i, k in enumerate(t_cal):
        by_month.setdefault(k % 12, []).append(i)
    tt = [float(k) for k in t_cal]
    yy = [float(v) for v in y]
    for idx in by_month.values():
        mt = sum(tt[i] for i in idx) / len(idx)
        my = sum(yy[i] for i in idx) / len(idx)
        for i in idx:
            tt[i] -= mt
            yy[i] -= my
    tm, ymean = sum(tt) / n, sum(yy) / n
    cov = sum((a - tm) * (b - ymean) for a, b in zip(tt, yy))
    var = sum((a - tm) ** 2 for a in tt)
    slope = cov / var
    resid = [b - ymean - slope * (a - tm) for a, b in zip(tt, yy)]
    ss = sum(r * r for r in resid)
    formal = math.sqrt(sum(((a - tm) / var * s) ** 2 for a, s in zip(tt, unc)))
    out = {"n": n, "trend": slope * 12.0, "formal_95": Z95 * formal * 12.0, "interval": False}
    r1 = (sum(resid[i] * resid[i + 1] for i in range(n - 1) if t_cal[i + 1] - t_cal[i] == 1) / ss
          if ss > 0 else 0.0)
    n_eff = min(float(n), n * (1.0 - r1) / (1.0 + r1))
    dof = n_eff - 2.0
    out.update({"r1": r1, "n_eff": n_eff, "dof": dof})
    if dof < 1.0:
        return out
    se = math.sqrt(ss / dof / var)
    tq = t_quantile(0.5 + CONFIDENCE / 2.0, dof)
    half = tq * se * 12.0
    out.update({"interval": True, "se": se * 12.0, "t_quantile": tq, "half_width": half,
                "ci_low": out["trend"] - half, "ci_high": out["trend"] + half})
    return out


def check_interval(block, c):
    """None when the block recomputes, else why not."""
    if not isinstance(block, dict):
        return "interval block missing or not an object"
    if block.get("confidence") != CONFIDENCE or block.get("n") != c["n"]:
        return f"confidence {block.get('confidence')} or n {block.get('n')} (series has {c['n']})"
    if block.get("deseasonalize") != "climatology":
        return "deseasonalize is not the climatology policy"
    for k in ("trend", "r1", "n_eff", "dof"):
        if not number(block.get(k)) or not close(block[k], c[k]):
            return f"{k} {block.get(k)} does not recompute ({c[k]})"
    if not number(block.get("formal_95_ZJ_yr")) or not close(block["formal_95_ZJ_yr"], c["formal_95"]):
        return f"formal_95_ZJ_yr {block.get('formal_95_ZJ_yr')} does not recompute ({c['formal_95']})"
    if block.get("stated") is not True:
        return "a computed receipt must state its interval"
    if not c["interval"]:
        return "block states an interval the recompute refuses"
    for k in ("ci_low", "ci_high", "half_width", "se", "t_quantile"):
        if not number(block.get(k)) or not close(block[k], c[k]):
            return f"{k} {block.get(k)} does not recompute ({c[k]})"
    if block.get("significant_at_confidence") is not (c["ci_low"] * c["ci_high"] > 0):
        return "significance flag disagrees with the interval"
    return None


# ---- the attestation

def attest(receipt_path: Path, computation: Path, data_root=None):
    """(verdict, refusal, checks, receipt) for one receipt; data_root
    is the tree a data-root receipt is verified against, when given."""
    checks = []
    tree = Path(data_root).expanduser().resolve() if data_root else None
    tree_series = None

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
          f"bundle {bundle} vs this tree {identity}; capability "
          f"{'well formed' if cap_ok else 'malformed'}")
    rt = r.get("runtime") or {}
    check("runtime", isinstance(rt, dict) and isinstance(rt.get("name"), str) and bool(rt.get("name")),
          f"runtime {rt.get('name')!r} {rt.get('version') or ''}".strip())

    data = r.get("data") or {}
    bound = r.get("bound_parameters") or {}
    window = str(bound.get("window", ""))
    depth = bound.get("depth")
    m = re.fullmatch(r"(\d{4}-\d{2}):(\d{4}-\d{2})", window)
    start, end = (m.group(1), m.group(2)) if m else (None, None)
    depth_ok = depth in mod.DEPTHS
    fx = None
    coverage = None
    if data.get("mode") == "fixture":
        seed = data.get("seed")
        ok = isinstance(seed, int) and depth_ok and data.get("depth") == depth
        if ok:
            fx = mod.make_fixture(seed, depth)
            digest = mod.fixture_digest(fx)
            ok = (data.get("digest") == digest and data.get("generator_sha256") == sanctioned
                  and data.get("span") == list(mod.FIXTURE_SPAN)
                  and data.get("truth") == mod.TRUTH[depth])
            detail = (f"regenerated fixture at seed {seed} depth {depth}: {digest}; receipt "
                      f"{data.get('digest')}; generator match {data.get('generator_sha256') == sanctioned}")
            coverage = tuple(mod.FIXTURE_SPAN)
        else:
            detail = "fixture seed or depth missing or malformed"
        check("data", ok, detail)
    elif data.get("mode") == "data-root":
        stamp = data.get("stamp")
        files = data.get("files")
        ok = (depth_ok and isinstance(data.get("record"), str) and data.get("record")
              and re.fullmatch(r"sha256:[0-9a-f]{64}", str(data.get("record_sha256")))
              and isinstance(data.get("manifest_sha256"), str)
              and isinstance(files, dict)
              and set(files) == {f"ohc-{depth}.csv", f"ohc-{depth}-stamp.json"}
              and all(re.fullmatch(r"sha256:[0-9a-f]{64}", str(v)) for v in files.values())
              and isinstance(stamp, dict) and isinstance(stamp.get("months"), list)
              and len(stamp["months"]) == 2)
        if ok:
            coverage = (stamp["months"][0], stamp["months"][1])
        detail = f"data root {data.get('data_root')} record {data.get('record')} ({data.get('record_sha256')})"
        if ok and tree is not None:
            problems = []
            rec_path = tree / "RECORD.json"
            if not rec_path.is_file():
                problems.append(f"{tree} carries no RECORD.json")
            else:
                if sha256_file(rec_path) != data["record_sha256"]:
                    problems.append("RECORD.json in the tree does not hash to the receipt's record_sha256")
                try:
                    rec = json.loads(rec_path.read_text(encoding="utf-8"))
                    if rec.get("record") != data["record"] or rec.get("manifest_sha256") != data["manifest_sha256"]:
                        problems.append("the tree's record name or manifest digest differs from the receipt's")
                except ValueError:
                    problems.append("RECORD.json in the tree is not JSON")
            for name, digest in files.items():
                fp = tree / name
                if not fp.is_file():
                    problems.append(f"{name} is missing from the tree")
                elif sha256_file(fp) != digest:
                    problems.append(f"{name} in the tree does not hash to the receipt's digest")
            stamp_path = tree / f"ohc-{depth}-stamp.json"
            if stamp_path.is_file():
                try:
                    if json.loads(stamp_path.read_text(encoding="utf-8")) != stamp:
                        problems.append("the stamp copied into the receipt differs from the tree's")
                except ValueError:
                    problems.append("the tree's stamp is not JSON")
            csv_path = tree / f"ohc-{depth}.csv"
            if csv_path.is_file() and not problems:
                tree_series = mod.read_csv_series(csv_path)
            ok = not problems
            detail += ("; verified against the tree: RECORD.json, the CSV and the stamp hash to the "
                       "receipt's digests" if ok else "; " + "; ".join(problems))
        elif ok:
            detail += "; digests well formed but NOT verified against a tree (give --data-root)"
        check("data", ok, detail)
    else:
        check("data", False, f"data mode {data.get('mode')!r} is neither fixture nor data-root")

    if refusal:
        code = r.get("reason_code")
        recognized = code in mod.REASONS
        reproduced, why = False, "reason not reproduced"
        series_for = fx["series"] if fx else tree_series
        if recognized and start and coverage and data.get("mode") == "data-root" and tree is None:
            why = ("a data-root refusal is taken on the executor's word and not reproduced: "
                   "give --data-root to reproduce it from the tree")
        elif recognized and start and coverage:
            if code == "window-outside-coverage":
                reproduced = not (ym(coverage[0]) <= ym(start) and ym(end) <= ym(coverage[1]))
                why = f"the window {window} leaves {coverage[0]}..{coverage[1]}: {reproduced}"
            elif code == "too-few-months" and series_for:
                n_cal = ym(end) - ym(start) + 1
                have = set(series_for["dates"])
                cal = [label(k) for k in range(ym(start), ym(end) + 1)]
                used = [d for d in cal if d in have]
                first = sum(d in have for d in cal[:mod.END_MONTHS])
                last = sum(d in have for d in cal[-mod.END_MONTHS:])
                reproduced = (n_cal < mod.MIN_MONTHS or len(used) < mod.MIN_MONTHS
                              or first < mod.END_MONTHS or last < mod.END_MONTHS)
                why = (f"{len(used)} of {n_cal} months, first year {first}, last year {last}, "
                       f"floor {mod.MIN_MONTHS}: {reproduced}")
            elif code == "interval-not-stated" and series_for:
                book = mod.FIXTURE_BOOKKEEPING if fx else (json.loads((tree / "RECORD.json").read_text(
                    encoding="utf-8")).get("bookkeeping") or {})
                body, again = mod.compute(series_for, start, end, depth, book, None)
                reproduced = body is None and again[0] == code
                why = f"the executor's compute refuses the same way: {reproduced}"
            else:
                why = "the series to reproduce the refusal from is not available"
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
    months_ok = (bool(start) and months.get("window") == [start, end]
                 and months.get("n_calendar") == n_cal and months.get("n_used") == len(used)
                 and sorted(used + miss) == cal and len(set(used)) == len(used)
                 and len(used) >= mod.MIN_MONTHS
                 and months.get("first_year") == [d for d in cal[:mod.END_MONTHS] if d in set(used)]
                 and months.get("last_year") == [d for d in cal[-mod.END_MONTHS:] if d in set(used)]
                 and len(months.get("first_year") or []) == mod.END_MONTHS
                 and len(months.get("last_year") or []) == mod.END_MONTHS)
    s = r.get("series") or {}
    series_ok = (months_ok and s.get("dates") == used and numbers(s.get("value_ZJ"), len(used))
                 and numbers(s.get("uncertainty_ZJ"), len(used)))
    detail = "months and series well formed" if series_ok else "months or series malformed"
    if series_ok and fx:
        by = {d: (v, u) for d, v, u in zip(fx["series"]["dates"], fx["series"]["value_ZJ"],
                                           fx["series"]["uncertainty_ZJ"])}
        expect_used = [d for d in cal if d in by]
        maxdev = max([abs(by[d][0] - s["value_ZJ"][i]) for i, d in enumerate(used) if d in by]
                     + [abs(by[d][1] - s["uncertainty_ZJ"][i]) for i, d in enumerate(used) if d in by]
                     + [0.0])
        series_ok = used == expect_used and maxdev <= 1e-9
        detail += (f"; {len(used)} of {n_cal} months as the regenerated fixture yields "
                   f"(max deviation {maxdev:.2e})")
    check("series", series_ok, detail)

    # recompute
    rec_ok, rec_detail = False, "series not checkable"
    terms = r.get("terms") or {}
    if series_ok:
        problems = []
        t_cal = [ym(d) - ym(start) for d in used]
        y, u = s["value_ZJ"], s["uncertainty_ZJ"]
        c = recompute_trend(t_cal, y, u)
        tr = terms.get("trend") if isinstance(terms.get("trend"), dict) else {}
        err = check_interval(tr.get("interval"), c) if c else "too short to recompute"
        if err:
            problems.append(f"terms.trend.interval: {err}")
        else:
            block = tr["interval"]
            trend_unc = max(block["half_width"], block["formal_95_ZJ_yr"])
            span = (n_cal - mod.END_MONTHS) / 12.0
            change = c["trend"] * span
            change_unc = trend_unc * span
            by = {d: (v, w) for d, v, w in zip(used, y, u)}
            first, last = months["first_year"], months["last_year"]
            m_first = sum(by[d][0] for d in first) / mod.END_MONTHS
            m_last = sum(by[d][0] for d in last) / mod.END_MONTHS
            end_change = m_last - m_first
            inflation = max(1.0, (1.0 + c["r1"]) / (1.0 - c["r1"]))
            end_unc = Z95 * math.sqrt(inflation * (sum(by[d][1] ** 2 for d in first) / mod.END_MONTHS ** 2
                                                   + sum(by[d][1] ** 2 for d in last) / mod.END_MONTHS ** 2))
            residual = end_change - change
            combined = math.sqrt(change_unc ** 2 + end_unc ** 2)
            ch = terms.get("change") if isinstance(terms.get("change"), dict) else {}
            ec = terms.get("endpoint_change") if isinstance(terms.get("endpoint_change"), dict) else {}
            want = [("terms.trend.value", tr.get("value"), c["trend"]),
                    ("terms.trend.uncertainty", tr.get("uncertainty"), trend_unc),
                    ("terms.change.value", ch.get("value"), change),
                    ("terms.change.uncertainty", ch.get("uncertainty"), change_unc),
                    ("terms.change.span_years", ch.get("span_years"), span),
                    ("terms.endpoint_change.value", ec.get("value"), end_change),
                    ("terms.endpoint_change.uncertainty", ec.get("uncertainty"), end_unc),
                    ("terms.endpoint_change.autocorrelation_inflation", ec.get("autocorrelation_inflation"), inflation),
                    ("terms.endpoint_change.first_year_mean_ZJ", ec.get("first_year_mean_ZJ"), m_first),
                    ("terms.endpoint_change.last_year_mean_ZJ", ec.get("last_year_mean_ZJ"), m_last),
                    ("residual.value", (r.get("residual") or {}).get("value"), residual),
                    ("combined_uncertainty.value", (r.get("combined_uncertainty") or {}).get("value"), combined),
                    ("verdict.residual_ZJ", (r.get("verdict") or {}).get("residual_ZJ"), residual),
                    ("verdict.bar_ZJ", (r.get("verdict") or {}).get("bar_ZJ"), combined)]
            for name, v, w in want:
                if not number(v) or not close(v, w):
                    problems.append(f"{name} {v} does not recompute ({w})")
            if (r.get("verdict") or {}).get("consistent_within_uncertainty") is not (abs(residual) <= combined):
                problems.append("verdict.consistent_within_uncertainty disagrees with the recompute")
            for name, v, w in (("trend_ZJ_yr", r.get("trend_ZJ_yr"), c["trend"]),
                               ("change_ZJ", r.get("change_ZJ"), change),
                               ("endpoint_change_ZJ", r.get("endpoint_change_ZJ"), end_change)):
                if not number(v) or abs(v - w) > ROUNDING + 1e-9:
                    problems.append(f"{name} {v} is not the term rounded ({w})")
            # units and stamps on every term
            for name in TERMS:
                term = terms.get(name)
                if not isinstance(term, dict) or "units" not in term or "stamp" not in term:
                    problems.append(f"terms.{name} lacks units or stamp")
            deep = terms.get("deep_omission") if isinstance(terms.get("deep_omission"), dict) else {}
            if deep.get("omitted") is not True or deep.get("value") is not None \
                    or deep.get("published") != mod.DEEP_OMISSION:
                problems.append("terms.deep_omission is not the sanctioned omission statement")
            # rates per unit area
            pa = tr.get("per_area") if isinstance(tr.get("per_area"), dict) else {}
            area = (r.get("bookkeeping") or {}).get("coverage", {}).get("domain_area_m2")
            if not number(area) or not number(pa.get("domain_area_m2")) or not close(pa["domain_area_m2"], area):
                problems.append("per_area.domain_area_m2 is not the bookkeeping coverage area")
            else:
                w_dom = c["trend"] * mod.ZJ / mod.SECONDS_PER_YEAR / area
                w_earth = c["trend"] * mod.ZJ / mod.SECONDS_PER_YEAR / mod.EARTH_AREA_M2
                for name, v, want_v in (("W_m2_of_domain", pa.get("W_m2_of_domain"), w_dom),
                                        ("W_m2_of_earth_surface", pa.get("W_m2_of_earth_surface"), w_earth),
                                        ("earth_surface_area_m2", pa.get("earth_surface_area_m2"), mod.EARTH_AREA_M2)):
                    if not number(v) or not close(v, want_v):
                        problems.append(f"per_area.{name} {v} does not recompute ({want_v})")
                # the anchor distance
                an = r.get("anchor")
                if an is not None:
                    pub = an.get("published") if isinstance(an, dict) else None
                    if not isinstance(pub, dict) or not number(pub.get("value_W_m2_global")):
                        problems.append("anchor carries no published value")
                    else:
                        a = float(pub["value_W_m2_global"])
                        ua = float(pub.get("uncertainty_W_m2_global") or 0.0)
                        pairs = [("run_W_m2_of_earth_surface", w_earth), ("run_W_m2_of_domain", w_dom),
                                 ("run_ZJ_yr", c["trend"]),
                                 ("anchor_ZJ_yr", a * mod.EARTH_AREA_M2 * mod.SECONDS_PER_YEAR / mod.ZJ),
                                 ("distance_W_m2_of_earth_surface", w_earth - a)]
                        if ua > 0:
                            pairs.append(("distance_over_anchor_uncertainty", (w_earth - a) / ua))
                        frac = pub.get("ocean_area_fraction")
                        if number(frac) and frac > 0:
                            pairs.append(("distance_W_m2_of_ocean", w_dom - a / frac))
                        for name, want_v in pairs:
                            v = an.get(name)
                            if not number(v) or not close(v, want_v):
                                problems.append(f"anchor.{name} {v} does not recompute ({want_v})")
        rec_ok = not problems
        rec_detail = ("; ".join(problems) if problems else
                      "trend, interval, formal error, change, endpoint change, residual, combined "
                      "uncertainty, verdict, rates per unit area and anchor distance recompute")
    check("recompute", rec_ok, rec_detail)

    # bookkeeping
    book = r.get("bookkeeping") or {}
    lacking = [f"{sec}.{key}" for sec, key in mod.REQUIRED_BOOKKEEPING
               if not (isinstance(book.get(sec), dict) and book[sec].get(key) not in (None, ""))]
    wh = book.get("window_handling") if isinstance(book.get("window_handling"), dict) else {}
    deep_ok = isinstance(book.get("deep_omission"), dict) and book["deep_omission"].get("published") == mod.DEEP_OMISSION
    book_ok = (not lacking and deep_ok and isinstance(wh.get("rule"), str) and wh.get("rule")
               and wh.get("months_missing") == miss)
    check("bookkeeping", book_ok,
          (f"lacks {lacking}; " if lacking else "statements complete; ")
          + f"deep omission {'sanctioned' if deep_ok else 'not the sanctioned statement'}; "
          f"window handling lists {len(miss)} missing months")

    # plausibility
    if rec_ok:
        tr = terms["trend"]
        area = float(book["coverage"]["domain_area_m2"])
        bounds_ok = (abs(tr["value"]) <= TREND_BOUND_ZJ_YR
                     and all(0.0 < v <= UNCERTAINTY_BOUND_ZJ for v in s["uncertainty_ZJ"])
                     and DOMAIN_AREA_BOUNDS_M2[0] <= area <= DOMAIN_AREA_BOUNDS_M2[1])
        detail = (f"trend {tr['value']:+.4f} within {TREND_BOUND_ZJ_YR} ZJ/yr; per-month uncertainty "
                  f"in (0, {UNCERTAINTY_BOUND_ZJ}]; domain area {area:.3e} m2 within bounds: {bounds_ok}")
        if fx is not None:
            truth = mod.TRUTH[depth]["rate_ZJ_yr"]
            kt = r.get("known_truth") if isinstance(r.get("known_truth"), dict) else {}
            block = tr["interval"]
            truth_ok = (abs(tr["value"] - truth) <= TRUTH_BAND_ZJ_YR
                        and number(kt.get("planted_rate_ZJ_yr")) and kt["planted_rate_ZJ_yr"] == truth
                        and number(kt.get("planted_change_ZJ"))
                        and close(kt["planted_change_ZJ"], truth * terms["change"]["span_years"])
                        and kt.get("rate_inside_interval") is (block["ci_low"] <= truth <= block["ci_high"])
                        and kt.get("change_within_uncertainty") is (
                            abs(kt["planted_change_ZJ"] - terms["change"]["value"]) <= terms["change"]["uncertainty"]))
            detail += (f"; known truth: planted {truth} ZJ/yr against recovered {tr['value']:+.4f} "
                       f"(band {TRUTH_BAND_ZJ_YR}), known_truth block agrees: {truth_ok}")
            bounds_ok = bounds_ok and truth_ok
        else:
            detail += "; a data root carries no known truth; the verdict stands on the recompute"
            bounds_ok = bounds_ok and r.get("known_truth") is None
        check("plausible", bounds_ok, detail)
    else:
        check("plausible", False, "not checkable: the recompute failed")

    verdict = "PASS" if all(c["ok"] for c in checks) else "FAIL"
    return verdict, False, checks, r


def attestation_doc(verdict, refusal, checks, r, receipt_path, computation):
    return {
        "verdict": verdict,
        "refusal": refusal,
        "attester": "skills/argo-ohc/scripts/argo_ohc_check.py",
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
    lines = [f"PASS {c['name']}" if c["ok"] else f"FAIL {c['name']}: {c['detail']}" for c in checks]
    bound = r.get("bound_parameters") or {}
    if verdict != "PASS":
        first = next(c for c in checks if not c["ok"])
        lines.append(f"FAIL {first['name']}: {first['detail']}")
    elif refusal:
        lines.append(f"PASS refusal ({r.get('reason_code')}) run {r.get('run_id')}: window "
                     f"{bound.get('window')} depth {bound.get('depth')} refused, {r.get('reason')}")
    else:
        v, t = r["verdict"], r["terms"]["trend"]["interval"]
        lines.append(f"PASS run {r.get('run_id')}: window {bound.get('window')}, 0 to {bound.get('depth')} "
                     f"dbar, {r['months']['n_used']} of {r['months']['n_calendar']} months, trend "
                     f"{t['trend']:+.4f} ZJ/yr [{t['ci_low']:+.4f}, {t['ci_high']:+.4f}], change "
                     f"{r['change_ZJ']:+.4f} ZJ, endpoint change {r['endpoint_change_ZJ']:+.4f} ZJ, "
                     f"residual {v['residual_ZJ']:+.4f} against bar {v['bar_ZJ']:.4f}, "
                     f"consistent_within_uncertainty {str(v['consistent_within_uncertainty']).lower()} "
                     "(recomputed)")
    return "\n".join(lines)


# ---- selftest

def selftest(computation: Path) -> int:
    mod = load(computation)

    def run(argv, path):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            return mod.main([*argv, "--runtime", "selftest", "--receipt", str(path)])

    def verdict_of(path, comp=None, tree=None):
        v, refusal, checks, _ = attest(path, comp or computation, tree)
        return v, refusal, [c["name"] for c in checks if not c["ok"]]

    def first_fail(path, comp=None, tree=None):
        v, _, failed = verdict_of(path, comp, tree)
        return failed[0] if v == "FAIL" and failed else None

    def tampered(src: Path, dst: Path, edit):
        doc = json.loads(src.read_text(encoding="utf-8"))
        edit(doc)
        dst.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        return dst

    with tempfile.TemporaryDirectory() as d:
        w = Path(d)
        ref = w / "ref.json"
        assert run(["--fixture", "--seed", "7", "--window", "2005-01:2016-12", "--depth", "2000"], ref) == 0
        assert verdict_of(ref) == ("PASS", False, []), verdict_of(ref)
        r = json.loads(ref.read_text(encoding="utf-8"))
        assert r["known_truth"]["rate_inside_interval"] and r["known_truth"]["change_within_uncertainty"]
        ref700 = w / "ref700.json"
        assert run(["--fixture", "--seed", "11", "--window", "2006-01:2020-12", "--depth", "700"], ref700) == 0
        assert verdict_of(ref700) == ("PASS", False, []), verdict_of(ref700)

        # tampers, each failing on its check
        t1 = tampered(ref, w / "t1.json", lambda r: r["series"]["value_ZJ"].__setitem__(3, r["series"]["value_ZJ"][3] + 1e-6))
        assert first_fail(t1) == "series", verdict_of(t1)
        t2 = tampered(ref, w / "t2.json", lambda r: r["terms"]["trend"].__setitem__("value", r["terms"]["trend"]["value"] * 1.001))
        assert first_fail(t2) == "recompute", verdict_of(t2)
        t3 = tampered(ref, w / "t3.json", lambda r: r["verdict"].__setitem__("consistent_within_uncertainty", False))
        assert first_fail(t3) == "recompute", verdict_of(t3)
        t4 = tampered(ref, w / "t4.json", lambda r: r["terms"]["trend"]["interval"].__setitem__("half_width", r["terms"]["trend"]["interval"]["half_width"] / 2))
        assert first_fail(t4) == "recompute", verdict_of(t4)
        t5 = tampered(ref, w / "t5.json", lambda r: r["bookkeeping"]["climatology"].pop("statement"))
        assert verdict_of(t5)[2] == ["bookkeeping"], verdict_of(t5)
        t6 = tampered(ref, w / "t6.json", lambda r: r["runtime"].__setitem__("name", ""))
        assert verdict_of(t6)[2] == ["runtime"], verdict_of(t6)
        t7 = tampered(ref, w / "t7.json", lambda r: r["data"].__setitem__("seed", 8))
        assert first_fail(t7) == "data", verdict_of(t7)
        t8 = tampered(ref, w / "t8.json", lambda r: r["terms"]["deep_omission"]["published"].__setitem__("published_rate_ZJ_yr", 0.0))
        assert first_fail(t8) == "recompute", verdict_of(t8)
        t9 = tampered(ref, w / "t9.json", lambda r: r["terms"]["trend"]["per_area"].__setitem__("W_m2_of_earth_surface", 0.0))
        assert first_fail(t9) == "recompute", verdict_of(t9)
        t10 = tampered(ref, w / "t10.json", lambda r: r["known_truth"].__setitem__("planted_rate_ZJ_yr", 9.0))
        assert verdict_of(t10)[2] == ["plausible"], verdict_of(t10)

        # wrong release: the bundle block names another version, or the
        # capability block is malformed
        w1 = tampered(ref, w / "w1.json", lambda r: r["bundle"].__setitem__("version", "0.0.0"))
        assert verdict_of(w1)[2] == ["release"], verdict_of(w1)
        w2 = tampered(ref, w / "w2.json", lambda r: r["capability"].__setitem__("name", ""))
        assert verdict_of(w2)[2] == ["release"], verdict_of(w2)

        # a tampered computation fails code and the generator digest
        bad = w / "argo_ohc.py"
        bad.write_bytes(computation.read_bytes() + b"\n")
        v, _, failed = verdict_of(ref, bad)
        assert v == "FAIL" and "code" in failed and "data" in failed, failed

        # refusals attest PASS as refusals, exit 3 from the executor
        rf = w / "outside.json"
        assert run(["--fixture", "--seed", "7", "--window", "2001-01:2016-12", "--depth", "2000"], rf) == 3
        v, refusal, checks, r = attest(rf, computation)
        assert (v, refusal) == ("PASS", True) and r["reason_code"] == "window-outside-coverage", checks
        assert "PASS refusal" in report(v, refusal, checks, r)
        late = w / "late.json"
        assert run(["--fixture", "--seed", "7", "--window", "2020-01:2025-12", "--depth", "700"], late) == 3
        assert verdict_of(late) == ("PASS", True, []), verdict_of(late)
        few = w / "toofew.json"
        assert run(["--fixture", "--seed", "7", "--window", "2010-01:2010-12", "--depth", "700"], few) == 3
        v, refusal, checks, r = attest(few, computation)
        assert (v, refusal) == ("PASS", True) and r["reason_code"] == "too-few-months", checks
        # a forged refusal is not reproduced
        forged = tampered(rf, w / "forged.json", lambda r: r["bound_parameters"].__setitem__("window", "2005-01:2016-12"))
        assert verdict_of(forged)[2] == ["refusal"], verdict_of(forged)

        # a data root: a stamped tree built here from the fixture series
        # runs, attests, and refuses a window past its stamp
        root = w / "root"
        root.mkdir()
        fx = mod.make_fixture(7, 2000)
        rows = ["month,value_ZJ,uncertainty_ZJ"] + [f"{d},{v:.6f},{u:.6f}" for d, v, u in zip(
            fx["series"]["dates"], fx["series"]["value_ZJ"], fx["series"]["uncertainty_ZJ"])]
        (root / "ohc-2000.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
        stamp = {"term": "ohc-2000", "months": list(mod.FIXTURE_SPAN),
                 "coverage": {"statement": "selftest tree", "domain_area_m2": 2.0e14}}
        (root / "ohc-2000-stamp.json").write_text(json.dumps(stamp) + "\n", encoding="utf-8")
        manifest = {p.name: sha256_file(p) for p in (root / "ohc-2000.csv", root / "ohc-2000-stamp.json")}
        book = json.loads(json.dumps(mod.FIXTURE_BOOKKEEPING))
        book["coverage"]["domain_area_m2"] = 2.0e14
        book["anchor"] = {"ohc-2000": {"value_W_m2_global": 0.62, "uncertainty_W_m2_global": 0.2,
                                       "ocean_area_fraction": 0.61, "source": "selftest"}}
        record = {"record": "selftest-root", "manifest": manifest,
                  "manifest_sha256": "sha256:" + "0" * 64, "bookkeeping": book}
        (root / "RECORD.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        dr = w / "dataroot.json"
        assert run(["--data-root", str(root), "--window", "2005-01:2016-12", "--depth", "2000"], dr) == 0
        v, refusal, checks, r = attest(dr, computation, root)
        assert (v, refusal) == ("PASS", False), checks
        assert "verified against the tree" in checks[4]["detail"]
        v, refusal, checks, r = attest(dr, computation)
        assert (v, refusal) == ("PASS", False) and "NOT verified" in checks[4]["detail"], checks
        assert r["anchor"]["distance_over_anchor_uncertainty"] is not None
        assert abs(r["terms"]["trend"]["value"] - json.loads(ref.read_text())["terms"]["trend"]["value"]) < 1e-5
        t11 = tampered(dr, w / "t11.json", lambda r: r["anchor"].__setitem__("distance_W_m2_of_earth_surface", 0.0))
        assert first_fail(t11) == "recompute", verdict_of(t11)
        # a fabricated but self-consistent data-root receipt fails against the tree
        t12 = tampered(dr, w / "t12.json", lambda r: r["data"]["files"].__setitem__("ohc-2000.csv", "sha256:" + "1" * 64))
        assert verdict_of(t12)[0] == "PASS" and first_fail(t12, tree=root) == "data", verdict_of(t12, tree=root)
        t13 = tampered(dr, w / "t13.json", lambda r: r["data"].__setitem__("record_sha256", "sha256:" + "2" * 64))
        assert first_fail(t13, tree=root) == "data", verdict_of(t13, tree=root)
        t14 = tampered(dr, w / "t14.json", lambda r: r["data"]["stamp"].__setitem__("months", ["2004-01", "2024-12"]))
        assert first_fail(t14, tree=root) == "data", verdict_of(t14, tree=root)
        # data-root refusals reproduce only against the tree
        drr = w / "dataroot-refused.json"
        assert run(["--data-root", str(root), "--window", "2015-01:2030-12", "--depth", "2000"], drr) == 3
        assert verdict_of(drr, tree=root) == ("PASS", True, []), verdict_of(drr, tree=root)
        assert verdict_of(drr)[2] == ["refusal"], verdict_of(drr)
        drf = w / "dataroot-toofew.json"
        assert run(["--data-root", str(root), "--window", "2010-01:2010-12", "--depth", "2000"], drf) == 3
        v, refusal, checks, r = attest(drf, computation, root)
        assert (v, refusal) == ("PASS", True) and r["reason_code"] == "too-few-months", checks
        assert verdict_of(drf)[2] == ["refusal"], verdict_of(drf)
        forged_dr = tampered(drf, w / "forged-dr.json", lambda r: r["bound_parameters"].__setitem__("window", "2005-01:2016-12"))
        assert verdict_of(forged_dr, tree=root)[2] == ["refusal"], verdict_of(forged_dr, tree=root)
        # an edited tree is not computed on
        (root / "ohc-2000.csv").write_text("\n".join(rows[:-1]) + "\n", encoding="utf-8")
        try:
            run(["--data-root", str(root), "--window", "2005-01:2016-12", "--depth", "2000"], w / "edited.json")
            raise AssertionError("an edited tree computed")
        except SystemExit as e:
            assert "manifest" in str(e), e

        # the attestation document carries the verdict and the identity blocks
        doc = attestation_doc(*attest(ref, computation), ref, computation)
        assert doc["verdict"] == "PASS" and doc["capability"]["name"] and doc["runtime"]["name"] == "selftest"
        assert {c["name"] for c in doc["checks"]} == {"fields", "code", "release", "runtime", "data",
                                                       "series", "recompute", "bookkeeping", "plausible"}
    print("argo_ohc_check selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("receipt", nargs="?", type=Path)
    ap.add_argument("--computation", type=Path, default=DEFAULT_COMPUTATION)
    ap.add_argument("--data-root", type=Path, default=None,
                    help="the tree a data-root receipt is verified against (RECORD.json, the CSV "
                         "and the stamp rehashed; a data-root refusal reproduced from it)")
    ap.add_argument("--out", type=Path, default=None, help="write the attestation JSON here")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    computation = args.computation.resolve()
    if args.selftest:
        return selftest(computation)
    if not args.receipt:
        ap.error("give a receipt, or --selftest")
    verdict, refusal, checks, r = attest(args.receipt, computation, args.data_root)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(attestation_doc(verdict, refusal, checks, r, args.receipt,
                                                       computation), indent=2) + "\n",
                            encoding="utf-8")
    print(report(verdict, refusal, checks, r) + (f"; attestation {args.out}" if args.out else ""))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
