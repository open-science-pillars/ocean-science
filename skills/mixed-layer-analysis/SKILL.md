---
name: mixed-layer-analysis
description: "Mixed layer depth analysis workflow: criterion choice, seasonal climatology, trend with uncertainty."
---

# mixed-layer-analysis

Run a mixed layer analysis with the criterion owned explicitly. Works by slash
command or conversationally ("how deep does the Labrador Sea mix?"). The
discipline authority is the mixed-layer knowledge skill; the criterion numbers,
the comparability and averaging rules, and the product MLD diagnostics live in
the knowledge bundle's concepts and are read from there per run, never carried
in this file.

## Non-negotiable gates (invariant method, fire on every run)

These are method discipline, universal across products and time; they fire
without consulting anything. The VALUES they reference (which thresholds, which
default) are read from the concepts in step 2, but the requirements themselves
are hardcoded.

- No MLD is computed or quoted without its full criterion block (criterion
  family, threshold, reference depth, input averaging).
- No criterion is ever silently assumed: it is stated by the user, or proposed
  explicitly and confirmed, before any computation.
- No headline MLD ships without a threshold-sensitivity check.
- MLD is never trended with an uncorrected significance test on autocorrelated
  (for example monthly) data; the test follows the basic-statistics decision
  tree.

## Behavior, in order

1. **Parse and show back:** region, period, and the deliverable (seasonal
   climatology, winter maxima, trend), plus the criterion: stated by the user,
   or proposed as the criteria convention's default and confirmed, never
   silently assumed.
2. **Consult the bundle for THIS analysis.** Discover and read the concepts
   that apply, do not restate them from memory: glob and grep
   `knowledge/conventions/`, `knowledge/gotchas/`, and `knowledge/datasets/`
   for the MLD criterion definitions and default, the comparability rule
   (which criterion, reference depth, threshold, and input averaging must
   match), the monthly-mean input caveat, and any product MLD-diagnostic
   gotcha (for ECCO, the MXLDEPTH-criterion gotcha). Restate what each changes
   about the plan and cite it by path. A concept added since you last ran is
   found this way.
3. **Inputs via load-ecco** (gated, geometry merged): the temperature and
   salinity collection (and the density collection when the model EOS
   matters), or the model's own MLD diagnostic only when its criterion is
   acceptable and stated per the gotcha consulted in step 2.
4. **Compute:** MLD per profile under the pinned criterion; seasonal
   climatology with month-length weighting; winter maxima reported per-year as
   well as climatologically (deep convection is episodic, so a climatological
   winter is an average over convecting and non-convecting years and is stated
   as such, never presented as a typical winter); trends per basic-statistics
   (autocorrelation-aware, per the core decision tree).
5. **Uncertainty framing:** the threshold-sensitivity check is mandatory
   (recompute under at least one alternative; the spread accompanies every
   headline MLD), trend significance per the corrected test, and the averaging
   chain stated with whatever caveat the criteria convention flags for the
   inputs used.
6. **Report:** climatology and extremes with the criterion block, the
   sensitivity spread, episodicity noted for convection regions, and the
   concepts consulted, each cited by path.

Dataset- and criterion-specific facts (the threshold values and the default,
the comparability and averaging rules, the model MLD diagnostic's own
criterion) are NOT restated here: they live in the criteria convention and the
product gotchas, and are consulted per step 2. That is what lets a corrected
number or a new product gotcha change this skill's behavior without editing it.
