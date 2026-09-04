---
type: recipe
title: "ECCO overturning at 26.5N confronted with the RAPID array"
description: "How the model's Atlantic overturning at the array latitude is placed beside the observed one: calendar-month colocation of the array's ten-day-filtered twelve-hourly series against the model's monthly-mean streamfunction maximum under the array's own zero-net convention, the representativeness gap named in both directions, four metrics with what each is sensitive to, and the measured scores with sampling intervals over 2004-04 through 2017-12: bias -3.23 Sv, RMSD 3.84 Sv, correlation +0.77, anomaly correlation +0.79."
tags: [ecco, rapid, amoc, overturning, confrontation, observations, "26n", recipe]
inputs: "The verified ECCO v4r4 record tree (the mass-weighted volume flux collection and the native llc90 geometry, RECORD.json stamp intact) and the RAPID-MOCHA-WBTS 26N overturning release v2024.1a retrieved, hashed, manifested and stamped in a tree outside the repository, as the record note describes"
expected: "Over 2004-04 through 2017-12, 165 calendar months (measured 2026-09-02): model mass-balanced overturning mean 13.96 Sv (sd 2.52), observed 17.20 Sv (sd 3.28); bias -3.23 Sv, 95 percent interval [-3.75, -2.72]; RMSD 3.84 Sv [3.33, 4.29], of which 2.07 Sv is not the bias; correlation +0.77 [+0.68, +0.84]; anomaly correlation +0.79 [+0.70, +0.85]; trends -0.14 and -0.11 Sv per year, neither distinguishable from zero"
expected_uncertainty: "The intervals are sampling intervals under a lag-1 autocorrelation model (the bias keeps 65 effective months of 165) and carry no measurement error: the array's published RMS uncertainty is 1.5 Sv on ten-day values and 0.9 Sv on annual values, and the model's own error is not quantified here. Colocation choices move the model mean by up to about 1 Sv (the streamfunction convention), 0.21 Sv (one grid row), 0.15 Sv (the Gulf of Mexico) and the observed mean by 0.12 Sv (maximum of the monthly mean instead of mean of the maxima); none of them reaches the bias"
generated: { by: claude-code/fable-5, at: 2026-09-02T18:40:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T02:40:20Z }
status: stable
stale_after: 2027-03-02
sources:
  - id: overturning-computation
    resource: ../computations/ecco-amoc-26n.md
    title: "The attested overturning computation whose receipt supplies the model series: Atlantic-only section faces, three conventions, the ecco_v4_py anchor, the mutation evidence"
  - id: confrontation-computation
    resource: ../computations/ecco-rapid-amoc-confrontation.md
    title: "The attested confrontation: the colocation, the four scores with intervals, the observational provenance fields, and the attester that recomputes every score"
  - id: rapid-dataset
    resource: ../datasets/rapid-mocha.md
    title: "The RAPID-MOCHA dataset concept: what the array is, its products and their versions"
  - id: rapid-record
    resource: ../../../docs/rapid-26n-record.md
    title: "The record note for release v2024.1a: files, hashes, overlap, the programme's uncertainty table, the processing events inside the overlap, the terms of use"
  - id: rapid-doi
    resource: https://doi.org/10.5285/48d0bf43-0598-ceb2-e063-7086abc062f1
    title: "Moat et al. (2026), Atlantic meridional overturning circulation observed by the RAPID-MOCHA-WBTS array at 26N from 2004 to 2024 (v2024.1a), NERC EDS British Oceanographic Data Centre NOC"
  - id: mccarthy-2015
    resource: https://doi.org/10.1016/j.pocean.2014.10.006
    title: "McCarthy et al. 2015, Measuring the Atlantic meridional overturning circulation at 26N, Progress in Oceanography 130, 91-111: the array's methodology paper (components, filter, uncertainty table)"
  - id: cunningham-2007
    resource: https://doi.org/10.1126/science.1141304
    title: "Cunningham et al. 2007, Temporal variability of the Atlantic meridional overturning circulation at 26.5N, Science 317, 935-938: the array's first year and its zero-net compensation convention"
  - id: kanzow-2007
    resource: https://doi.org/10.1126/science.1141293
    title: "Kanzow et al. 2007, Observed flow compensation associated with the MOC at 26.5N in the Atlantic, Science 317, 938-941: the mass-balance check behind the array's zero-net constraint"
  - id: v4r4-synopsis
    resource: https://doi.org/10.5281/zenodo.4533349
    title: "ECCO Consortium, Synopsis of the ECCO Central Production Global Ocean and Sea-Ice State Estimate, Version 4 Release 4 (2021): Table 2, the observations the estimate is constrained by"
  - id: consistency-doctrine
    resource: ../conventions/consistency-versus-confrontation.md
    title: "The convention that separates what this recipe shows from what the bundle's internal anchors show"
  - id: trend-method
    resource: ../computations/ecco-trend-ci.md
    title: "The sanctioned trend method behind the descriptive trends and the interval chain the scores reuse"
  - id: mht-recipe
    resource: ecco-mht-26n.md
    title: "The heat transport recipe at the same latitude, whose comparison to the array is a quoted spread, not a scored confrontation"
  - id: colocation-derivation
    resource: ../references/derivations/rapid_colocation_checks.py
    title: "The derivation that measured the observed-side colocation facts (series against profile maximum, maximum of the monthly mean against mean of the maxima, the ten-day product); output beside it"
  - id: western-boundary-derivation
    resource: ../references/derivations/ecco_western_boundary_26n.py
    title: "The derivation that measured the model's western boundary faces against the array's cable, Ekman and mid-ocean components; output beside it"
