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
2. **Consult the bundle for this analysis first.** Consult installed
   knowledge concepts first, as the core `consult-knowledge` skill
   sets out, by product, component, correction, and region; the
   sea-level skill lists the concepts this plugin resolves to (the
   ECCO dataset and SSH family, its SSH inverse-barometer variants, the
   SSH/OBP release caveat, the Boussinesq global-mean correction, the
   trend gotchas and the trend computation, and for any observational
   cross-check the GRACE and altimetry concepts); read the matches,
   restate what each changes about the plan, and cite
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

## Attested runs

Where the deliverable has an attested computation in the provider
bundle, step 4 runs its sanctioned executor and step 5 takes the trend
and its interval from the receipt; this section is that procedure,
with the paths and the parameters bound.
The provider bundle is installed with the nasa-daac-knowledge
dependency; its root is the `installPath` of that entry in
`claude plugin list --json`, or a checkout named by
`NASA_DAAC_KNOWLEDGE` (the way the receipt-figures renderer resolves
it). `$PODAAC` below stands for `<that root>/knowledge/podaac`. Never
edit an executor: its attester hashes it, and a changed hash fails by
construction. Run the named attester on the receipt before quoting any
number from it; a FAIL is reported as a FAIL with the failing field
named, never worked around. These executors take no `--runtime` flag
(their receipts carry no runtime block); record the runtime name
(`claude-code` here) in the report beside the receipt's run id.

Both executors read monthly native granules in the `~/ECCO_V4r4`
cache layout (`--data-root`, default `~/ECCO_V4r4`): for the period,
`ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4`,
`ECCO_L4_OBP_LLC0090GRID_MONTHLY_V4R4` and
`ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4`, plus the static
geometry granule (fetched with earthaccess under an Earthdata Login,
per the recorded static-collection quirk); a twelve-month period is
roughly 0.9 GB, most of it the density collection. Over the full
record pass `--period 1992-01:2017-12 --data-root ~/ECCO_V4r4_record`;
months are read one at a time, so a run costs the memory of one month.
The tree must carry the RECORD.json stamp the provider's verify tool
leaves (`<root>/tools/science_record_verify.py --stamp` against the
tree's manifest under `$PODAAC/references/retrieval/`), since the
attesters refuse a receipt from an unstamped tree.

**Regional sea level partition, `ecco-regional-sea-level`**
(`knowledge/podaac/computations/ecco-regional-sea-level.md`; executor
`references/computations/ecco_regional_sea_level.py`, attester
`references/attesters/sea_level_partition.py`). Binds `region` (from
the registry inside the sanctioned file: `gulf-of-mexico`,
`north-sea`, `us-northeast-coast`) and `period` (`YYYY-MM:YYYY-MM`
within 1992-01 to 2017-12):

```bash
uv run $PODAAC/references/computations/ecco_regional_sea_level.py \
  --region us-northeast-coast --period 2010-01:2010-12 \
  --data-root ~/ECCO_V4r4 --receipt /tmp/sea-level-receipt.json
uv run $PODAAC/references/attesters/sea_level_partition.py /tmp/sea-level-receipt.json
```

The receipt carries exactly the declared fields: the convention-bound
bookkeeping (`ssh_variant`, `months`, `cells_evaluated`), the three
monthly anomaly series and the residual series (`series_by_month`),
the three trends in mm per year, and beside each trend the interval
block the one sanctioned trend method states for it
(`trend_total_interval`, `trend_mass_interval`,
`trend_steric_interval`, each naming that method's file by hash), and
the maximum partition residual. PASS requires the sanctioned code
hash, exactly the declared parameters with a registered region and an
in-span period, `ssh_variant` exactly `SSH`, the partition residual
within the recorded measured tolerance and recomputed from the series
in the receipt, nonzero months and cells, and every trend and interval
recomputed from those series by the shared attester chain (or a
refusal of an interval the recompute reproduces). The step 4 sum
check is the receipt's partition residual; the step 5 interval is the
receipt's interval block, never a separately fitted one. The
briefing-generator skill consumes this receipt.

**Regional steric height, `ecco-steric-height`**
(`knowledge/podaac/computations/ecco-steric-height.md`; executor
`references/computations/ecco_steric_height.py`, attester
`references/attesters/steric_check.py`). Binds `region` (`global`,
`gulf-of-mexico`, `north-sea`, `us-northeast-coast`) and `months` (a
list of `YYYY-MM`, consecutive):

```bash
uv run $PODAAC/references/computations/ecco_steric_height.py \
  --region us-northeast-coast \
  --months 2010-01 2010-02 2010-03 2010-04 2010-05 2010-06 2010-07 2010-08 2010-09 2010-10 2010-11 2010-12 \
  --data-root ~/ECCO_V4r4 --receipt /tmp/steric-receipt.json
uv run $PODAAC/references/attesters/steric_check.py /tmp/steric-receipt.json
```

The receipt carries `steric_mean_m_by_month`, `steric_trend_mm_yr`
with `steric_trend_interval` (the sanctioned trend method's block,
named by hash) and `cells_in_region`; the attester recomputes the
trend and interval from the series, checks the cross-computation
anchor against the partition's receipt on the reference
configurations, and requires the Boussinesq caveat field on a global
run, so a global-mean steric change is never quoted as modeled
sea-surface rise. A trend with interval on any other monthly series a
receipt carries goes through the trend-with-interval computation the
ecco skill's attested runs describe, never through a bare fit.

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
