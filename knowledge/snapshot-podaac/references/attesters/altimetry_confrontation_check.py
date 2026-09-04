#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic attester for the attested comparison of the ECCO
regional sea level with the NASA-SSH gridded altimetry record.

No LLM, stdlib only, consumer-side. PASS (exit 0) only when ALL hold,
else FAIL (exit 1) naming the field:

  1. declared receipt fields present, including every observational
     provenance field: record stamp, grids digest, version, DOI,
     short name, mean sea surface, licence, citation, variable,
     units, the published uncertainty block and the independence
     statement. A comparison whose receipt does not say WHICH
     observations it used, at which version, under which terms, and
     how independent they are of the estimate, is not one the bundle
     can be held to;
  2. code hashes: this receipt's code_sha256 is the sanctioned
     comparison file, the cited model receipt's code_sha256 is the
     sanctioned sea level partition, the scores come from the
     sanctioned confrontation scoring file, and the interval method
     is the sanctioned trend method;
  3. the observation pinned: NASA_SSH_REF_SIMPLE_GRID_V11, version
     V1.1, DOI 10.5067/NSREF-SG0V11, mean sea surface DTU21, ssha in
     m, Creative Commons Attribution 4.0, the record
     nasa-ssh-ref-simple-grid-v1.1 at its manifest hash, and the
     grids digest of the 1315 grids. A later release is a different
     observation and needs a re-run and a re-signature. With the tree
     on disk (--obs-root), every grid is re-hashed and the digest
     recomputed;
  4. the model side pinned: region us-northeast-coast, the SSH
     variant, a verified-tree stamp; with the partition receipt on
     disk, its hash matches the citation, and the confronted ECCO
     values are that receipt's total anomalies over the overlap,
     re-centred on the overlap mean and in mm, exactly;
  5. the series: consecutive months inside 1992-11 through 2017-12
     (the first month with a full complement of grids and the model's
     last), finite values, each month's grid count at or above the
     bound minimum and at most five, both series centred on the
     overlap, both digests recomputed;
  6. EVERY SCORE RECOMPUTED from the two series in the receipt: RMSD,
     correlation and anomaly correlation with their intervals by the
     attested chain (lag-1 autocorrelation, effective sample size
     capped at n, Student's t on the effective degrees of freedom),
     the trend of the difference by the sanctioned trend method, every
     number within 1e-9 relative; the descriptive standard deviations
     and trend blocks likewise.

Usage: altimetry_confrontation_check.py RECEIPT.json
           [--model-receipt PATH] [--obs-root TREE]
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from trend_recompute import DEFAULT_METHOD, check_block, close, t_quantile

COMPUTATIONS = Path(__file__).resolve().parent.parent / "computations"
COMPARISON = COMPUTATIONS / "ecco_ssh_vs_altimetry.py"
PARTITION = COMPUTATIONS / "ecco_regional_sea_level.py"
SCORING = COMPUTATIONS / "ecco_rapid_amoc_confrontation.py"
OBS_SHORT_NAME = "NASA_SSH_REF_SIMPLE_GRID_V11"
OBS_VERSION = "V1.1"
OBS_DOI = "10.5067/NSREF-SG0V11"
OBS_MSS = "DTU21"
OBS_RECORD = "nasa-ssh-ref-simple-grid-v1.1"
OBS_MANIFEST_SHA256 = "578b8f29b8cd7aff69be3eea74fa330f32e0bad4635e38b6e37d0b97f3e3e449"
OBS_GRIDS = 1315
OBS_GRIDS_SHA256 = "b3dd9594c766986713eca8e3e0efd261561fde5d8e3c8160e303702f64c2ebe1"
OBS_VARIABLE = "ssha"
OBS_UNITS = "m"
OBS_LICENSE = "https://creativecommons.org/licenses/by/4.0/"
OVERLAP = ("1992-11", "2017-12")
MODEL_REGION = "us-northeast-coast"
MODEL_VARIANT = "SSH"
MAX_GRIDS_PER_MONTH = 5
MIN_DOF = 1.0
CONFIDENCE = 0.95
SERIES_TOL_MM = 1e-9
FIELDS = ["run_id", "code_sha256", "method_code_sha256", "scoring_code_sha256",
          "partition_code_sha256", "model", "observation", "bound_parameters",
          "series", "digests", "scores", "descriptive", "caveats"]
OBS_FIELDS = ["record", "grids", "grids_sha256", "version", "doi", "short_name",
              "mean_sea_surface", "license", "citation", "variable", "units",
              "convention", "cadence", "published_uncertainty", "independence"]
INDEPENDENCE_FIELDS = ["degree", "constraint", "overlap", "what_it_can_show",
                       "what_it_cannot_show"]
MODEL_FIELDS = ["receipt", "receipt_sha256", "run_id", "code_sha256", "data",
                "region", "period", "ssh_variant", "series_field"]
SERIES_FIELDS = ["months", "ecco_mm", "altimetry_mm", "difference_mm",
                 "grids_per_month"]
SCORES = ["rmsd_mm", "correlation", "anomaly_correlation", "trend_difference_mm_yr"]


def fail(msg):
    print(f"FAIL: {msg}")
    return 1


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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


def consecutive(months):
    ym = [int(m[:4]) * 12 + int(m[5:]) - 1 for m in months]
    return all(b - a == 1 for a, b in zip(ym[:-1], ym[1:]))


def check_model_receipt(r, path):
    """The cited partition receipt: hash, sanctioned code, and the
    confronted ECCO values derived from its total anomalies exactly."""
    if sha256_file(path) != r["model"]["receipt_sha256"]:
        return f"model receipt {path.name} does not hash to the cited receipt_sha256"
    pr = json.loads(path.read_text(encoding="utf-8"))
    if pr.get("run_id") != r["model"]["run_id"]:
        return "model receipt run_id differs from the citation"
    if sha256_file(PARTITION) != pr.get("code_sha256"):
        return "model receipt code_sha256 is not the sanctioned sea level partition"
    if pr.get("bound_parameters", {}).get("region") != MODEL_REGION:
        return "model receipt region is not the cited region"
    if pr.get("ssh_variant") != MODEL_VARIANT:
        return "model receipt variant is not the SSH variant"
    if not isinstance(pr.get("data", {}).get("record"), dict):
        return "model receipt names no verified data tree"
    by = dict(zip(pr["series_by_month"]["dates"],
                  pr["series_by_month"]["total_anomaly_m"]))
    months = r["series"]["months"]
    if any(mo not in by for mo in months):
        return "a confronted month is not in the model receipt"
    raw = [float(by[mo]) for mo in months]
    mu = sum(raw) / len(raw)
    mine = [(v - mu) * 1000.0 for v in raw]
    for mo, got, want in zip(months, r["series"]["ecco_mm"], mine):
        if abs(got - want) > SERIES_TOL_MM:
            return (f"confronted ECCO value for {mo} ({got}) is not the model "
                    f"receipt's anomaly re-centred on the overlap ({want})")
    return None


def check_tree(obs, root):
    files = sorted(p for p in root.glob("*.nc"))
    if len(files) != obs["grids"]:
        return f"tree holds {len(files)} grids, receipt says {obs['grids']}"
    lines = [f"{p.name} {sha256_file(p)}" for p in files]
    mine = hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()
    if mine != obs["grids_sha256"]:
        return "the tree's grids do not hash to the receipt's grids_sha256"
    stamp = root / "RECORD.json"
    if not stamp.exists() or json.loads(stamp.read_text()) != obs["record"]:
        return "the tree's RECORD.json is not the stamp the receipt carries"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--model-receipt", type=Path, default=None,
                    help="the cited partition receipt (default: beside this "
                         "receipt under the name the receipt cites; skipped "
                         "with a note if absent)")
    ap.add_argument("--obs-root", type=Path, default=None,
                    help="the verified NASA-SSH tree; when given, every grid "
                         "is re-hashed against the receipt's digest")
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
    for f in INDEPENDENCE_FIELDS:
        if not isinstance(obs["independence"].get(f), str) or not obs["independence"][f].strip():
            return fail(f"independence statement incomplete: observation.independence.{f}")
    for f in MODEL_FIELDS:
        if f not in model:
            return fail(f"model field missing: model.{f}")
    for f in SERIES_FIELDS:
        if f not in ser:
            return fail(f"series field missing: series.{f}")
    for f in SCORES:
        if f not in r["scores"]:
            return fail(f"score missing: scores.{f}")
    for f in ("ecco_series_sha256", "altimetry_series_sha256"):
        if f not in r["digests"]:
            return fail(f"digest missing: digests.{f}")

    if r["code_sha256"] != sha256_file(COMPARISON):
        return fail("code_sha256 does not match the sanctioned comparison computation")
    if model["code_sha256"] != sha256_file(PARTITION) or r["partition_code_sha256"] != sha256_file(PARTITION):
        return fail("model.code_sha256 does not match the sanctioned sea level partition")
    if r["scoring_code_sha256"] != sha256_file(SCORING):
        return fail("scoring_code_sha256 does not match the sanctioned confrontation scoring file")
    if r["method_code_sha256"] != sha256_file(args.method):
        return fail("method_code_sha256 does not match the sanctioned trend method")

    # the observation, pinned
    if obs["short_name"] != OBS_SHORT_NAME:
        return fail(f"observation.short_name {obs['short_name']!r} is not {OBS_SHORT_NAME}")
    if obs["version"] != OBS_VERSION:
        return fail(f"observation.version {obs['version']!r} is not {OBS_VERSION}; "
                    "a different release is a different observation")
    if obs["doi"] != OBS_DOI:
        return fail(f"observation.doi {obs['doi']!r} is not {OBS_DOI}")
    if obs["mean_sea_surface"] != OBS_MSS:
        return fail(f"observation.mean_sea_surface {obs['mean_sea_surface']!r} is not {OBS_MSS}")
    stamp = obs["record"]
    if not isinstance(stamp, dict):
        return fail("observation.record is not a verified-tree stamp; nothing "
                    "is attested against unmanifested observations")
    if stamp.get("record") != OBS_RECORD or stamp.get("manifest_sha256") != OBS_MANIFEST_SHA256:
        return fail("observation.record stamp is not the pinned record at its manifest hash")
    if obs["grids"] != OBS_GRIDS or obs["grids_sha256"] != OBS_GRIDS_SHA256:
        return fail("observation grids count or grids_sha256 is not the pinned tree")
    if obs["variable"] != OBS_VARIABLE or obs["units"] != OBS_UNITS:
        return fail("observation variable or units differ from the contract")
    if obs["license"] != OBS_LICENSE:
        return fail("observation.license is not the Creative Commons Attribution 4.0 URL")
    if not isinstance(obs["citation"], str) or OBS_DOI not in obs["citation"]:
        return fail("observation.citation is empty or does not carry the DOI")
    pu = obs["published_uncertainty"]
    if (not isinstance(pu, dict)
            or not isinstance(pu.get("regional_trend_uncertainty_mm_yr"), (int, float))
            or not isinstance(pu.get("regional_trend_uncertainty_source"), str)
            or not isinstance(pu.get("product_statement"), str)):
        return fail("observation.published_uncertainty lacks the product statement "
                    "or the regional trend uncertainty with its source")
    tree_note = ""
    if args.obs_root is not None:
        err = check_tree(obs, args.obs_root.expanduser())
        if err:
            return fail(err)
        tree_note = ", every grid re-hashed"

    # the model side, pinned
    if model["region"] != MODEL_REGION or model["ssh_variant"] != MODEL_VARIANT:
        return fail("model region or variant is not what the comparison is defined on")
    if not isinstance(model.get("data", {}).get("record"), dict):
        return fail("model.data.record is not a verified-tree stamp")
    mpath = args.model_receipt or args.receipt.parent / model["receipt"]
    if mpath.exists():
        err = check_model_receipt(r, mpath)
        if err:
            return fail(err)
        model_note = ", model receipt recomputed"
    else:
        model_note = f", model receipt {model['receipt']} not on disk (hash cited only)"

    # the series
    months, ecco, alt, d = ser["months"], ser["ecco_mm"], ser["altimetry_mm"], ser["difference_mm"]
    n = len(months)
    bp = r["bound_parameters"]
    if not (len(ecco) == len(alt) == len(d) == len(ser["grids_per_month"]) == n):
        return fail("series lengths differ")
    if bp.get("months") != n or bp.get("overlap") != f"{months[0]}:{months[-1]}":
        return fail("bound_parameters months or overlap disagree with the series")
    if bp.get("confidence") != CONFIDENCE:
        return fail(f"bound confidence {bp.get('confidence')} != {CONFIDENCE}")
    if n < 24 or not consecutive(months):
        return fail("series must be at least 24 consecutive months")
    if months[0] < OVERLAP[0] or months[-1] > OVERLAP[1]:
        return fail(f"series leaves the possible overlap {OVERLAP}")
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in ecco + alt + d):
        return fail("series has a non-finite value")
    mg = bp.get("min_grids")
    if not isinstance(mg, int) or not 1 <= mg <= MAX_GRIDS_PER_MONTH:
        return fail(f"min_grids is not an integer in 1..{MAX_GRIDS_PER_MONTH}")
    for mo, g in zip(months, ser["grids_per_month"]):
        if not isinstance(g, int) or not mg <= g <= MAX_GRIDS_PER_MONTH:
            return fail(f"{mo}: {g} grids is outside {mg}..{MAX_GRIDS_PER_MONTH}")
    for name, s in (("ecco_mm", ecco), ("altimetry_mm", alt)):
        if abs(sum(s) / n) > SERIES_TOL_MM:
            return fail(f"series.{name} is not centred on the overlap mean")
    for i, mo in enumerate(months):
        if abs(d[i] - (ecco[i] - alt[i])) > SERIES_TOL_MM:
            return fail(f"{mo}: difference_mm is not ECCO minus altimetry")
    if r["digests"]["ecco_series_sha256"] != digest(months, ecco):
        return fail("ecco_series_sha256 does not recompute from the series")
    if r["digests"]["altimetry_series_sha256"] != digest(months, alt):
        return fail("altimetry_series_sha256 does not recompute from the series")

    # every score
    sc = r["scores"]
    msd = mean_interval([v * v for v in d])
    rm = sc["rmsd_mm"]
    err = compare("scores.rmsd_mm.msd", rm.get("msd"), msd)
    if err:
        return fail(err)
    mine = {"value": math.sqrt(msd["value"]), "stated": msd["stated"]}
    if msd["stated"]:
        mine.update(ci_low=math.sqrt(max(msd["ci_low"], 0.0)),
                    ci_high=math.sqrt(msd["ci_high"]))
    err = compare("scores.rmsd_mm", rm, mine)
    if err:
        return fail(err)
    err = compare("scores.correlation", sc["correlation"], correlation_interval(ecco, alt))
    if err:
        return fail(err)
    err = compare("scores.anomaly_correlation", sc["anomaly_correlation"],
                  correlation_interval(deseasonalize(months, ecco),
                                       deseasonalize(months, alt)))
    if err:
        return fail(err)
    err = check_block(sc["trend_difference_mm_yr"], d, args.method)
    if err:
        return fail(f"scores.trend_difference_mm_yr: {err}")

    # descriptive
    de = r["descriptive"]
    for name, s in (("ecco", ecco), ("altimetry", alt)):
        mu = sum(s) / n
        sd = math.sqrt(sum((v - mu) ** 2 for v in s) / (n - 1))
        if not close(de.get(f"{name}_sd_mm"), sd):
            return fail(f"descriptive {name}_sd_mm does not recompute")
        err = check_block(de.get(f"{name}_trend"), s, args.method)
        if err:
            return fail(f"descriptive.{name}_trend: {err}")

    c, a, t = sc["correlation"], sc["anomaly_correlation"], sc["trend_difference_mm_yr"]
    print(f"PASS run {r['run_id']}: sanctioned code on both sides, "
          f"{obs['short_name']} {obs['version']} ({obs['doi']}) at its manifest "
          f"and grids digest{tree_note}, {n} months {months[0]} to {months[-1]}, "
          f"both digests and every score recomputed{model_note}: rmsd "
          f"{rm['value']:.4f} mm [{rm['ci_low']:.4f}, {rm['ci_high']:.4f}], "
          f"correlation {c['value']:+.4f} [{c['ci_low']:+.4f}, {c['ci_high']:+.4f}], "
          f"anomaly correlation {a['value']:+.4f} [{a['ci_low']:+.4f}, {a['ci_high']:+.4f}], "
          f"trend difference {t['trend']:+.4f} mm/yr [{t['ci_low']:+.4f}, {t['ci_high']:+.4f}]; "
          f"independence stated: {obs['independence']['degree']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
