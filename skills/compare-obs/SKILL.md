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
2. **Consult the bundle for BOTH sides of this comparison.** Consult
   installed knowledge concepts first, as the core `consult-knowledge`
   skill sets out, by product name, variable, and topic, for every
   concept touching the model quantity AND the observational reference
   (the ecco, swot, and sea-level skills list the concepts this plugin
   resolves to; the confrontation computations under
   `knowledge/podaac/computations/` and the
   consistency-versus-confrontation convention own the comparison
   discipline where they exist); read the matches, and restate what
   each changes about the comparison before computing, citing it by
   path. The obs product's own Uncertainty section and gotchas bind the
   comparison as much as the model side's; where a recipe or
   computation pins the comparison it carries the comparison
   discipline. A concept added since you last ran is found
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

## Attested runs

Where the comparison has an attested confrontation in the provider
bundle, step 4 is its sanctioned executor and the difference is
judged from its receipt; this section is that procedure, with the
paths and the parameters bound.
The executor and the attester of every computation below ship in this
package, in the scripts directory of the skill that runs them, and the
concept each one answers to is under `knowledge/computations/`.
`${CLAUDE_PLUGIN_ROOT}` below is this package's root, which the runtime
sets. Never
edit an executor: its attester hashes it, and a changed hash fails by
construction. Run the named attester on the receipt before quoting any
number from it; a FAIL is reported as a FAIL with the failing field
named, never worked around. These executors take no `--runtime` flag
(their receipts carry no runtime block); record the runtime name
(`claude-code` here) in the report beside the receipt's run id.

Each confrontation consumes a receipt of the model-side computation
(run under the transport-analysis or sea-level-analysis skill) and a
stamped tree of the observations: the record's files under a
RECORD.json written by the provider's verify tool
(`<root>/tools/science_record_verify.py --stamp`) against the record's
manifest under `${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/`. The attesters import
the shared trend recompute beside them; invoked by full path they
find it.

**ECCO overturning against RAPID at 26.5N,
`ecco-rapid-amoc-confrontation`**
(`knowledge/podaac/computations/ecco-rapid-amoc-confrontation.md`;
executor `skills/compare-obs/scripts/ecco_rapid_amoc_confrontation.py`,
attester `skills/compare-obs/scripts/rapid_confrontation_check.py`). Binds
`ecco-receipt` (a receipt of `ecco-amoc-26n`, scope atlantic,
convention mass-balanced, on a stamped tree), `rapid-root` (the
stamped tree of the RAPID release v2024.1a, manifest
`rapid-26n-manifest.json`), `min-valid-fraction` (default 0.5, the
share of a month's twelve-hourly samples that must be valid) and
`period` (default the whole consecutive overlap):

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/compare-obs/scripts/ecco_rapid_amoc_confrontation.py \
  --ecco-receipt /tmp/amoc-receipt.json --rapid-root ~/RAPID_26N/rapid.ac.uk-2026-09-02 \
  --receipt /tmp/rapid-confrontation-receipt.json
uv run ${CLAUDE_PLUGIN_ROOT}/skills/compare-obs/scripts/rapid_confrontation_check.py /tmp/rapid-confrontation-receipt.json \
  --model-receipt /tmp/amoc-receipt.json
```

The receipt carries both series in full with the RAPID sample counts,
the bias, RMSD, correlation and anomaly correlation each with its
interval from the attested chain, the observation's version, DOI,
hash, licence, citation and published measurement uncertainty. PASS
pins the observation to v2024.1a and its DOI and recomputes every
score; a later RAPID release is a different observation and needs a
re-run. The scores are read against the published uncertainty in the
receipt, and the sabotage and scope disclosures travel with them.

**ECCO regional sea level against NASA-SSH altimetry,
`ecco-ssh-vs-altimetry`** (a draft concept, voiced as such;
`knowledge/podaac/computations/ecco-ssh-vs-altimetry.md`; executor
`skills/compare-obs/scripts/ecco_ssh_vs_altimetry.py`, attester
`skills/compare-obs/scripts/altimetry_confrontation_check.py`). Binds
`partition-receipt` (a receipt of `ecco-regional-sea-level`, SSH
variant, registered region), `obs-root` (the stamped tree of the
NASA-SSH V1.1 simple grids, manifest `nasa-ssh-manifest.json`),
`min-grids` (default 4; 2 admits every month of the record) and
`period` (default the whole consecutive overlap):

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/compare-obs/scripts/ecco_ssh_vs_altimetry.py \
  --partition-receipt /tmp/sea-level-receipt.json --obs-root ~/NASA_SSH/podaac-2026-09-02 \
  --period 1993-01:2017-12 --min-grids 2 --receipt /tmp/altimetry-comparison-receipt.json
uv run ${CLAUDE_PLUGIN_ROOT}/skills/compare-obs/scripts/altimetry_confrontation_check.py /tmp/altimetry-comparison-receipt.json \
  --model-receipt /tmp/sea-level-receipt.json --obs-root ~/NASA_SSH/podaac-2026-09-02
```

Both series are centred on the overlap mean, so the mean difference
is zero by construction and not a score; the scores are RMSD,
correlation, anomaly correlation and the trend of the difference,
each with its interval. The receipt's independence statement says the
estimate was fitted to these missions' along-track heights, and the
report carries that statement with the scores: a PASS says the
comparison was done as described, not that the estimate is right for
reasons other than having been fitted.

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
