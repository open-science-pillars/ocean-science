---
type: dataset-gotcha
title: "ECCO V4R4 vs V4R4B: mixing releases conflates corrections with signal"
description: "SSH and OBP ship corrected V4R4B collections alongside V4R4; a time series or comparison spanning both silently mixes a baseline correction into the signal."
tags: [ecco, v4r4, v4r4b, release, ssh, obp]
timestamp: 2026-07-05
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: ecco-release-mixing
evidence:
  - https://podaac.jpl.nasa.gov/dataset/ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4
  - https://podaac.jpl.nasa.gov/dataset/ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4B
  - https://github.com/open-science-pillars/ocean-science/blob/main/skills/ecco/references/variable-catalog.md
status: verified
verified: 2026-07-05
verified_by: OSP steward review
---

# ECCO V4R4 vs V4R4B: mixing releases conflates corrections with signal

**Mechanism.** For sea surface height and ocean bottom pressure, PO.DAAC
publishes a corrected `V4R4B` collection alongside the original `V4R4`
(both live in CMR; the V4R4B SSH collection page resolves, evidence
above). V4R4B carries a baseline correction to those fields. The two
collections are separate ShortNames, not a silent in-place update.

**Wrong-result mode.** An SSH or OBP series, trend, or comparison
assembled from a mix of V4R4 and V4R4B granules folds the release
correction into the geophysical signal: an apparent step or drift at
the release boundary is an artifact of the switch, not the ocean.
Nothing errors; the ShortNames differ by one character and a careless
query can return either.

**Correct approach.** A correct analysis uses one release throughout
and states it. SSH and OBP work uses the corrected V4R4B; the other ECCO
fields have no B variant, so V4R4 is their release, and any cross-field
mix is stated. Each field's release is named.

**Verification.** Both collection pages resolve as distinct ShortNames
(evidence); the variable catalog's Variants section records which
fields have a B release.
