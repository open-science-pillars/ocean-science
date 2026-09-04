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
ShortNames, so an analysis can cite exactly what it touched. The
prescribed form (creator list, year, publisher, DOI, access date) is
recorded on the dataset concept, knowledge/podaac/datasets/ecco-v4r4.md
(Citation section, quoting the PO.DAAC landing pages); this tool
renders those elements in reference-list order:

  ECCO Consortium, Fukumori, I., Wang, O., Fenty, I., Forget, G.,
  Heimbach, P., & Ponte, R. M. (2021). <Dataset Title> (Version 4
  Release 4) [Data set]. NASA PO.DAAC. https://doi.org/10.5067/<suffix>
  Dataset accessed YYYY-MM-DD.

`tools/ecco_v4r4_dois.yaml` is the one authority for the ShortName to
DOI mapping. The manifest's per-family `dois:` blocks and the `DOI:`
rows in the fields concepts quote it, and `--selftest` cross-checks
every quoted DOI against it (run by tools/run_checks.sh), so a DOI can
only change in one place and the copies cannot drift unnoticed. The
selftest also checks that the creator list, year, and publisher this
template renders still appear in the dataset concept's Citation
section, so the two cannot drift either.

Usage:
  ecco_cite.py harvest tools/ecco_v4r4_families.yaml [--out dois.yaml]
  ecco_cite.py cite --dois dois.yaml SHORTNAME [SHORTNAME ...] [--accessed YYYY-MM-DD]
  ecco_cite.py --selftest
"""

import argparse
import datetime
import json
import re
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

# Where the authority and its quotations live, relative to this file.
HERE = Path(__file__).resolve().parent
DOIS_FILE = HERE / "ecco_v4r4_dois.yaml"
FAMILIES_FILE = HERE / "ecco_v4r4_families.yaml"
FIELDS_DIR = HERE.parent / "knowledge" / "podaac" / "fields" / "ecco-v4r4"
# The dataset concept records the prescribed citation form; these are the
# elements shared by every collection, which format_citation must match.
CITATION_CONCEPT = HERE.parent / "knowledge" / "podaac" / "datasets" / "ecco-v4r4.md"
CITATION_ELEMENTS = ("ECCO Consortium, Fukumori, I., Wang, O., Fenty, I., Forget, G.,",
                     "Heimbach, P., & Ponte, R. M.", "2021", "PO.DAAC")
# A fields concept lists a collection as `SHORTNAME`: ... DOI: 10.5067/SUFFIX.
DOI_ROW = re.compile(r"`(ECCO_[A-Z0-9_]+)`[^\n]*?DOI:\s*(10\.5067/[A-Za-z0-9-]+)")


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


def crosscheck(dois_path: Path = DOIS_FILE, families_path: Path = FAMILIES_FILE,
               fields_dir: Path = FIELDS_DIR) -> list:
    """Every DOI quoted in the manifest or a fields concept must match the
    authority, and every manifest ShortName must have one. Returns the
    list of problems (empty when the mapping has one voice)."""
    problems = []
    dois = {sn: m["doi"] for sn, m in
            yaml.safe_load(dois_path.read_text(encoding="utf-8"))["dois"].items()}
    quoted = 0

    def compare(where: str, sn: str, doi: str) -> None:
        nonlocal quoted
        quoted += 1
        if sn not in dois:
            problems.append(f"{where}: {sn} quotes {doi} but {dois_path.name} has no entry for it")
        elif dois[sn] != doi:
            problems.append(f"{where}: {sn} quotes {doi}, {dois_path.name} says {dois[sn]}")

    manifest = yaml.safe_load(families_path.read_text(encoding="utf-8"))
    for fam in manifest.get("families", []):
        for sn in fam.get("shortnames", []):
            if sn not in dois:
                problems.append(f"{families_path.name}: {sn} has no DOI in {dois_path.name}; run harvest")
        for sn, doi in (fam.get("dois") or {}).items():
            compare(f"{families_path.name} family {fam.get('slug', '?')}", sn, doi)
    for md in sorted(fields_dir.glob("*.md")):
        for sn, doi in DOI_ROW.findall(md.read_text(encoding="utf-8")):
            compare(md.name, sn, doi)
    print(f"crosscheck: {len(dois)} DOIs in {dois_path.name}; {quoted} quotations "
          f"in the manifest and {fields_dir.name} concepts checked; {len(problems)} problem(s)")
    for line in problems:
        print("  " + line)
    return problems


def selftest() -> int:
    accessed = "2026-08-28"
    c = format_citation("ECCO_L4_FRESH_FLUX_LLC0090GRID_DAILY_V4R4",
                        SEED_DOIS["ECCO_L4_FRESH_FLUX_LLC0090GRID_DAILY_V4R4"], accessed)
    print(c)
    ok = ("10.5067/ECL5D-FRE44" in c and "ECCO Consortium" in c
          and "Fenty" in c and accessed in c and "Freshwater Fluxes" in c)
    if DOIS_FILE.exists() and FAMILIES_FILE.exists() and FIELDS_DIR.is_dir():
        ok = ok and not crosscheck()
    else:
        print("crosscheck: skipped (authority, manifest, or fields concepts not beside this file)")
    if CITATION_CONCEPT.exists():
        text = CITATION_CONCEPT.read_text(encoding="utf-8")
        section = text.split("## Citation", 1)[1].split("\n## ", 1)[0] if "## Citation" in text else ""
        missing = [e for e in CITATION_ELEMENTS if e not in section or e not in c]
        print(f"citation form: {CITATION_CONCEPT.name} Citation section and the template "
              f"share {len(CITATION_ELEMENTS) - len(missing)}/{len(CITATION_ELEMENTS)} elements")
        for e in missing:
            print(f"  missing from the concept or the template: {e!r}")
        ok = ok and not missing
    else:
        print("citation form: skipped (dataset concept not beside this file)")
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
