---
type: Attested Computation
title: "Regional sea level partition from ECCO (attested)"
description: "Sanctioned regional partition of ECCO sea level into manometric and steric parts: the receipt carries the three monthly anomaly series, a machine-checked closure residual recomputed from them, each trend with the interval the one sanctioned trend method states for it, and convention-bound bookkeeping fields."
tags: [ecco, sea-level, steric, manometric, attested, native-grid]
runtime: python
parameters:
  - { name: region, type: string, required: true }
  - { name: period, type: string, required: true }
computation: references/computations/ecco_regional_sea_level.py
executor:
  resource: references/skills/run-sea-level.md
  receipt: [run_id, code_sha256, data, bound_parameters, ssh_variant, months, cells_evaluated, trend_total_mm_yr, trend_mass_mm_yr, trend_steric_mm_yr, trend_total_interval, trend_mass_interval, trend_steric_interval, partition_residual_max, series_by_month]
attester:
  resource: references/attesters/sea_level_partition.py
generated: { by: claude-code/fable-5, at: 2026-08-30T22:40:00Z }
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T22:08:00Z }
stale_after: 2027-01-04
sources:
  - id: convention-slbc
    resource: ../conventions/sea-level-budget-closure.md
    title: "Bundle convention: sea level budget closure, a correction-consistency problem first (steward-verified 2026-07-06)"
  - id: gotcha-ssh-ib
    resource: ../gotchas/ecco-ssh-ib-variants.md
    title: "Bundle gotcha: ECCO SSH inverse-barometer variants (steward-verified 2026-07-06)"
  - id: fields-ssh
    resource: ../fields/ecco-v4r4/ssh.md
    title: "Bundle fields concept: sea surface height (stable)"
  - id: fields-obp
    resource: ../fields/ecco-v4r4/obp.md
    title: "Bundle fields concept: ocean bottom pressure (stable)"
  - id: pattern-heat
    resource: ecco-heat-budget.md
    title: "Bundle attested computation: heat budget closure (the pattern; steward-signed stable)"
  - id: trend-ci
    resource: ecco-trend-ci.md
    title: "The one sanctioned trend method: the interval block each of the three trends carries, and the calibration behind it"
  - id: steric-height
    resource: ecco-steric-height.md
    title: "The attested steric height whose independent code reproduces this receipt's steric trend over 2010 and over the full record"
---

# Regional sea level partition from ECCO (attested)

The sanctioned computation behind receipted sea level briefings: over a
named coastal region and period, partition ECCO's sea level change into
the manometric (ocean-mass) piece and the steric piece, and prove the
partition closed. Version 1 scope is deliberately ECCO-internal: total
from the `SSH` variant, manometric from `OBP`, steric as the density
integral, all from one dynamically consistent product on the native
grid,[^fields-ssh][^fields-obp] so closure is a machine-checkable
identity rather than a cross-product reconciliation. Cross-product
budgets (altimetry, GRACE-FO) are governed by the closure convention's
full corrections table[^convention-slbc] and are OUT of this
computation's attested scope; a briefing may cite those concepts as
context but takes no computed numbers from them in v1.

## Parameters

- `region` (string, required): a named coastal segment or basin from
  the computation's region registry (native-grid mask; the registry is
  part of the sanctioned file, so an unregistered region fails
  attestation rather than improvising a mask).
- `period` (string, required): an inclusive month range within
  1992-01 to 2017-12 (ECCO v4r4's span; briefings state this boundary
  plainly).

## The attester criterion (deterministic, consumer-side)

A run PASSES only when ALL hold:

- **A1, sanctioned code**: `code_sha256` equals the sha256 of the
  computation file.
- **A2, declared parameters only**: `bound_parameters` binds exactly
  `region` and `period`, region in the registry, period within span.
- **A3, convention bookkeeping** (the closure convention's consistency
  requirements as receipt facts[^convention-slbc]): `ssh_variant` is
  stated and is exactly `SSH` (one variant, named, never
  mixed[^gotcha-ssh-ib]); all three trends cover identical `months`
  (matching-period rule, the dates in `series_by_month`); and the
  regional scope means the Boussinesq
  global-mean correction is out of scope by construction (recorded
  here, not in the receipt).
