#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Assemble and stamp the data root of the attested Argo ocean heat
content change: the two term files the loader wrote, their stamps,
SOURCES.json, and the RECORD.json the sanctioned computation refuses
to run without.

The record carries the record name, the SHA-256 manifest of every file
in the root (the two CSVs, the two stamps and SOURCES.json), the time
of stamping, the loader's stamps, and the bookkeeping table under
`bookkeeping` with every statement the computation requires:
`climatology` (the reference field and its period), `anomaly_convention`
(what a value and a difference between two values mean), `coverage`
(the mask, the cell count, the latitude band and the domain area in
square meters), `deep_omission` (the ocean below 2000 dbar, not in any
term), `uncertainty` (the basis of the per-month floor), and `anchor`
(the published Argo-era rate per layer that the concept compares the
run with, in watts per square meter of the Earth's surface, with its
uncertainty, period, ocean-area fraction and source). The statements
are read from the loader's stamps where the loader determined them
(the mask, the coverage, the area, the floor) and from the sources the
bundle's concepts cite for the rest; this file is where they are
written down, so a reader auditing a run starts here.

Usage:
  ohc_data_root.py --root DIR --record NAME
      DIR holds ohc-700.csv, ohc-2000.csv, ohc-700-stamp.json,
      ohc-2000-stamp.json and SOURCES.json
  ohc_data_root.py --root DIR --check
      verify an existing RECORD.json against the files (exit 1 on drift)
  ohc_data_root.py --selftest
      build and check a root from a synthetic pair of term files
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
import tempfile
from pathlib import Path

TERMS = ("ohc-700", "ohc-2000")
FILES = tuple(f"{t}.csv" for t in TERMS) + tuple(f"{t}-stamp.json" for t in TERMS) + ("SOURCES.json",)
ANCHOR_SOURCE = ("von Schuckmann and others (2023), Heat stored in the Earth system 1960 to 2020: "
                 "where does the energy go?, Earth System Science Data 15, 1675 to 1709, "
                 "doi:10.5194/essd-15-1675-2023, Table 1 (LOWESS trends 2006 to 2020, watts per "
                 "square meter relative to the global surface; the paper's ocean-surface factor "
                 "0.61 for the area 60S to 60N deeper than 300 m)")
ANCHORS = {
    "ohc-700": {"layer": "0 to 700 m", "value_W_m2_global": 0.39, "uncertainty_W_m2_global": 0.1,
                "period": "2006 to 2020", "ocean_area_fraction": 0.61, "source": ANCHOR_SOURCE},
    "ohc-2000": {"layer": "0 to 2000 m", "value_W_m2_global": 0.62, "uncertainty_W_m2_global": 0.2,
                 "period": "2006 to 2020", "ocean_area_fraction": 0.61, "source": ANCHOR_SOURCE},
}


