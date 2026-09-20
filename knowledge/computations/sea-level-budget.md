---
type: Attested Computation
spheres: [hydrosphere, cryosphere]
title: "Sea level budget closure from altimetry, Argo steric and GRACE-FO mass (attested)"
description: "Sanctioned closure of the global mean sea level budget over a stated period: altimetry against ocean mass plus steric, the monthly residual and every trend with the interval the one sanctioned trend method states, the combined uncertainty with the deep-steric systematic stated separately, a verdict closed_within_uncertainty, the convention's corrections table as receipt facts, and a refusal (exit 3, never a number) for a period that crosses the GRACE to GRACE-FO gap without independent continuity evidence. Proven on a synthetic fixture with a known closure and anchored on a real-data run over 2005 through 2016 that closes within uncertainty."
tags: [sea-level, budget, closure, altimetry, nasa-ssh, grace, grace-fo, mascons, argo, steric, manometric, attested]
runtime: python
parameters:
  - { name: period, type: string, required: true }
  - { name: bridge, type: string, required: false }
computation: skills/sea-level-budget/scripts/sea_level_budget.py
executor:
  resource: skills/sea-level-budget/scripts/sea_level_budget.py
  receipt: [run_id, computation, code_sha256, capability, bundle, runtime, generated_utc, data, bound_parameters, refused, months, series, trend_altimetry_mm_yr, trend_mass_mm_yr, trend_steric_mm_yr, trend_residual_mm_yr, trends, combined_uncertainty, verdict, bookkeeping, caveats]
attester:
  resource: skills/sea-level-budget/scripts/sea_level_budget_check.py