- **A4, closure**: `partition_residual_max`, the largest absolute
  monthly residual of (total minus mass minus steric) over the region's
  area-mean anomaly series, sits at or below **1.0e-3 m**. The
  tolerance is measured, not assumed (the heat-budget
  precedent[^pattern-heat]): the sanctioned fixture run
  (us-northeast-coast, 2010-01:2010-12, 102 cells) measures a maximum
  monthly residual of 5.061e-04 m, and the full record
  (1992-01:2017-12) 8.282e-04 m, inside the same bar. An earlier
  fixture figure of 5.085e-04 m carried a constant 0.0024 mm offset:
  the inputs and the per-month area means are single precision, and
  forming the period mean in single precision at a steric mean near
  -19.5 m (where the float32 quantum is 2e-6 m) put that quantum into
  every residual; the anomalies are now formed in double, and the
  per-month arithmetic is untouched so the anchor holds. The residual
  is the ECCO-internal wedge between the SSH variant and OBP plus
  model-density steric, and a residual above tolerance is a
  formulation or variant-pairing error, not data noise.
- **A5, evaluated substance**: `months` and `cells_evaluated` are
  positive.
- **A6, recomputable series and intervals**: the receipt carries
  `series_by_month` (the period's consecutive months, the three
  area-mean anomaly series, each summing to zero, and the residual
  series in mm), and the attester rebuilds the residual and its
  maximum from the three series rather than believing the stated
  number. Each of the three trends is the central value of the one
  sanctioned trend method[^trend-ci] and carries that method's
  interval block beside it, named by the method file's hash; the
  shared attester chain recomputes the block from the series in the
  receipt (trend, lag-1 autocorrelation, effective sample size,
  degrees of freedom, standard error, t quantile, both bounds and the
  significance flag) to within 1e-9 relative, or requires a refusal it
  reproduces. The trend is never bare; the anchor the steric
  computation checks is on the central value, and the interval travels
  beside it. Nine tampers (a shifted date, a halved half width, an
  effective sample size above the sample, a dropped series block, a
  series that is not an anomaly, a nudged residual, a stated maximum
  below the series, a nudged series value, a doctored trend) each fail
  naming their field.

## Reference runs

**Fixture run (us-northeast-coast, 2010-01 through 2010-12, 102
cells, measured 2026-09-02).** Total +146.7492 mm per year, 95
percent interval [-346.9, +640.3]; manometric +11.7851, interval
[-8.9, +32.5]; steric +135.7772, interval [-701.5, +973.1]. None of
the three is distinguishable from zero: twelve months of serially
correlated series hold 4.0, 12.0 and 3.4 effective samples, and the
intervals say so where the bare trends once did not. The steric trend
is the value the attested steric height computation reproduces from
independent code to four decimals.[^steric-height] Maximum residual
5.061e-04 m.

**Record run (us-northeast-coast, 1992-01 through 2017-12, 312
months, the verified science record, measured 2026-09-02).** Total
+5.2452 mm per year, interval [+4.0623, +6.4281] (r1 +0.821, 30.7
effective months); manometric +2.4535, interval [+2.1701, +2.7370]
(r1 +0.514, 100.3 effective months); steric +2.7999, interval
[+1.5103, +4.0895] (r1 +0.893, 17.6 effective months), the climatology
removed jointly with each fit over 26 complete years. All three are
distinguishable from zero, and the steric block is identical to every
digit to the one the steric height computation writes for the same
months.[^steric-height] Maximum residual 8.282e-04 m. Both receipts
ship as exhibits (references/retrieval/exhibit-sea-level-2010.json and
exhibit-sea-level-record.json) and pass the attester from a fresh
clone.

## Boundaries

ECCO v4r4 ends at 2017-12: every v1 briefing is a retrospective,
methodological demonstration and says so; the operational cadence
arrives with V4r5. Produced by Open Science Pillars (personal-hat open
source), not a NASA or JPL product.

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^convention-slbc]: conventions/sea-level-budget-closure.md, the corrections table and the consistency requirements
[^gotcha-ssh-ib]: gotchas/ecco-ssh-ib-variants.md, one SSH variant, named, never mixed
[^fields-ssh]: Bundle fields concept: sea surface height (stable)
[^fields-obp]: Bundle fields concept: ocean bottom pressure (stable)
[^pattern-heat]: Bundle attested computation: heat budget closure (the pattern)
[^trend-ci]: computations/ecco-trend-ci.md, the sanctioned trend method behind every interval here
[^steric-height]: computations/ecco-steric-height.md, the independent steric code that anchors on this receipt
