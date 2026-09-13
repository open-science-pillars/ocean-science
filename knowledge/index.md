---
okf_version: "0.2"
---

# ocean-science bundle

The ocean-science knowledge bundle: the concepts this plugin owns (the
climate index conventions, the mixed layer criteria convention, the
three observational connectors, and the gridded Argo product that is
the steric term of the plugin's sea level budget with its gotchas). OKF v0.2 conformant (okf_version "0.2"
above; the exact spec text is vendored in marketplace docs/upstream).

## The PO.DAAC provider bundle (a declared dependency)

- Canonical home: github.com/open-science-pillars/nasa-daac-knowledge
  (knowledge/podaac/), installed alongside this plugin as the
  nasa-daac-knowledge dependency at a release the plugin names a floor
  for (`.osp/package.yaml`, from which the plugin manifest is rendered);
  nothing from it is copied here.
- How it is consulted: the core skill consult-knowledge finds every
  installed bundle through the installer's record of installed plugins
  (`claude plugin list --json`, each entry's installPath) and globs
  each bundle root the same way; skills and agents here cite provider
  concepts by bundle path, `knowledge/podaac/<type>/<concept>.md`.
- Precedence: the provider concept wins on conflict; `stable` outranks
  `draft`; a draft is voiced as a draft.
- Eval coverage for the high gotchas lives in the agent-evals
  repository (its ECCO set, `ecco/cases/`), the one home of the ocean
  cases; nothing is copied here.

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

## datasets (local)

- [Roemmich and Gilson Argo climatology (Scripps, 2019 release with monthly extensions)](datasets/roemmich-gilson-argo-climatology.md), status: draft

The Scripps product is not a NASA DAAC product, so it has no provider
bundle to move to; it is local domain material.

## gotchas (local)

- [The Roemmich and Gilson product stops at 1975 dbar: a steric height or heat content from it is an upper 2000 dbar term, and a budget that carries it as the whole steric term omits the deep ocean](gotchas/rg-sampled-depth-floor.md), severity high, status: draft
- [The Roemmich and Gilson grid starts at 64.5S and its global average masks out the marginal seas and the Arctic: a global mean from this product is an open-ocean mean over that domain](gotchas/rg-coverage-excludes-high-latitudes-and-marginal-seas.md), severity medium, status: draft
- [The Roemmich and Gilson anomalies are departures from the 2004 to 2018 mean and annual cycle, and the extension files keep that reference: joining releases or re-baselining moves an intercept and a comparison, not a slope](gotchas/rg-anomaly-against-a-fixed-climatology.md), severity medium, status: draft

The high gotcha's eval case, rg-sampled-depth-floor, lives in the
agent-evals repository (`ecco/cases/`), the one home of the ocean
cases.

## connectors (local)

- [NOAA CO-OPS tide and water-level stations](connectors/coops-tides.md), status: stable
- [Argo profiling floats via ERDDAP](connectors/argo-floats.md), status: stable
- [PSMSL long-record tide gauges](connectors/psmsl-gauges.md), status: stable
