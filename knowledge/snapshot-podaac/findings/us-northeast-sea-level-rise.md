---
type: finding
title: "Sea level rise off the US northeast coast in ECCO v4r4, partitioned and confronted"
description: "In the ECCO v4r4 ocean state estimate, sea level averaged over the box from 35 to 45 degrees north and 75 to 65 degrees west rose at 5.25 mm/yr over 1992 through 2017 (95 percent interval 4.06 to 6.43), of which 2.45 mm/yr is water added to the column and 2.80 mm/yr is expansion of the water in it; over 1993 through 2017 the estimate's rise exceeds the NASA-SSH altimetry record's in the same box by 1.99 mm/yr (1.39 to 2.59), a disagreement the estimate's own fit to altimetry did not close."
tags: [finding, ecco, sea-level, steric, manometric, altimetry, nasa-ssh, us-northeast-coast, trend, confrontation]
generated: { by: claude-code/fable-5, at: 2026-09-03T06:30:00Z }
question: "Over 1992 through 2017, how fast did sea level rise in the ECCO v4r4 estimate over the box from 35 to 45 degrees north and 75 to 65 degrees west, and how did that rise divide between water added to the column and expansion of the water already in it?"
claim:
  statement: "Over 1992 through 2017 the estimate's sea level in the box rose at 5.25 mm/yr (95 percent interval 4.06 to 6.43), 2.45 mm/yr of it manometric (95 percent interval 2.17 to 2.74) and 2.80 mm/yr steric (95 percent interval 1.51 to 4.09), and over 1993 through 2017 that rise exceeds the NASA-SSH altimetry record's in the same box by 1.99 mm/yr (95 percent interval 1.39 to 2.59)."
  value: 5.2452
  interval: [4.0623, 6.4281]
  confidence: 0.95
  units: mm/year
  from:
    receipt: /references/retrieval/exhibit-sea-level-record.json
    value: trend_total_interval.trend
    interval: [trend_total_interval.ci_low, trend_total_interval.ci_high]
    confidence: trend_total_interval.confidence
computations:
  - concept: /computations/ecco-regional-sea-level.md
    receipt: /references/retrieval/exhibit-sea-level-record.json
  - concept: /computations/ecco-ssh-vs-altimetry.md
    receipt: /references/retrieval/exhibit-ssh-vs-altimetry-record.json
validity:
  declaration: {product: ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4, claim: trend, region: "35,45,-75,-65", period: "1992-01:2017-12"}
  verdict: UNADJUDICATED
  receipt: /references/retrieval/fitness-sea-level-record.json
  governing: []
confrontation:
  status: confronted
  concept: /computations/ecco-ssh-vs-altimetry.md
  receipt: /references/retrieval/exhibit-ssh-vs-altimetry-record.json
  observation: /datasets/nasa-ssh.md
limitations:
  - "The claim holds for the area mean over the box from 35 to 45 degrees north and 75 to 65 degrees west, and for the ECCO v4r4 estimate; nothing is stated for any point inside the box, for the coast itself, or for the ocean."
  - "The partition is a statement about the estimate: no observation in this finding bears on how the rise divides between the manometric and steric parts, and the confrontation shows the estimate's total rise is faster than the observed one."
  - "The altimetry the estimate is confronted with was among the observations the estimate was fitted to, so the agreement in the monthly variability is in part the fit; only the disagreement in the trend is a residual the fit could not remove."
  - "The estimate is Boussinesq: it conserves volume rather than mass with a fixed reference density of 1029 kg per cubic metre, and its global-mean sea level is adjusted by a spatially uniform correction, so the steric part of a regional rise carries a global term that is not local expansion."
  - "The box straddles the Gulf Stream and the continental shelf, which the estimate's one-degree grid class and the altimetry's half-degree smoothed grids both fail to resolve; the validity domain that would govern this claim is unsigned, so no steward has adjudicated whether a trend at this scale is within the estimate's fitness."
  - "The intervals are sampling intervals from each series' own autocorrelation (the total trend rests on an effective sample of 30.7 months out of 312, the steric trend on 17.6); they do not include the altimetry's measurement uncertainty, which the product does not publish for its grids, and the published order of a regional altimetry trend uncertainty (0.83 mm/yr at the 90 percent level, for a different product) is smaller than the trend disagreement."
  - "Four of the 300 confronted months are built from two or three weekly grids instead of four or five because eight grids in the record are empty; the receipt lists the grid count of every month."
