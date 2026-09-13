---
type: dataset-gotcha
spheres: [hydrosphere]
title: "The Roemmich and Gilson product stops at 1975 dbar: a steric height or heat content from it is an upper 2000 dbar term, and a budget that carries it as the whole steric term omits the deep ocean"
description: "The gridded Argo climatology has 58 pressure levels from 2.5 to 1975 dbar and nothing below, because Argo floats profile the upper 2000 m. A steric height, thermosteric sea level or ocean heat content integrated from it is a 0 to 2000 dbar quantity; quoted as full depth, or entered as the steric term of altimetry equals mass plus steric with no term for the ocean below 2000 m, it misstates the budget by the deep term, which the WCRP assessment carries as a separate estimate extrapolated from the Purkey and Johnson repeat-hydrography trend."
tags: [argo, roemmich-gilson, steric, thermosteric, ocean-heat-content, sea-level-budget, deep-ocean, abyssal, 2000-dbar]
generated: { by: knowledge-seeder/claude, at: 2026-09-13T20:20:00Z }
severity: high
dataset: ../datasets/roemmich-gilson-argo-climatology.md
eval_case: rg-sampled-depth-floor
status: draft
stale_after: 2027-03-13
sources:
  - id: rg-extension-202608
    resource: https://sio-argo.ucsd.edu/RG/RG_ArgoClim_202608_2019.nc.gz
    title: "The August 2026 monthly extension file, downloaded and read with netCDF4 on 2026-09-13: the PRESSURE axis of 58 levels from 2.5 to 1975 dbar"
  - id: rg-page
    resource: https://sio-argo.ucsd.edu/RG_Climatology.html
    title: "Scripps RG Argo Climatology product page (read 2026-09-13): the product's own global-average series is labelled 0 to 2000 dbar"
  - id: argo-doi
    resource: https://doi.org/10.17882/42182
    title: "Argo (2000), Argo float data and metadata from Global Data Assembly Centre (Argo GDAC), SEANOE (landing page read 2026-09-13: the array measures the upper 2000 m of the ocean)"
  - id: wcrp-2018
    resource: https://doi.org/10.5194/essd-10-1551-2018
    title: "WCRP Global Sea Level Budget Group, 2018, Global sea-level budget 1993-present, Earth System Science Data 10, 1551-1590 (read in full 2026-09-13: sections 2.3.1 to 2.3.3 and Table 2 on the thermosteric estimates and the deep-abyssal term, section 4 on closure)"
  - id: purkey-johnson-2010
    resource: https://doi.org/10.1175/2010JCLI3682.1
    title: "Purkey and Johnson, 2010, Warming of Global Abyssal and Deep Southern Ocean Waters between the 1990s and 2000s, Contributions to Global Heat and Sea Level Rise Budgets, Journal of Climate 23(23), 6336-6351 (the deep and abyssal trend the WCRP assessment extrapolates; Crossref record and abstract read 2026-09-13)"
  - id: closure-convention
    resource: https://github.com/open-science-pillars/nasa-daac-knowledge/blob/nasa-daac-knowledge--v2026.9.2/knowledge/podaac/conventions/sea-level-budget-closure.md
    title: "The provider bundle's sea level budget closure convention (knowledge/podaac/conventions/sea-level-budget-closure.md at the nasa-daac-knowledge--v2026.9.2 release tag), which names the deep-steric term among the consistency requirements"
  - id: dataset
    resource: ../datasets/roemmich-gilson-argo-climatology.md
    title: "This bundle's Roemmich and Gilson dataset concept, which lists the depth floor among the known issues"
---

# The Roemmich and Gilson product stops at 1975 dbar

