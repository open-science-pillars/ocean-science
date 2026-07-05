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
- swot-karin.md, PLACEHOLDER, authored Session 8b
- grace-fo-mascons.md, PLACEHOLDER, authored Session 8b
- ghrsst-mur.md, PLACEHOLDER, authored Session 8b

## gotchas

- [ECCO budgets and transports close only on the native llc90 grid](gotchas/ecco-native-vs-regridded.md), severity high, status: verified
- [ECCO heat budgets need the geothermal flux, which is not a PO.DAAC collection](gotchas/ecco-geothermal-flux.md), severity high, status: verified
- swot-calval-orbit-phases.md, PLACEHOLDER, authored Session 8b
- grace-coastal-leakage.md, PLACEHOLDER, authored Session 8b
- grace-gia-correction.md, PLACEHOLDER, authored Session 8b

## recipes

- ecco-heat-budget.md, PLACEHOLDER, authored Session 7
- ecco-mht-26n.md, PLACEHOLDER, authored Session 7
