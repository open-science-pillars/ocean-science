---
type: Attested Computation
title: "ECCO overturning against RAPID at 26.5N (attested)"
description: "The confrontation of the model's Atlantic overturning with the array's delivered record: calendar-month means of the twelve-hourly ten-day-filtered observed series against the model's mass-balanced streamfunction maximum over their consecutive overlap; bias, root-mean-square difference, correlation and anomaly correlation each with a 95 percent sampling interval from the attested uncertainty chain; the observation's version, DOI, hash, licence, citation and published uncertainty in the receipt; a stdlib attester that recomputes every score and refuses a receipt missing any of them."
tags: [ecco, rapid, amoc, overturning, confrontation, observations, "26n", attested]
runtime: python
parameters:
  - { name: ecco-receipt, type: "a receipt of the attested overturning computation, scope atlantic, convention mass-balanced, verified-tree stamp intact", required: true }
  - { name: rapid-root, type: "the stamped tree of the RAPID release v2024.1a (RECORD.json from the record manifest tool)", required: true }
  - { name: min-valid-fraction, type: "float in (0, 1], default 0.5: the share of a month's twelve-hourly samples that must be valid for the month to enter", required: false }
  - { name: period, type: "YYYY-MM:YYYY-MM to narrow the overlap, default the whole consecutive overlap", required: false }
computation: references/computations/ecco_rapid_amoc_confrontation.py
executor:
  resource: references/computations/ecco_rapid_amoc_confrontation.py
  receipt: [run_id, computation, code_sha256, method_code_sha256, generated_utc, model, observation, bound_parameters, series, digests, scores, descriptive, caveats]
attester:
  resource: references/attesters/rapid_confrontation_check.py
generated: { by: claude-code/fable-5, at: 2026-09-02T18:55:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T02:40:20Z }
status: stable
stale_after: 2027-03-02
sources:
  - id: overturning
    resource: ecco-amoc-26n.md
    title: "The attested overturning computation whose receipt is the model side"
  - id: rapid-record
    resource: ../../../docs/rapid-26n-record.md
    title: "The record note for release v2024.1a: the tree, its manifest, the file hashes, the overlap, the published uncertainty, the terms"
  - id: rapid-doi
    resource: https://doi.org/10.5285/48d0bf43-0598-ceb2-e063-7086abc062f1
    title: "Moat et al. (2026), the RAPID-MOCHA-WBTS 26N overturning release v2024.1a, BODC, Open Government Licence v3"
  - id: trend-method
    resource: ecco-trend-ci.md
    title: "The sanctioned trend method: the interval chain (lag-1 autocorrelation, effective sample size capped at n, Student's t) the scores reuse and the descriptive trends come from"
  - id: bretherton-1999
    resource: https://doi.org/10.1175/1520-0442(1999)012%3C1990:TENOSD%3E2.0.CO;2
    title: "Bretherton et al. 1999, The effective number of spatial degrees of freedom of a time-varying field, J. Climate 12, 1990-2009: the effective sample size for a correlation from the product of the two lag-1 autocorrelations"
  - id: recipe
    resource: ../recipes/ecco-rapid-amoc-26n.md
    title: "The recipe that states the colocation, the representativeness gap, the metric set and the measured scores"
  - id: doctrine
    resource: ../conventions/consistency-versus-confrontation.md
    title: "Why this computation's PASS means something the bundle's internal anchors cannot"
---

# ECCO overturning against RAPID at 26.5N (attested)

The first computation in the bundle whose other side is an
observation. It reads one receipt of the attested overturning
computation and the stamped tree of the array's release, forms the
two monthly series over their consecutive overlap, scores them, and
writes a receipt in which the observation is identified to the file
hash and the scores travel with their intervals.[^overturning]

**The observed series.** `moc_mar_hc10` from `moc_transports.nc`:
twelve-hourly, the programme's ten-day low-pass already applied. The
file is hashed live and its `version` and `DOI` attributes are read
from the file, never from a web page; the tree's RECORD.json stamp
(record name, manifest hash, verification time) is copied into the
receipt, and a tree without one is refused. Each calendar month's
valid samples are averaged; a month enters when its valid share is
at least `min_valid_fraction` (0.5 by default, which admits April
2004 with 48 of 60), and the receipt records the valid and expected
counts per month and the months dropped.[^rapid-record][^rapid-doi]

