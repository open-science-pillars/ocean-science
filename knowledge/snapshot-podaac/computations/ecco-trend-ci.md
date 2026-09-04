---
type: Attested Computation
title: "Linear trend with an honest interval from a monthly series (attested)"
description: "Sanctioned trend-with-interval for any monthly series a sanctioned receipt carries: OLS slope fitted jointly with the monthly climatology, lag-1 autocorrelation of the residuals, effective sample size capped at the sample, and a two-sided 95 percent interval on the effective degrees of freedom; the receipt carries the series and every intermediate so the attester recomputes the whole chain, other sanctioned computations embed the same block beside their own trends, and a Monte Carlo calibration with a negative control ships beside it."
tags: [ecco, trend, uncertainty, confidence-interval, autocorrelation, attested]
runtime: python
parameters:
  - { name: source, type: "path to a sanctioned receipt", required: true }
  - { name: field, type: "name of a monthly {YYYY-MM: value} field in it", required: true }
  - { name: value_units, type: "units of the stored values", required: true }
  - { name: scale, type: "multiplier applied before fitting", required: false, default: 1.0 }
  - { name: report_units, type: "units after scaling", required: false }
  - { name: deseasonalize, type: "climatology or none", required: false, default: climatology }
computation: references/computations/ecco_trend_ci.py
executor:
  resource: references/computations/ecco_trend_ci.py
  receipt: [run_id, code_sha256, data, bound_parameters, series, intermediates, results]
attester:
  resource: references/attesters/trend_ci_check.py
calibration: references/computations/ecco_trend_ci_calibration.py
calibration_report: references/calibration/trend-ci-coverage.json
generated: { by: claude-code/fable-5, at: 2026-09-02T05:10:00Z }
status: draft
stale_after: 2027-01-05
sources:
  - id: santer-2008
    resource: https://doi.org/10.1002/joc.1756
    title: "Santer et al. 2008, Int. J. Climatol. 28, 1703-1722: the effective-sample-size treatment of trend uncertainty under lag-1 autocorrelation this computation fixes"
  - id: calibration-report
    resource: references/calibration/trend-ci-coverage.json
    title: "The Monte Carlo coverage report the calibration writes: fifteen configurations, the asserted band, and the measured collapse of the naive interval"
  - id: steric-height
    resource: ecco-steric-height.md
    title: "The attested steric height whose reference series is this computation's reference run, whose receipt embeds this method's interval block beside its trend, and whose record run owns the full-record trend and interval this file cites rather than quotes"
  - id: sea-level-partition
    resource: ecco-regional-sea-level.md
    title: "The attested sea-level partition whose three trends each embed this method's interval block"
  - id: joint-gotcha
    resource: ../gotchas/ecco-trend-deseasonalize-jointly.md
    title: "Why the climatology is fitted jointly: removed first, it keeps 143/(144Y^2 - 1) of the trend; not removed at all, a raw fit over complete years carries a seasonal projection"
  - id: naked-trend
    resource: ../gotchas/ecco-trend-without-effective-n.md
    title: "The gotcha this computation exists to close: a trend fit without an effective-sample-size correction overstates certainty"
---

# Linear trend with an honest interval from a monthly series (attested)

A trend without an error bar is arithmetic, not a claim. This
computation fixes one method for turning a monthly series into a
trend and a two-sided 95 percent confidence interval that accounts
for the serial correlation every geophysical monthly series carries,
and it accepts only series that arrive inside a sanctioned receipt,
so a trend inherits the data provenance of the quantity it was fit
to.[^santer-2008]