context:
  - {value: 1029, meaning: "the Boussinesq reference density of the ECCO v4 configuration, kg per cubic metre", source: v4r4-config}
  - {value: 175, meaning: "the Gaussian scale of the NASA-SSH gridding, km", source: nasa-ssh-record}
  - {value: 600, meaning: "the radius within which passes contribute to a NASA-SSH grid cell, km", source: nasa-ssh-record}
status: draft
stale_after: 2027-03-03
sources:
  - id: partition
    resource: ../computations/ecco-regional-sea-level.md
    title: "Regional sea level partition from ECCO (attested): the sanctioned computation, its receipt fields and its attester"
  - id: trend-method
    resource: ../computations/ecco-trend-ci.md
    title: "Linear trend with an honest interval from a monthly series (attested): the interval chain every trend and score in this finding uses"
  - id: comparison
    resource: ../computations/ecco-ssh-vs-altimetry.md
    title: "ECCO regional sea level against NASA-SSH altimetry (attested): the confrontation, its scores and its independence statement"
  - id: nasa-ssh
    resource: ../datasets/nasa-ssh.md
    title: "NASA-SSH simple gridded sea surface height anomaly (observational reference): the record, its conventions and its uncertainty statement"
  - id: nasa-ssh-record
    resource: ../../../docs/nasa-ssh-record.md
    title: "The NASA-SSH record note: the tree, the manifest, the gridding parameters read from the files, the empty grids"
  - id: ecco-v4r4
    resource: ../datasets/ecco-v4r4.md
    title: "ECCO v4 Release 4 ocean state estimate: what the product is"
  - id: large-scale-domain
    resource: ../validity-domains/ecco-large-scale-statistics.md
    title: "ECCO v4r4 native monthly fields support large-scale statistics over 1992-2017 (validity domain, unsigned): the scope the estimate is fit for, and what it was fitted to"
  - id: doctrine
    resource: ../conventions/consistency-versus-confrontation.md
    title: "Consistency versus confrontation: the convention that separates a method agreeing with itself from a method agreeing with the world"
  - id: v4r4-config
    resource: https://github.com/ECCO-GROUP/ECCO-v4-Configurations/blob/master/ECCOv4%20Release%204/namelist/data
    title: "The ECCO v4 Release 4 model configuration namelist (rhoConst = 1029), ECCO-GROUP/ECCO-v4-Configurations"
  - id: prandi-2021
    resource: https://doi.org/10.1038/s41597-020-00786-7
    title: "Prandi et al. 2021, Local sea level trends, accelerations and uncertainties over 1993-2019, Scientific Data 8, 1"
---

# Question

Over 1992 through 2017, how fast did sea level rise in the ECCO v4r4
estimate over the box from 35 to 45 degrees north and 75 to 65
degrees west, and how did that rise divide between water added to
the column and expansion of the water already in it?

