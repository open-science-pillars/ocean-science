---
name: water-mass-analysis
description: "Water mass analysis workflow: T-S census, density-space transformation, volumetric inventories with uncertainty framing."
---

# water-mass-analysis

Run a water mass analysis end to end with the conventions stated. Works by slash
command or conversationally ("what water masses fill the Irminger
Sea?"). The discipline authority is the water-masses knowledge skill;
this workflow executes it.

## Behavior, in order

1. **Parse and show back:** region, period, depth range, and the
   deliverable (T-S census, water-mass volumes, transformation
   analysis).
2. **Knowledge first, restated:** the ecco-v4r4 concept (T and S
   flavors: THETA is potential temperature, SALT practical salinity),
   the water-masses rules that bind the request (reference pressure
   for the depth range, EOS consistency, boundary definitions with
   named sources), and any recipe concept that pins expectations.
3. **Inputs via load-ecco** (gated): TEMP_SALINITY monthly (or
   snapshots when the question is about change), geometry merged,
   density collection when the model's own EOS fields are needed.
4. **Compute with conventions pinned:** volumetric T-S census weighted
   by rA * drF * hFacC; density surfaces at the reference appropriate
   to the depth range, stated; water-mass classes only with a named,
   cited boundary definition; transformation in density space where
   asked.
5. **Uncertainty framing:** class volumes carry a
   boundary-sensitivity check (recompute under a perturbed or
   alternative published boundary; the spread IS the uncertainty
   statement, since ECCO provides no formal errors); flavor and EOS
   choices are recorded in methods.
6. **Report:** census and volumes with the sensitivity spread, the
   conventions block (flavors, reference pressure, EOS, boundary
   source), figures per cartography (volumetric census, not scatter),
   and concepts consulted.

## Must NOT

- Never census by grid-point count instead of volume.
- Never use sigma0 for deep classes or leave the reference pressure
  unstated.
- Never present class volumes without the boundary-sensitivity spread.
- Never mix T or S flavors silently (the water-masses rules).
- Never claim ventilation ages from properties alone.
