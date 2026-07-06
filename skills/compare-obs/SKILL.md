---
name: compare-obs
description: "Compare model or state-estimate output against observations: RAPID, Argo climatologies, altimetry; consistent masking and uncertainty framing."
---

# compare-obs

Model-versus-observations comparisons that measure the ocean, not the
bookkeeping.
Works by slash command or conversationally ("how does ECCO SSH compare
to altimetry?").

## Behavior, in order

1. **Parse and show back:** the model quantity, the observational
   reference (RAPID transports, Argo-based climatologies, altimetry
   SSH, GRACE mass, SST analyses), period, region.
2. **Consult the bundle for BOTH sides of this comparison.** Discover
   the concepts, do not restate them from memory: search
   `knowledge/datasets/`, `knowledge/gotchas/`, and `knowledge/recipes/`
   (glob and grep by product name, variable, and topic) for every
   concept touching the model quantity AND the observational reference,
   read the matches, and restate what each changes about the comparison
   before computing, citing it by path. The obs product's own
   Uncertainty section and gotchas bind the comparison as much as the
   model side's; where a recipe pins the comparison it carries the
   comparison discipline. A concept added since you last ran is found
   this way; a side with no concept in the bundle is reported as
   unconstrained, not assumed clean.
3. **Alignment before arithmetic**, each item stated in the report:
   - **Periods match** (or the mismatch is stated and its effect
     bounded); each product's own coverage window, read from its
     concept, sets where a comparison is possible.
   - **Conventions match:** SSH inverse-barometer variants, reference
     surfaces and baselines, temperature flavors (per water-masses),
     calendars (per core's conventions).
   - **Sampling is reconciled:** the model is sampled like the obs
     where feasible (along tracks, at array sections, on the obs
     grid's effective resolution); a smooth coarse-resolution state
     estimate compared pointwise against eddy-resolving observations
     measures resolution, not skill.
   - **Consistent masking:** one mask, applied to both fields (land,
     ice, obs coverage holes); statistics over different domains are
     not a comparison.
4. **Difference with uncertainty framing:** the obs product's
   uncertainty (its native fields, per its concept) combined with the
   model side's expected uncertainty (a recipe's spread, or the dataset
   concept's uncertainty framing where the product ships no formal
   error fields); differences are judged against that combined spread,
   and "model differs from obs" is asserted only where the difference
   exceeds it.
5. **Report:** the comparison statistics with the alignment items
   listed, the uncertainty framing stated, figures per cartography's
   comparison rules (shared color scales), and concepts consulted.
   Findings about the obs product (a suspected artifact, an
   undocumented convention) enter the ingest loop as concept
   candidates rather than staying buried in a comparison note.

## Must NOT (hard refusals: invariant, universal, gate-shaped)

- Never compare across mismatched periods, conventions, or masks
  without stating the mismatch and its direction of bias.
- Never treat resolution mismatch as model error.
- Never declare disagreement inside the combined uncertainty spread.
- Never tune or adjust either side to improve agreement; comparison
  reports, it does not calibrate.
- Never skip the obs product's own gotchas just because the model is
  the subject; step 2 discovers them and they bind the comparison.

Dataset-specific facts (a product's coverage window, its native
uncertainty fields, the smooth-coarse-grid and no-formal-error framing
of a state estimate, the leakage, orbit-phase, and analysis-error
caveats of the obs products, the recipe that pins a comparison's
spread) are NOT restated here: they live in the bundle's dataset,
gotcha, and recipe concepts and are consulted per step 2. That is what
lets a corrected concept change this skill's behavior without editing
it.
