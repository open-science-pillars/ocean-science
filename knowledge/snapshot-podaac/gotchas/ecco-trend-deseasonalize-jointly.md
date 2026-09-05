---
type: dataset-gotcha
title: "Deseasonalize jointly with the trend, or the climatology keeps part of it"
description: "Removing a monthly climatology first and fitting a trend second hands the climatology 143/(144Y^2 - 1) of the trend over Y complete years, a quarter of it at two years; a raw fit that skips the climatology carries a seasonal projection instead. The fix is one least-squares fit of trend and climatology together, which the bundle's sanctioned trend method now does; the record steric series reads +2.9932 raw and +2.7958 sequential against the joint value the steric height computation's record receipt owns."
tags: [ecco, trend, climatology, deseasonalize, least-squares, steric-height]
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: ecco-trend-deseasonalize-jointly
# eval id reserved for the eval-commons seed.
generated: { by: claude-code/fable-5, at: 2026-09-02T06:00:00Z }
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T22:08:00Z }
stale_after: 2027-01-05
sources:
  - id: attested-trend
    resource: ../computations/ecco-trend-ci.md
    title: "The sanctioned trend method: the joint fit, its derivation, and the calibration measured on it"
  - id: steric-height
    resource: ../computations/ecco-steric-height.md
    title: "The steric height computation whose record series is the worked example and whose record receipt owns the joint trend and its interval"
  - id: naked-trend
    resource: ecco-trend-without-effective-n.md
    title: "The companion trap: the interval that must travel beside the trend this note fits"
---

# Deseasonalize jointly with the trend, or the climatology keeps part of it

The obvious recipe for a trend through a monthly series has two
steps: subtract the mean of each calendar month, then fit a line to
what is left. It is wrong by a known fraction, and the fraction is
not small on short windows. Over Y complete years the calendar-month
means of the time index itself are not constant: month k's mean time
is k plus a multiple of twelve, so the climatology of time is a
sawtooth, and the sawtooth is correlated with the line. Subtracting a
climatology from the series alone therefore subtracts a climatology
of the trend as well, and the slope fitted afterward is the true
least-squares slope times 1 - 143/(144Y^2 - 1): 0.751 at two years,
0.960 at five, 0.9985 at twenty-six. A quarter of a two-year trend
goes into the twelve monthly means and never comes back.[^attested-trend]

The fix is one fit, not two. Least squares on trend and twelve
monthly offsets together gives the slope that is unbiased for both,
and the Frisch-Waugh-Lovell identity says the same slope comes from
subtracting the calendar-month means from the series AND from the
time index, then regressing one on the other. That is what the
sanctioned trend method does, and it requires complete years so every
calendar month is estimated from the same number of years. Skipping
the climatology altogether is not the escape: a raw least-squares fit
through complete years carries the projection of the annual cycle
onto the sawtooth, Y times the sum over months of the climatology
times (k - 5.5), divided by the sum of squares of time, and that is a
trend-like number with no trend in it.

The record steric series over the US northeast coast, 1992-01
through 2017-12, is the worked example. A raw fit reads +2.9932 mm
per year. Subtract the climatology first and fit second: +2.7958.
Fit the two together and the slope is the joint value both sanctioned
computations now carry with its interval; the steric height
computation's record receipt owns that number and this note cites it
rather than copying it.[^steric-height] Over 26 years the sequential
loss is fifteen hundredths of a percent and the raw excess is 0.19 mm
per year, seven percent of the trend. Over 2010 and 2011
alone the three numbers are +39.05, -0.33 and -0.44: the raw fit
reads a full year's seasonal swing as a rate, and the sequential fit
returns three quarters of the joint one, exactly the
143/575.[^steric-height] None of this is about ECCO; it is about
every monthly series, and the sanctioned method carries the interval
that the companion trap requires beside every one of these
numbers.[^naked-trend]

[^attested-trend]: computations/ecco-trend-ci.md, the method statement and its derivation
[^steric-height]: computations/ecco-steric-height.md, the record run and the 2010 reference run
[^naked-trend]: gotchas/ecco-trend-without-effective-n.md
