---
type: Attested Computation
spheres: [hydrosphere]
title: "Ocean heat content change from gridded Argo, 0 to 700 and 0 to 2000 dbar (attested)"
description: "Sanctioned computation of the open-ocean heat content change over a stated window from the Roemmich and Gilson gridded Argo product, for the 0 to 700 dbar and 0 to 2000 dbar layers: the monthly anomaly series against the product's 2004 to 2018 climatology, the rate with the sanctioned interval, the change the rate implies from the first year of the window to the last, the endpoint change read directly, the residual and the combined uncertainty, a verdict consistent_within_uncertainty, the ocean below 2000 m as a stated omission with its published rate, the rates per unit area, the distance from the published Argo-era rate, and a refusal (exit 3, never a number) for a window that leaves the product's coverage. Proven on a synthetic fixture with a planted change recovered and anchored on a real-data run over 2006 through 2020 on the stamped data root."
tags: [argo, roemmich-gilson, ocean-heat-content, teos-10, conservative-temperature, earth-heat-inventory, deep-ocean, attested]
runtime: python
parameters:
  - { name: window, type: string, required: true }
  - { name: depth, type: integer, required: true }
computation: skills/argo-ohc/scripts/argo_ohc.py
executor:
  resource: skills/argo-ohc/scripts/argo_ohc.py
  receipt: [run_id, computation, code_sha256, capability, bundle, runtime, generated_utc, data, bound_parameters, refused, months, series, terms, trend_ZJ_yr, change_ZJ, endpoint_change_ZJ, residual, combined_uncertainty, verdict, anchor, bookkeeping, known_truth, caveats]
attester:
  resource: skills/argo-ohc/scripts/argo_ohc_check.py