**Mechanism.** The product's PRESSURE axis has 58 levels from 2.5 to
1975 dbar and no level below, in the climatology and in every monthly
extension file.[^rg-extension-202608] The floor is the observing
system's: the Argo array measures the temperature and salinity of the
upper 2000 m of the ocean, and the product is an analysis of Argo
data alone.[^argo-doi][^rg-page] The product's own headline series is
labelled a 0 to 2000 dbar global average.[^rg-page] The WCRP sea level
budget assessment lists the Scripps product among its in situ
thermosteric estimates as a 0 to 2000 m product, and builds its
full-depth thermosteric series for the Argo era by summing a 0 to
2000 m ensemble of nine estimates and one estimate for 2000 m and
below; that deep-abyssal estimate is the updated linear trend of
Purkey and Johnson (2010) for 1990 to 2010, extrapolated to 2016,
with no variability superimposed.[^wcrp-2018] Purkey and Johnson
derive the trend from 28 full-depth repeat hydrographic sections
across 24 of 32 ocean basins and report that abyssal warming (below
4000 m) contributes 0.053 plus or minus 0.017 mm per year to global
average sea level and that deep warming (1000 to 4000 m) south of the
Subantarctic Front adds another 0.093 plus or minus 0.081 mm per
year.[^purkey-johnson-2010] The assessment's full-depth ensemble trend
is 1.3 plus or minus 0.4 mm per year over 2005 to 2015, and its
budget residual over 2005 to present is minus 0.1 plus or minus 0.3
mm per year, a closure within 0.3 mm per year reached with the deep
term included.[^wcrp-2018]

**Wrong-result mode.** A thermosteric or steric sea level integrated
over the product's 58 levels and reported as the ocean's steric
change, or entered as the steric term of altimetry equals ocean mass
plus steric with no term for the ocean below 2000 dbar, is short by
the deep contribution. The shortfall appears as a budget residual
that reads as non-closure, or as a discrepancy against the GRACE mass
term, when it is a missing term. An ocean heat content quoted as
global from the same integral understates the full-depth value for
the same reason. Nothing in the files flags the floor: the anomaly
fields end at 1975 dbar and the integral simply stops there.

**Correct approach.** An integral from this product carries its
pressure range in its name (0 to 2000 dbar, or the range actually
integrated) and its domain (the product's open-ocean mask). A sea
level budget that uses it as the steric term carries a separate term
for the ocean below 2000 m, as the WCRP assessment does with the
Purkey and Johnson trend, and states that term's nature: a linear
trend from decadal repeat hydrography, extrapolated, with an
uncertainty quoted on its own rather than folded into the spread of
the upper-ocean products.[^wcrp-2018][^purkey-johnson-2010] The
provider bundle's closure convention names the deep-steric term among
the consistency requirements of the budget.[^closure-convention]

**Verification.** The pressure axis was read from the August 2026
extension file with netCDF4 on 2026-09-13 (58 levels, 2.5 to 1975
dbar).[^rg-extension-202608] The product page's 0 to 2000 dbar label
on its global-average series and the Argo DOI landing page's
statement that the array measures the upper 2000 m were read the same
day.[^rg-page][^argo-doi] The WCRP paper was read in full from the
publisher's PDF on 2026-09-13, and its Crossref record (Earth System
Science Data, 2018, volume 10, pages 1551 to 1590, author WCRP Global
Sea Level Budget Group) was verified the same day; the Purkey and
Johnson record (Journal of Climate, 2010, volume 23, pages 6336 to
6351) and the abstract carrying the two deep contributions were read
from the Crossref registry, the journal page itself not being
fetched.[^wcrp-2018][^purkey-johnson-2010] The dataset concept lists
the floor among the product's known issues.[^dataset]

[^rg-extension-202608]: RG_ArgoClim_202608_2019.nc.gz, downloaded and read 2026-09-13
[^rg-page]: Scripps RG Argo Climatology product page, read 2026-09-13
[^argo-doi]: Argo (2000), SEANOE, doi:10.17882/42182
[^wcrp-2018]: WCRP Global Sea Level Budget Group, 2018, Earth System Science Data, doi:10.5194/essd-10-1551-2018
[^purkey-johnson-2010]: Purkey and Johnson, 2010, Journal of Climate, doi:10.1175/2010JCLI3682.1
[^closure-convention]: The provider bundle's sea level budget closure convention, knowledge/podaac/conventions/sea-level-budget-closure.md
[^dataset]: This bundle's Roemmich and Gilson dataset concept