---

# ECCO overturning at 26.5N confronted with the RAPID array

This is the one comparison in the bundle where the other side is not
the model. Every other check here, budget closure, cross-computation
anchors, agreement with ecco_v4_py, shows that a method agrees with
itself; this recipe places the model's overturning at the array's
latitude beside what the array measured, at a fixed version of the
observed record, with the colocation stated, the representativeness
gap named in both directions, and four scores that carry their
intervals. What such a comparison supports, and what internal
consistency never can, is the doctrine note beside this
recipe.[^consistency-doctrine] The split is the bundle's usual one:
two attested computations do the arithmetic and write receipts, the
attester recomputes every score from the series in the receipt, this
recipe states the choices and the numbers, and how to diagnose a
disagreement stays in the skills.

## Colocation

**The observed quantity** is `moc_mar_hc10` in `moc_transports.nc`
of release v2024.1a: the twelve-hourly overturning transport, the sum
of the Florida Straits cable, the Ekman transport and the upper
mid-ocean transport with the programme's ten-day low-pass applied and
the first and last five days of the record set absent. McCarthy et
al. 2015 describe the components and the filter; the record note
lists the file, its hash, and the twenty absent
samples.[^mccarthy-2015][^rapid-record][^rapid-doi]

**The monthly mean** is the calendar-month mean of every valid
twelve-hourly sample. A month enters when at least half of its
samples are valid (the bound parameter `min_valid_fraction` 0.5),
which admits April 2004 with 48 valid samples of the 60 a full April
holds and makes the overlap 2004-04 through 2017-12, 165 consecutive
months. The model side is a monthly mean of mass-weighted velocities,
so a calendar month on both sides is the closest the two records
come; the array's own annual values run April to April and are not
used here.

**The model quantity** is the maximum over depth of the Atlantic-only
zonally integrated transport across the llc90 face row nearest 26.5N,
accumulated from the surface after the net section transport is
removed in proportion to each level's open area: the mass-balanced
convention. It is chosen because it is the array's: the array closes
its section by spreading the compensation for the cable plus Ekman
plus mid-ocean sum uniformly over the section, the constraint
Cunningham et al. 2007 adopted and Kanzow et al. 2007 tested against
the bottom pressure recorders.[^cunningham-2007][^kanzow-2007] The
surface-down and bottom-up conventions travel in the receipt beside
it: over the full model record they sit 0.22 Sv below and 0.97 Sv
above the primary, so the convention alone moves the mean by up to a
third of the bias measured below, and a comparison that does not name
its convention has not stated its number.[^overturning-computation]

