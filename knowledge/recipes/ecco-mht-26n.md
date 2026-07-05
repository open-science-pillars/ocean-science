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
  - quantity: "multi-year mean MHT at 26.5N"
    range: [0.8, 1.4]
    units: PW
  - quantity: "single-year annual mean (reproducing anchor, 2010)"
    value: 1.098
    units: PW
expected_uncertainty:
  - quantity: "RAPID-comparison spread at 26.5N"
    statement: "RAPID/MOCHA observes mean MHT near 1.3 PW with temporal standard deviation about 0.4 PW (Johns et al. 2011, 2004-2007 period: 1.33 +/- 0.40 PW); ECCO v4 means sit near the low side of the observed mean, so model-minus-RAPID offsets of 0.1 to 0.3 PW are expected, not anomalous. Monthly values swing hard: the 2010 reproducing run spans -0.31 to +1.92 PW within one year (2010 is a documented AMOC-minimum year)."
  - quantity: "comparison discipline"
    statement: "compare like periods (RAPID begins April 2004; ECCO ends 2017) and state the averaging window; a single-year mean carries a wider envelope than the multi-year range above."
evidence:
  - https://rapid.ac.uk/rapidmoc/
  - https://doi.org/10.1175/2010JCLI3997.1
  - ../../skills/ecco/references/variable-catalog.md
status: verified
verified: 2026-07-04
verified_by: Paul Ramirez (steward pro tem)
---

# Meridional heat transport at 26.5N from ECCO v4r4

The validated pattern: load the monthly 3D temperature-flux collection
and the geometry granule, merge, and compute the section heat transport
at 26.5N with ecco_v4_py's section machinery (masks over native faces;
the advective flux diagnostics include bolus and sub-monthly covariance
by construction, per the meridional-transport skill's framing). Output
units PW.

**Reproducing run (validation provenance).** 2026-07-04, ECCO v4r4
2010 monthly granules (12 files, live PO.DAAC): monthly MHT at 26.5N of
[-0.313, -0.115, 1.031, 1.303, 1.234, 1.629, 1.922, 1.897, 1.670,
1.500, 1.211, 0.206] PW; 2010 mean 1.098 PW, inside the expected
multi-year range. The negative winter months are consistent with the
documented 2009/2010 AMOC minimum, which is itself a soft validation
that the section machinery captures real variability. The durable
executable home for this run is the Session 9 golden notebook
`verification/transport_analysis.py`, which asserts against this
recipe's ranges.

**Range provenance.** The 0.8 to 1.4 PW multi-year band is the build
specification's pinned expectation (IMPLEMENTATION-GUIDE v2.3.3,
Session 7) bracketing published ECCO v4 means near 1.0 to 1.1 PW and
the RAPID-observed mean near 1.3 PW (evidence links above).
