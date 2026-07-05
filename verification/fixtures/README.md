# Fixture provenance (ocean-science)

Required by SPECIFICATION.md v0.5.1 §6. Two fixture kinds serve the four
golden notebooks:

| Fixture | Kind | Source | License |
|---|---|---|---|
| synthetic SWOT swath (in-notebook) | synthesized deterministically inside load_swot.py (seed 20260704), structure mirrored from a live Basic-tier granule inspected 2026-07-04 | this repo | public domain (synthetic) |
| 2010 ECCO subset (~1.3 GB, cached at ~/ECCO_V4r4) | scripted, cached real data per §6: fetched on demand by `fixtures/fetch_ecco_2010.py` (Earthdata login required on first fetch); never committed | PO.DAAC, ECCO v4r4 collections listed in fetch_ecco_2010.py; geothermalFlux.bin from the ECCO-v4-Python-Tutorial misc directory | NASA data, public; tutorial file per its repo license |

Reference numbers the goldens assert (recorded 2026-07-04):
- transport_analysis: MHT 26.5N 2010 mean 1.098 PW (recipe anchor),
  monthly span -0.31 to +1.92 PW.
- ocean_budget: absolute pointwise residual on tile-1 interior wet cells,
  max 5.0e-11 degC/s, p99.9 7.4e-12, median 8.7e-14 (3,341,772
  cell-months); tolerance 1e-10 / 1e-11 per the re-grounded recipe.
- load_ecco: wet surface footprint 60646 cells; native-weighted 2010
  SST 18.425 degC.
