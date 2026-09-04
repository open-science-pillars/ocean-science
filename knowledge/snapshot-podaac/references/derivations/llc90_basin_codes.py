# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "ecco_v4_py"]
# ///
"""Derive the llc90 basin code field the section computations use to
scope a latitude circle to one ocean basin.

The source is ECCO's own basin definition, binary_data/basins.data in
the ECCOv4-py repository (a compact llc90 float32 field of integer
basin codes; the code-to-name order is ecco_v4_py's
get_available_basin_names, where code = index + 1 and 0 is land or
unassigned). The file is fetched at a pinned commit, its SHA-256 is
checked against the value recorded here, and ecco_v4_py's own
compact-to-tiles conversion turns it into (13, 90, 90). The result is
written beside this file as references/masks/llc90_basin_codes.npz
with a JSON sidecar carrying the names, the source, the commit, both
hashes, and the cell count per basin, so a computation that reads the
npz can name its basin definition by hash without needing ecco_v4_py
or the network.

The extended basins ecco_v4_py composes (atlExt = atl + mexico +
hudson + med + north + barents; pacExt and indExt likewise) are NOT
stored: a computation composes them from the codes if it wants them,
and says so. The RAPID-comparable Atlantic section at 26.5N is "atl"
alone (Florida to Africa); "mexico" is the Gulf of Mexico, which the
26.5N circle also crosses and the array does not observe.
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np

REPO = "https://raw.githubusercontent.com/ECCO-GROUP/ECCOv4-py"
COMMIT = "5e0abd596d50d821df658a0b5ef32ed7fe8ee4c5"   # master, 2026-09-02
SOURCE_SHA256 = "65a6ada6f1cbdd6de424a0d666048977fece391aed013400c8f535700cab422e"
OUT = Path(__file__).resolve().parent.parent / "masks" / "llc90_basin_codes"


def main() -> int:
    work = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "binary_data"
    work.mkdir(parents=True, exist_ok=True)
    for name in ("basins.data", "basins.meta"):
        p = work / name
        if not p.exists():
            urllib.request.urlretrieve(f"{REPO}/{COMMIT}/binary_data/{name}", p)
    got = hashlib.sha256((work / "basins.data").read_bytes()).hexdigest()
    if got != SOURCE_SHA256:
        sys.exit(f"basins.data sha256 {got} is not the pinned {SOURCE_SHA256}")

    from ecco_v4_py.get_basin import get_available_basin_names
    from ecco_v4_py.read_bin_llc import read_llc_to_tiles
    names = get_available_basin_names()
    codes = np.asarray(read_llc_to_tiles(str(work), "basins.data",
                                         less_output=True))
    assert codes.shape == (13, 90, 90), codes.shape
    assert np.all(codes == np.round(codes)), "non-integer basin code"
    codes = codes.astype(np.int8)
    counts = {n: int((codes == i + 1).sum()) for i, n in enumerate(names)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT.with_suffix(".npz"), codes=codes)
    side = {
        "field": "basin code per llc90 cell, (13, 90, 90) int8; 0 is land "
                 "or unassigned; code = index + 1 in names",
        "names": names,
        "cells": counts,
        "source": f"{REPO}/{COMMIT}/binary_data/basins.data",
        "source_sha256": SOURCE_SHA256,
        "converted_with": "ecco_v4_py 1.8.1 read_llc_to_tiles",
        "codes_sha256": hashlib.sha256(codes.tobytes()).hexdigest(),
        "codes_sha256_note": "sha256 of the (13, 90, 90) int8 array in C "
                             "order; the identity a computation records, "
                             "stable across re-derivations (the npz "
                             "container carries a timestamp)",
        "derived_by": Path(__file__).name,
    }
    OUT.with_suffix(".json").write_text(json.dumps(side, indent=1) + "\n")
    print(f"{OUT.with_suffix('.npz')}: {len(names)} basins; "
          f"atl {counts['atl']} cells, mexico {counts['mexico']} cells; "
          f"codes sha256 {side['codes_sha256'][:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
