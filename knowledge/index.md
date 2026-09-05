---
okf_version: "0.2"
---

# ocean-science bundle

The ocean-science knowledge bundle: the concepts this plugin owns (the
climate index conventions, the mixed layer criteria convention, the
three observational connectors) beside a pinned copy of the PO.DAAC
provider bundle. OKF v0.2 conformant (okf_version "0.2" above; the
exact spec text is vendored in marketplace docs/upstream). Skills and
agents consult both parts the same way: glob the bundle root and the
copy directory, read every match in full, cite by path with status.

## snapshot-podaac (pinned copy of the PO.DAAC bundle, SPEC 5.7)

- Canonical home: github.com/open-science-pillars/nasa-daac-knowledge (knowledge/podaac/)
- Snapshot source commit: b6ac8fc0d5c1
- Snapshot date: 2026-09-04
- Scope: the whole bundle except tutorial/ (the tutorial companions
  are inputs to the tutorials, not to skills), declared in
  `snapshot.yaml` and checked by `tools/sync_check.py` in the
  canonical repository (byte-identity at the pin, MISSING, EXTRA,
  DANGLING, PIN-DRIFT). The pin is the steward's signing commit; the
  copy refreshes at every plugin release.
- Precedence: the canonical concept wins on conflict; a copied concept
  is the provider's text and ranks with it. Each copy keeps its own
  frontmatter, so a draft is copied as a draft and voiced as one.
- Contents at the pin, 135 files: datasets 6, fields 10 (plus the
  family index), gotchas 21, recipes 13, computations 18, conventions
  4, validity-domains 3, findings 1, connectors 1, and references 57
  (sanctioned code, attesters, derivations, masks, retrieval receipts
  and exhibits, the run-golden and run-sea-level skill notes). The
  concept-level listing with titles, severities and status is the
  canonical index at the pin:
  https://github.com/open-science-pillars/nasa-daac-knowledge/blob/24b27927c387fc78494a68eefa52d31a6a1c110f/knowledge/podaac/index.md
- Eval coverage for the high gotchas ships here (evals/); the cases'
  declared authority is the ecco-agent-evals repository.

## conventions (local)

- [Mixed layer depth criteria](conventions/mld-criteria.md), status: stable
- [ENSO SST indices (Nino regions, ONI)](conventions/enso-sst-indices.md), status: stable
- [NAO index](conventions/nao-index.md), status: stable
- [PDO index](conventions/pdo-index.md), status: stable
- [AMO index](conventions/amo-index.md), status: stable

The MLD criteria convention is the plugin's; the ECCO MXLDEPTH gotcha
that cites it now lives in the copy
([snapshot-podaac/gotchas/ecco-mxldepth-criterion.md](snapshot-podaac/gotchas/ecco-mxldepth-criterion.md))
and pins its link to this repository at the commit it was upstreamed
from.

## connectors (local)

- [NOAA CO-OPS tide and water-level stations](connectors/coops-tides.md), status: stable
- [Argo profiling floats via ERDDAP](connectors/argo-floats.md), status: stable
- [PSMSL long-record tide gauges](connectors/psmsl-gauges.md), status: stable
