# podaac-arc bundle (PINNED SNAPSHOT per SPEC v0.6 §5.7)

- Canonical home: github.com/open-science-pillars/nasa-daac-knowledge (podaac/)
- Snapshot source commit: 41d5ffadd1aa
- Snapshot date: 2026-08-30
- Precedence: the canonical concept wins on conflict; this snapshot
  refreshes at plugin releases (tools/sync_check.py in the canonical
  repo verifies byte-identity; run green 2026-08-30, 22 files).
- Eval coverage for high gotchas ships HERE (evals/), per the rule-9
  ruling of 2026-07-05.

The PO.DAAC arc knowledge bundle: ECCO, SWOT, GRACE-FO, GHRSST MUR.
OKF v0.2 conformant in the snapshotted concepts (the canonical root
index declares okf_version "0.2"; the exact spec text is vendored in
marketplace docs/upstream). The plugin-local concepts noted below are
still v0.1-form, pending their own migration.

## datasets

- [ECCO v4 Release 4 ocean state estimate](datasets/ecco-v4r4.md), status: stable
- [SWOT KaRIn Level 2 Low Rate SSH](datasets/swot-karin.md), status: stable
- [GRACE/GRACE-FO JPL mascon solutions](datasets/grace-fo-mascons.md), status: stable
- [GHRSST MUR Level 4 SST](datasets/ghrsst-mur.md), status: stable
- [RAPID-MOCHA transports at 26.5N (observational reference)](datasets/rapid-mocha.md), status: stable (live-ingested)

## gotchas

- [ECCO budgets and transports close only on the native llc90 grid](gotchas/ecco-native-vs-regridded.md), severity high, status: stable
- [ECCO heat budgets need the geothermal flux, which is not a PO.DAAC collection](gotchas/ecco-geothermal-flux.md), severity high, status: stable
- [SWOT orbit phases: cal/val and science data are not one record](gotchas/swot-calval-orbit-phases.md), severity high, status: stable
- [GRACE mascon coastal leakage: land signal bleeds into ocean mascons](gotchas/grace-coastal-leakage.md), severity high, status: stable
- [GRACE GIA correction: a model choice already baked into the product](gotchas/grace-gia-correction.md), severity medium, status: stable
- [ECCO V4R4 vs V4R4B: mixing releases conflates corrections with signal](gotchas/ecco-release-mixing.md), severity high, status: stable
- [ECCO meridional heat transport: no basin mask means the full latitude circle](gotchas/ecco-mht-basin-scope.md), severity high, status: stable
- [SWOT KaRIn ssha_karin: crossover calibration arrives UNAPPLIED](gotchas/swot-crossover-unapplied.md), severity high, status: stable
- [ECCO SSH inverse-barometer variants: pick the convention and never mix them](gotchas/ecco-ssh-ib-variants.md), severity medium, status: stable (local, v0.1-form)
- [ECCO Boussinesq global-mean steric correction](gotchas/ecco-boussinesq-global-steric.md), severity medium, status: stable (local, v0.1-form)
- [ECCO MXLDEPTH uses the model's own MLD criterion](gotchas/ecco-mxldepth-criterion.md), severity medium, status: stable (local, v0.1-form)
- [ECCO native-grid density and equation of state](gotchas/ecco-native-density-eos.md), severity medium, status: stable (local, v0.1-form)

## conventions

- [Mixed layer depth criteria](conventions/mld-criteria.md), status: stable (local, v0.1-form)
- [Sea level budget closure](conventions/sea-level-budget-closure.md), status: stable (local, v0.1-form)
- [ENSO SST indices (Nino regions, ONI)](conventions/enso-sst-indices.md), status: stable (local, v0.1-form)
- [NAO index](conventions/nao-index.md), status: stable (local, v0.1-form)
- [PDO index](conventions/pdo-index.md), status: stable (local, v0.1-form)
- [AMO index](conventions/amo-index.md), status: stable (local, v0.1-form)

## recipes

- [Closed heat budget on the ECCO v4r4 native grid](recipes/ecco-heat-budget.md), status: stable
- [Meridional heat transport at 26.5N from ECCO v4r4](recipes/ecco-mht-26n.md), status: stable
- [Closed salt budget on the ECCO v4r4 native grid](recipes/ecco-salt-budget.md), status: stable
- [Closed volume budget on the ECCO v4r4 native grid](recipes/ecco-volume-budget.md), status: stable

## fields (ECCO V4r4 fields layer, snapshotted)

One Data Collection concept per V4r4 collection family; see
[fields/ecco-v4r4/index.md](fields/ecco-v4r4/index.md) for the family
listing (ten demo-critical families stable as of 2026-08-30; the
remaining sixteen arrive via the community lane).

## computations (OKF v0.2 section 10, snapshotted)

- [Heat budget closure on the ECCO v4r4 native grid (attested)](computations/ecco-heat-budget.md), status: stable
- [Salt budget closure on the ECCO v4r4 native grid (attested, draft)](computations/ecco-salt-budget.md), status: draft
- [Volume budget closure on the ECCO v4r4 native grid (attested, draft)](computations/ecco-volume-budget.md), status: draft
- [Meridional heat transport at 26.5N from ECCO v4r4 (attested, draft)](computations/ecco-mht-26n.md), status: draft

## connectors

- [NOAA CO-OPS tide and water-level stations](connectors/coops-tides.md), status: stable
- [Argo profiling floats via ERDDAP](connectors/argo-floats.md), status: stable
- [PSMSL long-record tide gauges](connectors/psmsl-gauges.md), status: stable
