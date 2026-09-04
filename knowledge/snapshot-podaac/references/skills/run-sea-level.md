---
type: Reference
title: "Run instructions: attested regional sea level partition"
description: "Executor instructions for the sea level partition: stage the monthly inputs, run the sanctioned computation for a receipt, attest the receipt."
generated: { by: claude-code/fable-5, at: 2026-08-30T22:50:00Z }
status: draft
---

# Run instructions: attested regional sea level partition

The executor contract for
[the regional sea level computation](../../computations/ecco-regional-sea-level.md):
a runner binds VALUES for `region` (from the registry inside the
sanctioned file) and `period`, and never edits the computation; the
attester hashes it. Receipts and verdicts are runtime artifacts, never
committed to the bundle.

## 1. Stage the data

Monthly granules for the period, in the `~/ECCO_V4r4` cache layout
(an Earthdata Login is needed to retrieve them, from the environment
or `~/.netrc`): `ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4`,
`ECCO_L4_OBP_LLC0090GRID_MONTHLY_V4R4`,
`ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4`, plus the static
geometry granule (fetched via earthaccess, per the recorded
static-collection quirk). A 12-month period is roughly 0.9 GB, most of
it the density collection.

## 2. Run the sanctioned computation

```bash
uv run references/computations/ecco_regional_sea_level.py \
  --region us-northeast-coast --period 2010-01:2010-12 \
  --receipt /tmp/sea-level-receipt.json
```

The receipt carries exactly the declared fields: the convention-bound
bookkeeping (`ssh_variant`, `months`), the three monthly anomaly
series and the residual series (`series_by_month`), the three trends
in mm per year, and beside each trend the interval block the one
sanctioned trend method states for it (`trend_total_interval`,
`trend_mass_interval`, `trend_steric_interval`, each naming that
method's file by hash). Over the full record, pass
`--period 1992-01:2017-12 --data-root ~/ECCO_V4r4_record`; months
are read one at a time, so the run costs the memory of one month.

## 3. Attest the receipt

```bash
uv run references/attesters/sea_level_partition.py /tmp/sea-level-receipt.json
```

PASS requires the sanctioned code hash, exactly the declared parameters
with a registered region and in-span period, `ssh_variant` exactly
`SSH`, the partition residual within the recorded measured tolerance
and recomputed from the series in the receipt, nonzero months and
cells, and every trend and interval recomputed from those series by
the shared attester chain (or a refusal of an interval the recompute
reproduces). While no tolerance is recorded, every run fails A4 by
design; the tolerance is written into the concept and the attester
together, from the sanctioned fixture run.