**For a reader new to this.** ECCO v4r4 is NASA's ocean state
estimate: a global ocean model fitted, by adjusting its uncertain
inputs, to most of the ocean observations of 1992 through 2017 until
it agrees with them about as well as their errors allow. It is a
synthesis, not an observation, and every number in this finding is a
statement about that synthesis unless it says otherwise.[^ecco-v4r4]
The box is a rectangle of ocean off the northeast coast of the
United States, from Cape Hatteras to the Gulf of Maine, chosen
because sea level there rises faster than the global average and the
reasons are argued about. A regional rise in sea level can come from
two places: more water in the column (the manometric part, which the
model measures as the pressure on the sea floor) or the same water
taking more room because it warmed or freshened (the steric part).
The estimate carries both, so they can be separated, and the two
parts should add up to the whole. Every number below was produced by
a sanctioned program whose output, the receipt, is stored in this
repository beside the program's hash, and a separate program, the
attester, has recomputed every trend, interval and score from the
receipt and passed. The receipts are the evidence; this page is what
they show.

# Claim

Over 1992 through 2017 the estimate's sea level in the box rose at
5.25 mm/yr (95 percent interval 4.06 to 6.43), 2.45 mm/yr of it
manometric (95 percent interval 2.17 to 2.74) and 2.80 mm/yr steric
(95 percent interval 1.51 to 4.09), and over 1993 through 2017 that
rise exceeds the NASA-SSH altimetry record's in the same box by 1.99
mm/yr (95 percent interval 1.39 to 2.59).

Three things are being claimed, in decreasing order of what supports
them. The total rate is a property of the estimate, attested. The
partition of that rate is a property of the estimate, attested, and
no observation here bears on it. The excess of the estimate's rate
over the altimetric one is a measured disagreement between the
estimate and an observational record, with its own interval, which
the estimate's fit to that same record did not remove.

# Evidence

**The partition receipt** (`exhibit-sea-level-record.json`, written
by the sanctioned regional sea level partition over the verified
ECCO v4r4 science record of 4056 granules). The computation averages
three monthly fields over the wet cells of the box on the model's
native grid, 102 cells, for all 312 months: the inverse-barometer
corrected sea surface height (the total), ocean bottom pressure
expressed as an equivalent water height (the manometric part), and
the depth integral of the model's own density anomaly divided by the
reference density (the steric part, computed independently of the
other two). The three monthly anomaly series are in the receipt.
Their residual, total minus manometric minus steric, is below a
millimetre in every month, which is the internal check that the
three fields were read consistently; it says nothing about the
ocean. Each series' trend comes from the bundle's sanctioned trend
method: a linear fit after removing the monthly climatology, with
the interval widened for the series' own persistence (the lag-1
autocorrelation of the residuals sets an effective sample size, and
Student's t is taken on that). The total trend is 5.25 mm/yr with
interval 4.06 to 6.43 (residual autocorrelation 0.82, effective
sample 30.7 months of 312); the manometric trend 2.45 with interval
2.17 to 2.74 (autocorrelation 0.51, effective sample 100.3); the
steric trend 2.80 with interval 1.51 to 4.09 (autocorrelation 0.89,
effective sample 17.6). The steric interval is the widest because
the steric series is the most persistent. The partition attester
recomputed every trend, interval and residual from the series in
the receipt and passed.[^partition][^trend-method]

**The comparison receipt** (`exhibit-ssh-vs-altimetry-record.json`,
written by the sanctioned comparison over the partition receipt and
the verified NASA-SSH V1.1 tree of 1315 weekly grids). The model
side is the partition receipt's total series over 1993 through 2017,
300 months, re-centred on that span. The observed side is the
altimetric sea surface height anomaly averaged over the same box
from each weekly grid, the grids of each calendar month averaged
together. Both are anomalies about their own mean, so their level is
not compared, only their variability and their trend. The monthly
variability agrees closely: correlation 0.91 (95 percent interval
0.84 to 0.95), with the seasonal cycle removed 0.82 (0.69 to 0.90),
root-mean-square difference 29.3 mm (25.3 to 32.8) against standard
deviations of 71.2 mm in the estimate and 66.6 mm in the altimetry.
The trends do not agree: over the 300 months the estimate rises at
5.18 mm/yr (3.90 to 6.46) and the altimetry at 3.19 mm/yr (2.11 to
4.27), and the trend of the month-by-month difference, which is the
score that bears on the claim because it removes the variability
the two share, is 1.99 mm/yr with interval 1.39 to 2.59 (residual
autocorrelation 0.53, effective sample 91.9). The interval excludes
zero, and the disagreement is larger than the published order of a
regional altimetry trend uncertainty, 0.83 mm/yr at the 90 percent
level (range 0.78 to 1.22, for a different gridded product; NASA-SSH
publishes no uncertainty for its grids). The comparison attester
re-hashed every grid, re-derived the model values from the partition
receipt, recomputed every score and interval, and
passed.[^comparison][^prandi-2021]

