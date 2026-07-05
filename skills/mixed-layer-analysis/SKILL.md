---
name: mixed-layer-analysis
description: Mixed layer depth analysis workflow: criterion choice, seasonal climatology, trend with uncertainty.
---

# mixed-layer-analysis

Run a mixed layer analysis with the criterion owned explicitly.
Authored in Session 9 per SPECIFICATION.md v0.5.1 §4.4. Works by slash
command or conversationally ("how deep does the Labrador Sea mix?").
The discipline authority is the mixed-layer knowledge skill.

## Behavior, in order

1. **Parse and show back:** region, period, and the deliverable
   (seasonal climatology, winter maxima, trend), plus the criterion:
   stated by the user, or proposed explicitly (density threshold
   0.03 kg/m3 at 10 m reference as the default proposal) and
   confirmed, never silently assumed.
2. **Knowledge first, restated:** mixed-layer's comparison rule
   (criterion, reference depth, threshold, AND input averaging named
   with every number), the monthly-mean shallow-bias caveat when
   monthly inputs are all that is available, ECCO's own MXLDEPTH
   diagnostic and its internal criterion (using it means comparing
   like criteria or recomputing).
3. **Inputs via load-ecco** (gated): TEMP_SALINITY (and the density
   collection when the model EOS matters), or MXLDEPTH directly when
   its criterion is acceptable and stated; geometry merged.
4. **Compute:** MLD per profile per the pinned criterion; seasonal
   climatology with month-length weighting; winter maxima reported
   per-year as well as climatologically (deep convection is episodic,
   and the climatological mean of a bimodal winter is nobody's
   winter); trends per basic-statistics (autocorrelation-aware, per
   the core decision tree).
5. **Uncertainty framing:** the threshold-sensitivity check is
   mandatory (recompute under at least one alternative; the spread
   accompanies every headline MLD), trend significance per the
   corrected test, and the averaging-chain bias stated when monthly
   means fed the computation.
6. **Report:** climatology and extremes with the criterion block
   (criterion, threshold, reference depth, averaging chain), the
   sensitivity spread, episodicity noted for convection regions, and
   concepts consulted.

## Must NOT

- Never compute or quote an MLD without its full criterion block.
- Never skip the threshold-sensitivity check on a headline number.
- Never average convecting and non-convecting winters into a "typical"
  winter without saying so.
- Never mix ECCO's MXLDEPTH with a differently-defined MLD in one
  series.
- Never trend MLD with an uncorrected test on monthly data.
