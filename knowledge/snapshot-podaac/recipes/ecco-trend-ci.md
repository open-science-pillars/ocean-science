---
type: recipe
title: "A trend with an honest interval from any ECCO monthly series"
description: "How to turn a monthly series out of a sanctioned receipt into a trend with a 95 percent interval that respects serial correlation: fit the trend jointly with the climatology over complete years, estimate r1, shrink the sample to n_eff (never above n), and let the t distribution on the effective degrees of freedom set the width."
tags: [ecco, trend, uncertainty, confidence-interval, autocorrelation, recipe]
inputs: "A receipt from a sanctioned computation carrying a monthly {YYYY-MM: value} field over consecutive months (steric_mean_m_by_month from the steric height computation is the reference), its data.record stamp intact"
expected: "Reference series us-northeast-coast steric height, 2010-01 through 2010-12, scaled to mm, deseasonalize none (measured 2026-09-02): trend +135.7772 mm per year, r1 +0.555, n_eff 3.43 of 12, 95 percent interval [-701.5, +973.1] mm per year; naive half width 109.8, honest 837.3. The same series over the full record, 1992-01 through 2017-12, climatology removed jointly, gives the record trend and interval that ../computations/ecco-steric-height.md owns and states; this recipe cites them there and quotes none of the digits"
expected_uncertainty: "The interval is calibrated in the regime it is meant for: at 120 months or more and lag-1 autocorrelation up to 0.8 the measured coverage is 91.8 to 95.1 percent (asserted band 90 to 97.5). At 24 months coverage is 67 to 86 percent and at 12 months 74 to 95, worst at high autocorrelation, and the tool declines to state an interval in up to 7 percent of trials; treat any n_eff below about 10 as a description of the window, not a trend. The interval is a statement about sampling under an AR(1) residual model, not about model or observational error in the series"
generated: { by: claude-code/fable-5, at: 2026-09-02T05:10:00Z }
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T22:08:00Z }
stale_after: 2027-01-05
sources:
  - id: attested-computation
    resource: ../computations/ecco-trend-ci.md
    title: "The attested computation this recipe walks: method, contract, calibration, reference run"
  - id: steric-height
    resource: ../computations/ecco-steric-height.md
    title: "The attested steric height whose receipt supplies the reference series and whose record run owns the full-record trend and interval"
  - id: naked-trend
    resource: ../gotchas/ecco-trend-without-effective-n.md
    title: "Why the interval is not optional: the trap this recipe avoids"
---

# A trend with an honest interval from any ECCO monthly series

Start from a receipt, not from a series. The sanctioned trend tool
reads a monthly field out of a receipt another sanctioned computation
wrote, so the trend carries that receipt's run id, code hash and
verified-tree stamp forward; a series pasted from anywhere else is
refused by the attester whatever its arithmetic.[^attested-computation]
Then: remove the monthly climatology jointly with the fit, the
calendar-month means coming off the time index as well as the series
(removed first and fitted second, the climatology keeps
143/(144Y^2 - 1) of the trend, a quarter of it over two years), and
only over complete years (the tool refuses otherwise); fit an ordinary
least squares slope against months; take the lag-1 autocorrelation r1
of the residuals; shrink the sample to n_eff = n (1 - r1) / (1 + r1),
never above n; and let Student's t on n_eff - 2 degrees of freedom
set the interval. Report the trend, the interval, r1 and n_eff
together. Never the trend alone.[^naked-trend]

    uv run knowledge/podaac/references/computations/ecco_trend_ci.py \
        --source steric_receipt.json --field steric_mean_m_by_month \
        --value-units m --scale 1000 --report-units mm \
        --deseasonalize climatology --receipt trend_receipt.json
    uv run knowledge/podaac/references/attesters/trend_ci_check.py trend_receipt.json

The number to reproduce is a warning rather than an anchor: the
bundle's signed steric trend, +135.7772 mm per year over the twelve
months of 2010, comes back from this tool with r1 +0.555, 3.43
effective samples, and an interval of [-701.5, +973.1] mm per year.
The naive interval (plus or minus 109.8) would have called it
significant; the honest one says the year's wobble is seven times the
trend.[^steric-height] Twelve months cannot form a climatology either,
so that run declares `none` and the receipt says so. The regime the
tool is built for is the full record: 312 months, where the
calibration measures 92 to 95 percent coverage and the naive interval
covers under half the time once r1 reaches 0.8, and where the same
steric series comes back as the record trend with the interval the
steric height computation's receipt carries, a rate at
last.[^attested-computation][^steric-height] The steric
and sea-level computations embed this block beside their own trends,
so a run of either already carries the interval; the standalone tool
is for any other monthly field a sanctioned receipt holds.

[^attested-computation]: computations/ecco-trend-ci.md, method, contract, calibration
[^steric-height]: computations/ecco-steric-height.md, the signed reference trend and the record run that owns the full-record numbers
[^naked-trend]: gotchas/ecco-trend-without-effective-n.md
