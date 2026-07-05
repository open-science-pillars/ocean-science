---
type: dataset-gotcha
title: "GRACE GIA correction: a model choice already baked into the product"
description: "A specific glacial isostatic adjustment model is pre-applied to mascon products; comparisons across products or literature with different GIA choices shift trends."
tags: [grace, gia, trends, corrections]
timestamp: 2026-07-04
severity: medium
# medium, not high: the correction is documented product behavior and
# bites through comparison inconsistency rather than silently wrong
# single-product statistics; no Phase-1 eval case is specified for it.
dataset: ../datasets/grace-fo-mascons.md
evidence:
  - https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4
  - https://grace.jpl.nasa.gov/
status: verified
verified: 2026-07-04
verified_by: Paul Ramirez (steward pro tem)
---

# GRACE GIA correction: a model choice already baked into the product

**Mechanism.** GRACE senses total mass change, including the solid
Earth's ongoing response to the last deglaciation (GIA). The standard
mascon product arrives with a specific GIA model already subtracted
(the product documentation names the model and version). GIA is a
model, not a measurement: alternatives differ regionally, most
strongly near formerly glaciated regions (Hudson Bay, Fennoscandia,
Antarctica) and in ocean-mass trends.

**Wrong-result mode.** Two forms: (1) comparing mass trends across
products or against literature values computed under a different GIA
model attributes the GIA-model difference to the ocean or ice sheet;
(2) applying a GIA correction again on top of the pre-corrected
product double-corrects the trend. Both bite trends specifically;
monthly anomaly variability is largely immune.

**Correct approach.** Any trend statement from mascon data names the
GIA model the product applied (read it from the product metadata and
documentation at analysis time); cross-product comparisons align GIA
treatments or quote the GIA-model spread as a systematic term beside
the formal errors; nothing gets re-corrected without confirming what
was applied.

**Verification.** The product landing page and its documentation
record the applied GIA model (link above; verified live 2026-07-04);
the double-correction failure mode follows from the product being
pre-corrected.
