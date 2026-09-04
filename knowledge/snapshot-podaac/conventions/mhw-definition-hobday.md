---
type: convention
title: "Marine heatwave definition (Hobday family)"
description: "The operational MHW definition and category scale this bundle computes against: 90th-percentile seasonal threshold, five-day minimum, two-day gap joining, fixed baseline as a stated parameter, categories as multiples of the climatology-to-threshold difference."
tags: [marine-heatwave, sst, convention]
generated: { by: claude-code/fable-5, at: 2026-08-30T23:20:00Z }
status: draft
stale_after: 2027-01-04
sources:
  - id: hobday-2016
    resource: https://doi.org/10.1016/j.pocean.2015.12.014
    title: "Hobday et al. 2016, A hierarchical approach to defining marine heatwaves (the origin definition paper; paywalled, see verification route)"
  - id: hobday-2018
    resource: https://doi.org/10.5670/oceanog.2018.205
    title: "Hobday et al. 2018, Categorizing and naming marine heatwaves (open full text; restates the 2016 operational definition verbatim)"
  - id: mhw-code
    resource: https://github.com/ecjoliver/marineHeatWaves
    title: "Oliver, marineHeatWaves: the reference implementation of the Hobday et al. 2016 definition (detect() defaults)"
  - id: mhw-org
    resource: http://www.marineheatwaves.org/mhw-overview.html
    title: "Marine Heatwaves International Working Group, MHW overview (the definition group's own site)"
---

# Marine heatwave definition (Hobday family)

The operational definition this bundle computes against; seeded by
ecco-scout/claude 2026-08-28, every number verified against the open
sources 2026-08-30, queued for steward signature.

**The definition.** A marine heatwave is a period when sea surface
temperature exceeds a seasonally varying threshold, defined as the 90th
percentile relative to the local long-term climatology, for at least
five days; successive exceedances separated by no more than two
below-threshold days are joined as one event. The 2018 paper states the
2016 operational definition in one sentence: an upper locally
determined threshold "(90th percentile relative to the local long-term
climatology) is exceeded for at least a five-day period, with no more
than two below-threshold days".[^hobday-2018] The definition group's
site states the same: at least 5 consecutive days, gaps of 2 days or
less joined.[^mhw-org] The reference implementation encodes these as
its defaults: `pctile=90`, `minDuration=5`, `joinAcrossGaps=True`,
`maxGap=2`.[^mhw-code]

**Categories.** Severity categories are based on multiples of the local
difference between the climatological mean and the climatological 90th
percentile (the detection threshold): moderate (1-2x, Category I),
strong (2-3x, Category II), severe (3-4x, Category III), and extreme
(above 4x, Category IV), allocated at each point in space and time from
the intensity measure.[^hobday-2018]

**The baseline is a parameter, not a constant.** The climatology
baseline window of any computation citing this convention is always
stated with results: the 2018 paper recommends the baseline period be
fixed, since baseline updates as the world warms would change the
categories of past events, and notes a moving 30-year climatology as
the deliberate alternative reading ("unusual for the time") rather than
a default.[^hobday-2018] The reference implementation likewise takes
`climatologyPeriod` as an explicit argument.[^mhw-code] Operational
detail recorded for reproducibility: the reference implementation
computes the daily climatology and threshold with an 11-day window
centered on each calendar day (`windowHalfWidth=5`) and smooths the
percentile with a 31-day moving average
(`smoothPercentileWidth=31`).[^mhw-code]

**Verification route, stated for the steward.** Hobday et al. 2016 is
the origin source but is paywalled; every number above was verified
against the same author family's open 2018 restatement (quoted), the
definition group's own site, and the reference implementation's
defaults, which agree with each other on all points. Page-level
citations into the 2016 paper itself are queued for steward review with
the PDF in hand; the recorded secondary verification follows the
authoring guide's bot-block rule.[^hobday-2016]

[^hobday-2016]: Hobday et al. 2016 (origin; page-level verification queued with the steward's PDF)
[^hobday-2018]: Hobday et al. 2018, open full text: the definition restatement and the category sentence ("moderate (1-2x, Category I), strong (2-3x, Category II), severe (3-4x, Category III), and extreme (>4x, Category IV)")
[^mhw-code]: marineHeatWaves detect() signature: pctile=90, minDuration=5, joinAcrossGaps=True, maxGap=2, windowHalfWidth=5, smoothPercentileWidth=31, climatologyPeriod as argument
[^mhw-org]: marineheatwaves.org MHW overview: "exceed a seasonally-varying threshold (usually the 90th percentile) for at least 5 consecutive days. Successive events with gaps of 2 days or less are considered part of the same MHW."