def sha256(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def manifest(root: Path) -> dict:
    out = {}
    for name in FILES:
        p = root / name
        if not p.is_file():
            sys.exit(f"{root} lacks {name}")
        out[name] = sha256(p)
    return out


def bookkeeping(stamps: dict) -> dict:
    s7, s20 = stamps["ohc-700"], stamps["ohc-2000"]
    cov = s20.get("coverage") or {}
    return {
        "climatology": {
            "statement": s20.get("climatology", ""),
            "period": "2004-01 through 2018-12, the RG 2019 release's mean field",
            "product_version": s20.get("product_version", ""),
        },
        "anomaly_convention": {
            "statement": s20.get("anomaly_convention", ""),
            "note": "the extension files carry anomalies against the same 2004 to 2018 mean, so "
                    "the series joins the climatology months and the extension months on one "
                    "baseline (the bundle's rg-anomaly-against-a-fixed-climatology gotcha)",
        },
        "coverage": {
            "statement": f"{s20.get('mask', '')}; {cov.get('statement', '')}",
            "cells": cov.get("cells"), "cells_total": cov.get("cells_total"),
            "domain_area_m2": cov.get("domain_area_m2"),
            "latitude_min": cov.get("latitude_min"), "latitude_max": cov.get("latitude_max"),
            "months": s20.get("months"),
            "note": "the domain is the product's mapped open ocean, not the global ocean: the "
                    "grid starts at 64.5S, the marginal seas mapped to a shallower limit drop "
                    "out of the fixed mask, and the value is never scaled up (the bundle's "
                    "rg-coverage-excludes-high-latitudes-and-marginal-seas gotcha)",
            "grid": s20.get("grid", ""),
        },
        "layers": {t: stamps[t].get("layer") for t in TERMS},
        "deep_omission": {
            "statement": s20.get("deep_omission", ""),
            "note": "the product stops at 1975 dbar (the bundle's rg-sampled-depth-floor gotcha); "
                    "the computation states the published rate below 2000 m beside the terms "
                    "and never adds it",
        },
        "uncertainty": {
            "basis": s20.get("uncertainty_basis", ""),
            "ohc-700_ZJ": s7.get("uncertainty_ZJ"), "ohc-2000_ZJ": s20.get("uncertainty_ZJ"),
            "note": "the sanctioned computation takes the larger of this floor's formal "
                    "propagation and the sampling half width of its trend",
        },
        "anchor": dict(ANCHORS),
    }


def build(root: Path, record: str):
    stamps = {}
    for t in TERMS:
        p = root / f"{t}-stamp.json"
        if not p.is_file():
            sys.exit(f"{root} lacks {t}-stamp.json (the loader's stamp)")
        stamps[t] = json.loads(p.read_text(encoding="utf-8"))
    files = manifest(root)
    mh = hashlib.sha256("\n".join(f"{k} {v}" for k, v in sorted(files.items())).encode()).hexdigest()
    stamp = {
        "record": record,
        "manifest": files,
        "manifest_sha256": "sha256:" + mh,
        "verified_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "terms": stamps,
        "bookkeeping": bookkeeping(stamps),
    }
    (root / "RECORD.json").write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")
    print(f"RECORD.json written for {record}: manifest sha256:{mh[:16]}, "
          + ", ".join(f"{t} {stamps[t]['months'][0]} to {stamps[t]['months'][1]}" for t in TERMS))


def check(root: Path) -> None:
    stamp = json.loads((root / "RECORD.json").read_text(encoding="utf-8"))
    files = manifest(root)
    if files != stamp.get("manifest"):
        sys.exit("RECORD.json manifest does not match the files")
    mh = hashlib.sha256("\n".join(f"{k} {v}" for k, v in sorted(files.items())).encode()).hexdigest()
    if stamp.get("manifest_sha256") != "sha256:" + mh:
        sys.exit("RECORD.json manifest_sha256 does not match the manifest")
    for section, key in (("climatology", "statement"), ("anomaly_convention", "statement"),
                         ("coverage", "statement"), ("coverage", "domain_area_m2"),
                         ("deep_omission", "statement"), ("uncertainty", "basis")):
        if not (stamp.get("bookkeeping") or {}).get(section, {}).get(key):
            sys.exit(f"RECORD.json bookkeeping lacks {section}.{key}")
    print(f"RECORD.json matches the files ({len(files)} files, record {stamp.get('record')})")


def selftest():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for t in TERMS:
            (root / f"{t}.csv").write_text("month,value_ZJ,uncertainty_ZJ\n2005-01,0.0,1.0\n2005-02,1.0,1.0\n")
            (root / f"{t}-stamp.json").write_text(json.dumps({
                "term": t, "months": ["2005-01", "2005-02"], "climatology": "selftest mean",
                "anomaly_convention": "selftest anomaly", "mask": "selftest mask",
                "coverage": {"statement": "2 cells", "cells": 2, "cells_total": 4,
                             "domain_area_m2": 2.0e14, "latitude_min": -1.0, "latitude_max": 1.0},
                "deep_omission": "not sampled", "uncertainty_basis": "selftest floor",
                "uncertainty_ZJ": 1.0, "layer": {"floor_dbar": float(t.split("-")[1])}}) + "\n")
        (root / "SOURCES.json").write_text("{}\n")
        build(root, "selftest-root")
        check(root)
        rec = json.loads((root / "RECORD.json").read_text())
        assert rec["bookkeeping"]["coverage"]["domain_area_m2"] == 2.0e14
        assert rec["bookkeeping"]["anchor"]["ohc-2000"]["value_W_m2_global"] == 0.62
        assert set(rec["manifest"]) == set(FILES)
        (root / "ohc-700.csv").write_text("month,value_ZJ,uncertainty_ZJ\n2005-01,0.0,1.0\n")
        try:
            check(root)
            raise AssertionError("drift not caught")
        except SystemExit as e:
            assert "manifest" in str(e)
    print("ohc_data_root selftest: ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path)
    ap.add_argument("--record")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if not a.root:
        ap.error("--root is required")
    if a.check:
        check(a.root); return
    if not a.record:
        ap.error("--record is required to build")
    build(a.root, a.record)


if __name__ == "__main__":
    main()
