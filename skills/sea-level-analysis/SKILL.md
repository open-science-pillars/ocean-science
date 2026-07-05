---
name: sea-level-analysis
description: "Sea level analysis workflow: regional trends, steric vs manometric attribution, uncertainty on all headline rates."
---

# sea-level-analysis

Run a sea level analysis where every rate carries its uncertainty and
every component is named. Authored in Session 9 per SPECIFICATION.md
v0.5.1 §4.4. Works by slash command or conversationally ("sea level
trends in the North Atlantic from ECCO"). The discipline authority is
the sea-level knowledge skill.

## Behavior, in order

1. **Parse and show back:** region, period, and the deliverable
   (regional trend map, basin series, steric vs manometric
   attribution), plus which SSH convention the question implies.
2. **Knowledge first, restated:** sea-level's decomposition and
   correction rules (IB variants, the V4R4B release rule for SSH and
   OBP, Boussinesq global-mean correction), the ecco-v4r4 concept, and
   for any observational cross-check the GRACE gotchas (leakage, GIA)
   and altimetry conventions via compare-obs.
3. **Inputs via load-ecco** (gated): the SSH family (variant chosen to
   match the question, release stated), OBP for manometric, density
   for steric, geometry merged; snapshots when budgets of change are
   the point.
4. **Compute:** regional series and trends area-weighted natively;
   steric and manometric components decomposed and their sum checked
   against total SSH change (a decomposition that does not add up is
   reported as such, then diagnosed); global means carry the
   Boussinesq correction.
5. **Uncertainty on all headline rates, no exceptions:** trend CIs
   from autocorrelation-aware methods (basic-statistics), internal
   variability acknowledged for short windows and small regions,
   ECCO's no-formal-errors line where it applies, and the smell-test
   anchor (analysis-review's table) as the sanity gate. Dynamic
   decadal variability is named as the dominant regional signal where
   it is.
6. **Report:** rates with CIs and periods, the convention block
   (SSH variant, release, corrections applied), component attribution
   with the closure check, figures per cartography, concepts
   consulted. Observational comparisons hand off to compare-obs.

## Must NOT

- Never quote a rate without a CI and its period.
- Never mix IB variants or V4R4/V4R4B releases silently.
- Never present a steric-plus-manometric decomposition without the
  sum check.
- Never quote a Boussinesq global mean uncorrected.
- Never attribute a short-window regional trend to forced change
  without the internal-variability caveat.
