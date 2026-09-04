---
type: Attested Computation
title: "ECCO regional sea level against NASA-SSH altimetry (attested)"
description: "The comparison of the attested regional sea level partition's total series with the NASA-SSH gridded altimetry record over the same box and their consecutive overlap: root-mean-square difference, correlation, anomaly correlation and the trend of the difference, each with a 95 percent sampling interval from the attested uncertainty chain; the observation's version, DOI, grids digest, licence, citation, published uncertainty and a statement of its independence from the estimate in the receipt; a stdlib attester that recomputes every score and refuses a receipt missing any of them."
tags: [ecco, altimetry, nasa-ssh, sea-level, confrontation, observations, attested]
runtime: python
parameters:
  - { name: partition-receipt, type: "a receipt of the attested regional sea level partition, SSH variant, registered region, verified-tree stamp intact", required: true }
  - { name: obs-root, type: "the stamped tree of NASA-SSH V1.1 simple grids (RECORD.json from the record manifest tool)", required: true }
  - { name: min-grids, type: "integer in 1..5, default 4: the least number of grids whose centre falls in a calendar month for the month to enter; 2 admits every month of the record, since eight grids are empty", required: false }
  - { name: period, type: "YYYY-MM:YYYY-MM to narrow the overlap, default the whole consecutive overlap", required: false }
computation: references/computations/ecco_ssh_vs_altimetry.py
executor:
  resource: references/computations/ecco_ssh_vs_altimetry.py
  receipt: [run_id, computation, code_sha256, method_code_sha256, scoring_code_sha256, partition_code_sha256, generated_utc, model, observation, bound_parameters, series, digests, scores, descriptive, caveats]
attester:
  resource: references/attesters/altimetry_confrontation_check.py
generated: { by: claude-code/fable-5, at: 2026-09-03T06:10:00Z }
status: draft
stale_after: 2027-03-03
sources:
  - id: partition
    resource: ecco-regional-sea-level.md
    title: "The attested regional sea level partition whose receipt is the model side"
  - id: nasa-ssh
    resource: ../datasets/nasa-ssh.md
    title: "The observational record: NASA-SSH V1.1 simple grids, its conventions, its uncertainty statement and its independence from the estimate"
  - id: record-note
    resource: ../../../docs/nasa-ssh-record.md
    title: "The record note for release V1.1: the tree, its manifest, the archive checksums, the empty grids, the terms"
  - id: nasa-ssh-doi
    resource: https://doi.org/10.5067/NSREF-SG0V11
    title: "Willis et al. (2026), NASA-SSH: JPL Sea Surface Height Anomalies, Version 1.1, PO.DAAC, Creative Commons Attribution 4.0"
  - id: scoring
    resource: ecco-rapid-amoc-confrontation.md
    title: "The first confrontation, whose scoring functions (mean and correlation intervals, deseasonalizing, digests) this computation imports by path"
  - id: trend-method
    resource: ecco-trend-ci.md
    title: "The sanctioned trend method: the interval chain the scores reuse and the trend of the difference comes from"
  - id: large-scale-domain
    resource: ../validity-domains/ecco-large-scale-statistics.md
    title: "The validity domain that quotes what the estimate was fitted to, which is the source of the independence statement"
  - id: doctrine
    resource: ../conventions/consistency-versus-confrontation.md
    title: "Why the receipt has to carry the observation's identity and the degree of its independence"
---

# ECCO regional sea level against NASA-SSH altimetry (attested)

The bundle's second computation whose other side is an observation,
and the first whose observation the estimate was fitted to. It reads
one receipt of the attested regional sea level partition, the stamped
tree of the NASA-SSH V1.1 simple grids, forms the two monthly series
over the partition's registered box and their consecutive overlap,
scores them, and writes a receipt in which the observation is
identified to the digest of every grid, the scores travel with their
intervals, and the degree of independence is stated in
words.[^partition][^nasa-ssh]

**The observed series.** Every grid in the tree is hashed and read.
For each grid, `ssha` is averaged with cosine-latitude weights over
the half-degree cells whose centres lie in the registered box and
that carry a value; the grid is assigned to the calendar month of its
centre date (the file's `time` variable); the month's value is the
mean of its grids. A month enters when at least `min_grids` grids
fall in it. Eight grids of the 1315 hold no values anywhere
(reference mission outages, listed in the receipt), which leaves four
months of the overlap with two or three grids instead of four or
five; the reference run binds `min_grids` to 2 so that every month
enters and the overlap has no gap, and the receipt carries the grid
count of every month so a reader can see which are thin. The
release identity (`product_version`, the DOI in `id`, short name,
mean sea surface, licence, units, gridding method, along-track DOI)
is read from every file and the run refuses if any grid disagrees
with the first. The tree's RECORD.json stamp is copied into the
receipt; a tree without one is refused.[^record-note][^nasa-ssh-doi]

**The model series.** The cited receipt must be the sanctioned
partition by hash, on a registered region, in the `SSH` variant (the
inverse-barometer corrected one, which is the altimetry's convention
too), on a stamped tree. Its `total_anomaly_m` series over the
overlap, re-centred on the overlap mean and converted to mm, is the
model side; the receipt names the partition receipt by path, hash and
run id and copies its region, box, period, variant and cell count.
Both series are anomalies about their own overlap mean, so no bias is
scored: the model's dynamic height and an anomaly about a mean sea
surface share no level. The overlap must be consecutive and at least
24 months.

**Scores, each with a 95 percent interval.** Root-mean-square
difference: the mean of the squared monthly differences with the
trend method's chain (lag-1 autocorrelation, effective sample size
n (1 - r1) / (1 + r1) capped at n, Student's t on the effective
degrees of freedom), then the square root of the mean and of its
interval ends, clipped at zero. Correlation and anomaly correlation
(each series' own monthly climatology over the overlap removed
first): Fisher's z with the effective sample size from the product of
the two lag-1 autocorrelations. The trend of the difference series by
the sanctioned trend method: this is the score that bears on a trend
claim, and an interval that excludes zero is a trend disagreement of
the stated size. The descriptive block carries each series' standard
deviation and its own trend block, as context and not as scores.
Both series are digested so the attester can tell an edited series
from a recomputed one.[^scoring][^trend-method]