**What the two receipts together support.** The estimate's box-mean
sea level tracks the altimetric one month by month at nine tenths
correlation, and rises about two millimetres a year faster than it
over the same twenty-five years. Because the partition is internal
to the estimate, the disagreement cannot be assigned to the
manometric or the steric part from this evidence.

# Validity

Declared as a trend claim on ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4
over the box and the full period, the claim was adjudicated against
the bundle's validity domains by the fitness attester: verdict
UNADJUDICATED, receipt `fitness-sea-level-record.json`. The one
domain that speaks to it, the large-scale statistics domain (native
monthly fields support large-scale statistics over 1992-2017), is an
unsigned draft, and an unsigned domain never adjudicates; the receipt
lists it as advisory. That domain also records the limit that
matters most here: the estimate's grid is of the one-degree class
and does not resolve shelf processes or the Gulf Stream's meanders,
and the domain has no spatial-scale axis on which a ten-degree
coastal box could be placed. Until a steward signs a domain that
admits or excludes trends at this scale, this finding cannot become
stable, whatever its evidence.[^large-scale-domain]

# Confrontation

Confronted, against NASA-SSH V1.1 (JPL's gridded sea surface height
anomaly from the reference altimetry missions, DOI
10.5067/NSREF-SG0V11, Creative Commons Attribution licence), pinned
in the receipt to the version and DOI read from every file, the
record's manifest hash and the digest of all 1315 grids, with its
citation, licence and published uncertainty
statement.[^nasa-ssh][^nasa-ssh-record]

**Independence is low, and the receipt says so.** The estimate was
fitted to along-track sea surface height from the same missions
this product regrids; the bundle's convention requires a
confrontation to state what the estimate was constrained by and
where the observation overlaps it, and this one overlaps it almost
entirely. So the close agreement in the monthly variability is in
part the fit, and shows that the altimetric constraint reached this
box at these scales, not that the estimate's sea level is right for
reasons the fit did not supply. The disagreement in the trend is the
other side of the same coin: a residual the fit did not, or could
not, remove, and it stands as measured. Under the convention, the
acceptable deviation is what the comparison and its uncertainty say
it is, not a reviewer's judgement, and here the comparison says the
estimate's rate is 1.99 mm/yr above the record's with an interval
that excludes zero and exceeds the published order of the record's
own trend uncertainty.[^doctrine][^comparison]

**What was compared, exactly.** Cosine-latitude weighted means of
the half-degree altimetry cells in the box, each weekly grid
assigned to the month of its centre date and the month's grids
averaged (a month enters on two grids or more; four months of the
300 have two or three because eight grids in the record are empty),
against the model's area mean over its 102 native wet cells. The
footprints differ: the altimetry cells are already smoothed with a
Gaussian scale of 175 km over passes up to 600 km away, so coastal
cells carry offshore information; the model averages its own coarse
cells. Neither is a coastal measurement. The scores' intervals are
sampling intervals from the series' own autocorrelation and do not
include the altimetry's measurement error.[^comparison]

# Limitations

