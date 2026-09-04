---
type: validity-domain
title: "MUR L4 SST supports basin-scale mean-state claims outside the high Arctic"
description: "Supporting domain: mean-state claims on MUR v4.1 at basin scale, 2002 onward, below 66N; the honest basis is near-zero residuals against ingested in situ data and ensemble-level agreement, not independent validation."
tags: [validity-domain, mur, sst, mean-state, supporting]
status: draft
generated: { by: claude-code/fable-5, at: 2026-08-31T03:54:16Z }
stale_after: 2026-11-30
domain:
  products: ["MUR-JPL-L4-GLOB-v4.1"]
  claim_classes: [mean-state]
  polarity: supporting
  region: { bbox: [-90, 66, -180, 180] }
  period: { start: "2002-06", end: "2026-08" }
sources:
  - id: chin-2017
    resource: https://doi.org/10.1016/j.rse.2017.07.029
    title: "Chin, Vazquez-Cuervo, and Armstrong 2017 (RSE 200, 154-169): residual statistics and the feature-resolution caveat, quoted verbatim below; verified against a third-party copy of the typeset article, stated plainly"
  - id: podaac-landing
    resource: https://podaac.jpl.nasa.gov/dataset/MUR-JPL-L4-GLOB-v4.1
    title: "PO.DAAC landing page: coverage from 2002-05-31, global 0.01 degree grid, per-pixel estimated error standard deviation variable"
  - id: dataset-concept
    resource: ../datasets/ghrsst-mur.md
    title: "The signed dataset concept for GHRSST MUR"
---

# MUR L4 SST supports basin-scale mean-state claims outside the high Arctic

Mean-state claims on MUR v4.1 at basin scale and larger are supported
from June 2002, below 66N. The basis, stated honestly: the product's
residuals against the in situ data it ingests are near zero at global
scale ("In-situ iQuam -0.003 +/- 0.020" degrees C bias, RMS 0.489,
2002 through 2013), and "The MUR SST values agree with the GHRSST
Multi-Product Ensemble (GMPE) SST field to 0.36°C on average, except
in summer-time Arctic region where the existing SST analysis products
are known to disagree with each other".[^chin-2017] Neither figure is
independent validation (the in situ data are ingested by the analysis;
GMPE is an ensemble of peer analyses), which is why this domain claims
mean-state only and carries its region bound: the summer Arctic
disagreement among analyses is excluded structurally by the 66N cap
rather than flagged in prose. Coverage from 2002-05-31 and the
per-pixel estimated error variable are producer-stated.[^podaac-landing]

**Feature-scale caveat, worded to the paper.** Analyzed "SST feature
resolution is often much lower than the grid resolution" due to
procedures that effectively impose smoothing, and interpolated regions
deserve caution;[^chin-2017] gradient-class claims are deliberately
outside this domain, and the 0.01 degree grid never implies 0.01
degree features. The period end tracks the most recent verification
sweep, and stale_after does the cadence for this ongoing product.

[^chin-2017]: Chin et al. 2017, abstract, Table 3, and section 4.3, quoted 2026-08-30; DOI paywalled to automated fetch, content verified against a third-party posting of the typeset publisher PDF (identity confirmed by running header), cited by DOI
[^podaac-landing]: PO.DAAC MUR v4.1 landing page, fetched 2026-08-30
[^dataset-concept]: datasets/ghrsst-mur.md, steward-verified
