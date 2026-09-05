#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib"]
# ///
"""Draw a figure from an attested receipt, and from nothing else.

Two modes, both of which first run the receipt's attester and stop on
anything but PASS, so a figure exists only for a receipt that attests:

  map     A per-cell array from the receipt's `fields` file (the .npz a
          sanctioned computation writes with --fields), scattered at
          the cell centers XC and YC. The file must hash to the sha256
          in the receipt and every array drawn must hash to its own
          recorded sha256 and match its recorded shape; a file that
          does not is refused. Draws one array (--array), or the speed
          of a component pair (--speed U V), which needs no rotation.
          Components are tile-frame and are NOT drawn as east and north
          here; a vector map needs the CS and SN rotation the
          vector-orientation concept describes.

  series  The deseasonalized series behind an attested trend receipt
          (intermediates.series_fit of the trend-with-interval
          computation), with the fitted trend and the interval the
          attester recomputed.

Every figure carries a caption with the receipt's run id, the code
sha256 prefix, the fields file sha256 prefix when one was used, and the
attester's verdict, so a reader can trace the picture to the receipt
and the receipt to the sanctioned code and the verified data tree.

The attester is named by --attester: a path, or a bare name resolved
under the installed provider plugin's references/attesters (the
installer's record via `claude plugin list --json`, or a checkout named
by NASA_DAAC_KNOWLEDGE).

Usage:
  receipt_figure.py map RECEIPT.json --attester curl_check \
      --array w_ekman --mask mask_interior --symmetric --scale 1e6 \
      --units "1e-6 m/s" --title "Ekman pumping" --out w_ekman.png
  receipt_figure.py map RECEIPT.json --attester geos_check \
      --speed u_geostrophic v_geostrophic --mask mask_interior \
      --units "m/s" --out speed.png
  receipt_figure.py series TREND_RECEIPT.json --attester trend_ci_check \
      --out ohc_series.png
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import numpy as np

PROVIDER_PLUGIN = "nasa-daac-knowledge"


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


def resolve_attester(name: str) -> Path:
    p = Path(name).expanduser()
    if p.is_file():
        return p.resolve()
    candidate = (provider_root() / "knowledge" / "podaac" / "references"
                 / "attesters" / (name if name.endswith(".py") else name + ".py"))
    if not candidate.is_file():
        sys.exit(f"attester {name} not found at {candidate}")
    return candidate


def attest(receipt: Path, attester: Path) -> str:
    """Run the deterministic attester; return its PASS line or exit."""
    run = subprocess.run([sys.executable, str(attester), str(receipt)],
                         capture_output=True, text=True)
    verdict = (run.stdout.strip() or run.stderr.strip()).splitlines()
    line = verdict[-1] if verdict else ""
    if run.returncode != 0 or not line.startswith("PASS"):
        sys.exit(f"refusing to draw: {attester.name} did not PASS this receipt\n"
                 + "\n".join(verdict))
    return line


def load_fields(receipt: dict, receipt_path: Path):
    """The fields file, located and hashed as the attesters do it."""
    fb = receipt.get("fields")
    if not isinstance(fb, dict):
        sys.exit("this receipt carries no `fields` block; rerun the "
                 "computation with --fields PATH to get per-cell arrays")
    candidates = [Path(fb["path"]), receipt_path.parent / Path(fb["path"]).name]
    found = next((c for c in candidates if c.is_file()), None)
    if found is None:
        sys.exit(f"fields file {fb['path']} not found at its recorded path "
                 "or beside the receipt")
    got = hashlib.sha256(found.read_bytes()).hexdigest()
    if got != fb["sha256"]:
        sys.exit(f"fields file {found} does not hash to the receipt's sha256")
    return np.load(found), fb, found


def take(z, fb: dict, name: str) -> np.ndarray:
    """One array, checked against its recorded shape and raw-bytes hash."""
    if name not in fb["arrays"]:
        sys.exit(f"array {name} is not recorded in the receipt's fields block "
                 f"(recorded: {', '.join(fb['arrays'])})")
    if name not in z.files:
        sys.exit(f"array {name} is recorded in the receipt but missing from "
                 "the fields file")
    a = np.ascontiguousarray(z[name])
    spec = fb["arrays"][name]
    if list(a.shape) != list(spec["shape"]):
        sys.exit(f"array {name} shape {list(a.shape)} != recorded {spec['shape']}")
    if hashlib.sha256(a.tobytes()).hexdigest() != spec["sha256"]:
        sys.exit(f"array {name} does not hash to its recorded sha256")
    return a


def caption(receipt: dict, verdict: str, attester: Path, fields_sha=None) -> str:
    bits = [f"receipt run {receipt['run_id']}",
            f"code sha256 {receipt['code_sha256'][:12]}"]
    if fields_sha:
        bits.append(f"fields sha256 {fields_sha[:12]}")
    rec = receipt.get("data", {}).get("record")
    if isinstance(rec, dict) and rec.get("record"):
        bits.append(f"data {rec['record']}")
    bits.append(f"{attester.name} {verdict.split()[0]}")
    return " · ".join(bits)


def draw_map(args) -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    receipt_path = Path(args.receipt).expanduser().resolve()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    attester = resolve_attester(args.attester)
    verdict = attest(receipt_path, attester)
    z, fb, found = load_fields(receipt, receipt_path)

    xc = take(z, fb, "XC").astype(np.float64)
    yc = take(z, fb, "YC").astype(np.float64)
    if args.speed:
        u = take(z, fb, args.speed[0]).astype(np.float64)
        v = take(z, fb, args.speed[1]).astype(np.float64)
        val = np.hypot(u, v)
        what = f"speed from {args.speed[0]}, {args.speed[1]}"
    else:
        val = take(z, fb, args.array).astype(np.float64)
        what = args.array
    val = val * args.scale
    keep = np.isfinite(val)
    if args.mask:
        keep &= take(z, fb, args.mask).astype(bool)
    n = int(keep.sum())
    if n == 0:
        sys.exit("nothing to draw: no finite values under the mask")
    x, y, c = xc[keep], yc[keep], val[keep]

    if args.vmin is not None and args.vmax is not None:
        vmin, vmax = args.vmin, args.vmax
    elif args.symmetric:
        vmax = float(np.percentile(np.abs(c), 98)); vmin = -vmax
    else:
        vmin, vmax = (float(np.percentile(c, 2)), float(np.percentile(c, 98)))
    cmap = args.cmap or ("RdBu_r" if args.symmetric else "viridis")

    fig, ax = plt.subplots(figsize=(11, 5.8), dpi=150)
    sc = ax.scatter(x, y, c=c, s=args.marker_size, marker="s", linewidths=0,
                    cmap=cmap, vmin=vmin, vmax=vmax, rasterized=True)
    ax.set_xlim(-180, 180); ax.set_ylim(-90, 90)
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    ax.set_facecolor("#f2f2f2")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    cb = fig.colorbar(sc, ax=ax, pad=0.02, shrink=0.85)
    cb.set_label(args.units or "")
    bp = receipt.get("bound_parameters", {})
    title = args.title or what
    if bp.get("month"):
        title = f"{title}, {bp['month']}"
    ax.set_title(f"{title}  (n = {n:,} cells{', mask ' + args.mask if args.mask else ''})")
    fig.text(0.01, 0.01, textwrap.fill(caption(receipt, verdict, attester, fb["sha256"]), 150),
             fontsize=7, family="monospace", alpha=0.85)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"{out}: {what}, {n:,} cells, range [{vmin:.4g}, {vmax:.4g}] "
          f"{args.units or ''}".rstrip())
    print(f"  {caption(receipt, verdict, attester, fb['sha256'])}")
    return 0


def draw_series(args) -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    import datetime as dt

    receipt_path = Path(args.receipt).expanduser().resolve()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    attester = resolve_attester(args.attester)
    verdict = attest(receipt_path, attester)
    if receipt.get("computation") != "trend-ci":
        sys.exit("series mode reads a trend-with-interval receipt "
                 "(computation trend-ci); this receipt is not one")

    dates = [dt.date(int(d[:4]), int(d[5:7]), 15) for d in receipt["series"]["dates"]]
    fit = np.asarray(receipt["intermediates"]["series_fit"], dtype=np.float64)
    inter = receipt["intermediates"]; res = receipt["results"]; bp = receipt["bound_parameters"]
    n = len(fit)
    t = np.arange(n, dtype=np.float64); t0 = t - t.mean()
    slope_m = inter["slope_per_month"]; b0 = inter["intercept"]
    mpy = bp.get("months_per_year", 12.0)
    line = b0 + slope_m * t0
    lo = b0 + (res["ci_low"] / mpy) * t0
    hi = b0 + (res["ci_high"] / mpy) * t0
    units = res.get("units", "").split("/")[0] or bp.get("report_units", "")
    src = receipt.get("data", {}).get("source_receipt", {})

    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=150)
    ax.fill_between(dates, np.minimum(lo, hi), np.maximum(lo, hi),
                    color="#c9a227", alpha=0.25, linewidth=0,
                    label=f"{int(bp.get('confidence', 0.95) * 100)} percent interval on the trend")
    ax.plot(dates, fit, color="#1f4e79", linewidth=1.1,
            label=f"monthly, seasonal cycle removed ({bp.get('field', 'series')})")
    ax.plot(dates, line, color="#b2411c", linewidth=1.6,
            label=f"trend {res['trend']:+.2f} [{res['ci_low']:+.2f}, {res['ci_high']:+.2f}] {res['units']}")
    ax.axhline(0, color="k", linewidth=0.4)
    ax.set_ylabel(f"anomaly, {units}")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_title(args.title or f"{bp.get('field', 'series')} from {receipt['series']['dates'][0]} "
                 f"to {receipt['series']['dates'][-1]}, deseasonalized "
                 f"({bp.get('deseasonalize')}), n {n}, n_eff {res['n_eff']:.1f}, r1 {res['r1']:.3f}")
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    cap = caption(receipt, verdict, attester)
    if src.get("run_id"):
        cap += f" · source receipt run {src['run_id']} code {src.get('code_sha256', '')[:12]}"
    fig.text(0.01, 0.01, textwrap.fill(cap, 150), fontsize=7, family="monospace",
             alpha=0.85)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"{out}: {n} months, trend {res['trend']:+.4f} [{res['ci_low']:+.4f}, "
          f"{res['ci_high']:+.4f}] {res['units']}, n_eff {res['n_eff']:.2f}")
    print(f"  {cap}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    m = sub.add_parser("map", help="scatter one per-cell array at XC, YC")
    m.add_argument("receipt")
    m.add_argument("--attester", required=True,
                   help="attester path, or a bare name under the provider's references/attesters")
    g = m.add_mutually_exclusive_group(required=True)
    g.add_argument("--array", help="array name in the fields file")
    g.add_argument("--speed", nargs=2, metavar=("U", "V"),
                   help="draw hypot(U, V), rotation-free")
    m.add_argument("--mask", help="boolean array in the fields file to restrict to")
    m.add_argument("--scale", type=float, default=1.0, help="multiply values before drawing")
    m.add_argument("--units", default="", help="colorbar label")
    m.add_argument("--symmetric", action="store_true",
                   help="diverging colormap centered on zero (98th percentile of |value|)")
    m.add_argument("--vmin", type=float); m.add_argument("--vmax", type=float)
    m.add_argument("--cmap")
    m.add_argument("--marker-size", type=float, default=4.0,
                   help="scatter marker area in points squared; 4 lets one-degree cells touch")
    m.add_argument("--title")
    m.add_argument("--out", required=True)
    m.set_defaults(func=draw_map)
    s = sub.add_parser("series", help="deseasonalized series and trend from a trend receipt")
    s.add_argument("receipt")
    s.add_argument("--attester", default="trend_ci_check")
    s.add_argument("--title")
    s.add_argument("--out", required=True)
    s.set_defaults(func=draw_series)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
