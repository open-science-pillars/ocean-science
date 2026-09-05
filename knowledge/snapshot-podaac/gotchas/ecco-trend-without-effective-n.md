---
type: dataset-gotcha
title: "A trend fit without an effective-sample-size correction overstates certainty"
description: "Monthly ocean series are serially correlated, so a least-squares trend with a textbook standard error, or with no error bar at all, claims far more certainty than the data hold; the bundle's own signed steric trend of +135.7772 mm per year over 2010 is the example, and with an honest interval it is not distinguishable from zero."
tags: [ecco, trend, uncertainty, autocorrelation, confidence-interval, steric-height]
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: ecco-trend-without-effective-n
# eval id reserved for the eval-commons seed.
generated: { by: claude-code/fable-5, at: 2026-09-02T05:10:00Z }
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T22:08:00Z }
stale_after: 2027-01-05
sources:
  - id: attested-trend
    resource: ../computations/ecco-trend-ci.md
    title: "The attested trend-with-interval computation, its calibration report, and the reference run on the steric series"
  - id: steric-height
    resource: ../computations/ecco-steric-height.md
    title: "The signed steric height computation whose reference trend, +135.7772 mm per year over twelve months, carried no interval, and whose record run owns the full-record trend and interval"
  - id: santer-2008
    resource: https://doi.org/10.1002/joc.1756
    title: "Santer et al. 2008: the effective-sample-size correction for trends in autocorrelated series"
---

# A trend fit without an effective-sample-size correction overstates certainty

Every monthly ocean series remembers last month. Steric height, sea
level, heat content, transports: their residuals about a straight
line are serially correlated, typically with a lag-1 coefficient
between 0.5 and 0.9. Ordinary least squares does not know this. It
counts every month as an independent witness, and its textbook
standard error is too small by roughly the square root of
(1 + r1) / (1 - r1): a factor of three at r1 0.8. A trend reported
with that error bar, or with no error bar at all, is a statement of
certainty the data do not contain.[^santer-2008]

We did this ourselves, and signed it. The steric height computation's
reference run fits a line through twelve monthly area means over the
US northeast coast in 2010 and reports +135.7772 mm per year; the
attested sea-level partition reproduces the same figure to four
decimals from independent code, and that agreement became the anchor
both attesters check. It is a correct number. It is also naked. Run
the same twelve values through the sanctioned trend computation and
the residuals have r1 +0.555, which leaves 3.43 effective samples and
1.43 degrees of freedom; Student's t at that many degrees of freedom
is 6.43, and the 95 percent interval is [-701.5, +973.1] mm per year.
A naive interval would have been plus or minus 109.8 and would have
called the trend significant. The honest one says that a year's
wobble in this box is seven times the trend, and that +135.7772 is a
description of 2010, not a rate.[^steric-height][^attested-trend]

The correction is not optional and it is not sufficient on its own.
Shrink the sample to n_eff = n (1 - r1) / (1 + r1), never above n,
and put the interval on n_eff - 2 degrees of freedom: the calibration
that ships with the computation measures 92 to 95 percent coverage
for series of 120 months or more, against 47 to 49 percent for the
uncorrected interval at r1 0.8. But r1 estimated from a handful of
residuals is biased toward zero, so over twenty-four months even the
corrected interval covers only 67 to 86 percent of the time, over
twelve 74 to 95, and the tool refuses to state one at all when fewer
than one degree of freedom remains. Twelve months is a year, not a
trend. Fit trends over the record, report the interval beside the
slope, and read an n_eff below about ten as the series telling you it
has nothing to say about the long term. Over the full record the same
steric series is a rate: the steric height computation's record
receipt carries the trend beside an honest interval several times the
naive one that still excludes zero, and the numbers live there, not
here.[^steric-height][^attested-trend]

[^santer-2008]: Santer et al. 2008, doi:10.1002/joc.1756
[^steric-height]: computations/ecco-steric-height.md, the signed reference run, its anchor, and the record run
[^attested-trend]: computations/ecco-trend-ci.md, reference run and calibration report