generated: { by: knowledge-seeder/claude, at: 2026-09-15T16:00:00Z }
verified:
  - { by: human:PaulMRamirez, at: 2026-09-15T14:26:35Z, role: maintainer, source: https://github.com/open-science-pillars/ocean-science/pull/56 }
  - { by: human:PaulMRamirez, at: 2026-09-16T05:49:23Z, role: maintainer, source: https://github.com/open-science-pillars/ocean-science/pull/63 }
status: draft
stale_after: 2027-03-15
sources:
  - id: dataset
    resource: knowledge/podaac/datasets/roemmich-gilson-argo-climatology.md
    title: "This bundle's Roemmich and Gilson dataset concept: the 2019 release, the grid, the masks, the extension files and the uncertainty statement"
  - id: gotcha-floor
    resource: knowledge/podaac/gotchas/rg-sampled-depth-floor.md
    title: "This bundle's gotcha: the product stops at 1975 dbar, so a heat content from it is a 0 to 2000 dbar quantity and the deep ocean is a separate term"
  - id: gotcha-coverage
    resource: knowledge/podaac/gotchas/rg-coverage-excludes-high-latitudes-and-marginal-seas.md
    title: "This bundle's gotcha: the grid starts at 64.5S and a mean labelled global from it is a mean over the mapped, masked open ocean"
  - id: gotcha-baseline
    resource: knowledge/podaac/gotchas/rg-anomaly-against-a-fixed-climatology.md
    title: "This bundle's gotcha: the anomalies are departures from the fixed 2004 to 2018 climatology, and the extension files keep that reference"
  - id: recipe
    resource: knowledge/podaac/recipes/argo-ohc.md
    title: "This bundle's recipe: the layer, the domain, the baseline and the deep term it does not carry"
  - id: rg-page
    resource: https://sio-argo.ucsd.edu/RG_Climatology.html
    title: "Scripps RG Argo Climatology product page (read 2026-09-15): the 2019 release, the climatology and extension file links through August 2026, the global-average series computed under the file's mask"
  - id: rg-files
    resource: https://sio-argo.ucsd.edu/RG/RG_ArgoClim_Temperature_2019.nc.gz
    title: "The 2004 to 2018 temperature and salinity climatology files and the 92 monthly extension files 2019-01 through 2026-08, downloaded by the loader on 2026-09-15 and hashed in the data root's stamps and SOURCES.json; the two base files hash to the same digests the provider bundle's steric loader recorded on 2026-09-13"
  - id: teos-10
    resource: https://www.teos-10.org/pubs/TEOS-10_Manual.pdf
    title: "IOC, SCOR and IAPSO (2010), The international thermodynamic equation of seawater 2010 (TEOS-10): calculation and use of thermodynamic properties, IOC Manuals and Guides 56; section 3.3 (Conservative Temperature, the exact constant cp0 in equation 3.3.3) and appendix A.18 (Conservative Temperature as the heat content variable), read 2026-09-15"
  - id: vs-2023
    resource: https://doi.org/10.5194/essd-15-1675-2023
    title: "von Schuckmann and others (2023), Heat stored in the Earth system 1960 to 2020: where does the energy go?, Earth System Science Data 15, 1675 to 1709 (read in full 2026-09-15 on the journal's site: Table 1 for the 2006 to 2020 layer rates and the ocean-surface factor, section 2 for the deep ocean below 2000 m and the Earth's surface area convention; Crossref record verified the same day)"
  - id: roemmich-2015
    resource: https://doi.org/10.1038/nclimate2513
    title: "Roemmich and others (2015), Unabated planetary warming and its ocean structure since 2006, Nature Climate Change 5, 240 to 245 (the 0 to 2000 m heat gain of 0.4 to 0.6 W per m2 over 2006 to 2013 from three Argo-only analyses, this product among them; the abstract read on the publisher's landing page and the Crossref record verified 2026-09-15)"
  - id: purkey-johnson-2010
    resource: https://doi.org/10.1175/2010JCLI3682.1
    title: "Purkey and Johnson (2010), Warming of global abyssal and deep Southern Ocean waters between the 1990s and 2000s: contributions to global heat and sea level rise budgets, Journal of Climate 23, 6336 to 6351 (the abyssal and deep Southern Ocean warming the deep rate descends from; Crossref record and abstract read 2026-09-15)"
  - id: desbruyeres-2016
    resource: https://doi.org/10.1002/2016GL070413
    title: "Desbruyeres and others (2016), Deep and abyssal ocean warming from 35 years of repeat hydrography, Geophysical Research Letters 43 (the trend below 2000 m over 1991 to 2010 equivalent to 0.065 plus or minus 0.040 W per m2 of the Earth's surface; Crossref record and abstract read 2026-09-15)"
  - id: roemmich-gilson-2009
    resource: https://doi.org/10.1016/j.pocean.2009.03.004
    title: "Roemmich and Gilson (2009), The 2004 to 2008 mean and annual cycle of temperature, salinity, and steric height in the global ocean from the Argo Program, Progress in Oceanography 82, 81 to 100 (the mapping method; the Crossref registry record verified 2026-09-15, the publisher's page behind a bot check)"
  - id: ecco-ohc-recipe
    resource: https://github.com/open-science-pillars/nasa-daac-knowledge/blob/nasa-daac-knowledge--v2026.9.2/knowledge/podaac/recipes/ecco-ocean-heat-content.md
    title: "The provider bundle's ECCO ocean heat content recipe (knowledge/podaac/recipes/ecco-ocean-heat-content.md at the nasa-daac-knowledge--v2026.9.2 release tag): the model-based counterpart, and its ocean surface area anchor of 3.5801E+08 km2 on the ECCO grid"
  - id: data-root
    resource: ../references/retrieval/argo-ohc-root/RECORD.json
    title: "The stamped data root committed beside this concept: the loader's stamps, the bookkeeping table with the anchor, the manifest of the five files, and SOURCES.json for the downloads"
  - id: loaders
    resource: skills/argo-ohc/scripts/ohc_data_root.py
    title: "The loader and the stamp assembler in the argo-ohc skill's scripts (ohc_rg_loader.py, ohc_data_root.py), each with a selftest"
---

# Ocean heat content change from gridded Argo (attested)

**Placement, 2026-09-20 (ADR E, a computation is a skill).** This
concept came out of `knowledge/references/` in this package, and the
executor and the attester it names now ship in this package under
`skills/argo-ohc/scripts/`. The golden `verification/argo_ohc.py` names
every script it does. The executor `skills/argo-ohc/scripts/argo_ohc.py`
changed only where it resolves a path, so its sha256 moved from
889817705d09b691 to f48f5caf58c917d8 and no number in it did. The
reference runs `argo-ohc-2000` and `argo-ohc-700` of
verification/reference_runs.yaml were re-run at the new paths on the
committed root and reproduced every value stated below to the digit,
each attested PASS. The receipt run digests quoted below were measured
at an earlier release and fold in the package version and release lock
as well as the code, so they are left as they were rather than restated
from a run of this branch. The signature block is the one the maintainer
left; the concept sits at `status: draft` with no verified event added,
and the maintainer re-signs it after merge.

The sanctioned computation behind any receipted statement of how much
heat the upper ocean gained over a window from the Roemmich and Gilson
gridded Argo product: the 0 to 700 dbar or 0 to 2000 dbar heat content
anomaly per month, summed over the product's mapped open-ocean domain,
its rate over the window with an interval, the change that rate
implies from the first year of the window to the last against the
change read directly from the two years' means, and the ocean below
2000 m named as the term the product cannot supply.[^dataset][^recipe]
It is the observational counterpart of the provider bundle's ECCO
ocean heat content computation
(knowledge/podaac/recipes/ecco-ocean-heat-content.md), which sums
potential temperature over a model grid, and it exists in this bundle
so that the layer, the domain, the baseline and the deep omission are
receipt facts an attester checks rather than a paragraph a reader
trusts.[^ecco-ohc-recipe] Version 1 is proven on a synthetic fixture
with a planted change, and its real-data anchor is the stamped data
root committed beside it, run for 2006 through 2020 in the reference
run below.[^data-root] A fixture receipt says in its caveats that it
proves the chain, not the ocean.

## Parameters

- `window` (string, required): an inclusive month range
  `YYYY-MM:YYYY-MM` within the record (the fixture spans 2005-01
  through 2024-12; a data root spans what its stamp holds, 2004-01
  through 2026-08 for the committed root).
- `depth` (integer, required): the layer floor in dbar, 700 or 2000.
  The receipt names the CSV and the stamp it read for that layer.

## The quantity and the bookkeeping

Heat content is written in Conservative Temperature, which is
proportional to potential enthalpy and is the variable the ocean
conserves as heat; the constant is cp0, exactly 3991.86795711963 J per
kg per K by definition.[^teos-10] The loader takes the product's in
situ temperature and practical salinity on the 58 pressure levels,
converts through gsw to Absolute Salinity, Conservative Temperature
and in situ density, integrates cp0 times density times Conservative
Temperature over each column's height (the layer of each level bounded
by the midpoints to its neighbours, the top from 0 dbar, the bottom
cut at the floor, pressure to height at the cell's latitude), subtracts
the same integral of the product's 2004 to 2018 mean field, and sums
over the fixed cell set with each cell's spherical area from the
grid's latitude bounds.[^loaders][^dataset] The value is in
zettajoules over the mapped domain, never scaled to the global ocean.

The bookkeeping table of the data root travels as the receipt's
`bookkeeping` block, and the attester refuses a receipt missing any
of it:

- **Climatology**: the RG 2004 to 2018 mean field, the reference of
  every anomaly in the base files and the extension files alike; a
  value is that reference's departure, and a difference between two
  months is a change that does not depend on the
  baseline.[^gotcha-baseline]
- **Anomaly convention**: value_ZJ is the layer's heat content over
  the domain minus the mean field's over the same domain; zero is the
  climatological state.[^gotcha-baseline]
- **Coverage**: the fixed mask is the set of columns the product maps
  at all 58 levels in every month written, which is the open ocean
  mapped to 2000 dbar; the grid starts at 64.5S, and the marginal
  seas mapped to a shallower limit drop out; the stamp states the cell
  count, the latitude band and the domain area in square meters, and
  both layers share the one mask.[^gotcha-coverage]
- **Deep omission**: the product stops at 1975 dbar. The ocean below
  2000 m is a real term of the full-depth change and is not in any
  term of this receipt; the published rate below 2000 m, 0.97 plus or
  minus 0.48 ZJ per year (0.06 plus or minus 0.03 watts per square
  meter of the Earth's surface) over 1992 to 2020 as a constant linear
  trend from repeat hydrography, is stated beside the terms and never
  added.[^gotcha-floor][^vs-2023][^purkey-johnson-2010][^desbruyeres-2016]
- **Uncertainty**: the product ships no error field, so the loader's
  per-month uncertainty is a stated noise floor (the standard
  deviation of adjacent-month differences of the finished series over
  the square root of two), and the computation takes the larger of
  its formal propagation and the sampling half width of the
  trend.[^dataset]
- **Anchor**: the published 2006 to 2020 rates for the two layers in
  watts per square meter of the Earth's surface, 0.39 plus or minus
  0.1 for 0 to 700 m and 0.62 plus or minus 0.2 for 0 to 2000 m,
  with the ocean-surface factor of 0.61 the source uses for the
  ocean between 60S and 60N deeper than 300 m, so the receipt can
  state the run's distance in both conventions.[^vs-2023]
- **Window handling**: a calendar month of the window with no value
  is a hole dropped from the fit and never interpolated; the endpoint
  means need all twelve months of the first and last year.

## The terms, the residual and the verdict

The rate is a least-squares slope over the calendar epochs of the
window with the annual cycle removed jointly as calendar-month group
means, its 95 percent interval under a lag-1 autocorrelated residual
(the effective sample size capped at the sample, Student's t on the
effective degrees of freedom), and beside it the formal error the
per-month uncertainties propagate to the slope; the term's
uncertainty is the larger of the two. The change is the rate times
the span between the centres of the first and last year of the
window, with the same uncertainty scaled; the endpoint change is the
mean of the last twelve months minus the mean of the first twelve,
with the per-month floor propagated at 95 percent and the variance of
each twelve-month mean inflated by (1 + r1) over (1 - r1), r1 the
lag-1 autocorrelation of the trend's residuals, so that the floor's
white noise is not the whole statement of a mean over autocorrelated
months. The residual is
endpoint change minus change, the combined uncertainty their
quadrature, and the verdict `consistent_within_uncertainty` is true
when the residual lies within it: a record that departs from a line
over the window says so here. The receipt also states the rate per
unit area of the domain and per unit area of the Earth's surface (4
pi R squared with the 6371 km mean radius, the convention the
published inventories use), and, where the record carries an anchor
for the layer, the distance from it in both
conventions.[^vs-2023][^teos-10]

## The fixture and its known truth

`--fixture --seed N --depth D` generates the record deterministically
from a hash-based Gaussian stream (no numeric library in the path, so
the digest cannot drift with a release): a monthly series 2005-01
through 2024-12 with a planted rate of 6.3 ZJ per year for 0 to 700
dbar and 10.0 for 0 to 2000 dbar (the order of the published 2006 to
2020 rates converted with the Earth's surface area), an annual cycle
peaking in March, an interannual AR(1) component, and noise at the
stated per-month uncertainty.[^vs-2023] The receipt carries the seed,
the depth, the fixture digest, the generator's digest (the executor
itself), the planted truth, and a `known_truth` block with the planted
rate and change beside the recovered ones and whether the planted rate
lies inside the interval and the planted change within the change's
uncertainty; the attester regenerates the fixture and compares every
value.

## The refusal rule

A run writes a refusal receipt (`refused: true`, a `reason_code` and
the reason in words) and exits 3, never a number, when the window
leaves the record's coverage (`window-outside-coverage`), when fewer
than 24 months, or fewer than twelve in the first or last year, carry a
value (`too-few-months`), or when the trend's interval cannot be
stated (`interval-not-stated`). The attester attests a refusal PASS
only as a refusal, with the reason reproduced from the window and the
record's coverage or the regenerated fixture, and its verdict line
reads `PASS refusal`.

## The attester criterion (deterministic, consumer-side)

A run PASSES only when all hold, one `PASS name` or `FAIL name:
reason` line per check: every declared field present; the code hash is
the sanctioned file; the `bundle` block names this repository's
package, version and release lock digest and the `capability` block is
well formed; a runtime is named; the fixture regenerated at the
receipt's seed and depth hashes to the receipt's digest and so does the
generator (for a data root, the record's name, digest, files and stamp
are present); the months used and missing partition the window and the
series is what the regenerated fixture yields (1e-9); the trend, its
interval and formal error, the change, the endpoint change, the
residual, the combined uncertainty, the verdict, the rates per unit
area and the anchor distance recompute from the series (1e-9 relative,
with the attester's own Student's t integrated from the density); the
bookkeeping statements are complete, the deep omission is the
sanctioned published statement and the window handling agrees with
the months; (for a data root given with `--data-root`, the record,
the CSV and the stamp in the tree hash to the receipt's digests, and a
data-root refusal is reproduced from the tree; without the tree the
digests are reported as not verified and a data-root refusal fails);
and the stated plausibility bounds hold: the trend within
40 ZJ per year of zero (four times the published 0 to 2000 m rate),
the per-month uncertainty positive and below 50 ZJ, the domain area
between 1e14 and 4e14 square meters, and on the fixture the planted
rate within 1.5 ZJ per year of the recovered one with the
`known_truth` block agreeing with the recompute. The selftest covers a
pass on both layers, ten tampers each failing on its check, a
wrong-release receipt, a tampered computation, three refusals and a
forged one, and a data root built in a temporary directory that runs,
attests against its tree, fails on three forged digests when the tree
is given, refuses a window past its stamp and a window too short
(reproduced against the tree, failed without it), and rejects an
edited tree.

## Reference run

A receipt's `run_id` digests the receipt without its timestamp, so it
is bound to the runtime name and, on a data root, to the tree's path
as recorded (package-relative when the tree sits under this
repository); the ids below were made with the runtime name
`claude-code` on the committed root and reproduce with that name on
any machine. A data-root receipt is attested with `--data-root` so the
attester rehashes the tree.

**Fixture run (seed 7, 0 to 2000 dbar, 2005-01 through 2016-12,
measured 2026-09-15; receipt run sha256:4f5e4c0f60e48ff8).** 144 of
144 months used. Trend +10.0594 ZJ per year, 95 percent interval
[+9.5547, +10.5640] (lag-1 autocorrelation +0.4786, effective sample
50.78 of 144); change +110.6532 ZJ over the 11.00 years between the
first and last year centres against a planted change of 110.0;
endpoint change +110.4110 ZJ; residual minus 0.2423 ZJ against a bar
of 7.7370; `consistent_within_uncertainty` true; the planted rate of
10.0 lies inside the interval and the planted change within the
change's uncertainty. The refusal case the golden exercises is
2001-01 through 2016-12 with depth 700: exit 3, attested as a refusal.

**Real-data run (the stamped data root argo-ohc-root-2026-09-15, 2006-01 through
2020-12, measured 2026-09-15).** The two terms were built by the
loader from the product's two climatology files and the 92 extension
files through 2026-08, over the fixed mask of 30,650 cells (latitudes
64.5S to 65.5N, domain area 3.0598e+14 square meters, 85.5 percent of the
ECCO ocean surface area the provider bundle's recipe anchors), and
stamped by the assembler.[^loaders][^data-root][^rg-files][^ecco-ohc-recipe]
180 of 180 months carry a value in each layer.

- 0 to 2000 dbar (receipt run sha256:a3f1f2cf52272fe3): trend +9.6664 ZJ per year,
  95 percent interval [+8.4546, +10.8782], the per-month floor
  9.8442 ZJ; change +135.3300 ZJ over the 14.00 years between the
  first and last year centres; endpoint change +110.0473 ZJ; residual
  minus 25.2827 against a bar of 24.1291 (the endpoint uncertainty
  17.1580 with the autocorrelation inflation 4.745, the change
  uncertainty 16.9647); `consistent_within_uncertainty` false. Per unit area: 1.0011 watts per square meter of the
  domain, 0.6005 of the Earth's surface.
- 0 to 700 dbar (receipt run sha256:ac1fa7bf8e15c437): trend +5.9498 ZJ per year,
  95 percent interval [+4.9916, +6.9080], floor 7.1262 ZJ; change
  +83.2973 ZJ; endpoint change +65.6873 ZJ; residual minus 17.6100 against a
  bar of 18.6705 (endpoint uncertainty 12.9861 with the inflation
  5.187, change uncertainty 13.4152); `consistent_within_uncertainty`
  true. Per unit
  area: 0.6162 of the domain, 0.3696 of the Earth's surface.

**The verdict on the record.** The change the linear rate implies
exceeds the endpoint change by 25 ZJ (0 to 2000 dbar) and 18 ZJ (0 to
700 dbar). The 0 to 2000 dbar layer fails
`consistent_within_uncertainty` by about one zettajoule against its
bar of 24, and the 0 to 700 dbar layer passes by about one against
its bar of 19. The record over 2006 through 2020 is not a line: the
annual means sit low and flat through 2012 and rise faster after, and
2020 sits just below 2019, so a rate fitted through the whole window
overstates the first-year to last-year difference. The bar is partly
the floor: the endpoint uncertainty propagates the loader's stated
per-month floor, inflated for the residuals' lag-1 autocorrelation
but with no term for the mapping or the interannual variability the
floor does not see, so it is a lower bound on the endpoint change's
uncertainty and a verdict this close to its bar is a statement about
the record's shape, not a finding. The attester confirms both numbers,
and a reader quoting the change over this window quotes the endpoint
change and the rate side by side, as the receipt does. The product page's note that the
early years lean warm toward the baseline where the array was sparse
bears on the low start of the window and is recorded in the dataset
concept.[^dataset][^rg-page]

**The anchor.** The published 2006 to 2020 rates are 0.62 plus or
minus 0.2 watts per square meter of the Earth's surface for 0 to 2000
m and 0.39 plus or minus 0.1 for 0 to 700 m, LOWESS trends of an
ensemble of products over the ocean between 60S and 60N deeper than
300 m with an ocean-surface factor of 0.61.[^vs-2023] The run's rate
per unit Earth surface lands 0.0195 watts per square meter below the
0 to 2000 m anchor (0.10 of its uncertainty) and 0.0204 below the
0 to 700 m anchor (0.20 of its uncertainty). Per unit area of the
ocean the anchors read 1.02 plus or minus 0.33 and 0.64 plus or minus
0.16 watts per square meter, against the run's 1.0011 and 0.6162
over its own domain. The run's domain omits the ocean poleward of the
grid, the marginal seas mapped short and the shelves, and the
published estimate omits the shallow ocean above 300 m depth and the
ocean poleward of 60 degrees, so part of any distance is a difference
of domains; the receipt's per-unit-domain-area rate is the number a
reader compares with an ocean-area rate. The Argo-era 0 to 2000 m
heat gain of 0.4 to 0.6 watts per square meter over 2006 to 2013 from
three Argo-only analyses, this product among them, is the earlier
published figure the run is consistent with in the same
convention.[^roemmich-2015]

**Pass bar.** There is no measured tolerance to record: the verdict is
a comparison of the residual against the uncertainty the receipt
itself carries, and the attester recomputes both. The plausibility
bounds and the fixture band are sanity bounds on the chain, not
science tolerances, and the anchor distance is stated, not gated.

## Boundaries

One real-data run exists per layer, over 2006 through 2020, the
window the anchor's source uses; a window into the extension months
runs but is anchored to nothing published here. The value is the
mapped open ocean's, not the global ocean's, and the coverage
statement is the first thing a reader compares before a number. The
per-month uncertainty is a stated noise floor, since the product
ships no error field, and the interval is a statement about sampling
under an AR(1) residual model, not about the mapping. The ocean below
2000 m is an acknowledged omission with a published rate, not a
measurement. The early-year anomalies lean toward the baseline where
the array was sparse, which the dataset concept records and this
computation does not correct.[^dataset] Produced by Open Science
Pillars, not a Scripps or Argo product.

**Verification.** The bundle-path sources are this bundle's own
concepts; the data root and its record are committed in this
repository and the real-data run was made and attested on 2026-09-15
from them.[^data-root] The product page and the product files were
read on 2026-09-15, the two base files hashing to the digests the
provider bundle's steric loader recorded two days earlier;[^rg-page][^rg-files]
the TEOS-10 manual's section 3.3 and appendix A.18 were read for the
constant and the variable;[^teos-10] the Earth heat inventory paper
was read in full on the journal's site and is the source of the
anchor and the deep rate;[^vs-2023] every DOI was verified against the
Crossref registry the same day (title, authors, journal, year), the
Nature abstract was read on the publisher's landing page, and the
Elsevier page sits behind a bot check, so Roemmich and Gilson 2009 is
cited on its registry record.[^roemmich-2015][^purkey-johnson-2010][^desbruyeres-2016][^roemmich-gilson-2009]
The chain is verified on every change by the golden
verification/argo_ohc.py, which runs the attester's selftest, the
fixture run and refusal, the loader and data-root selftests, the
record check and the record runs.

[^dataset]: knowledge/podaac/datasets/roemmich-gilson-argo-climatology.md, the files, the grid, the masks and the uncertainty statement
[^gotcha-floor]: knowledge/podaac/gotchas/rg-sampled-depth-floor.md
[^gotcha-coverage]: knowledge/podaac/gotchas/rg-coverage-excludes-high-latitudes-and-marginal-seas.md
[^gotcha-baseline]: knowledge/podaac/gotchas/rg-anomaly-against-a-fixed-climatology.md
[^recipe]: knowledge/podaac/recipes/argo-ohc.md, the layer, the domain, the baseline and the deep term
[^rg-page]: Scripps RG Argo Climatology product page, read 2026-09-15
[^rg-files]: the RG climatology and extension files, downloaded and hashed 2026-09-15
[^teos-10]: TEOS-10 Manual, IOC Manuals and Guides 56, section 3.3 and appendix A.18
[^vs-2023]: von Schuckmann and others (2023), Earth System Science Data 15, doi:10.5194/essd-15-1675-2023
[^roemmich-2015]: Roemmich and others (2015), Nature Climate Change 5, doi:10.1038/nclimate2513
[^purkey-johnson-2010]: Purkey and Johnson (2010), Journal of Climate 23, doi:10.1175/2010JCLI3682.1
[^desbruyeres-2016]: Desbruyeres and others (2016), Geophysical Research Letters 43, doi:10.1002/2016GL070413
[^roemmich-gilson-2009]: Roemmich and Gilson (2009), Progress in Oceanography 82, doi:10.1016/j.pocean.2009.03.004
[^ecco-ohc-recipe]: knowledge/podaac/recipes/ecco-ocean-heat-content.md in nasa-daac-knowledge, the ECCO-based counterpart
[^data-root]: references/retrieval/argo-ohc-root/RECORD.json, the stamped data root
[^loaders]: skills/argo-ohc/scripts, the loader and the stamp assembler
