---
type: dataset-gotcha
spheres: [hydrosphere, geosphere]
title: "The GIA correction at a tide gauge is a model prediction that names its ice and Earth model"
description: "Glacial isostatic adjustment at a tide gauge is not measured but predicted by a model of the ice history and the Earth's viscosity structure. The set PSMSL distributes is Peltier's ICE-5G version 1.3 with the VM2 Earth model and a 90 km lithosphere, supplied in 2012, as separate relative sea level and crustal uplift rates at each PSMSL station; ICE-5G (VM4) and the models of Mitrovica, Lambeck, Sabadini and Wahr give other values. A GIA-corrected gauge trend that does not name the model and which of the two rates was applied cannot be reproduced, and the three rate variants in the files are, in the supplier's words, not an error bar."
tags: [tide-gauge, gia, glacial-isostatic-adjustment, ice-5g, vm2, peltier, psmsl, sea-level, trend, correction]
generated: { by: knowledge-seeder/claude, at: 2026-09-14T05:30:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-14T12:13:17Z, role: maintainer, source: https://github.com/open-science-pillars/ocean-science/pull/51 }
severity: medium
dataset: ../connectors/psmsl-gauges.md
status: stable
stale_after: 2027-03-14
sources:
  - id: psmsl-gia
    resource: https://psmsl.org/train_and_info/geo_signals/gia/
    title: "PSMSL, glacial isostatic adjustment (read 2026-09-14): GIA as one of the most modelled geophysical signals in tide gauge data, the crustal and sea surface parts of the signal, the partial removal by a crustal correction alone, and the models available from Peltier (ICE-5G VM2 and VM4), Mitrovica, Lambeck, Sabadini and Wahr"
  - id: psmsl-peltier
    resource: https://psmsl.org/train_and_info/geo_signals/gia/peltier/
    title: "PSMSL, Peltier GIA data sets (read 2026-09-14): files supplied by Drummond and Peltier on 13 August 2012 from ICE-5G version 1.3 with VM2 and a 90 km lithosphere, one table of relative sea level rates and one of crustal uplift rates at the PSMSL stations plus one degree grids, three rate variants per station of which the centred one is recommended and the spread is stated not to be an error bar, spherical harmonics to degree 256"
  - id: peltier-2004
    resource: https://doi.org/10.1146/annurev.earth.32.082503.144359
    title: "Peltier, W. R., 2004, Global glacial isostasy and the surface of the ice-age Earth, the ICE-5G (VM2) model and GRACE, Annual Review of Earth and Planetary Sciences 32, 111 to 149 (Crossref record and abstract read 2026-09-14; the publisher's page was not fetched, the proxy having refused the redirect)"
  - id: vlm-gotcha
    resource: tide-gauge-relative-sea-level-and-land-motion.md
    title: "This bundle's companion gotcha on relative sea level and the observed land motion"
  - id: connector
    resource: ../connectors/psmsl-gauges.md
    title: "This bundle's PSMSL connector concept, whose RLR series the correction is applied to"
---

# The GIA correction at a tide gauge is a model prediction that names its ice and Earth model

**Mechanism.** GIA is, in PSMSL's words, one of the most modelled of the
geophysical signals present in tide gauge data: near the former ice
loads the crust still rises and relative sea level falls, around them
the forebulge collapses and relative sea level rises, and GIA also
changes the sea surface, so a correction of crustal motion alone, a
GPS uplift rate for example, removes only part of it.[^psmsl-gia] The
models are named by their ice history and their Earth model: Peltier's
ICE-5G (VM2) and ICE-5G (VM4) predictions are available, and
Mitrovica, Lambeck, Sabadini and Wahr have models of their
own.[^psmsl-gia] ICE-5G (VM2) is described in Peltier 2004, whose
abstract presents it as a refined global model of glacial isostatic
adjustment built from geological and geophysical observations of the
Earth's shape, gravity field and sea level history, with the GRACE
gravity mission named as its test.[^peltier-2004] The files PSMSL
distributes, supplied by Drummond and Peltier on 13 August 2012, use
ICE-5G version 1.3 with the VM2 Earth model and a 90 km lithosphere,
computed with spherical harmonics to degree 256, and come as two
tables at the PSMSL station locations, one of the rate of relative sea
level change (the tide gauge quantity) and one of crustal uplift (the
GNSS quantity), with the same fields on a one degree grid; each
station carries three rates, from the model's past 250 years, its
coming 250 years and the average centred on now, and the supplier
recommends the third and states that the spread of the other two is
definitely not an error bar.[^psmsl-peltier] The correction is applied
to the RLR series the connector serves.[^connector]

**Wrong-result mode.** A gauge trend corrected for GIA with no model
named is a number that another model changes, by most near and around
the former ice sheets; a crustal uplift rate applied where the
relative sea level rate was needed, or a GNSS uplift used as the whole
GIA effect, leaves the sea surface part of GIA in the
record.[^psmsl-gia][^psmsl-peltier] A GIA correction quoted with no
uncertainty is a model value treated as an observation, and the
three-rate spread in the files is not one.[^psmsl-peltier] The
observed land motion at the gauge is a separate matter and has its own
gotcha.[^vlm-gotcha]

**Correct approach.** A GIA-corrected trend names the model with its ice
history, Earth model, lithosphere thickness and version (ICE-5G v1.3,
VM2, 90 km, 2012, for the PSMSL set), which of the two predicted rates
was applied (relative sea level for a gauge, crustal uplift for a GNSS
rate) and where the value came from, and the uncorrected relative
trend stands beside it so that a reader with another model can
substitute it.[^psmsl-peltier][^psmsl-gia]

**Verification.** PSMSL's GIA page and its Peltier GIA data sets page
were read on 2026-09-14; the model files were not
downloaded.[^psmsl-gia][^psmsl-peltier] Peltier 2004 is cited through
its Crossref record (W. R. Peltier, Annual Review of Earth and
Planetary Sciences, volume 32, pages 111 to 149, 2004) and the
abstract carried there, read the same day; the publisher's page was
not fetched because the drafting environment's proxy refused the
redirect.[^peltier-2004]

[^psmsl-gia]: PSMSL, glacial isostatic adjustment page, read 2026-09-14
[^psmsl-peltier]: PSMSL, Peltier GIA data sets page, read 2026-09-14
[^peltier-2004]: Peltier, 2004, Annual Review of Earth and Planetary Sciences, doi:10.1146/annurev.earth.32.082503.144359, Crossref record and abstract read 2026-09-14
[^vlm-gotcha]: This bundle's gotcha on relative sea level and land motion
[^connector]: This bundle's PSMSL connector concept
