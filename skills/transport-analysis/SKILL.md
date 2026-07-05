---
name: transport-analysis
description: "Meridional transport analysis: MHT at chosen latitudes, overturning streamfunction, expected range and spread from the recipe concept."
---

# transport-analysis

Compute meridional transports and judge them against validated
expectations. Authored in Session 9 per SPECIFICATION.md v0.5.1 §4.4.
Works by slash command or conversationally ("what's the heat transport
at 26.5N?"). The methods authority is the meridional-transport skill;
the numbers authority is `knowledge/recipes/ecco-mht-26n.md` (and
future recipe concepts for other sections); this skill carries no
expected values of its own.

## Behavior, in order

1. **Parse and show back:** quantity (heat, volume, freshwater,
   overturning streamfunction), latitude or named section, period,
   basin scope.
2. **Knowledge first, restated:** the recipe concept for the section
   when one exists (expected range AND expected-uncertainty, quoted
   with citation); meridional-transport's rules that bind the request
   (flux diagnostics over reconstructed v-times-theta, mass-balance
   caveat for heat, Eulerian-plus-bolus for totals); the ecco-v4r4
   concept's no-formal-errors framing.
3. **Inputs via load-ecco** (gated): 3D temperature fluxes for heat,
   volume fluxes for volume and streamfunction, geometry merged.
4. **Compute natively:** section masks over faces (ecco_v4_py section
   machinery), transports summed over masked faces, streamfunction by
   vertical cumulation; no regridding anywhere in the path.
5. **Judge against the recipe:** the computed mean against the
   expected range; variability against the expected-uncertainty
   spread; time-sampling discipline applied (a single-year mean gets
   the wider single-year envelope, and any RAPID comparison matches
   overlap periods or says it cannot). Out-of-range results are
   reported as out-of-range with the recipe cited, then diagnosed
   (period mismatch, wrong fluxes, mask errors) rather than accepted
   quietly.
6. **Report:** the transport with its uncertainty statement (recipe
   spread, or the explicit ECCO no-formal-uncertainty line), the
   period, the method one-liner, and the concepts consulted. Where the
   comparison against observations is the point, hand off to
   compare-obs rather than improvising one here.

## Must NOT

- Never hardcode an expected transport or spread; the recipe is the
  authority and gets cited.
- Never regrid anything in a transport computation.
- Never present a single-year mean against a multi-year expectation
  without the envelope caveat.
- Never quote heat transport across a mass-unbalanced section without
  the reference-temperature statement.
- Never accept an out-of-range result without diagnosis.
