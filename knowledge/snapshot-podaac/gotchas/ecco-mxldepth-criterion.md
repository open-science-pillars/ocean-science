---
type: dataset-gotcha
title: "ECCO MXLDEPTH uses the model's own MLD criterion, not yours"
description: "ECCO ships a diagnosed MXLDEPTH computed with the model's internal criterion; splicing it into a series built under a different density or temperature criterion measures the criteria, not the ocean."
tags: [ecco, mixed-layer, mxldepth, criterion, mld]
generated: { by: claude-code/opus-4.8, at: 2026-07-05T00:00:00Z }
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: mxldepth-criterion-mixing
# eval case id fixed here so a consumer's dangling-case check closes
# when the case lands, as geothermal-omission does for ecco-geothermal-flux.
sources:
  - id: mld-granule
    resource: https://doi.org/10.5067/ECL5M-OML44
    title: "ECCO Ocean Mixed Layer Depth, monthly mean llc90 (ECCO_L4_MIXED_LAYER_DEPTH_LLC0090GRID_MONTHLY_V4R4); the MXLDEPTH variable attributes, read from the 2009-12 granule on 2026-09-04"
  - id: kara-2000
    resource: https://doi.org/10.1029/2000JC900072
    title: "Kara, Rochford and Hurlburt (2000), An optimal definition for ocean mixed layer depth, Journal of Geophysical Research: Oceans 105(C7)"
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
status: stable
stale_after: 2027-03-04
---

# ECCO MXLDEPTH uses the model's own MLD criterion, not yours

**Mechanism.** ECCO v4r4 ships a diagnosed mixed layer depth field
(`MXLDEPTH`, the ECCO_L4_MIXED_LAYER_DEPTH collections) computed inside
MITgcm with the model's own criterion: the depth where the water is
first 0.8 degrees C colder than the surface, the temperature-difference
criterion of Kara et al. (2000), as the granule attributes state. The
same attributes warn that the criterion may not suit every application
and point at `DRHODR` and `RHOAnoma` for recomputing under
another.[^mld-granule][^kara-2000] That criterion is fixed by the model
configuration, not by the analyst, and it is not the density 0.03 kg/m3
or temperature 0.2 C definition an observational climatology uses (see
the criteria convention,
[mld-criteria](https://github.com/open-science-pillars/ocean-science/blob/14a4eeab071d6f7d10f04e72c4878fef87c8b8de/knowledge/conventions/mld-criteria.md)).

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

[^mld-granule]: ECCO_L4_MIXED_LAYER_DEPTH_LLC0090GRID_MONTHLY_V4R4, doi:10.5067/ECL5M-OML44, MXLDEPTH attributes of the 2009-12 granule
[^kara-2000]: Kara, Rochford and Hurlburt (2000), J. Geophys. Res. Oceans 105(C7), doi:10.1029/2000JC900072