generated: { by: knowledge-seeder/claude, at: 2026-09-13T21:00:00Z }
verified:
  - { by: human:PaulMRamirez, at: 2026-09-13T18:39:32Z, role: maintainer, source: https://github.com/open-science-pillars/nasa-daac-knowledge/pull/125 }
  - { by: human:PaulMRamirez, at: 2026-09-13T18:50:46Z, role: maintainer, source: https://github.com/open-science-pillars/nasa-daac-knowledge/pull/126 }
  - { by: human:PaulMRamirez, at: 2026-09-13T21:22:05Z, role: maintainer, source: https://github.com/open-science-pillars/nasa-daac-knowledge/pull/127 }
  - { by: human:PaulMRamirez, at: 2026-09-16T05:51:09Z, role: maintainer, source: https://github.com/open-science-pillars/nasa-daac-knowledge/pull/183 }
status: draft
stale_after: 2027-03-13
sources:
  - id: convention-slbc
    resource: knowledge/podaac/conventions/sea-level-budget-closure.md
    title: "Bundle convention: sea level budget closure, a correction-consistency problem first (the corrections table this receipt carries as facts)"
  - id: nasa-ssh
    resource: knowledge/podaac/datasets/nasa-ssh.md
    title: "Bundle dataset concept: NASA-SSH simple gridded sea surface height anomaly, the altimetry term's product and its corrections"
  - id: mascons
    resource: knowledge/podaac/datasets/grace-fo-mascons.md
    title: "Bundle dataset concept: GRACE/GRACE-FO JPL mascon solutions, the mass term's product and its formal uncertainty grids"
  - id: gotcha-gia
    resource: knowledge/podaac/gotchas/grace-gia-correction.md
    title: "Bundle gotcha: the GIA model already applied to the mascon product"
  - id: gotcha-leakage
    resource: knowledge/podaac/gotchas/grace-coastal-leakage.md
    title: "Bundle gotcha: coastal leakage in the ocean mascons"
  - id: gotcha-gap
    resource: knowledge/podaac/gotchas/grace-intermission-gap.md
    title: "Bundle gotcha: the GRACE to GRACE-FO gap and the missing months a continuous-looking series hides"
  - id: gotcha-low-degree
    resource: knowledge/podaac/gotchas/grace-low-degree-replacements.md
    title: "Bundle gotcha: the degree-1 and C20/C30 series substituted in the mascon product"
  - id: recipe-mass
    resource: knowledge/podaac/recipes/grace-mass-to-sea-level.md
    title: "Bundle recipe: from a GRACE mass change to a sea level equivalent, with every uncertainty term"
  - id: recipe-budget
    resource: knowledge/podaac/recipes/sea-level-budget.md
    title: "Bundle recipe: the three terms of the budget, which product supplies each, and how the residual is read"
  - id: release-note
    resource: https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/gracefo/open/docs/GRACE_GRACE-FO_ReleaseNotes_JPL_MASCON.txt
    title: "JPL GRACE mascon solution release notes (RL06.3M version 4): the GAD added back over the ocean part of the mascons, and the July 2025 fix to it"
  - id: months-rl06
    resource: https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/gracefo/open/docs/GRACE_GRACE-FO_Months_RL06.csv
    title: "GRACE and GRACE-FO RL06 month list (PO.DAAC): the months the fixture removes are checked against it"
  - id: data-root
    resource: ../references/retrieval/sea-level-budget-root/RECORD.json
    title: "The stamped three-term data root committed beside this concept: the loaders' stamps, the corrections table, the manifest of the three term files, and SOURCES.json for the downloads"
  - id: loaders
    resource: skills/sea-level-budget/scripts/slb_data_root.py
    title: "The term loaders and the stamp assembler in the sea-level-budget skill's scripts (slb_altimetry_nasa_ssh.py, slb_steric_rg.py, slb_mass_mascons.py, slb_data_root.py), each with a selftest"
  - id: trend-ci
    resource: ecco-trend-ci.md
    title: "The one sanctioned trend method: the interval block every trend here carries, and the calibration behind it"
  - id: wcrp-2018
    resource: https://doi.org/10.5194/essd-10-1551-2018
    title: "WCRP Global Sea Level Budget Group (2018), Global sea-level budget 1993 to present, Earth System Science Data 10, 1551 to 1590"
  - id: frederikse-2020
    resource: https://doi.org/10.1038/s41586-020-2591-3
    title: "Frederikse and others (2020), The causes of sea-level rise since 1900, Nature 584, 393 to 397"
  - id: purkey-johnson-2010
    resource: https://doi.org/10.1175/2010JCLI3682.1
    title: "Purkey and Johnson (2010), Warming of global abyssal and deep Southern Ocean waters between the 1990s and 2000s: contributions to global heat and sea level rise budgets, Journal of Climate 23, 6336 to 6351 (the deep-steric term the 2018 budget carries)"
  - id: argo-doi
    resource: https://doi.org/10.17882/42182
    title: "Argo (2000 onward), Argo float data and metadata from the Global Data Assembly Centre (Argo GDAC), SEANOE"
  - id: roemmich-gilson-2009
    resource: https://doi.org/10.1016/j.pocean.2009.03.004
    title: "Roemmich and Gilson (2009), The 2004 to 2008 mean and annual cycle of temperature, salinity, and steric height in the global ocean from the Argo Program, Progress in Oceanography 82, 81 to 100 (the gridded Argo steric estimate)"
---

# Sea level budget closure from altimetry, Argo steric and GRACE-FO mass (attested)

**Placement, 2026-09-20 (ADR E, a computation is a skill).** This
concept came from the nasa-daac-knowledge bundle at
`knowledge/podaac/computations/sea-level-budget.md`, and the executor
and the attester it names now ship in this package under
`skills/sea-level-budget/scripts/`. The golden
`verification/sea_level_budget.py` names every script it does. The
executor `skills/sea-level-budget/scripts/sea_level_budget.py` changed
only where it resolves a path, so its sha256 moved from c1064cfce95c8471
to 9b94e156ba0de471 and no number in it did. The reference runs
`sea-level-budget` and `sea-level-budget-record` of
verification/reference_runs.yaml were re-run at the new paths and
reproduced every value stated below to the digit, each attested PASS.
The signature block is the one the maintainer left; the concept sits at
`status: draft` with no verified event added, and the maintainer
re-signs it after merge.

The sanctioned computation behind any receipted statement that the
global mean sea level budget closes, or does not, over a period: the
altimetric sea level from NASA-SSH against the ocean-mass term from the
GRACE-FO mascons plus the steric term from Argo-era hydrography, the
identity the closure convention states and the bookkeeping it
demands.[^convention-slbc][^wcrp-2018][^frederikse-2020] It is the
cross-product budget the ECCO-internal partition
(ecco-regional-sea-level.md) declared out of its scope, and it exists
in this bundle so that the corrections table the convention demands is
a set of receipt facts an attester checks rather than a paragraph a
reader trusts. Version 1 is proven on a synthetic fixture with a known
closure, and its real-data anchor is the stamped three-term data root
committed beside it, run for 2005 through 2016 in the reference run
below.[^data-root] A fixture receipt says in its caveats that it proves
the chain, not the ocean.

## Parameters

- `period` (string, required): an inclusive month range
  `YYYY-MM:YYYY-MM` within the record (the fixture spans 2005-01
  through 2022-12; a data root spans what its files hold).
- `bridge` (string, optional): a citation of the independent
  continuity evidence across the GRACE to GRACE-FO gap. Required for a
  period that crosses the gap (mass months on both sides of 2017-07
  through 2018-05); without it the run refuses.[^gotcha-gap]

## The identity and the bookkeeping

Each month of the period carries three global-mean values in
millimeters with a per-month uncertainty: altimetry from the NASA-SSH
record with its corrections as the product applies them,[^nasa-ssh]
steric from gridded Argo (the Roemmich and Gilson estimate is the
reference; the sampled depth floor is stated),[^argo-doi][^roemmich-gilson-2009]
and mass from the CRI-filtered mascons summed over the ocean mascons
per the mass recipe, with the product's formal uncertainty.[^mascons][^recipe-mass]
The residual is altimetry minus mass minus steric, month by month, and
the receipt carries the three series, their uncertainties and the
residual at full precision.

The corrections table of the convention travels as the receipt's
`bookkeeping` block, one entry per term where the term has a trap, and
the attester refuses a receipt missing any of them:[^convention-slbc]

- **GIA**, altimetry and mass: the mascon product arrives with one GIA
  model subtracted, and a trend compared across products under a
  different model attributes the model to the ocean.[^gotcha-gia]
- **Inverse barometer**, altimetry and mass: NASA-SSH has the dynamic
  atmospheric correction applied; the mass term states how atmospheric
  pressure over the ocean was handled, or the two disagree by a term
  that is not sea level.[^nasa-ssh] For the mascon product the release
  note answers: the GAD de-aliasing product (atmosphere and ocean) is
  added back over the ocean part of the mascons, so the product's ocean
  mass carries that loading, and a July 2025 fix corrected the amount
  added back over land/ocean mascons in files whose series extends past
  March 2025.[^release-note]
- **Reference frame**, altimetry and mass: the mass term's frame is
  set by the degree-1 series the product substituted, since the
  satellites do not sense it.[^gotcha-low-degree]
- **Effective smoothing**, altimetry and mass: the mascon footprint is
  three degrees and the coastal mascons leak land signal, so a
  global-mean mass term states its ocean mask and the leakage
  caveat.[^gotcha-leakage]
- **Low-degree replacements**, mass: the degree-1 and C20/C30 series
  the product applied, named, nothing re-applied.[^gotcha-low-degree]
- **Deep steric**: the sampled depth floor of the steric term and the
  systematic below it, stated as a value with its own uncertainty and
  never folded into the noise. The stated value, 0.1 mm per year with
  an uncertainty of 0.1, is the order of the term the 2018 budget
  carries below 2000 m, which it takes as the Purkey and Johnson 2010
  linear trend for 1990 to 2010 extrapolated: abyssal warming below
  4000 m, 0.053 with an uncertainty of 0.017, plus deep Southern Ocean
  warming between 1000 and 4000 m, 0.093 with an uncertainty of 0.081,
  in millimeters per year. It is a stated assumption until a real-data
  run states its own from the source it
  cites.[^wcrp-2018][^purkey-johnson-2010]
- **Gap handling**: the months missing from the period (the
  inter-mission gap and the battery-management months), the rule that
  a month with no solution in any term is a hole dropped from every
  term and never interpolated (the matching-period rule at the month),
  whether the period crosses the gap, and the bridge if it
  does.[^gotcha-gap]

## Trends, the combined uncertainty and the verdict

Every trend (the three terms and the residual) is fitted over the same
epochs, the months that carry all three terms, and carries the
interval block of the one sanctioned trend method.[^trend-ci] Where
the period has no missing month the block is that method verbatim
(the chain imported by path and named by hash), and the shared
attester chain binds it. Where months are missing the same method
statement is applied on the calendar epochs: the climatology removed
jointly with the trend as group means over the existing months of each
calendar month, ordinary least squares on the epochs, the lag-1
autocorrelation over adjacent-epoch residual pairs, the effective
sample size capped at the sample, Student's t on the effective degrees
of freedom. It reduces to the chain exactly when no month is missing,
and the attester recomputes it independently either way. Beside each
interval the receipt states the formal error the product's per-month
uncertainties propagate to the slope.

The combined uncertainty takes, per term, the larger of the sampling
half width and the formal error at the same confidence, combines the
three in quadrature, and states the deep-steric systematic separately,
adding its uncertainty to the bar rather than folding it in. The
verdict `closed_within_uncertainty` is true when the residual trend
minus the stated deep-steric value lies within that bar. A residual
that fails to close is read as a correction-consistency finding before
a missing-physics one: the bookkeeping block is the first thing a
reader audits, as the convention says.[^convention-slbc][^recipe-budget]

## The fixture and its known truth

`--fixture --seed N` generates the record deterministically from a
hash-based Gaussian stream (no numeric library in the path, so the
digest cannot drift with a release): monthly series 2005-01 through
2022-12; mass rising 2.1 mm per year with an 8.5 mm annual cycle
peaking in October, steric rising 1.3 with a 4.0 mm cycle peaking in
March, each with an interannual AR(1) component; a deep-steric trend
of 0.1 mm per year; altimetry equal to mass plus steric plus deep
steric plus noise at the stated uncertainty (1.2 mm; mass 1.5 to 1.9
in an annual pattern; steric 2.2 falling to 1.6 as the array
matured); and the mass months the real record lacks removed: the
2017-07 through 2018-05 gap, August and September 2018, and the
seventeen battery-management months from January 2011 through February
2017, which match the product's public month list from the fixture's
start in 2005 onward (checked 2026-09-13; the list also lacks June and
July 2002 and June 2003, before the fixture begins).[^months-rl06] `--fixture-offset MM` injects
an inter-mission offset into the mass series after the gap, zero by
default, so a bridged run across the gap has an offset to fail on. The
receipt records the seed, the offset, the fixture digest and the
generator's digest (the executor itself), and the attester regenerates
the fixture and compares every series value.

## The refusal rule

A run writes a refusal receipt (`refused: true`, a `reason_code` and
the reason in words) and exits 3, never a number, when the period
crosses the inter-mission gap and no bridge is bound
(`gap-without-bridge`); when any term, or the set of months carrying
all three, has fewer than 24 months in the period (`too-few-months`);
when the period lies outside the record (`period-outside-record`); or
when the chain refuses to state a term's interval
(`interval-not-stated`). The attester attests a refusal PASS only as a
refusal, with the reason reproduced from the period and the
regenerated fixture, and its verdict line carries the word refusal.

## The attester criterion (deterministic, consumer-side)

A run PASSES only when all hold: every declared field present; the
code hash is the sanctioned file; the `bundle` block names this
bundle's package, version and release lock digest and the `capability`
block (the package the run is evidence for) is well formed; a runtime
is named; the fixture regenerated at the receipt's seed hashes to the
receipt's digest, and so does the generator (for a data root, the
RECORD.json stamp is present); the series and the months used and
missing are what the regenerated fixture yields (1e-9); every trend,
interval, formal error, the combined uncertainty and the verdict
recompute from the series (1e-9 relative); the corrections table is
complete and the gap handling agrees with the months; and, on the
fixture with no injected offset, the known truth holds: the closure
gap lies within the bar, the verdict says closed, and each term's
trend is within 1 mm per year of the imposed one. The selftest covers
a pass, a hole-free period bound to the shared chain, eight tampers
each failing on its check, a wrong-release receipt, a tampered
computation, three refusals and a forged one, a bridged run across the
gap, the same receipt with its bridge stripped (fails bookkeeping),
and an injected offset that fails to close.

## Reference run

**Fixture run (seed 7, 2005-01 through 2016-12, measured
2026-09-13).** 128 of 144 months carry all three terms (16 mass
months missing). Altimetry +3.4553 mm per year, 95 percent interval
[+3.2943, +3.6163]; mass +2.0162, [+1.8889, +2.1435]; steric +1.3300,
[+1.2019, +1.4582]; residual +0.1091, [-0.0250, +0.2432]. Closure gap
+0.0091 mm per year against a bar of 0.3420 (quadrature of the term
uncertainties 0.2420, plus the deep-steric uncertainty 0.1);
`closed_within_uncertainty` true. The imposed truth is altimetry 3.5,
mass 2.1, steric 1.3 and a residual of 0.1, each inside its interval.
Those rates are the order of the 2018 budget's table for 2005 onward
(sea level 3.5 with an uncertainty of 0.2, full-depth thermosteric 1.3
with an uncertainty of 0.4, thermosteric plus GRACE ocean mass 3.6
with an uncertainty of 0.4, residual minus 0.1 with an uncertainty of
0.3, in millimeters per year), which is also the published comparison
the first real-data run reports against.[^wcrp-2018]
The refusal case the gate and the ocean-science golden exercise is
2016-01 through 2019-12 with no bridge: exit 3, attested as a
refusal. The registry entry `sea-level-budget` in
verification/reference_runs.yaml reruns the fixture run for the
re-attestation ritual.

**Real-data run (the stamped data root
sea-level-budget-root-2026-09-13, 2005-01 through 2016-12, measured
2026-09-13).** The three terms were built by the loaders under
the skill's loaders and stamped by the assembler: altimetry from 1,124
NASA-SSH V1.1 grids as monthly global means with the +0.3 mm per year
GIA convention; steric from the Roemmich and Gilson product as TEOS-10
steric height to 2000 dbar over the cells valid in every month; mass
from the JPL mascon CRI grid over the product's own ocean mask with
the formal error combined per mascon.[^loaders][^data-root] 127 of
144 months carry all three terms: sixteen mass months are missing
(the battery-management months the product's list names) and one
altimetry month, 2006-11, had too few grids. Altimetry +3.682 mm per
year, 95 percent half width 0.475; mass +2.299, half width 0.205,
and the provider's own ocean mass series carried in the data root
trends at +2.366 over the same months, inside that half width;
steric +1.104, half width 0.223; residual +0.279, interval [+0.092,
+0.466]. Closure gap +0.179 mm per year against a bar of 0.663
(quadrature of the term uncertainties 0.563, plus the deep-steric
uncertainty 0.1); `closed_within_uncertainty` true. Against the 2018
budget's table for 2005 onward, altimetry sits 0.2 high and mass 0.1
high, and the steric term 0.2 low as a 0 to 2000 m term against a
full-depth one, each inside the stated uncertainties.[^wcrp-2018] The
registry entry `sea-level-budget-record` reruns it, and the golden
verification/sea_level_budget.py verifies the stamp, reruns the
executor on the data root and attests the receipt on every change.

**Pass bar.** There is no measured tolerance to record: the verdict is
a comparison of the residual trend against the uncertainty the receipt
itself carries, and the attester recomputes both. The plausibility
band on the fixture (1 mm per year around the imposed trends) is a
sanity bound on the chain, not a science tolerance.

## Boundaries

One real-data run exists, over 2005 through 2016, a period that does
not cross the inter-mission gap; a run across the gap needs a bridge
citation and has not been made. The per-month uncertainties of the
altimetry and steric terms are stated noise floors, since neither
product ships an error field, and the mass term's formal error treats
mascons as independent; in the anchor run the sampling half width
was the larger term for all three. The altimetry term reaches 71
degrees of latitude, the steric term 64.5 S to 79.5 N, the mass term the whole
ocean, and the residual carries that mismatch in coverage. The
steric term below the sampling floor is an acknowledged systematic,
not a measurement. The verdict is about the global mean; a regional
budget adds the smoothing and leakage terms the convention lists and
is not this computation. Produced by Open Science Pillars, not a NASA
or JPL product.

**Verification.** The bundle-path sources are this bundle's own
concepts; the data root and its stamp are committed in this
repository and the real-data run was made and attested on 2026-09-13
from them.[^data-root] The mascon product's release note and month list were read
on 2026-09-13 and are the basis of the GAD entry and the fixture's
month list above;[^release-note][^months-rl06] every DOI was verified
against the Crossref registry the same day (title, authors, journal,
year); the 2018 budget paper was read in full on the journal's site,
and the deep-steric entry and the fixture paragraph cite what it
carries;[^wcrp-2018][^purkey-johnson-2010] the Nature abstract and the
SEANOE landing page were read;[^frederikse-2020][^argo-doi] the
Elsevier page sits behind a bot check, so Roemmich and Gilson 2009 is
cited on its registry record.[^roemmich-gilson-2009] The chain is verified on every
change by the golden verification/sea_level_budget.py, which runs the
attester's selftest and the end-to-end fixture run and refusal.

[^convention-slbc]: knowledge/podaac/conventions/sea-level-budget-closure.md, the corrections table and the consistency requirements
[^nasa-ssh]: knowledge/podaac/datasets/nasa-ssh.md, the altimetry term's product, its dynamic atmospheric correction and its era dependence
[^mascons]: knowledge/podaac/datasets/grace-fo-mascons.md, the mass term's product and its formal uncertainty grids
[^gotcha-gia]: knowledge/podaac/gotchas/grace-gia-correction.md
[^gotcha-leakage]: knowledge/podaac/gotchas/grace-coastal-leakage.md
[^gotcha-gap]: knowledge/podaac/gotchas/grace-intermission-gap.md, the hole, the missing months and the bridging evidence
[^gotcha-low-degree]: knowledge/podaac/gotchas/grace-low-degree-replacements.md
[^recipe-mass]: knowledge/podaac/recipes/grace-mass-to-sea-level.md, the mascon sum, the trend on the epochs and the gigatonne to millimeter constant
[^recipe-budget]: knowledge/podaac/recipes/sea-level-budget.md, the three terms and how the residual is read
[^trend-ci]: computations/ecco-trend-ci.md, the sanctioned trend method behind every interval here
[^wcrp-2018]: WCRP Global Sea Level Budget Group (2018), Earth System Science Data 10, doi:10.5194/essd-10-1551-2018
[^frederikse-2020]: Frederikse and others (2020), Nature 584, doi:10.1038/s41586-020-2591-3
[^argo-doi]: Argo float data and metadata from the Global Data Assembly Centre, doi:10.17882/42182
[^roemmich-gilson-2009]: Roemmich and Gilson (2009), Progress in Oceanography 82, doi:10.1016/j.pocean.2009.03.004
[^release-note]: JPL GRACE mascon solution release notes, RL06.3M version 4
[^months-rl06]: GRACE and GRACE-FO RL06 month list, PO.DAAC
[^purkey-johnson-2010]: Purkey and Johnson (2010), Journal of Climate 23, doi:10.1175/2010JCLI3682.1
[^data-root]: references/retrieval/sea-level-budget-root/RECORD.json, the stamped data root
[^loaders]: skills/sea-level-budget/scripts, the term loaders and the stamp assembler