**The model series.** The cited receipt must be the sanctioned
overturning computation by hash, scope `atlantic`, convention
`mass-balanced`, on a stamped tree; the confrontation refuses
anything else, and refuses an overlap shorter than 24 months or with
a gap. The receipt names the model receipt by path, hash and run id
and copies its section identity (mask hash, face count, period).

**Scores, each with a 95 percent interval.** Bias (mean of model
minus observed) and mean square difference use the trend method's
chain, the lag-1 autocorrelation of the differences giving an
effective sample size n (1 - r1) / (1 + r1) capped at n and Student's
t on the effective degrees of freedom; the root-mean-square
difference is the square root of the mean square difference and of
its interval ends, clipped at zero.[^trend-method] Correlation and
anomaly correlation (each series' own monthly climatology over the
overlap removed first) use Fisher's z with the effective sample size
from the product of the two lag-1 autocorrelations.[^bretherton-1999]
No interval is stated below one effective degree of freedom. The
descriptive block carries each series' mean, standard deviation and
the trend method's full interval block. Both series are digested
(sha256 of the months and values) so the attester can tell an edited
series from a recomputed one.

**Provenance in the receipt, by name.** `observation` carries the
record name, data root, file, file hash, version, DOI, creation date,
citation, acknowledgement, licence, institution, variable, units,
cadence, filter, sample count, first and last sample, and the
published RMS uncertainty (1.5 Sv on ten-day values, 0.9 Sv on
annual values, McCarthy et al. 2015 as the README reproduces it).
`caveats` state the representativeness gap, that the intervals are
sampling intervals, and that the array's transports are not
assimilated by the estimate.

**Attester.** `rapid_confrontation_check.py`, stdlib plus the shared
trend recompute, run from its own directory. PASS only when every
receipt field and every observational provenance field is present
and non-empty; the receipt's code hash is the sanctioned confrontation
and the cited model hash the sanctioned overturning; the observation
is pinned to version v2024.1a, its DOI, the record's manifest hash
and the transport file's hash, in Sverdrups, under a licence that
names the Open Government Licence, with the RMS figures present; the
model side is scope atlantic and convention mass-balanced on a
stamped tree; the series are consecutive months inside 2004-04
through 2017-12, at least 24 of them, every month's valid share at or
above the bound fraction, both digests recomputing; and every score,
every interval and every descriptive trend block recomputes from the
series in the receipt within 1e-9 relative. With the model receipt on
disk (by default beside the confrontation receipt under the cited
name) it also hashes it against the citation and recomputes the
primary series, the anchor and the sabotage flags as the overturning
concept describes.

**Reference run and demonstrations.**
`exhibit-rapid-amoc-26n-confrontation.json` under
references/retrieval/, from `exhibit-amoc-26n-record.json` and the
stamped tree `rapid.ac.uk-2026-09-02`: overlap 2004-04:2017-12, 165
months, PASS, run 2026-09-02. The scores are stated in the
recipe.[^recipe] The attester was demonstrated to FAIL on nine
doctored variants: a changed bias, a changed RMSD, a changed interval
bound, a changed series value with its digest left alone, the DOI
removed, the licence removed, an unstamped observation tree, a
different release version, and a doctored model receipt.

    uv run knowledge/podaac/references/computations/ecco_rapid_amoc_confrontation.py \
        --ecco-receipt amoc.json --rapid-root ~/RAPID_26N/rapid.ac.uk-2026-09-02 \
        --receipt confrontation.json
    cd knowledge/podaac/references/attesters && \
        uv run rapid_confrontation_check.py confrontation.json --model-receipt amoc.json

A PASS here is a different kind of statement from a PASS on the
bundle's budget closures and cross-computation anchors, and the
convention beside the recipe says which kind.[^doctrine]

[^overturning]: Atlantic overturning at 26.5N from ECCO v4r4 (attested), the model side
[^rapid-record]: docs/rapid-26n-record.md, the record note for release v2024.1a
[^rapid-doi]: Moat et al. (2026), doi:10.5285/48d0bf43-0598-ceb2-e063-7086abc062f1
[^trend-method]: Linear trend with an honest interval from a monthly series (attested), the shared chain
[^bretherton-1999]: Bretherton et al. 1999, J. Climate 12, 1990-2009, equation for the effective sample size of a correlation between two AR(1) series
[^recipe]: ECCO overturning at 26.5N confronted with the RAPID array, the recipe
[^doctrine]: Consistency versus confrontation, the convention