**Scope and path.** Atlantic by basin code, the Gulf of Mexico
excluded because the array's line runs from Florida to Africa; the
section is the 66 stored faces between longitudes 80.5W and 14.5W
along the grid's face row at 26.1N (the cell rows at 25.7N and 26.6N
on either side of it), the face row nearest 26.5N on the two tiles
that carry the latitude. Both choices are measured in every receipt
as disclosures: including the Gulf moves the model mean by +0.15 Sv
(at most 0.97 Sv in a month), and moving the path to the next face
row north, at 27.0N, moves it by 0.21 Sv (at most
0.93).[^overturning-computation]

**Two questions the record note left open, now
measured.**[^colocation-derivation] First, the ten-day product's
`amoc_depth` is not a subsample of the twelve-hourly series but a
ten-day average of it: at coinciding times the two differ by up to
4.85 Sv, and their monthly means differ by up to 1.90 Sv (mean
-0.09). This recipe uses the twelve-hourly series; a comparison built
on the ten-day product is a different comparison and must say so.
Second, the observed series is not the maximum of the distributed
streamfunction profile sample by sample, because the profile is
delivered unfiltered (the two differ by up to 14 Sv on a
twelve-hourly sample); low-passing the profile with a sixth-order
zero-phase Butterworth at one cycle per ten days and then taking its
maximum reproduces the series to a standard deviation of 0.15 Sv,
which is how the recipe knows what the series is. From that profile
the max-of-mean asymmetry of the colocation is measured: the model
value is by construction the maximum of a monthly-mean field, while
the observed value is the mean of twelve-hourly maxima, and taking
the maximum of the observed monthly-mean profile instead lowers the
observed value by 0.12 Sv on average (at most 0.53 Sv in a month).
The asymmetry is real, it favours the model, and it is small against
the bias.

## Representativeness, in both directions

**What the array measures that the grid does not resolve.** The
Florida Straits. The cable measures 31.71 Sv (monthly sd 2.12 Sv over
the overlap) through a channel about 80 km wide and 800 m deep
between Florida and the Bahamas. The llc90 grid has no strait at this
latitude: its four westernmost Atlantic faces, at 80.5W, 79.5W, 78.5W
and 77.5W, are all 861 m deep, one smoothed shelf standing in for
the Straits and the Bahama Banks together and closed by a land cell
at 76.5W, and they carry 27.08 Sv northward between them (sd
1.29 Sv, monthly correlation 0.50 with the cable). Whatever the model
routes over this shelf is its Florida Current and its Antilles
Current in one, and the southward return begins immediately east of
the land cell (the next four faces, 4.8 to 5.2 km deep, carry
11.7 Sv southward over their full depth).[^western-boundary-derivation] The Ekman
transport: the array's is computed from reanalysis wind stress
(3.70 Sv mean, sd 2.21 over the overlap), the model's is whatever its
own estimated wind stress drives. The interior: the array's upper
mid-ocean transport (-18.14 Sv mean, sd 2.95) is geostrophy between
moorings hundreds of kilometres apart plus direct current
measurements in the western boundary wedge; the model's is a resolved
one-degree velocity field with parameterized eddies. The depth
structure: the observed monthly-mean streamfunction peaks at 1009 m
on average (median 1031 m, range 615 to 1169 m), the model's at
880 m over its record, a cell about 130 m shallower. And the
observed record carries its own history: mooring losses and
instrument failures inside the overlap are filled by the programme's
methods, listed by date in the record note.[^rapid-record]

**What the model resolves that the array does not.** The model's
transport is the full velocity field across the section, every level
and every cell, mass-conserving to round-off, with nothing assumed
about how the net closes; the array's zero-net closure is an
assumption applied uniformly with depth, justified to the array's
error by Kanzow et al. 2007 but not measured every month. The model's
monthly mean is a true time average; the observed monthly mean is an
average of an already ten-day-filtered series, so variability between
ten days and a month is suppressed before the calendar month is
formed (the twelve-hourly series has sd 4.40 Sv against 4.83 Sv for
the unfiltered profile maximum). The model carries no measurement
error, while the array's published RMS uncertainty, 1.5 Sv on
ten-day values and 0.9 Sv on annual values, and the README's
statement that these do not reduce substantially in annual averages,
set the floor below which no bias or RMSD is distinguishable from
measurement.[^mccarthy-2015][^rapid-record]

