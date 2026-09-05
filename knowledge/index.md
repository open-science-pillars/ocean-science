---
okf_version: "0.2"
---

# ocean-science bundle

The ocean-science knowledge bundle: the concepts this plugin owns (the
climate index conventions, the mixed layer criteria convention, the
three observational connectors). OKF v0.2 conformant (okf_version "0.2"
above; the exact spec text is vendored in marketplace docs/upstream).

## The PO.DAAC provider bundle (a declared dependency)

- Canonical home: github.com/open-science-pillars/nasa-daac-knowledge
  (knowledge/podaac/), installed alongside this plugin as the
  nasa-daac-knowledge dependency at a release the plugin names a floor
  for (`.claude-plugin/plugin.json`); nothing from it is copied here.
- How it is consulted: the core skill consult-knowledge finds every
  installed bundle through the installer's record of installed plugins
  (`claude plugin list --json`, each entry's installPath) and globs
  each bundle root the same way; skills and agents here cite provider
  concepts by bundle path, `knowledge/podaac/<type>/<concept>.md`.
- Precedence: the provider concept wins on conflict; `stable` outranks
  `draft`; a draft is voiced as a draft.
- Eval coverage for the high gotchas lives in the ecco-agent-evals
  repository, the one home of the ocean cases; nothing is copied here.

## conventions (local)

- [Mixed layer depth criteria](conventions/mld-criteria.md), status: stable
- [ENSO SST indices (Nino regions, ONI)](conventions/enso-sst-indices.md), status: stable
- [NAO index](conventions/nao-index.md), status: stable
- [PDO index](conventions/pdo-index.md), status: stable
- [AMO index](conventions/amo-index.md), status: stable

The MLD criteria convention is the plugin's; the ECCO MXLDEPTH gotcha
that cites it lives in the provider bundle
(`knowledge/podaac/gotchas/ecco-mxldepth-criterion.md`) and pins its
link to this repository at the commit it was upstreamed from.

## connectors (local)

- [NOAA CO-OPS tide and water-level stations](connectors/coops-tides.md), status: stable
- [Argo profiling floats via ERDDAP](connectors/argo-floats.md), status: stable
- [PSMSL long-record tide gauges](connectors/psmsl-gauges.md), status: stable
