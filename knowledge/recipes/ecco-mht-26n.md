---
type: recipe
title: "Meridional heat transport at 26.5N from ECCO v4r4"
description: "Validated pattern for Atlantic MHT at 26.5N on the native grid, with the expected mean range and the RAPID-comparison spread."
tags: [ecco, mht, amoc, rapid, transport]
timestamp: 2026-07-04
inputs:
  - dataset: ../datasets/ecco-v4r4.md
  - collections: "ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4 (ADVx_TH, ADVy_TH) plus the geometry granule"
  - method: "ecco_v4_py.calc_meridional_heat_trsp at lat_vals 26.5 (section masks over native faces; output in PW)"
expected:
  - quantity: "multi-year mean ATLANTIC MHT at 26.5N (the RAPID-comparable section, basin_name atlExt)"
    range: [0.8, 1.4]
    units: PW
  - quantity: "single-year 2010 anchor, Atlantic (atlExt)"
    value: 0.666
    units: PW
    note: "below the multi-year band: 2010 is the documented AMOC-minimum year and single-year means carry a wider envelope; scope-verified 2026-07-04 by basin decomposition"
  - quantity: "single-year 2010 anchor, GLOBAL latitude circle (no basin mask)"
    value: 1.098
    units: PW
    note: "method-reproducibility anchor; equals the basin sum atlExt 0.666 + pacExt 0.430 + indExt 0.002 (verified 2026-07-04)"
expected_uncertainty:
  - quantity: "RAPID-comparison spread at 26.5N (Atlantic scope ONLY)"
    statement: "RAPID/MOCHA observes mean MHT near 1.3 PW with temporal standard deviation about 0.4 PW (Johns et al. 2011, 2004-2007 period: 1.33 +/- 0.40 PW); ECCO v4 Atlantic means sit low of the observed mean, so model-minus-RAPID offsets are expected, not anomalous. RAPID comparisons use the atlExt-masked value; comparing the global-circle number against RAPID is a scope error. Monthly values swing hard: global-circle 2010 spans -0.31 to +1.92 PW; Atlantic 2010 spans +0.09 to +1.14 PW."
  - quantity: "comparison discipline"
    statement: "compare like periods (RAPID begins April 2004; ECCO ends 2017) and state the averaging window; a single-year mean carries a wider envelope than the multi-year range above."
evidence:
  - https://rapid.ac.uk/rapidmoc/
  - https://doi.org/10.1175/2010JCLI3997.1
  - https://github.com/open-science-pillars/ocean-science/blob/main/skills/ecco/references/variable-catalog.md
status: verified
verified: 2026-07-04
verified_by: OSP steward review
---

# Meridional heat transport at 26.5N from ECCO v4r4

The validated pattern: load the monthly 3D temperature-flux collection
and the geometry granule, merge, and compute the section heat transport
at 26.5N with ecco_v4_py's section machinery (masks over native faces;
the flux diagnostics include bolus and sub-monthly covariance by
construction, per the meridional-transport skill's framing). Output
units PW.

**SCOPE, load-bearing (corrected 2026-07-04):**
`calc_meridional_heat_trsp(ds, lat_vals=26.5)` with no `basin_name`
computes the FULL latitude circle (Atlantic plus Pacific plus Indian).
The RAPID-comparable Atlantic section requires
`basin_name="atlExt"`, and the basin masks require ecco_v4_py's binary
data files to be present in the environment. The original Session 7
anchor (1.098 PW) was the global circle; the scope was identified by a
skill-following test agent 2026-07-04 and verified by basin
decomposition (the three basins sum to the no-mask value exactly).

**Reproducing runs (validation provenance).** 2026-07-04, ECCO v4r4
2010 monthly granules, live PO.DAAC: global-circle monthly series
[-0.313, -0.115, 1.031, 1.303, 1.234, 1.629, 1.922, 1.897, 1.670,
1.500, 1.211, 0.206] PW, mean 1.098; Atlantic (atlExt) monthly range
+0.09 to +1.14 PW, mean 0.666; Pacific 0.430; Indian 0.002. The
anomalously low Atlantic winter months are consistent with the
documented 2009/2010 AMOC minimum. The durable executable home is the
Session 9 golden notebook `verification/transport_analysis.py`, which
asserts both anchors and the basin-sum identity.

**Range provenance.** The 0.8 to 1.4 PW multi-year band is the build
specification's pinned expectation (IMPLEMENTATION-GUIDE v2.3.3,
bracketing published ECCO v4 means near 1.0 to 1.1 PW and
the RAPID-observed mean near 1.3 PW (evidence links above).