**Independence, stated as a degree.** The receipt's
`observation.independence` block says, in words the attester requires
to be present: that the estimate was fitted to along-track sea
surface height from these same missions (the validity domain quotes
the synopsis); that the observed side is therefore a reprocessing of
measurements the estimate was constrained by; that agreement is in
part the fit and disagreement is a residual the fit could not
remove; what the comparison can show (the model's box-mean sea level
follows the altimetric one to the measured degree, and any departure)
and cannot (that the partition into steric and manometric parts is
right; that the agreement would survive a record the estimate never
saw); and which un-fitted record exists for the box (coastal tide
gauges, a different quantity and a different
computation).[^large-scale-domain][^doctrine]

**Provenance in the receipt, by name.** `observation` carries the
record stamp, data root, grid count and digest with its rule, version,
DOI, short name, title, institution, mean sea surface, licence,
citation, User Guide, variable, units, convention, cadence, first and
last grid and window, the box cell counts, the empty grids, the
published uncertainty block (the product's own statement, and the
published order of a regional altimetry trend uncertainty with its
source and confidence level) and the independence block. `caveats`
state the level, the footprint mismatch, that the intervals are
sampling intervals, and that the record was fitted.

**Attester.** `altimetry_confrontation_check.py`, stdlib plus the
shared trend recompute, run from its own directory. PASS only when
every receipt field and every observational provenance field is
present, the independence statement complete; the receipt's code hash
is the sanctioned comparison, the cited model hash the sanctioned
partition, the scoring hash the first confrontation's file and the
method hash the trend method; the observation is pinned to
NASA_SSH_REF_SIMPLE_GRID_V11 version V1.1, DOI 10.5067/NSREF-SG0V11,
mean sea surface DTU21, `ssha` in m, the Creative Commons Attribution
4.0 licence, the record's manifest hash and the digest of its 1315
grids; the model side is the registered region in the `SSH` variant
on a stamped tree; the series are consecutive months inside 1992-11
through 2017-12, at least 24 of them, every month's grid count within
the bound minimum and five, both series centred, the difference exact,
both digests recomputing; and every score, every interval and every
descriptive block recomputes from the series in the receipt within
1e-9 relative. With the partition receipt on disk (by default beside
the comparison receipt under the cited name) it hashes it against the
citation and re-derives the confronted model values from its
`total_anomaly_m` exactly; with the tree on disk (`--obs-root`) it
re-hashes every grid against the digest.

**Reference run and demonstrations.**
`exhibit-ssh-vs-altimetry-record.json` under references/retrieval/,
from `exhibit-sea-level-record.json` (region us-northeast-coast,
1992-01 through 2017-12) and the stamped tree
`podaac-2026-09-02`: overlap 1993-01:2017-12 (complete years, so the
trend method deseasonalizes over whole cycles), 300 months, PASS with
every grid re-hashed and the model receipt recomputed, run
2026-09-03. The scores are stated in the finding that cites this
run. The attester was demonstrated to FAIL on five doctored variants:
a changed trend of the difference, a different release version, a
changed observed series value with its digest left alone, the
independence statement with a field removed, and a confronted model
value that no longer derives from the partition receipt.

    uv run knowledge/podaac/references/computations/ecco_ssh_vs_altimetry.py \
        --partition-receipt partition.json --obs-root ~/NASA_SSH/podaac-2026-09-02 \
        --period 1993-01:2017-12 --min-grids 2 --receipt comparison.json
    cd knowledge/podaac/references/attesters && \
        uv run altimetry_confrontation_check.py comparison.json \
            --model-receipt partition.json --obs-root ~/NASA_SSH/podaac-2026-09-02

A PASS here says the comparison was done as described and the
observation is the one named. What the agreement can mean, given that
the estimate saw these measurements, is the independence block's
question, and the convention says a confrontation must answer
it.[^doctrine]

[^partition]: Regional sea level partition from ECCO (attested), the model side
[^nasa-ssh]: NASA-SSH simple gridded sea surface height anomaly (observational reference), the dataset concept
[^record-note]: docs/nasa-ssh-record.md, the record note for release V1.1
[^nasa-ssh-doi]: Willis et al. (2026), doi:10.5067/NSREF-SG0V11
[^scoring]: ECCO overturning against RAPID at 26.5N (attested), whose scoring functions are imported by path and named by hash in the receipt
[^trend-method]: Linear trend with an honest interval from a monthly series (attested), the shared chain
[^large-scale-domain]: ECCO v4r4 native monthly fields support large-scale statistics over 1992-2017, the domain that quotes what the estimate fits
[^doctrine]: Consistency versus confrontation, the convention
