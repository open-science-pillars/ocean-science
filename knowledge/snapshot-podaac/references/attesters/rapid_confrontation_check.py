#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested confrontation of the ECCO
overturning at 26.5 north with the RAPID observed overturning.

No LLM, stdlib only, consumer-side. PASS (exit 0) only when ALL hold,
else FAIL (exit 1) naming the field:

  1. declared receipt fields present, including every observational
     provenance field: record stamp, file and its hash, version, DOI,
     citation, acknowledgement, licence, variable, units, and the
     published measurement uncertainty. A confrontation whose receipt
     does not say WHICH observations it confronted, at which version,
     under which terms, is not a confrontation;
  2. code hashes: this receipt's code_sha256 is the sanctioned
     confrontation file, the cited model receipt's code_sha256 is the
     sanctioned overturning file, and the interval method is the
     sanctioned trend method;
  3. the observation pinned: version v2024.1a, DOI
     10.5285/48d0bf43-0598-ceb2-e063-7086abc062f1, record
     rapid-26n-v2024.1a at its manifest hash, moc_transports.nc at
     its file hash, variable moc_mar_hc10 in Sv. A later release is a
     different observation and needs a re-run and a re-signature, not
     a silent pass;
  4. the model side pinned: scope atlantic, convention mass-balanced,
     a verified-tree stamp; with the model receipt on disk, its hash
     matches the citation, its primary series is recomputed from the
     per-level transports it carries, the confronted months are its
     values exactly, its anchor against the independent
     implementation holds, and every structural mutation was caught;
  5. the series: consecutive months inside 2004-04 through 2017-12
     (the array's first month and the model's last), finite values,
     RAPID sample counts consistent with twelve-hourly sampling and
     the bound minimum fraction, both digests recomputed;
  6. EVERY SCORE RECOMPUTED from the two series in the receipt: bias,
     RMSD, correlation and anomaly correlation, each with its
     interval by the attested chain (lag-1 autocorrelation, effective
     sample size capped at n, Student's t on the effective degrees of
     freedom), every number within 1e-9 relative; the descriptive
     means, standard deviations and trend blocks likewise.