The method, fixed in the sanctioned file and declared in every
receipt: (1) remove the monthly climatology jointly with the trend:
the mean of each calendar month is subtracted from the series and
from the time index alike, so the slope that follows is the
least-squares estimate of trend and climatology fitted together (the
Frisch-Waugh-Lovell identity; the same numbers as the
thirteen-parameter regression). The two are not orthogonal, even over
complete years: the calendar-month means of time form a sawtooth that
carries 143/(144Y^2 - 1) of any trend over Y years, a quarter of it
at two years, and subtracting the climatology from the series alone
hands that fraction to the climatology.[^joint-gotcha] Complete years
(a multiple of 12 months, at least 24) are required so every calendar
month is estimated from the same number of years; otherwise `none`,
and the receipt says which; (2) ordinary least squares slope against
time in months; (3) lag-1 autocorrelation r1 of the residuals; (4)
effective sample size n_eff = n (1 - r1) / (1 + r1), capped at n: a
sample cannot be more effective than itself, and r1 estimated from a
short residual series is biased negative, which would otherwise hand
a short series an interval narrower than the independent-samples one;
(5) residual variance on n_eff - 2 degrees of freedom and the slope's
standard error from it; (6) the interval from Student's t on n_eff - 2
degrees of freedom, fractional and evaluated exactly (regularized
incomplete beta, no scipy). Below one effective degree of freedom the
tool refuses to state an interval at all: the series is too short or
too autocorrelated for a finite one, and the receipt says so instead
of printing a number. Changing any step is a new computation, not an
edit to this file.

**Attestation contract.** The receipt carries the series itself
(dates and values), the deseasonalized series, and every intermediate
(slope, intercept, sum of squares of time, r1, n_eff, degrees of
freedom, standard error, t quantile, and the naive standard error for
comparison). The attester does not sample: from the series and the
bound parameters alone it rebuilds the entire chain with its own
stdlib arithmetic and requires every intermediate and every result to
agree within 1e-9 relative (measured agreement below 1e-12; the two
implementations differ only in summation order). It refuses a receipt
whose code hash is not the sanctioned file's, whose series is not
consecutive calendar months, whose method parameters are not the
contract, whose significance flag contradicts its own interval, or
whose provenance chain is broken: the source must be named by path
and sha256, must be a sanctioned receipt (run id and code hash
carried through), and that receipt's `data.record` must be the verify
tool's stamp for a manifested tree. A trend over a series of unknown
origin is not attested, whatever its arithmetic. Eleven distinct
tampers (a nudged r1, a nudged series value, a dropped source
receipt, an unverified tree, a flipped significance flag, a nudged
trend, the naive half width substituted for the honest one, a
climatology claimed over twelve months, wrong units, a month gap, a
wrong code hash) each fail naming their field. The recompute is one
shared stdlib chain, written from the method statement rather than
copied from the executor, and every attester that meets this method's
block imports it.

**Embedded beside other trends.** The steric height and sea-level
partition computations do not fit trends of their own: each calls
this file's `interval_block` on its monthly series and embeds the
result beside its trend field (`steric_trend_mm_yr`, the three
`trend_X_mm_yr`), the block naming this file by hash, and their
attesters recompute it through the same shared chain from the series
in that receipt.[^steric-height][^sea-level-partition] One method,
one hash, one recompute behind every trend the bundle reports, and
the cross-computation anchor those two share stays on the central
value while the interval travels beside it. Over the full record the
steric series gives the trend and interval block the steric height
computation's record receipt carries, and the partition's record
receipt carries the same block to every digit; those two receipts own
the record numbers and this file states none of them.[^steric-height]
A raw least-squares fit through the same 312 months reads +2.9932 mm
per year, above the joint value by the seasonal projection the joint
fit removes. Removing the climatology first and fitting second, as an
earlier form of this method did, reads +2.7958: the 143/(144Y^2 - 1)
attenuation at 26 years, small here and a quarter of the trend at
two.[^joint-gotcha]

