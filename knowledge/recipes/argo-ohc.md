---
type: recipe
spheres: [hydrosphere]
title: "Ocean heat content change from gridded Argo: the layer, the domain, the baseline and the deep term it does not carry"
description: "How an ocean heat content change for 0 to 700 m and 0 to 2000 m is read off the Roemmich and Gilson gridded Argo product: Conservative Temperature and in situ density through TEOS-10, the heat capacity constant cp0, layer thickness from the pressure levels, cell area from the grid's latitude bounds under the product's own mask, the 2004 to 2018 climatology as the anomaly baseline, a rate with an interval over a stated window, the deep ocean below 2000 m stated as an omission with its published rate, and the published Argo-era rate the result is anchored to."
tags: [argo, roemmich-gilson, ocean-heat-content, teos-10, conservative-temperature, recipe, deep-ocean, earth-heat-inventory]
generated: { by: knowledge-seeder/claude, at: 2026-09-15T16:00:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-15T14:26:35Z, role: maintainer, source: https://github.com/open-science-pillars/ocean-science/pull/56 }
status: stable
stale_after: 2027-03-15
inputs:
  - dataset: ../datasets/roemmich-gilson-argo-climatology.md
  - temperature_and_salinity: "the RG 2004 to 2018 mean fields plus each month's anomaly, from the two climatology files through 2018-12 and one extension file per month after, on the 1 degree grid over 58 pressure levels from 2.5 to 1975 dbar"
  - thermodynamics: "TEOS-10 through gsw: Absolute Salinity from practical salinity, Conservative Temperature from in situ temperature, in situ density, and the heat capacity constant cp0 of 3991.86795711963 J per kg per K"
  - geometry: "layer thickness from the midpoints between pressure levels (the top layer from 0 dbar, the bottom cut at the layer floor) converted to height at the cell's latitude; cell area from the grid's 1 degree latitude bounds on a 6371 km sphere; the fixed mask of columns the product maps at all 58 levels in every month"
  - method: "the attested computation ../computations/argo-ohc.md: the monthly series over a window, the rate with the sanctioned interval, the change the rate implies from the first year to the last, the endpoint change read directly, the residual, the combined uncertainty, the verdict, the deep omission as a stated term, and the anchor distance"
expected:
  - quantity: "the identity"
    statement: "the heat content of a layer over the mapped domain is cp0 times the integral of density times Conservative Temperature over the layer's volume; a value against the 2004 to 2018 mean field is an anomaly, and the difference between two months is a heat content change; the full-depth change is this layer's change plus the deep ocean's, which the product does not carry"
  - quantity: "numeric anchor"
    statement: "the real-data run over 2006-01 through 2020-12 on the stamped data root, its rate per unit Earth surface against the published 2006 to 2020 rates of 0.39 plus or minus 0.1 (0 to 700 m) and 0.62 plus or minus 0.2 (0 to 2000 m) watts per square meter, with the distances recorded in ../computations/argo-ohc.md"
expected_uncertainty:
  - quantity: "per layer"
    statement: "the larger of the sampling half width of the trend under a lag-1 autocorrelated residual and the formal error the per-month noise floor propagates; the product ships no error field, so the floor is the loader's statement, not the product's"
  - quantity: "deep ocean"
    statement: "the ocean below 2000 m is not measured by the core Argo array; the published rate of 0.97 plus or minus 0.48 ZJ per year (0.06 plus or minus 0.03 watts per square meter) over 1992 to 2020 is stated beside the terms and never added; a result quoted as full depth without it has omitted a real term"
  - quantity: "domain"
    statement: "the value is the mapped open ocean's, about 61 percent of the Earth's surface in the published inventories' convention and the RG mask's own fraction in the stamp; a comparison with a global product is a comparison of domains unless both are put per unit area of their own domain"
sources:
  - id: computation
    resource: ../computations/argo-ohc.md
    title: "The attested computation this recipe walks: the terms, the fixture, the refusal rule, the reference run and the anchor"
  - id: dataset
    resource: ../datasets/roemmich-gilson-argo-climatology.md
    title: "This bundle's Roemmich and Gilson dataset concept: the files, the grid, the masks, the uncertainty statement"
  - id: gotcha-floor
    resource: ../gotchas/rg-sampled-depth-floor.md
    title: "This bundle's gotcha: the product stops at 1975 dbar, so a heat content from it is a 0 to 2000 dbar quantity"
  - id: gotcha-coverage
    resource: ../gotchas/rg-coverage-excludes-high-latitudes-and-marginal-seas.md
    title: "This bundle's gotcha: the grid starts at 64.5S and the product's global average masks out the marginal seas and the Arctic"
  - id: gotcha-baseline
    resource: ../gotchas/rg-anomaly-against-a-fixed-climatology.md
    title: "This bundle's gotcha: the anomalies are departures from the fixed 2004 to 2018 climatology"
  - id: teos-10
    resource: https://www.teos-10.org/pubs/TEOS-10_Manual.pdf
    title: "IOC, SCOR and IAPSO (2010), The international thermodynamic equation of seawater 2010 (TEOS-10): calculation and use of thermodynamic properties, IOC Manuals and Guides 56; section 3.3 defining Conservative Temperature and cp0, appendix A.18 on Conservative Temperature as the heat content variable (read 2026-09-15)"
  - id: vs-2023
    resource: https://doi.org/10.5194/essd-15-1675-2023
    title: "von Schuckmann and others (2023), Heat stored in the Earth system 1960 to 2020: where does the energy go?, Earth System Science Data 15, 1675 to 1709; Table 1 for the 2006 to 2020 layer rates and section 2 for the deep ocean below 2000 m (read in full 2026-09-15 on the journal's site; the Crossref record verified the same day)"
  - id: ecco-ohc
    resource: https://github.com/open-science-pillars/nasa-daac-knowledge/blob/nasa-daac-knowledge--v2026.9.2/knowledge/podaac/recipes/ecco-ocean-heat-content.md
    title: "The provider bundle's ECCO ocean heat content recipe (knowledge/podaac/recipes/ecco-ocean-heat-content.md at the nasa-daac-knowledge--v2026.9.2 release tag): the model-based counterpart on the native grid, with its own attested computation and its ocean area anchor"
---

# Ocean heat content change from gridded Argo

The quantity is the heat content of a layer of the ocean, cp0 times
the integral of in situ density times Conservative Temperature over
the layer's volume, and the only physically meaningful number is its
change between two times, because the absolute value is set by the
temperature scale's zero.[^teos-10][^computation] On the Roemmich and
Gilson product that change is an anomaly against the product's 2004
to 2018 mean field, and every extension month keeps the same baseline,
so a series that joins the climatology months and the extension months
sits on one reference; a re-baseline moves the intercept and not a
change between two months.[^gotcha-baseline][^dataset]

Conservative Temperature is the variable the heat content is written
in because it is proportional to potential enthalpy, which the ocean
conserves to two orders of magnitude better than potential temperature
or entropy; the constant of proportionality is cp0, defined exactly as
3991.86795711963 J per kg per K.[^teos-10] The product distributes in
situ temperature and practical salinity on pressure levels, so the
loader converts through the gsw implementation of TEOS-10 (Absolute
Salinity, then Conservative Temperature, then in situ density) and
takes the layer thickness of each level from the midpoints to its
neighbours, the top layer from 0 dbar and the bottom cut at the floor,
converted from pressure to height at the cell's latitude.[^computation]

The domain is the product's, not the global ocean's. The grid starts
at 64.5S, the marginal seas the product maps to a shallower limit
than 2000 dbar fall out of the fixed mask of columns mapped at all 58
levels, and the sum is weighted by each cell's spherical area from
the grid's latitude bounds; the stamp states the domain's area in
square meters and the receipt states the rate per unit area of that
domain beside the rate per unit Earth surface, which is the
published inventories' convention.[^gotcha-coverage][^computation]
The published rates for 2006 to 2020 in that convention are 0.39
plus or minus 0.1 watts per square meter for 0 to 700 m and 0.62 plus
or minus 0.2 for 0 to 2000 m, quoted for the ocean between 60S and
60N deeper than 300 m with an ocean-surface factor of 0.61, so a
per-unit-domain-area comparison divides the published rate by that
factor.[^vs-2023]

The product stops at 1975 dbar, and the ocean below 2000 m is a real
term of the full-depth change that this product cannot supply: the
published rate below 2000 m is 0.97 plus or minus 0.48 ZJ per year
(0.06 plus or minus 0.03 watts per square meter) over 1992 to 2020, a
constant linear trend from repeat hydrography, and the receipt states
it beside the terms as an omission, never adding
it.[^gotcha-floor][^vs-2023] The rate over a window carries the
interval of the trend under a lag-1 autocorrelated residual, and the
change the rate implies from the first year of the window to the last
is checked against the endpoint change read directly from the two
years' means; the residual between the two says how far the record
departs from a line over the window.[^computation] The
sanctioned, receipt-producing form of this recipe is the attested
computation beside it; the model-based counterpart on the ECCO native
grid, with its own attested computation and ocean area anchor, is the
provider bundle's recipe at knowledge/podaac/recipes/ecco-ocean-heat-content.md.[^ecco-ohc]

[^computation]: computations/argo-ohc.md, the terms, the fixture, the refusal rule, the reference run and the anchor
[^dataset]: datasets/roemmich-gilson-argo-climatology.md, the files, the grid and the masks
[^gotcha-floor]: gotchas/rg-sampled-depth-floor.md
[^gotcha-coverage]: gotchas/rg-coverage-excludes-high-latitudes-and-marginal-seas.md
[^gotcha-baseline]: gotchas/rg-anomaly-against-a-fixed-climatology.md
[^teos-10]: TEOS-10 Manual, IOC Manuals and Guides 56, section 3.3 and appendix A.18
[^vs-2023]: von Schuckmann and others (2023), Earth System Science Data 15, doi:10.5194/essd-15-1675-2023, Table 1 and section 2
[^ecco-ohc]: knowledge/podaac/recipes/ecco-ocean-heat-content.md in nasa-daac-knowledge, the ECCO-based counterpart
