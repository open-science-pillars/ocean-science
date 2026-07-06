# podaac-arc bundle (PINNED SNAPSHOT per SPEC v0.6 §5.7)

- Canonical home: github.com/open-science-pillars/nasa-daac-knowledge (podaac/)
- Snapshot source commit: a0c84fff959f
- Snapshot date: 2026-07-05
- Precedence: the canonical concept wins on conflict; this snapshot
  refreshes at plugin releases (tools/sync_check.py in the canonical
  repo verifies byte-identity; run green 2026-07-05).
- Eval coverage for high gotchas ships HERE (evals/), per the rule-9
  ruling of 2026-07-05.

The PO.DAAC arc knowledge bundle: ECCO, SWOT, GRACE-FO, GHRSST MUR.
OKF v0.1 conformant per SPEC §5.

## datasets

- [ECCO v4 Release 4 ocean state estimate](datasets/ecco-v4r4.md), status: verified
- [SWOT KaRIn Level 2 Low Rate SSH](datasets/swot-karin.md), status: verified
- [GRACE/GRACE-FO JPL mascon solutions](datasets/grace-fo-mascons.md), status: verified
- [GHRSST MUR Level 4 SST](datasets/ghrsst-mur.md), status: verified
- [RAPID-MOCHA transports at 26.5N (observational reference)](datasets/rapid-mocha.md), status: verified (live-ingested)

## gotchas

- [ECCO budgets and transports close only on the native llc90 grid](gotchas/ecco-native-vs-regridded.md), severity high, status: verified
- [ECCO heat budgets need the geothermal flux, which is not a PO.DAAC collection](gotchas/ecco-geothermal-flux.md), severity high, status: verified
- [SWOT orbit phases: cal/val and science data are not one record](gotchas/swot-calval-orbit-phases.md), severity high, status: verified
- [GRACE mascon coastal leakage: land signal bleeds into ocean mascons](gotchas/grace-coastal-leakage.md), severity high, status: verified
- [GRACE GIA correction: a model choice already baked into the product](gotchas/grace-gia-correction.md), severity medium, status: verified
- [ECCO V4R4 vs V4R4B: mixing releases conflates corrections with signal](gotchas/ecco-release-mixing.md), severity high, status: verified
- [ECCO meridional heat transport: no basin mask means the full latitude circle](gotchas/ecco-mht-basin-scope.md), severity high, status: verified
- [SWOT KaRIn ssha_karin: crossover calibration arrives UNAPPLIED](gotchas/swot-crossover-unapplied.md), severity high, status: verified
- [ECCO SSH inverse-barometer variants: pick the convention and never mix them](gotchas/ecco-ssh-ib-variants.md), severity medium, status: verified
- [ECCO Boussinesq global-mean steric correction](gotchas/ecco-boussinesq-global-steric.md), severity medium, status: verified
- [ECCO MXLDEPTH uses the model's own MLD criterion](gotchas/ecco-mxldepth-criterion.md), severity medium, status: verified
- [ECCO native-grid density and equation of state](gotchas/ecco-native-density-eos.md), severity medium, status: verified

## conventions

- [Mixed layer depth criteria](conventions/mld-criteria.md), status: verified
- [Sea level budget closure](conventions/sea-level-budget-closure.md), status: verified
- [ENSO SST indices (Nino regions, ONI)](conventions/enso-sst-indices.md), status: verified
- [NAO index](conventions/nao-index.md), status: verified
- [PDO index](conventions/pdo-index.md), status: verified
- [AMO index](conventions/amo-index.md), status: verified

## recipes

- [Closed heat budget on the ECCO v4r4 native grid](recipes/ecco-heat-budget.md), status: verified
- [Meridional heat transport at 26.5N from ECCO v4r4](recipes/ecco-mht-26n.md), status: verified
- [Closed salt budget on the ECCO v4r4 native grid](recipes/ecco-salt-budget.md), status: verified
- [Closed volume budget on the ECCO v4r4 native grid](recipes/ecco-volume-budget.md), status: verified