**Calibration with teeth.** A confidence interval is a promise about
coverage, and the promise is tested on the sanctioned code itself:
`ecco_trend_ci_calibration.py` imports `trend_ci` from the executor,
generates synthetic monthly series with a known trend, an annual
cycle, and stationary AR(1) noise of known lag-1 coefficient phi, and
measures how often the interval contains the true trend over 2000
seeded trials for each of fifteen configurations (12, 24, 60, 120,
312 months; phi 0, 0.5, 0.8). The run exits 1 unless, in the regime
the bundle uses the method (at least 120 months, phi at most 0.8),
coverage lies within the asserted band of 90 to 97.5 percent AND the
negative control collapses: the same trials scored with the naive
interval (n - 2 degrees of freedom, no effective-sample-size
correction, what a bare polyfit with a textbook standard error gives)
must cover below 80 percent at phi 0.8. Measured 2026-09-02: honest
coverage 91.8 to 95.1 percent in the asserted regime; naive coverage
47 to 49 percent at phi 0.8 and 71 to 73 percent at phi 0.5 at 120
months or more, and below 80 percent at phi 0.8 at every length. The
band is set from measurement, not from hope: the correction is known
to under-cover because r1 estimated from residuals is biased toward
zero (estimated n_eff 16.6 against a true 13.3 at 120 months, phi
0.8). Two alternatives were measured on the same seeded trials and
one adopted. Charging the climatology's thirteen parameters to the
degrees of freedom (n_eff - 13) lifts the survivors' coverage to 97.5
percent at phi 0.8 only by refusing an interval in 688 of 2000 trials
at 120 months and in more than half of the 24-month trials, which is
the hard cases dropped rather than covered, so it was rejected.
Capping n_eff at n costs nothing where r1 is positive and repairs the
white-noise cases where a short residual series estimates r1 below
zero: coverage at phi 0 rises from 86 to 95 percent at 12 months, 78
to 86 at 24, 92 to 94 at 60 and 120, so it stands in the method.
Short series are measured and reported, not asserted: at 60 months 89
to 94 percent; at 24 months 67 to 86 percent and at 12 months 74 to
95, the low ends at phi 0.8, and the tool declines to state an
interval in up to 7 percent of trials there because fewer than one
degree of freedom remains. Removing the correction from a copy of the
executor makes the calibration fail four ways.[^calibration-report]

**Reference run (2026-09-02, fixture tree, from the attested steric
receipt).** The series behind the bundle's signed steric trend: the
us-northeast-coast area-mean steric height over the twelve months of
2010, values in metres scaled to millimetres, deseasonalization
`none` (twelve months cannot form a climatology). Trend +135.7772 mm
per year, identical to the signed value; r1 +0.555; n_eff 3.43 of 12;
1.43 degrees of freedom; t quantile 6.43; 95 percent interval
[-701.5, +973.1] mm per year. The naive half width would have been
109.8 and would have called the trend significant; the honest one is
837.3 and does not.[^steric-height] That is the whole content of the
naked-trend gotcha, measured on our own number.[^naked-trend] Both
receipts ship as exhibits (references/retrieval/exhibit-steric-2010.json
and exhibit-trend-steric-2010.json) and pass their attesters from a
fresh clone.

**Data provenance.** The receipt's `data` block names the source
receipt by path and sha256, carries its run id, code hash and the
field read, and copies through the `RECORD.json` stamp the verify
tool left in the tree that receipt was computed from (record name,
manifest SHA-256, verification time, report SHA-256). The attester
refuses a receipt whose chain does not reach that stamp, so nothing is
attested against a series this bundle has not itself computed from a
manifested and verified tree. The two trees and the rule are in
docs/science-record.md.

[^santer-2008]: Santer et al. 2008, doi:10.1002/joc.1756, the effective-sample-size treatment
[^calibration-report]: references/calibration/trend-ci-coverage.json, the seeded Monte Carlo report
[^steric-height]: computations/ecco-steric-height.md, the signed reference trend, its receipt, and the record run that owns the full-record numbers
[^naked-trend]: gotchas/ecco-trend-without-effective-n.md, the trap this closes
[^sea-level-partition]: computations/ecco-regional-sea-level.md, three trends, three embedded blocks
[^joint-gotcha]: gotchas/ecco-trend-deseasonalize-jointly.md, the sawtooth in the calendar-month means of time
