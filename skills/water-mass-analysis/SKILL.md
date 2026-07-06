---
name: water-mass-analysis
description: "Water mass analysis workflow: T-S census, density-space transformation, volumetric inventories with uncertainty framing."
---

# water-mass-analysis

Run a water mass analysis end to end with the conventions stated. Works by slash
command or conversationally ("what water masses fill the Irminger
Sea?"). The discipline authority is the water-masses knowledge skill;
this workflow executes it, and reads the dataset facts it needs from the
knowledge bundle rather than carrying them here.

## Behavior, in order

1. **Parse and show back:** region, period, depth range, and the
   deliverable (T-S census, water-mass volumes, transformation
   analysis).
2. **Consult the bundle for THIS analysis first.** Discover and read the
   concepts that apply, do not restate them from memory: glob and grep
   `knowledge/datasets/`, `knowledge/gotchas/`, and `knowledge/recipes/`
   by product name, variable, depth range, and topic. The T and S
   variable flavors and the uncertainty framing for the product live in
   the dataset concept (`knowledge/datasets/ecco-v4r4.md` for ECCO); any
   recipe that pins expected classes or volumes lives in
   `knowledge/recipes/`. Restate what each changes about the plan and
   cite it by path. A concept added since you last ran is found this
   way; if no recipe pins expectations for this region, the analysis
   says its class volumes are unvalidated. The water-masses knowledge
   skill remains the discipline authority for reference-pressure,
   EOS-consistency, and boundary conventions.
3. **Inputs via load-ecco** (gated): the T-S collection the question
   needs (monthly, or snapshots when the question is about change),
   geometry merged, and the density collection when the model's own EOS
   fields are needed. load-ecco supplies the exact collections and
   restates the applicable gotchas.
4. **Compute with conventions pinned:** volumetric T-S census weighted
   by cell volume (rA * drF * hFacC on the native grid, per
   ocean-grids); density surfaces at the reference pressure appropriate
   to the depth range, stated; water-mass classes only with a named,
   cited boundary definition; transformation in density space where
   asked.
5. **Uncertainty framing:** class volumes carry a
   boundary-sensitivity check (recompute under a perturbed or
   alternative published boundary; the spread IS the uncertainty
   statement, per the product uncertainty framing read from the bundle
   concept); flavor and EOS choices are recorded in methods.
6. **Report:** census and volumes with the sensitivity spread, the
   conventions block (flavors, reference pressure, EOS, boundary
   source), figures per cartography (volumetric census, not scatter),
   and the concepts consulted.

## Must NOT (hard refusals: invariant, universal, fire on method not on any dataset fact)

- Never census by grid-point count instead of volume.
- Never use sigma0 for deep classes or leave the reference pressure
  unstated.
- Never present class volumes without the boundary-sensitivity spread.
- Never mix T or S flavors silently.
- Never claim ventilation ages from properties alone.

Dataset-specific facts (which product variable is which T or S flavor,
that the product ships no formal error fields, any expected class
volumes) are NOT restated here: they live in the bundle's concepts
(datasets/ecco-v4r4.md and any water-mass recipe) and in the
water-masses discipline skill, and are consulted per step 2. That is
what lets a new or corrected concept change this skill's behavior
without editing it.
