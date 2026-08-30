#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""ecco_cite: per-collection DOIs and exact ECCO citations.

Two subcommands. `harvest` queries CMR for each ShortName in the family
manifest and writes shortname-to-DOI mappings (CMR carries the DOI in
collection metadata), ready to merge into the manifest and the fields
concepts. `cite` emits the ECCO Consortium citation block for a list of
ShortNames in the PO.DAAC-prescribed template, so an analysis can cite
exactly what it touched:

  ECCO Consortium, Fukumori, I., Wang, O., Fenty, I., Forget, G.,
  Heimbach, P., & Ponte, R. M. (2021). <Dataset Title> (Version 4
  Release 4) [Data set]. NASA PO.DAAC. https://doi.org/10.5067/<suffix>
  Dataset accessed YYYY-MM-DD.

Usage:
  ecco_cite.py harvest data/ecco_v4r4_families.yaml [--out dois.yaml]
  ecco_cite.py cite --dois dois.yaml SHORTNAME [SHORTNAME ...] [--accessed YYYY-MM-DD]
  ecco_cite.py --selftest
"""

import argparse
import datetime
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pyyaml required", file=sys.stderr)
    sys.exit(2)

# The .json feed omits the DOI field entirely (observed live 2026-08-30);
# the umm_json format carries it as umm.DOI.DOI.
CMR = "https://cmr.earthdata.nasa.gov/search/collections.umm_json"

# Real entries confirmed during program research (PO.DAAC release
# announcement and dataset pages); harvest fills the rest from CMR.
SEED_DOIS = {
    "ECCO_L4_FRESH_FLUX_LLC0090GRID_DAILY_V4R4": {
        "doi": "10.5067/ECL5D-FRE44",
        "title": "ECCO Ocean and Sea-Ice Surface Freshwater Fluxes - Daily Mean llc90 Grid (Version 4 Release 4)"},
}


def harvest(manifest_path: Path, out: Path) -> int:
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    sns = [sn for f in manifest.get("families", []) for sn in f.get("shortnames", [])]
    result, missing = {}, []
    for sn in sorted(sns):
        req = urllib.request.Request(
            CMR + "?" + urllib.parse.urlencode({"short_name": sn, "page_size": 1}),
            headers={"User-Agent": "osp-ecco-cite/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                item = (json.loads(r.read()).get("items") or [{}])[0]
        except Exception as e:
            print(f"ERROR {sn}: {e}", file=sys.stderr)
            missing.append(sn)
            continue
        umm = item.get("umm", {})
        doi = (umm.get("DOI") or {}).get("DOI")
        title = umm.get("EntryTitle") or ""
        if doi:
            result[sn] = {"doi": doi, "title": title}
            print(f"OK      {sn}  {doi}")
        else:
            missing.append(sn)
            print(f"NO-DOI  {sn}")
    out.write_text(yaml.safe_dump({"harvested": datetime.date.today().isoformat(),
                                   "dois": result, "missing": missing},
                                  sort_keys=False), encoding="utf-8")
    print(f"\n{len(result)} DOIs -> {out}; {len(missing)} without")
    return 0 if not missing else 1


def format_citation(sn: str, meta: dict, accessed: str) -> str:
    doi = meta["doi"] if meta["doi"].startswith("10.") else meta["doi"]
    return (f"ECCO Consortium, Fukumori, I., Wang, O., Fenty, I., Forget, G., "
            f"Heimbach, P., & Ponte, R. M. (2021). {meta['title']} "
            f"[Data set]. NASA PO.DAAC. https://doi.org/{doi} "
            f"Dataset accessed {accessed}.")


def cite(dois_path: Path, shortnames: list, accessed: str) -> int:
    data = yaml.safe_load(dois_path.read_text(encoding="utf-8"))
    dois = data.get("dois", data)
    rc = 0
    for sn in shortnames:
        meta = dois.get(sn)
        if not meta:
            print(f"UNKNOWN {sn}: not in {dois_path}; run harvest first", file=sys.stderr)
            rc = 1
            continue
        print(format_citation(sn, meta, accessed))
        print()
    return rc


def selftest() -> int:
    accessed = "2026-08-28"
    c = format_citation("ECCO_L4_FRESH_FLUX_LLC0090GRID_DAILY_V4R4",
                        SEED_DOIS["ECCO_L4_FRESH_FLUX_LLC0090GRID_DAILY_V4R4"], accessed)
    print(c)
    ok = ("10.5067/ECL5D-FRE44" in c and "ECCO Consortium" in c
          and "Fenty" in c and accessed in c and "Freshwater Fluxes" in c)
    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    h = sub.add_parser("harvest")
    h.add_argument("manifest", type=Path)
    h.add_argument("--out", type=Path, default=Path("ecco_v4r4_dois.yaml"))
    c = sub.add_parser("cite")
    c.add_argument("shortnames", nargs="+")
    c.add_argument("--dois", type=Path, required=True)
    c.add_argument("--accessed", default=datetime.date.today().isoformat())
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.cmd == "harvest":
        return harvest(args.manifest, args.out)
    if args.cmd == "cite":
        return cite(args.dois, args.shortnames, args.accessed)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
