---
type: Attested Computation
spheres: [hydrosphere]
title: "Regional steric height from ECCO v4r4 (attested)"
description: "Sanctioned column-integral steric height over registered regions; the trend travels with the interval the one sanctioned trend method states for it, the reference runs' trends must match the attested sea-level partition's receipts over 2010 and over the full record, and a global run cannot pass attestation without the Boussinesq caveat in the receipt."
tags: [ecco, steric-height, sea-level, attested, native-grid]
runtime: python
parameters:
  - { name: region, type: "registered region name", required: true }
  - { name: months, type: "list of YYYY-MM strings", required: true }
computation: skills/sea-level-analysis/scripts/ecco_steric_height.py
executor:
  resource: skills/sea-level-analysis/scripts/ecco_steric_height.py
  receipt: [run_id, code_sha256, data, bound_parameters, steric_mean_m_by_month, steric_trend_mm_yr, steric_trend_interval, cells_in_region]
attester:
  resource: skills/sea-level-analysis/scripts/steric_check.py
generated: { by: claude-code/fable-5, at: 2026-09-01T05:35:00Z }
verified:
  - { by: human:PaulMRamirez, at: 2026-09-02T14:51:04Z }
  - { by: human:PaulMRamirez, at: 2026-09-16T05:51:09Z, role: maintainer, source: https://github.com/open-science-pillars/nasa-daac-knowledge/pull/183 }
status: draft
stale_after: 2027-01-04
sources:
  - id: sea-level-partition
    resource: ecco-regional-sea-level.md
    title: "The attested regional sea level partition: its signed receipt records the steric trend this computation must independently reproduce"
  - id: ecco-skills-corroboration
    resource: https://github.com/podaac/ecco-skills
    title: "podaac/ecco-skills compute-steric-height acceptance record: an independent implementation whose steric field matches SSH spatially at correlation 0.92"
  - id: trend-ci
    resource: ecco-trend-ci.md
    title: "The one sanctioned trend method: the interval block this receipt embeds beside its trend, and the calibration behind it"
---

# Regional steric height from ECCO v4r4 (attested)

**Placement, 2026-09-20 (ADR E, a computation is a skill).** This
concept came from the nasa-daac-knowledge bundle at
`knowledge/podaac/computations/ecco-steric-height.md`, and the executor
and the attester it names now ship in this package under
`skills/sea-level-analysis/scripts/`. The golden
`verification/sea_level_analysis.py` names every script it does. The
executor `skills/sea-level-analysis/scripts/ecco_steric_height.py`
changed only where it resolves a path, so its sha256 moved from
efde39a167aded57 to e07b8940d4c51695 and no number in it did. The
reference run `steric` reads the ECCO 2010 fixture cache, which this
environment does not hold, so it was not re-run here; the golden runs it
where the cache is present. The two committed steric exhibits no longer
attest, because they were produced by the executor before its import of
the trend method moved; the maintainer regenerates them where the cache
is present. The signature block is the one the maintainer left; the
concept sits at `status: draft` with no verified event added, and the
maintainer re-signs it after merge.

Steric height per water column as minus one over rho0 times the sum
over depth of RHOAnoma times hFacC times drF, area-weighted by rA over
a registered region, from the density collection
(ECCO_L4_DENS_STRAT_PRESS) with rho0 1029 kg m-3. Regions are a fixed
registry (us-northeast-coast, gulf-of-mexico, north-sea, global);
free-text boxes do not pass attestation.

**Attestation contract.** A run passes only when the receipt's
code_sha256 matches the sanctioned computation, the bound parameters
are exactly the contract set, and every monthly area-mean sits in the
physical band -60 to 0 m. The reference configuration carries a
CROSS-COMPUTATION ANCHOR: for us-northeast-coast over 2010, the steric
trend must match the trend the attested sea-level partition's signed
receipt records, +135.7772 mm per year, within 0.05, and the region
must contain exactly 102 wet columns; over the full record, 1992-01
through 2017-12, the same anchor holds at +2.7999 mm per
year.[^sea-level-partition] The trend is never bare. It is the central
value of the one sanctioned trend method,[^trend-ci] and the receipt
carries that method's interval block beside it, named by the method
file's hash: the attester recomputes trend and interval from the
monthly series in the receipt and refuses a block that does not
recompute, a claimed refusal the recompute does not reproduce, or a
significance flag that contradicts its own interval. The anchor is on
the central value; the interval travels beside it. A global run cannot
pass without the Boussinesq caveat field in the receipt, so no
consumer can quote a global-mean steric change as modeled sea-surface
rise.

**Reference run (2026-09-01, cached native granules; interval added
2026-09-02).** Trend +135.7772 mm per year, 95 percent interval
[-701.5, +973.1]: identical to the partition's signed receipt to four
decimals from independent code, and not distinguishable from zero,
because twelve months of a series with lag-1 autocorrelation +0.555
hold 3.43 effective samples. That is the honest content of a single
year, and the receipt says so beside the anchor. 102 columns; regional
means near -19.6 m; global means near -30.9 m with the caveat carried.
Attester PASS on the reference and the global runs; FAIL demonstrated
on a doctored trend (140.0) and on ten tampers of the interval block
(a nudged bound, a nudged r1, a nudged series value, a flipped
significance flag, a claimed refusal, a foreign method hash, an
effective sample size above the sample, a missing block, a wrong
deseasonalization, a nudged trend), each naming its field. An
independent PO.DAAC implementation reaches a spatial SSH correlation
of 0.92 for the same quantity.[^ecco-skills-corroboration]

**Record run (2026-09-02, the verified science record, 1992-01
through 2017-12).** Trend +2.7999 mm per year, 95 percent interval
[+1.5103, +4.0895], the monthly climatology removed jointly with the
fit over 26 complete years; r1 +0.893 leaves 17.6 effective months of
312, so the honest half width (1.29 mm per year) is nearly five times
the naive one (0.27), and the trend is still distinguishable from
zero. The partition's record receipt carries the identical block to
every digit. Both runs ship as exhibits
(references/retrieval/exhibit-steric-2010.json and
exhibit-steric-record.json) and pass the attester from a fresh clone.

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^sea-level-partition]: computations/ecco-regional-sea-level.md, the signed receipt whose steric term is the anchor
[^ecco-skills-corroboration]: podaac/ecco-skills steric-height acceptance record
[^trend-ci]: computations/ecco-trend-ci.md, the sanctioned trend method and its calibration
