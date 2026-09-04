---
type: dataset-gotcha
title: "ECCO V4R4 vs V4R4B: mixing releases conflates corrections with signal"
description: "SSH and OBP ship corrected V4R4B collections alongside V4R4; a time series or comparison spanning both silently mixes a baseline correction into the signal."
tags: [ecco, v4r4, v4r4b, release, ssh, obp]
generated: { by: knowledge-seeder/claude, at: 2026-07-05T00:00:00Z }
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: ecco-release-mixing
sources:
  - id: nasa-ecco-l4-ssh-llc0090grid-monthly-v4r4
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4
    title: "PO.DAAC collection page: ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4"
  - id: nasa-ecco-l4-ssh-llc0090grid-monthly-v4r4b
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4B
    title: "PO.DAAC collection page: ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4B"
  - id: fields-ssh
    resource: ../fields/ecco-v4r4/ssh.md
    title: "Fields concept: sea surface height, whose Variants section lists the V4R4 and V4R4B ShortNames verified in CMR"
  - id: fields-obp
    resource: ../fields/ecco-v4r4/obp.md
    title: "Fields concept: ocean bottom pressure, whose Variants section lists the V4R4 and V4R4B ShortNames verified in CMR"
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
stale_after: 2027-01-04
---

# ECCO V4R4 vs V4R4B: mixing releases conflates corrections with signal

**Mechanism.** For sea surface height and ocean bottom pressure, PO.DAAC
publishes a corrected `V4R4B` collection alongside the original `V4R4`
(both live in CMR; the V4R4B SSH collection page resolves, evidence
above).[^nasa-ecco-l4-ssh-llc0090grid-monthly-v4r4][^nasa-ecco-l4-ssh-llc0090grid-monthly-v4r4b] V4R4B carries a baseline correction to those fields. The two
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
(evidence)[^nasa-ecco-l4-ssh-llc0090grid-monthly-v4r4][^nasa-ecco-l4-ssh-llc0090grid-monthly-v4r4b]; the Variants sections of the sea surface height and ocean
bottom pressure fields concepts record which collections have a B
release, verified in CMR by the ShortName sweep.[^fields-ssh][^fields-obp]

[^nasa-ecco-l4-ssh-llc0090grid-monthly-v4r4]: PO.DAAC collection page: ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4
[^nasa-ecco-l4-ssh-llc0090grid-monthly-v4r4b]: PO.DAAC collection page: ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4B
[^fields-ssh]: fields/ecco-v4r4/ssh.md, Variants
[^fields-obp]: fields/ecco-v4r4/obp.md, Variants