**Independence, stated rather than assumed.** No transport, cable or
Ekman series enters the ECCO v4r4 estimate: Table 2 of the release
synopsis lists altimetry, global mean sea level, temperature and
salinity profiles (Argo, XBT, CTD, marine mammals, gliders, ice
tethered profilers and moorings), SST, SSS, sea ice concentration,
GRACE bottom pressure, a climatology and a mean dynamic
topography.[^v4r4-synopsis] Whether hydrography from the array's own
moorings is among the mooring profiles the table lists is not stated
there; if it is, the boundary density gradients the array's
geostrophic estimate rests on partly constrained the model's, and
the two series are then independent in their transports but not in
everything beneath them. The recipe calls this a confrontation on
the strength of the transports; the residual entanglement is named
here so nobody has to discover it.

## The metric set and what each is sensitive to

All four scores are computed on the two monthly series over the
overlap, model minus observed where a sign
applies.[^confrontation-computation]

- **Bias**, the mean difference. It measures the offset and nothing
  else; it is sensitive to the streamfunction convention (up to
  1 Sv), the path (0.21 Sv), the scope (0.15 Sv) and the max-of-mean
  asymmetry (0.12 Sv), and above all to the western boundary
  transport the grid cannot carry; it is insensitive to phase and
  amplitude.
- **Root-mean-square difference.** The bias plus the variability
  mismatch: RMSD squared minus bias squared is the centred part,
  2.07 Sv here against a bias of 3.23 Sv, so the offset carries most
  of it and the rest is amplitude and timing (the model's sd is
  2.52 Sv against the observed 3.28 Sv). Sensitive to everything the
  bias is, and to amplitude and phase besides.
- **Correlation** of the two monthly series. Phase agreement
  including the seasonal cycle the two share (a seasonal range of
  3.7 Sv in the model and 4.8 Sv observed, both lowest in April and
  highest in November or December); insensitive to bias and to
  amplitude.
- **Anomaly correlation**, each series' own monthly climatology over
  the overlap removed first. The same agreement without the seasonal
  cycle. That it is not lower than the plain correlation here says
  the agreement is not carried by the seasonal cycle: the interannual
  and intra-seasonal variability is shared (annual means 2005 through
  2017 correlate at 0.79; the 2009 to 2010 minimum is in both, 2010
  annual means 11.97 and 15.26 Sv; the lowest month in both records
  is March 2013, 4.71 and 6.64 Sv).
- **Trends**, descriptive only, from the sanctioned trend method with
  its interval; over 165 months the method removes no climatology
  (it wants complete years) and neither trend is distinguishable from
  zero.[^trend-method]

The intervals are 95 percent sampling intervals. The bias and the
mean square difference use Student's t on an effective sample size
n (1 - r1) / (1 + r1) from the lag-1 autocorrelation of the
differences, never above n, exactly the trend method's chain; the
correlations use Fisher's z with the effective sample size from the
product of the two series' lag-1 autocorrelations. They say how much
the scores could move under resampling of the overlap; they say
nothing about the array's measurement error or the model's, and a
comparison that quotes them as total uncertainty has misread them.

## The measured scores

Overlap 2004-04 through 2017-12, 165 months, measured 2026-09-02 on
the receipts named below; the attester recomputes each one from the
series in the receipt and fails on 1e-9 relative.

| score | value | 95 percent interval | effective months |
| --- | --- | --- | --- |
| bias, model minus observed | -3.2322 Sv | [-3.7484, -2.7160] | 64.7 of 165 |
| root-mean-square difference | 3.8394 Sv | [3.3268, 4.2911] | 65.6 |
| correlation | +0.7729 | [+0.6818, +0.8404] | 106.4 |
| anomaly correlation | +0.7850 | [+0.7045, +0.8455] | 121.4 |

Model mean 13.9644 Sv (sd 2.5201); observed 17.1966 Sv (sd 3.2753).
Trends -0.1443 [-0.2946, +0.0061] and -0.1072 [-0.3245, +0.1100] Sv
per year. The largest single-month differences are -8.47 Sv in
September 2004 and +2.67 Sv in September 2009.

## What the scores support