Usage: rapid_confrontation_check.py RECEIPT.json [--model-receipt PATH]
"""

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path

from trend_recompute import DEFAULT_METHOD, REL_TOL, check_block, close, t_quantile

COMPUTATIONS = Path(__file__).resolve().parent.parent / "computations"
CONFRONTATION = COMPUTATIONS / "ecco_rapid_amoc_confrontation.py"
OVERTURNING = COMPUTATIONS / "ecco_amoc_26n.py"
OBS_VERSION = "v2024.1a"
OBS_DOI = "10.5285/48d0bf43-0598-ceb2-e063-7086abc062f1"
OBS_RECORD = "rapid-26n-v2024.1a"
OBS_MANIFEST_SHA256 = "ff1b261502a5359b2e0522bf9466c6750f63850be58e0973ca996d16e7dc55d5"
OBS_FILE = "moc_transports.nc"
OBS_FILE_SHA256 = "ba135d9447a87c2bf5dcc8870e2cb73ff348c412fa1bc3501145e01c79788eed"
OBS_VARIABLE = "moc_mar_hc10"
OBS_UNITS = "Sv"
OVERLAP = ("2004-04", "2017-12")
SAMPLES_PER_DAY = 2
MIN_DOF = 1.0
CONFIDENCE = 0.95
ANCHOR_TOL_SV = 0.01
SERIES_TOL_SV = 1e-4      # the model receipt rounds per-level transports to 1e-6
FIELDS = ["run_id", "code_sha256", "method_code_sha256", "model",
          "observation", "bound_parameters", "series", "digests",
          "scores", "descriptive"]
OBS_FIELDS = ["record", "file", "file_sha256", "version", "doi",
              "citation", "acknowledgement", "licence", "variable",
              "units", "cadence", "filter", "published_uncertainty"]
MODEL_FIELDS = ["receipt", "receipt_sha256", "run_id", "code_sha256",
                "data", "scope", "convention", "mask_sha256"]
SERIES_FIELDS = ["months", "ecco_Sv", "rapid_Sv", "rapid_samples_valid",
                 "rapid_samples_expected"]
SCORES = ["bias_Sv", "rmsd_Sv", "correlation", "anomaly_correlation"]


def fail(msg):
    print(f"FAIL: {msg}")
    return 1


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def digest(months, values):
    text = json.dumps({"months": list(months), "values": [float(v) for v in values]},
                      separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()


def lag1(a):
    return sum(x * y for x, y in zip(a[:-1], a[1:])) / sum(x * x for x in a)


def n_effective(r1, n):
    return min(float(n), n * (1.0 - r1) / (1.0 + r1))


def mean_interval(values):
    n = len(values)
    mean = sum(values) / n
    a = [v - mean for v in values]
    r1 = lag1(a)
    n_eff = n_effective(r1, n)
    dof = n_eff - 1.0
    sd = math.sqrt(sum(x * x for x in a) / (n - 1))
    se = sd / math.sqrt(n_eff)
    out = {"value": mean, "n": n, "r1": r1, "n_eff": n_eff, "dof": dof,
           "sd": sd, "se": se, "stated": dof >= MIN_DOF}
    if out["stated"]:
        tq = t_quantile(0.5 + CONFIDENCE / 2.0, dof)
        out.update(t_quantile=tq, half_width=tq * se,
                   ci_low=mean - tq * se, ci_high=mean + tq * se)
    return out


def correlation_interval(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    ax, ay = [v - mx for v in x], [v - my for v in y]
    r = sum(a * b for a, b in zip(ax, ay)) / math.sqrt(
        sum(v * v for v in ax) * sum(v * v for v in ay))
    r1x, r1y = lag1(ax), lag1(ay)
    n_eff = n_effective(r1x * r1y, n)
    dof = n_eff - 3.0
    out = {"value": r, "n": n, "r1_a": r1x, "r1_b": r1y, "n_eff": n_eff,
           "dof": dof, "stated": dof >= MIN_DOF and abs(r) < 1.0}
    if out["stated"]:
        z = math.atanh(r)
        se_z = 1.0 / math.sqrt(dof)
        tq = t_quantile(0.5 + CONFIDENCE / 2.0, dof)
        out.update(fisher_z=z, se_z=se_z, t_quantile=tq,
                   ci_low=math.tanh(z - tq * se_z), ci_high=math.tanh(z + tq * se_z))
    return out


def deseasonalize(months, values):
    by = {}
    for mo, v in zip(months, values):
        by.setdefault(mo[5:], []).append(v)
    clim = {k: sum(v) / len(v) for k, v in by.items()}
    return [v - clim[mo[5:]] for mo, v in zip(months, values)]


def compare(name, got, mine):
    """Every number the block states must recompute; the stated flag
    must agree; the interval must be present exactly when stated."""
    if not isinstance(got, dict):
        return f"{name}: block missing or not an object"
    if got.get("confidence") != CONFIDENCE:
        return f"{name}: confidence {got.get('confidence')} != {CONFIDENCE}"
    if got.get("stated") is not mine["stated"]:
        return f"{name}: stated {got.get('stated')} but the recompute says {mine['stated']}"
    for k, v in mine.items():
        if k == "stated":
            continue
        g = got.get(k)
        if isinstance(v, bool) or isinstance(v, int) and not isinstance(v, bool):
            if g != v:
                return f"{name}: {k} {g} != {v}"
        elif not isinstance(g, (int, float)) or not close(g, v):
            return f"{name}: {k} {g} does not recompute ({v})"
    return None


def days_in_month(mo):
    y, m = int(mo[:4]), int(mo[5:])
    return (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.date(y, m, 1)).days


def consecutive(months):
    ym = [int(m[:4]) * 12 + int(m[5:]) - 1 for m in months]
    return all(b - a == 1 for a, b in zip(ym[:-1], ym[1:]))


def check_model_receipt(r, path):
    """The cited model receipt: hash, series recomputed from per-level
    transports, values used here, anchor, structural mutations."""
    if sha256_file(path) != r["model"]["receipt_sha256"]:
        return f"model receipt {path.name} does not hash to the cited receipt_sha256"
    er = json.loads(path.read_text(encoding="utf-8"))
    if er.get("run_id") != r["model"]["run_id"]:
        return "model receipt run_id differs from the citation"
    if sha256_file(OVERTURNING) != er.get("code_sha256"):
        return "model receipt code_sha256 is not the sanctioned overturning computation"
    res, sec = er["results"], er["resolved_section"]
    area = sec["open_area_m2_by_level"]
    total = sec["open_area_total_m2"]
    if not close(total, sum(area)):
        return "model receipt open_area_total_m2 is not the sum of the profile"
    months = res["months"]
    for i, (mo, row) in enumerate(zip(months, res["transport_per_level_Sv_by_month"])):
        net = sum(row)
        psi, acc, best = [], 0.0, -math.inf
        for k, t in enumerate(row):
            acc += t - net * area[k] / total
            best = max(best, acc)
        if abs(best - res["amoc_Sv"][i]) > SERIES_TOL_SV:
            return (f"model receipt {mo}: mass-balanced maximum {best:.6f} "
                    f"does not recompute from the per-level transports "
                    f"({res['amoc_Sv'][i]:.6f})")
        if abs(net - res["net_transport_Sv"][i]) > SERIES_TOL_SV:
            return f"model receipt {mo}: net transport does not recompute"
    by = dict(zip(months, res["amoc_Sv"]))
    for mo, v in zip(r["series"]["months"], r["series"]["ecco_Sv"]):
        if mo not in by or by[mo] != v:
            return f"confronted ECCO value for {mo} is not the model receipt's"
    anchor = er.get("anchor")
    if any(mo.startswith("2010-") for mo in months):
        if not isinstance(anchor, dict):
            return "model receipt covers 2010 but carries no anchor block"
        for c in ("surface-down", "bottom-up"):
            if abs(anchor[f"{c}_measured_Sv"] - anchor[f"{c}_anchor_Sv"]) > ANCHOR_TOL_SV:
                return f"model receipt anchor {c} is outside {ANCHOR_TOL_SV} Sv"
    for e in er.get("mutation_evidence", []):
        if e.get("applicable", True) and not e.get("caught"):
            return f"model receipt: structural mutation {e['mutation']} not caught"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--model-receipt", type=Path, default=None,
                    help="the cited model receipt (default: beside this receipt "
                         "under the name the receipt cites; skipped with a note "
                         "if absent)")
    ap.add_argument("--method", type=Path, default=DEFAULT_METHOD)
    args = ap.parse_args()
    r = json.loads(args.receipt.read_text(encoding="utf-8"))

    for f in FIELDS:
        if f not in r:
            return fail(f"receipt field missing: {f}")
    obs, model, ser = r["observation"], r["model"], r["series"]
    for f in OBS_FIELDS:
        if f not in obs:
            return fail(f"observational provenance field missing: observation.{f}")
    for f in MODEL_FIELDS:
        if f not in model:
            return fail(f"model field missing: model.{f}")
    for f in SERIES_FIELDS:
        if f not in ser:
            return fail(f"series field missing: series.{f}")
    for f in SCORES:
        if f not in r["scores"]:
            return fail(f"score missing: scores.{f}")
    for f in ("ecco_series_sha256", "rapid_series_sha256"):
        if f not in r["digests"]:
            return fail(f"digest missing: digests.{f}")

    if r["code_sha256"] != sha256_file(CONFRONTATION):
        return fail("code_sha256 does not match the sanctioned confrontation computation")
    if model["code_sha256"] != sha256_file(OVERTURNING):
        return fail("model.code_sha256 does not match the sanctioned overturning computation")
    if r["method_code_sha256"] != sha256_file(args.method):
        return fail("method_code_sha256 does not match the sanctioned trend method")

    # the observation, pinned
    if obs["version"] != OBS_VERSION:
        return fail(f"observation.version {obs['version']!r} is not {OBS_VERSION}; "
                    "a different release is a different observation")
    if obs["doi"] != OBS_DOI:
        return fail(f"observation.doi {obs['doi']!r} is not {OBS_DOI}")
    stamp = obs["record"]
    if not isinstance(stamp, dict):
        return fail("observation.record is not a verified-tree stamp; nothing "
                    "is attested against unmanifested observations")
    if stamp.get("record") != OBS_RECORD or stamp.get("manifest_sha256") != OBS_MANIFEST_SHA256:
        return fail("observation.record stamp is not the pinned record at its manifest hash")
    if obs["file"] != OBS_FILE or obs["file_sha256"] != OBS_FILE_SHA256:
        return fail("observation file or file_sha256 is not the pinned transport file")
    if obs["variable"] != OBS_VARIABLE or obs["units"] != OBS_UNITS:
        return fail("observation variable or units differ from the contract")
    for f in ("citation", "acknowledgement", "licence"):
        if not isinstance(obs[f], str) or not obs[f].strip():
            return fail(f"observation.{f} is empty")
    if "Open Government Licence" not in obs["licence"]:
        return fail("observation.licence does not name the Open Government Licence")
    pu = obs["published_uncertainty"]
    if not isinstance(pu, dict) or not all(
            isinstance(pu.get(k), (int, float)) for k in ("rms_ten_day_Sv", "rms_annual_Sv")):
        return fail("observation.published_uncertainty lacks the RMS figures")

    # the model side, pinned
    if model["scope"] != "atlantic" or model["convention"] != "mass-balanced":
        return fail("model scope or convention is not what the array observes")
    if not isinstance(model.get("data", {}).get("record"), dict):
        return fail("model.data.record is not a verified-tree stamp")
    model_note = ""
    mpath = args.model_receipt or args.receipt.parent / model["receipt"]
    if mpath.exists():
        err = check_model_receipt(r, mpath)
        if err:
            return fail(err)
        model_note = ", model receipt recomputed"
    else:
        model_note = f", model receipt {model['receipt']} not on disk (hash cited only)"

    # the series
    months, ecco, rapid = ser["months"], ser["ecco_Sv"], ser["rapid_Sv"]
    n = len(months)
    bp = r["bound_parameters"]
    if not (len(ecco) == len(rapid) == len(ser["rapid_samples_valid"])
            == len(ser["rapid_samples_expected"]) == n):
        return fail("series lengths differ")
    if bp.get("months") != n or bp.get("overlap") != f"{months[0]}:{months[-1]}":
        return fail("bound_parameters months or overlap disagree with the series")
    if bp.get("confidence") != CONFIDENCE:
        return fail(f"bound confidence {bp.get('confidence')} != {CONFIDENCE}")
    if n < 24 or not consecutive(months):
        return fail("series must be at least 24 consecutive months")
    if months[0] < OVERLAP[0] or months[-1] > OVERLAP[1]:
        return fail(f"series leaves the possible overlap {OVERLAP}")
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in ecco + rapid):
        return fail("series has a non-finite value")
    frac = bp.get("min_valid_fraction")
    if not isinstance(frac, (int, float)) or not 0 < frac <= 1:
        return fail("min_valid_fraction is not in (0, 1]")
    for mo, valid, exp in zip(months, ser["rapid_samples_valid"], ser["rapid_samples_expected"]):
        if exp != days_in_month(mo) * SAMPLES_PER_DAY:
            return fail(f"{mo}: expected sample count {exp} is not twelve-hourly")
        if not 0 < valid <= exp or valid / exp < frac:
            return fail(f"{mo}: {valid} valid of {exp} samples is under the bound fraction")
    if r["digests"]["ecco_series_sha256"] != digest(months, ecco):
        return fail("ecco_series_sha256 does not recompute from the series")
    if r["digests"]["rapid_series_sha256"] != digest(months, rapid):
        return fail("rapid_series_sha256 does not recompute from the series")

    # every score
    d = [a - b for a, b in zip(ecco, rapid)]
    sc = r["scores"]
    err = compare("scores.bias_Sv", sc["bias_Sv"], mean_interval(d))
    if err:
        return fail(err)
    msd = mean_interval([v * v for v in d])
    rm = sc["rmsd_Sv"]
    err = compare("scores.rmsd_Sv.msd", rm.get("msd"), msd)
    if err:
        return fail(err)
    mine = {"value": math.sqrt(msd["value"]), "stated": msd["stated"]}
    if msd["stated"]:
        mine.update(ci_low=math.sqrt(max(msd["ci_low"], 0.0)),
                    ci_high=math.sqrt(msd["ci_high"]))
    err = compare("scores.rmsd_Sv", rm, mine)
    if err:
        return fail(err)
    err = compare("scores.correlation", sc["correlation"], correlation_interval(ecco, rapid))
    if err:
        return fail(err)
    err = compare("scores.anomaly_correlation", sc["anomaly_correlation"],
                  correlation_interval(deseasonalize(months, ecco),
                                       deseasonalize(months, rapid)))
    if err:
        return fail(err)

    # descriptive
    de = r["descriptive"]
    for name, s in (("ecco", ecco), ("rapid", rapid)):
        mu = sum(s) / n
        sd = math.sqrt(sum((v - mu) ** 2 for v in s) / (n - 1))
        if not close(de.get(f"{name}_mean_Sv"), mu) or not close(de.get(f"{name}_sd_Sv"), sd):
            return fail(f"descriptive {name} mean or sd does not recompute")
        err = check_block(de.get(f"{name}_trend"), s, args.method)
        if err:
            return fail(f"descriptive.{name}_trend: {err}")

    b, c, a = sc["bias_Sv"], sc["correlation"], sc["anomaly_correlation"]
    print(f"PASS run {r['run_id']}: sanctioned code on both sides, RAPID "
          f"{obs['version']} ({obs['doi']}) at its file hash, {n} months "
          f"{months[0]} to {months[-1]}, both digests and every score "
          f"recomputed{model_note}: bias {b['value']:+.4f} Sv "
          f"[{b['ci_low']:+.4f}, {b['ci_high']:+.4f}], rmsd {rm['value']:.4f} Sv "
          f"[{rm['ci_low']:.4f}, {rm['ci_high']:.4f}], correlation {c['value']:+.4f} "
          f"[{c['ci_low']:+.4f}, {c['ci_high']:+.4f}], anomaly correlation "
          f"{a['value']:+.4f} [{a['ci_low']:+.4f}, {a['ci_high']:+.4f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
