---
type: dataset-gotcha
title: "ECCO MXLDEPTH uses the model's own MLD criterion, not yours"
description: "ECCO ships a diagnosed MXLDEPTH computed with the model's internal criterion; splicing it into a series built under a different density or temperature criterion measures the criteria, not the ocean."
tags: [ecco, mixed-layer, mxldepth, criterion, mld]
timestamp: 2026-07-05
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: mxldepth-criterion-mixing
# eval case id fixed here per CLAUDE.md rule 9; the matching case lands
# in the ocean-science plugin's evals/ at steward promotion, exactly as
# the geothermal-omission placeholder does for ecco-geothermal-flux.
status: verified
verified: 2026-07-06
verified_by: OSP steward review
evidence:
  - "internal: skills/mixed-layer/SKILL.md and skills/ecco/references/variable-catalog.md (the MXLDEPTH row); the authorities the mixed-layer-analysis workflow cited"
  - https://github.com/open-science-pillars/ocean-science/blob/main/skills/ecco/references/variable-catalog.md
---

# ECCO MXLDEPTH uses the model's own MLD criterion, not yours

**Mechanism.** ECCO v4r4 ships a diagnosed mixed layer depth field
(MXLDEPTH in the variable catalog) computed inside MITgcm with the
model's own internal criterion. That criterion is fixed by the model
configuration, not by the analyst, and it is generally not the density
0.03 kg/m3 or temperature 0.2 C definition an observational climatology
uses (see the criteria convention,
[mld-criteria](../conventions/mld-criteria.md)).

**Wrong-result mode.** Splicing MXLDEPTH into a series, comparison, or
trend that was built under a different criterion measures the difference
between the criteria as much as any difference in the ocean. A
"deepening" or a model-vs-observation gap produced this way can be an
artifact of the definition, not a physical signal.

**Correct approach.** Either (a) accept MXLDEPTH and state its criterion
explicitly, comparing only against other MLDs computed the same way, or
(b) recompute MLD from the TEMP_SALINITY collection under the criterion
you have pinned, and use that everywhere in the series. Never mix
MXLDEPTH with a differently-defined MLD in one record.
