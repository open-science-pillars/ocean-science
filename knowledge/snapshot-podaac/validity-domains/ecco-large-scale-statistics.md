---
type: validity-domain
title: "ECCO v4r4 native monthly fields support large-scale statistics over 1992-2017"
description: "Supporting domain: mean state, trend, and variability claims on the native llc90 monthly fields, global ocean, within the estimation period; the verified basis is dynamical consistency and fit to the modern observation system at the large scales V4 aims to resolve."
tags: [validity-domain, ecco, statistics, supporting]
status: draft
generated: { by: claude-code/fable-5, at: 2026-08-31T03:54:16Z }
stale_after: 2027-02-28
domain:
  products: ["ECCO_L4_*_LLC0090GRID_MONTHLY_*"]
  claim_classes: [statistics]
  polarity: supporting
  region: global
  period: { start: "1992-01", end: "2017-12" }
  releases: [V4R4]
sources:
  - id: forget-2015
    resource: https://gmd.copernicus.org/articles/8/3071/2015/
    title: "Forget et al. 2015, ECCO version 4 (GMD 8, 3071-3104): dynamical consistency and fit, quoted verbatim below"
  - id: v4r4-synopsis
    resource: https://doi.org/10.5281/zenodo.4533349
    title: "ECCO Consortium, Fukumori et al. 2021, V4r4 Synopsis: the 1992-2017 period and the large-scale aim, quoted verbatim below"
  - id: dataset-concept
    resource: ../datasets/ecco-v4r4.md
    title: "The signed dataset concept: state estimate, not observations; no formal error fields"
---

# ECCO v4r4 native monthly fields support large-scale statistics over 1992-2017

Mean state, trend, and variability claims (the statistics umbrella) on
the native llc90 monthly fields are supported within 1992-2017. The
verified basis, quoted exactly: the baseline solution is "a dynamically
consistent ocean state estimate without unidentified sources of heat
and buoyancy" that "fits altimetry (Forget and Ponte, 2015), SST
(Buckley et al., 2014), and subsurface hydrography data (Sect. 5.2) at
or close to the specified noise level",[^forget-2015] Release 4
"further extends the analysis period to 1992-2017", and Version 4
"aims to resolve large-scale low-frequency variations of the
ocean".[^v4r4-synopsis] The estimate is a synthesis, not observations,
and ships no formal error fields; statistics cited from it carry that
framing.[^dataset-concept]

**Known limits (read before signing).** The attester's schema carries
no spatial-scale axis, so as encoded this domain would answer IN for a
statistics declaration on an arbitrarily small box. The verified basis
covers large-scale statistics: the producers state the large-scale aim
explicitly, and the nominal 1 degree class resolution does not resolve
eddies or shelf processes (an inference from the resolution class, not
a quoted producer sentence). Refinement under dispute narrows this
domain; the coarse-first alternative is to sign it with this stated
limit and let the first disputed small-box claim drive the refinement.

[^forget-2015]: Forget et al. 2015, abstract and section 5, fetched and quoted 2026-08-30
[^v4r4-synopsis]: V4r4 Synopsis, summary and section 4.1, fetched and quoted 2026-08-30
[^dataset-concept]: datasets/ecco-v4r4.md, steward-verified