The acceptable deviation falls out of the comparison, not out of
anyone's judgment. A recomputation of the model's overturning at this
latitude that lands within 1e-4 Sv of the receipt's series
reproduces the bundle, and one that does not has changed a choice
this recipe names. The statement "ECCO v4r4 reproduces the observed
overturning at 26.5N to within 1 Sv" is false by this measurement:
the bias interval excludes every value above -2.72 Sv. The statement
"ECCO v4r4 carries the observed variability of the overturning" is
supported at the level the numbers give it: the phase, at three
quarters of the amplitude, with the seasonal cycle and the 2009 to
2010 event both present. A reader who needs the observed overturning
takes it from the array, at its version and under its terms; a reader
who needs its variability in a dynamically closed field finds it
here, 3.2 Sv low. What produces the bias is a question for the skills
and for a later confrontation, not for this recipe; the recipe's job
is to have measured it and to keep the choices that could move it
in view.[^consistency-doctrine] The heat transport recipe at the
same latitude quotes the array as a published spread; this one
scores against the delivered record, and the two are not the same
kind of statement.[^mht-recipe]

## Run it

From the repository root, the model series over its whole record
(the confrontation selects the overlap; 2010 must be inside so the
anchor is checked), then the confrontation, then the attester from
its own directory:

    uv run knowledge/podaac/references/computations/ecco_amoc_26n.py \
        --period 1992-01:2017-12 --scope atlantic \
        --data-root ~/ECCO_V4r4_record --receipt amoc.json

    uv run knowledge/podaac/references/computations/ecco_rapid_amoc_confrontation.py \
        --ecco-receipt amoc.json --rapid-root ~/RAPID_26N/rapid.ac.uk-2026-09-02 \
        --receipt confrontation.json

    cd knowledge/podaac/references/attesters && \
        uv run rapid_confrontation_check.py confrontation.json \
            --model-receipt amoc.json

The reference receipts are `references/retrieval/exhibit-amoc-26n-record.json`
and `references/retrieval/exhibit-rapid-amoc-26n-confrontation.json`;
the attester passes on the pair and fails on each of the nine
doctored variants the confrontation concept
lists.[^confrontation-computation]

## Terms

The observed record is cited at its fixed version and DOI, retrieved
under the Open Government Licence v3, and never redistributed by this
repository: the data tree stays outside it, and only the manifest,
the verification report and the receipts are here. Any use of the
numbers above carries the citation the release asks for, Moat et al.
(2026), and the programme's acknowledgement, both reproduced in the
record note and in every confrontation
receipt.[^rapid-doi][^rapid-record][^rapid-dataset]

[^consistency-doctrine]: Consistency versus confrontation, the convention beside this recipe
[^mccarthy-2015]: McCarthy et al. 2015, Prog. Oceanogr. 130, 91-111, doi:10.1016/j.pocean.2014.10.006
[^rapid-record]: docs/rapid-26n-record.md, the record note for release v2024.1a
[^rapid-doi]: Moat et al. (2026), doi:10.5285/48d0bf43-0598-ceb2-e063-7086abc062f1
[^cunningham-2007]: Cunningham et al. 2007, Science 317, 935-938, doi:10.1126/science.1141304
[^kanzow-2007]: Kanzow et al. 2007, Science 317, 938-941, doi:10.1126/science.1141293
[^overturning-computation]: The attested overturning computation, computations/ecco-amoc-26n.md
[^colocation-derivation]: references/derivations/rapid_colocation_checks.py and its output rapid-colocation-checks.json, run 2026-09-02
[^western-boundary-derivation]: references/derivations/ecco_western_boundary_26n.py and its output ecco-western-boundary-26n.json, run 2026-09-02
[^v4r4-synopsis]: ECCO Consortium 2021, V4r4 Synopsis, Table 2, doi:10.5281/zenodo.4533349, fetched and read 2026-09-02
[^confrontation-computation]: The attested confrontation, computations/ecco-rapid-amoc-confrontation.md
[^trend-method]: The sanctioned trend method, computations/ecco-trend-ci.md
[^mht-recipe]: Meridional heat transport at 26.5N, recipes/ecco-mht-26n.md
[^rapid-dataset]: RAPID-MOCHA transports at 26.5N, datasets/rapid-mocha.md
