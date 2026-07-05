# podaac-arc bundle

The PO.DAAC arc knowledge bundle: ECCO, SWOT, GRACE-FO, GHRSST MUR.
OKF v0.1 conformant per SPECIFICATION.md v0.5.1 §5. Snapshot
source-metadata fields are placeholders until the Session 17
canonical-home handoff (SPEC §5.7):

- Snapshot source repository: (pending; this bundle is currently the original)
- Snapshot source commit: (n/a until Session 17)
- Snapshot date: (n/a until Session 17)

## datasets

- [ECCO v4 Release 4 ocean state estimate](datasets/ecco-v4r4.md), status: verified
- [SWOT KaRIn Level 2 Low Rate SSH](datasets/swot-karin.md), status: verified
- [GRACE/GRACE-FO JPL mascon solutions](datasets/grace-fo-mascons.md), status: verified
- [GHRSST MUR Level 4 SST](datasets/ghrsst-mur.md), status: verified
- [RAPID-MOCHA transports at 26.5N (observational reference)](datasets/rapid-mocha.md), status: verified (live-ingested Session 10)

## gotchas

- [ECCO budgets and transports close only on the native llc90 grid](gotchas/ecco-native-vs-regridded.md), severity high, status: verified
- [ECCO heat budgets need the geothermal flux, which is not a PO.DAAC collection](gotchas/ecco-geothermal-flux.md), severity high, status: verified
- [SWOT orbit phases: cal/val and science data are not one record](gotchas/swot-calval-orbit-phases.md), severity high, status: verified
- [GRACE mascon coastal leakage: land signal bleeds into ocean mascons](gotchas/grace-coastal-leakage.md), severity high, status: verified
- [GRACE GIA correction: a model choice already baked into the product](gotchas/grace-gia-correction.md), severity medium, status: verified

## recipes

- [Closed heat budget on the ECCO v4r4 native grid](recipes/ecco-heat-budget.md), status: verified
- [Meridional heat transport at 26.5N from ECCO v4r4](recipes/ecco-mht-26n.md), status: verified
