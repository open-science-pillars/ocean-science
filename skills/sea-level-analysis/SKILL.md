---
name: sea-level-analysis
description: "Sea level analysis workflow: regional trends, steric vs manometric attribution, uncertainty on all headline rates."
---

# sea-level-analysis

Run a sea level analysis where every rate carries its uncertainty and
every component is named. Works by slash command or conversationally ("sea level
trends in the North Atlantic from ECCO"). The discipline authority is
the sea-level knowledge skill.

## Behavior, in order

1. **Parse and show back:** region, period, and the deliverable
   (regional trend map, basin series, steric vs manometric
   attribution), plus which SSH convention the question implies.
2. **Consult the bundle for this analysis first.** DISCOVER the
   applicable concepts, do not work from a remembered list: glob and
   grep `knowledge/datasets/`, `knowledge/gotchas/`, and
   `knowledge/recipes/` for every product, component, and correction in
   play (the ECCO dataset, its SSH inverse-barometer variants, the
   SSH/OBP release caveat, the Boussinesq global-mean correction, and
   for any observational cross-check the GRACE and altimetry concepts);
   read the matches, restate what each changes about the plan, and cite
   each by path. Do not carry these facts here; a concept added or
   corrected since you last ran is found this way. Observational
   cross-checks hand the altimetry and gravimetry conventions to
   compare-obs.
3. **Inputs via load-ecco** (gated): the SSH family (variant chosen to
   match the question, release stated), OBP for manometric, density
   for steric, geometry merged; snapshots when budgets of change are
   the point.
4. **Compute:** regional series and trends area-weighted natively;
   steric and manometric components decomposed and their sum checked
   against total SSH change (a decomposition that does not add up is
   reported as such, then diagnosed); global means carry the
   correction the applicable concept names.
5. **Uncertainty on all headline rates, no exceptions:** trend CIs
   from autocorrelation-aware methods (basic-statistics), internal
   variability acknowledged for short windows and small regions, the
   no-formal-errors framing where it applies (read from the dataset
   concept), and the smell-test anchor (analysis-review's table) as the
   sanity gate. Dynamic decadal variability is named as the dominant
   regional signal where it is.
6. **Report:** rates with CIs and periods, the convention block
   (SSH variant, release, corrections applied), component attribution
   with the closure check, figures per cartography, concepts
   consulted. Observational comparisons hand off to compare-obs.

## Hard refusals and gates (fire without consulting anything)

- Never quote a rate without a CI and its period. (Universal
  discipline: fires regardless of dataset.)
- Never present a steric-plus-manometric decomposition without the sum
  check against total SSH change. (Invariant method gate: a
  decomposition must add up.)
- Never attribute a short-window regional trend to forced change
  without the internal-variability caveat. (Universal statistical
  gate.)

Dataset-specific rules (the SSH inverse-barometer variant choice, the
V4R4/V4R4B release caveat for SSH and OBP, the Boussinesq global-mean
correction, the GRACE leakage and GIA cautions, the no-formal-errors
framing) are NOT restated here: they live in the bundle's concepts and
are consulted per step 2. That is what lets a corrected or new concept
change this skill's behavior without editing it.
