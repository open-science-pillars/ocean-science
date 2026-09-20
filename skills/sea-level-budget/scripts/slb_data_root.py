#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Assemble and stamp the data root of the attested sea level budget
closure: the three term files the loaders wrote and the RECORD.json the
sanctioned computation refuses to run without.

The stamp carries the record name, the SHA-256 manifest of the three
CSV files, the time of stamping, the three loaders' own stamps (what
each read and how), and the corrections table under `bookkeeping` with
every statement the computation requires: `gia`, `inverse_barometer`,
`reference_frame` and `effective_smoothing` for altimetry and mass,
`low_degree.mass`, and `deep_steric.sampled_depth_floor_m` and
`deep_steric.steric_source`. The statements are read from the loaders'
stamps where the loader determined them (the mask, the coverage, the
GIA choice, the floor) and from the product documentation the bundle's
concepts cite for the rest; this file is where they are written down,
so a reader auditing a residual starts here.

Usage:
  slb_data_root.py --root DIR --record NAME
      DIR holds altimetry.csv, steric.csv, mass.csv and the loaders'
      stamps altimetry-stamp.json, steric-stamp.json, mass-stamp.json
  --check   verify an existing RECORD.json against the files (exit 1 on drift)
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

TERMS = ("altimetry", "steric", "mass")


def sha256(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def manifest(root: Path) -> dict:
    out = {}
    for t in TERMS:
        p = root / f"{t}.csv"
        if not p.is_file():
            sys.exit(f"{root} lacks {t}.csv")
        out[p.name] = sha256(p)
    return out


def bookkeeping(stamps: dict) -> dict:
    alt, ste, mas = stamps["altimetry"], stamps["steric"], stamps["mass"]
    return {
        "gia": {
            "altimetry": alt.get("gia", ""),
            "mass": "ICE-6G_D (Peltier and others 2018) subtracted by the product before the "
                    "CRI filter and from the released fields, referenced to the 2008-01-01 "
                    "epoch of the static field (the release note; the bundle's GIA gotcha)",
        },
        "inverse_barometer": {
            "altimetry": "dynamic atmospheric correction applied by the product (the NASA-SSH "
                         "user guide): the inverse-barometer response and the high-frequency "
                         "wind and pressure response removed from ssha",
            "mass": mas.get("gad", ""),
        },
        "reference_frame": {
            "altimetry": "the orbit frame of the reference missions (ITRF through the precise "
                         "orbits; the product's mean sea surface " + str(alt.get("mean_sea_surface")) + ")",
            "mass": "centre of figure restored through JPL's mascon-consistent geocenter "
                    "(degree 1 computed with the mascon field as background, the release note)",
        },
        "effective_smoothing": {
            "altimetry": f"{alt.get('gridding_method')}; latitude coverage "
                         f"{alt.get('latitude_coverage')}; global mean over the cells that carry "
                         "a value, so the polar oceans the reference missions do not reach are "
                         "not in the term",
            "mass": "3-degree spherical-cap mascons on a 0.5-degree grid; " + str(mas.get("ocean_mask")) +
                    "; leakage from land into the coastal ocean mascons is the product's CRI "
                    "residual (the bundle's coastal-leakage gotcha)",
        },
        "low_degree": {
            "mass": "C20 and C30 from TN-14 version 3 across the whole series, degree 1 from "
                    "JPL's mascon-consistent geocenter; nothing re-applied (the release note; "
                    "the bundle's low-degree gotcha)",
        },
        "deep_steric": {
            "sampled_depth_floor_m": ste.get("sampled_depth_floor_m"),
            "steric_source": ste.get("product", "") + "; " + ste.get("method", ""),
        },
        "uncertainty": {
            "altimetry": alt.get("uncertainty_basis", ""),
            "steric": ste.get("uncertainty_basis", ""),
            "mass": mas.get("uncertainty_basis", ""),
        },
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


def check(root: Path):
    stamp = json.loads((root / "RECORD.json").read_text(encoding="utf-8"))
    files = manifest(root)
    if files != stamp.get("manifest"):
        sys.exit("RECORD.json manifest does not match the files")
    print("RECORD.json matches the files")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--record")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check(a.root); return
    if not a.record:
        ap.error("--record is required to build")
    build(a.root, a.record)


if __name__ == "__main__":
    main()