The limitations listed in the frontmatter, in prose. The claim is
about the area mean of a ten-degree box in one state estimate; no
point, no coastline and no ocean is claimed. The partition is the
estimate's own bookkeeping, checked for consistency to below a
millimetre, and nothing observational here tests it; given that the
total rises faster than the observed record, at least one of the two
parts is too large, and the evidence does not say which. The estimate
is Boussinesq, conserving volume with a fixed reference density of
1029 kg per cubic metre,[^v4r4-config] and its sea level carries a
spatially uniform global-mean correction, so its regional steric part
includes a global term. The box crosses the Gulf Stream and the shelf, which
neither the one-degree model grid nor the half-degree smoothed
altimetry resolves; the governing validity domain is unsigned and
says so. The intervals do not include measurement uncertainty, and
the one published figure for the order of a regional altimetry trend
uncertainty is smaller than the disagreement. Four confronted months
are thin, and the receipt shows which.

# What would overturn this

- **A confrontation with the un-fitted record.** Coastal tide
  gauges in the box (the research-quality daily series at Eastport,
  Portland, Boston, Woods Hole, Nantucket, Newport, New London,
  Montauk, The Battery, Atlantic City and Cape May) were not among
  the estimate's constraints and measure a different quantity:
  relative sea level, with vertical land motion and without the
  inverse-barometer correction. A comparison that accounts for those
  differences and finds the estimate's rate within the gauges'
  uncertainty would undercut the trend disagreement claimed here; one
  that finds a similar excess would strengthen it. Either is a new
  computation with its own receipt, not an edit to this finding.
- **The attester failing.** Anyone can re-run
  `sea_level_partition.py` on the partition receipt and
  `altimetry_confrontation_check.py` on the comparison receipt, from
  their own directories, with the trees on disk. A recompute that
  lands outside the receipts' tolerance means a number here is not
  what the sanctioned code produces, and the finding is withdrawn
  until it is.
- **A signed validity domain excluding the claim.** If a steward
  signs a domain that puts trends at this box's scale outside the
  estimate's fitness, the verdict becomes OUT and the finding cannot
  be stated; it is retracted with the domain as the reason.
- **The record moving.** A later ECCO release, or a later NASA-SSH
  version, is a different product; this finding stays true of V4r4
  against V1.1 and is superseded, not edited, by one derived over
  the successor. The `stale_after` date is the sweep for that.
- **A different partition choice.** The steric part is computed from
  the model's own density anomaly with partial cells; a steric series
  from a foreign equation of state, or one that mixes the
  inverse-barometer variants of sea surface height, would not
  reproduce the partition and would be a different, and worse,
  computation, not a refutation. A recomputation that keeps the
  sanctioned choices and lands outside tolerance is the refutation.

[^ecco-v4r4]: ECCO v4 Release 4 ocean state estimate, the dataset concept
[^partition]: Regional sea level partition from ECCO (attested), the computation; its attester is references/attesters/sea_level_partition.py
[^trend-method]: Linear trend with an honest interval from a monthly series (attested), the shared interval chain
[^comparison]: ECCO regional sea level against NASA-SSH altimetry (attested), the comparison; its attester is references/attesters/altimetry_confrontation_check.py
[^prandi-2021]: Prandi et al. 2021, Scientific Data 8, 1, doi:10.1038/s41597-020-00786-7, abstract; the figure is carried in the comparison receipt under observation.published_uncertainty with this source
[^large-scale-domain]: ECCO v4r4 native monthly fields support large-scale statistics over 1992-2017, the validity domain, status draft, unsigned
[^nasa-ssh]: NASA-SSH simple gridded sea surface height anomaly (observational reference), the dataset concept
[^nasa-ssh-record]: docs/nasa-ssh-record.md, the record note: tree, manifest, verification, empty grids, terms
[^v4r4-config]: The ECCO v4 Release 4 configuration namelist in ECCO-GROUP/ECCO-v4-Configurations, which sets `rhoConst=1029.`
[^doctrine]: Consistency versus confrontation, the convention: only a confrontation supports a claim about the world; the acceptable deviation is measured, not judged; independence is a degree, and it is stated
