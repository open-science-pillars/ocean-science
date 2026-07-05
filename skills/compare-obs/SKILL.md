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
2. **Knowledge first, restated:** BOTH sides' dataset concepts (the
   obs product's Uncertainty section and gotchas as much as ECCO's),
   plus the recipe concept where one pins the comparison (ecco-mht-26n
   carries the RAPID discipline).
3. **Alignment before arithmetic**, each item stated in the report:
   - **Periods match** (or the mismatch is stated and its effect
     bounded); ECCO ends 2017, which truncates many comparisons.
   - **Conventions match:** SSH inverse-barometer variants, reference
     surfaces and baselines, temperature flavors (per water-masses),
     calendars (per core's conventions).
   - **Sampling is reconciled:** the model is sampled like the obs
     where feasible (along tracks, at array sections, on the obs
     grid's effective resolution); a smooth 1-degree state estimate
     compared pointwise against eddy-resolving observations measures
     resolution, not skill.
   - **Consistent masking:** one mask, applied to both fields (land,
     ice, obs coverage holes); statistics over different domains are
     not a comparison.
4. **Difference with uncertainty framing:** obs product uncertainty
   (native fields per its concept) combined with the model side's
   expected-uncertainty (recipe spread, or the ECCO
   no-formal-uncertainty line); differences are judged against that
   combined spread, and "model differs from obs" is asserted only
   where the difference exceeds it.
5. **Report:** the comparison statistics with the alignment items
   listed, the uncertainty framing stated, figures per cartography's
   comparison rules (shared color scales), and concepts consulted.
   Findings about the obs product (a suspected artifact, an
   undocumented convention) enter the ingest loop as concept
   candidates rather than staying buried in a comparison note.

## Must NOT

- Never compare across mismatched periods, conventions, or masks
  without stating the mismatch and its direction of bias.
- Never treat resolution mismatch as model error.
- Never declare disagreement inside the combined uncertainty spread.
- Never tune or adjust either side to improve agreement; comparison
  reports, it does not calibrate.
- Never skip the obs product's own gotchas (leakage, orbit phases,
  analysis-error caveats) just because the model is the subject.
