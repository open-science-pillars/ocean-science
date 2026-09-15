---
okf_version: "0.2"
---

# ocean-science bundle

The ocean-science knowledge bundle: the concepts this plugin owns (the
climate index conventions, the mixed layer criteria convention, the
three observational connectors, the gridded Argo climatology
whose steric height and heat content cover the upper 2000 dbar of
the open ocean, with its gotchas, the attested ocean heat content
computation on it with its recipe, and the tide gauge datum and land
motion gotchas on the PSMSL and CO-OPS connectors). OKF v0.2 conformant (okf_version "0.2"
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

- [Roemmich and Gilson Argo climatology (Scripps, 2019 release with monthly extensions)](datasets/roemmich-gilson-argo-climatology.md), status: stable

The Scripps product is not a NASA DAAC product, so it has no provider
bundle to move to; it is local domain material.

## gotchas (local)

- [Roemmich and Gilson steric height and heat content stop at 1975 dbar](gotchas/rg-sampled-depth-floor.md), severity high, status: stable
- [The Roemmich and Gilson grid starts at 64.5S and its global average masks out the marginal seas and the Arctic](gotchas/rg-coverage-excludes-high-latitudes-and-marginal-seas.md), severity medium, status: stable
- [The Roemmich and Gilson anomalies are departures from a fixed 2004 to 2018 climatology](gotchas/rg-anomaly-against-a-fixed-climatology.md), severity medium, status: stable
- [PSMSL RLR records are reduced to one station datum and metric records are not](gotchas/psmsl-rlr-versus-metric.md), severity high, status: stable
- [CO-OPS water levels are heights above a chosen datum on the 1983 to 2001 epoch](gotchas/coops-datum-and-epoch.md), severity medium, status: stable
- [A tide gauge trend is relative sea level and carries the land's vertical motion](gotchas/tide-gauge-relative-sea-level-and-land-motion.md), severity high, status: stable
- [The GIA correction at a tide gauge is a model prediction that names its ice and Earth model](gotchas/tide-gauge-gia-is-modelled.md), severity medium, status: stable
- [A tide gauge trend carries its record length and its gaps](gotchas/tide-gauge-record-length-and-gaps.md), severity medium, status: stable
- [A coastal height names its surface: ellipsoidal, orthometric and local datum heights at one site differ by metres to tens of metres](gotchas/coastal-heights-ellipsoidal-versus-orthometric.md), severity high, status: draft
- [A vertical velocity carries its reference frame: the IGS20, IGS14, ITRF2014 and plate-fixed rates of one station are different numbers](gotchas/velocity-reference-frame.md), severity medium, status: draft

The Roemmich and Gilson high gotcha's eval case,
rg-sampled-depth-floor, lives in the agent-evals repository under
`ecco/cases/`, the one home of the ocean cases, and is registered in
the evals repository's ocean-science manifest. The tide gauge gotchas
qualify the two tide gauge connector concepts (PSMSL and CO-OPS)
rather than a dataset concept; the eval cases of the two high ones,
psmsl-rlr-versus-metric and
tide-gauge-relative-sea-level-and-land-motion, are proposed for the
same directory in agent-evals pull request 16 (branch
claude/seed-tide-gauge-datums), and their registration in the evals
repository's manifest is a follow-up. The coastal heights gotcha
qualifies the PSMSL connector and the velocity reference frame gotcha
the GNSS vertical velocity connector; the eval case of the high one,
coastal-heights-ellipsoidal-versus-orthometric, is proposed for the
same directory in agent-evals (branch claude/r3-regional-sea-level),
and its registration in the evals repository's manifest is the
coordinator's follow-up.

## computations (local)

- [Ocean heat content change from gridded Argo, 0 to 700 and 0 to 2000 dbar (attested)](computations/argo-ohc.md), status: stable

The executor, the attester, the loaders and the stamped data root sit
under knowledge/references (computations/argo_ohc.py,
attesters/argo_ohc_check.py, loaders/ohc_rg_loader.py and
loaders/ohc_data_root.py, retrieval/argo-ohc-root), with the run
skill at references/skills/run-argo-ohc.md; the golden is
verification/argo_ohc.py. The ECCO-based counterpart is the provider
bundle's `knowledge/podaac/recipes/ecco-ocean-heat-content.md`.

## recipes (local)

- [Ocean heat content change from gridded Argo: the layer, the domain, the baseline and the deep term it does not carry](recipes/argo-ohc.md), status: stable
- [Regional sea level trend at a coast: the altimetry trend, the GIA model, the land motion at the gauge and the tide gauge relative trend reconciled](recipes/regional-sea-level-trend.md), status: draft

## connectors (local)

- [NOAA CO-OPS tide and water-level stations](connectors/coops-tides.md), status: stable
- [Argo profiling floats via ERDDAP](connectors/argo-floats.md), status: stable
- [PSMSL long-record tide gauges](connectors/psmsl-gauges.md), status: stable
- [GNSS vertical land motion: the Nevada Geodetic Laboratory MIDAS velocity table](connectors/gnss-vertical-velocity.md), status: draft
