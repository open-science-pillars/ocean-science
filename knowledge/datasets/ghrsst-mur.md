---
type: dataset
title: GHRSST MUR Level 4 SST
description: "Gap-free daily 0.01-degree foundation SST analysis (v4.1, with a 0.25-degree companion); the analysis_error field is the product's own uncertainty estimate."
tags: [ghrsst, mur, sst, level4, podaac]
timestamp: 2026-07-04
resource: https://podaac.jpl.nasa.gov/dataset/MUR-JPL-L4-GLOB-v4.1
version: "MUR v4.1 (MUR-JPL-L4-GLOB-v4.1) and MUR25 v04.2 (MUR25-JPL-L4-GLOB-v04.2), both CMR-verified 2026-07-04"
status: verified
verified: 2026-07-04
verified_by: Paul Ramirez (steward pro tem)
---

# GHRSST MUR Level 4 SST

**Identity.** The Multi-scale Ultra-high Resolution analysis: a
gap-free daily global foundation SST field at 0.01-degree nominal
posting, blending microwave, infrared, and in-situ observations
(2002-06 to present), with a 0.25-degree companion product (MUR25).
Level 4 means ANALYSIS: every pixel has a value because interpolation
filled it, not because something measured it there.

**Structure.** Daily `analysed_sst` (foundation temperature: free of
diurnal warming by construction, so it is not a skin or buoy-depth
temperature), `analysis_error`, a land/ice `mask`, and `sea_ice_fraction`.
Foundation SST compares against pre-dawn or depth-consistent
references, not against skin SST products, without a stated
adjustment (the core data-formats and QC rules on product-type mixing
apply).

## Uncertainty

- **`analysis_error` is the product's own uncertainty estimate** (a
  1-sigma standard deviation of the analyzed SST); it is the native
  uncertainty field that accompanies any MUR-derived result (reporting
  it alongside results is workflow behavior owned by the core
  uncertainty-quantification rules, not by this concept).
- It is an ANALYSIS error: largest where observations were sparse
  (persistent cloud, high latitudes, ice edge) and it does not
  capture systematic retrieval biases or the smoothing itself.
- The 0.01-degree grid oversells effective resolution: feature scales
  under clouds are interpolation, not observation; `analysis_error`
  rises there, which is exactly when to read it. Averaging
  `analysis_error` down by sqrt(N) over a region ignores its spatial
  correlation; regional means keep the error near the regional mean
  of the field, not far below it.

## Known issues

- Product-type mixing (foundation vs skin) is the standing trap for
  MUR comparisons; no dedicated gotcha concept yet (the caveat lives
  here and in the QC rules), a candidate for the bundle's next
  revision.
