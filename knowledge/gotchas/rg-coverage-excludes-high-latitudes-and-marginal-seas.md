---
type: dataset-gotcha
spheres: [hydrosphere]
title: "The Roemmich and Gilson grid starts at 64.5S and its global average masks out the marginal seas and the Arctic"
description: "The gridded Argo climatology has no cells south of 64.5S; its 2019 release maps some marginal seas and the Nordic seas and Arctic north to 79.5N, but only to a shallower pressure limit, and the product's own global-average series excludes them by a mask carried only in the climatology files; the columns mapped to 2000 dbar end at 66.5N, several enclosed seas hold no values at all, and the mapped open ocean covers about 61 percent of the Earth's surface. A mean labelled global from these fields is a mean over the mapped, masked, ice-free open ocean, and it differs from a truly global product or from the same product averaged under a different mask by the coverage, not by the ocean."
tags: [argo, roemmich-gilson, coverage, mask, marginal-seas, arctic, southern-ocean, global-mean, ocean-heat-content]
generated: { by: knowledge-seeder/claude, at: 2026-09-13T20:20:00Z }
severity: medium
dataset: ../datasets/roemmich-gilson-argo-climatology.md
status: draft
stale_after: 2027-03-13
sources:
  - id: rg-extension-202608
    resource: https://sio-argo.ucsd.edu/RG/RG_ArgoClim_202608_2019.nc.gz
    title: "The August 2026 monthly extension file, downloaded and read with netCDF4 on 2026-09-13: the latitude axis, and the count of mapped cells by latitude band and by region"
  - id: rg-climatology-temperature
    resource: https://sio-argo.ucsd.edu/RG/RG_ArgoClim_Temperature_2019.nc.gz
    title: "The 2004 to 2018 temperature climatology file: its header read 2026-09-13 from the first 4 MB of the archive, then the whole file downloaded the same day and read with netCDF4 for the MAPPING_MASK pressure limits by column and the BATHYMETRY_MASK, counted by latitude band and by region"
  - id: rg-page
    resource: https://sio-argo.ucsd.edu/RG_Climatology.html
    title: "Scripps RG Argo Climatology product page (read 2026-09-13): the marginal seas and the Arctic added in the 2019 release, and the global-average series computed under the file's spatial mask with marginal seas and the Arctic excluded"
  - id: wcrp-2018
    resource: https://doi.org/10.5194/essd-10-1551-2018
    title: "WCRP Global Sea Level Budget Group, 2018, Global sea-level budget 1993-present, Earth System Science Data 10, 1551-1590 (read in full 2026-09-13: Argo's coverage of the ice-free ocean and the latitude ranges of the compiled thermosteric products in Table 2)"
  - id: dataset
    resource: ../datasets/roemmich-gilson-argo-climatology.md
    title: "This bundle's Roemmich and Gilson dataset concept, which lists the coverage among the known issues"
---

# The Roemmich and Gilson grid starts at 64.5S and its global average is masked

**Mechanism.** The LATITUDE axis of the 2019 release runs from 64.5S
to 79.5N in 1 degree steps, so the ocean south of 64.5S, the
Antarctic margin included, is outside the grid
altogether.[^rg-extension-202608] The 2019 release added several
marginal seas and the Arctic Ocean to the mapped domain, but the
product's own global-average series is computed under a spatial mask
defined within the climatology netCDF file, with the marginal seas
and the Arctic Ocean excluded from the calculation.[^rg-page] That
mask is not in the extension files: the climatology file carries a
BATHYMETRY_MASK and a MAPPING_MASK, while an extension file carries
the two anomaly fields and their axes
only.[^rg-climatology-temperature][^rg-extension-202608] The mapping
mask holds one pressure limit per column: 2000 dbar for 30,999
columns, which span 64.5S to 66.5N and are the open ocean, and a
shallower limit for every mapped marginal sea (675 dbar in the Sea of
Japan, 975 dbar in the Nordic seas and the mapped Arctic from 61.5N
to 79.5N, 1025 dbar in the Gulf of Mexico and the Caribbean, 1175
dbar in the Mediterranean and the South China Sea region), with
20,002 columns not mapped at all; the columns mapped to 2000 dbar
cover about 61 percent of the Earth's surface and all mapped columns
about 63 percent, each 1 degree cell counted whole with its cosine of
latitude.[^rg-climatology-temperature] No column is mapped in the
Red Sea, the Black Sea, the Baltic, Hudson Bay, the Persian Gulf, the
Canada Basin or the Barents Sea, and every column between 64.5S and
60S is mapped to 2000 dbar.[^rg-climatology-temperature] The observing
system behind the product samples the ice-free ocean, with
quasi-global coverage between 60S and 60N, and the WCRP assessment's
compilation of thermosteric products records latitude ranges from
60S to 60N and 65S to 65N for the Argo-era products against 89S to
89N for the products that fill the gaps with a model or a
climatology.[^wcrp-2018]

**Wrong-result mode.** A mean over every mapped cell in the grid is
not the product's own global average: it includes the marginal seas
and the Nordic and Arctic cells the product masks out, each mapped
only to its shallower limit. A mean labelled "global"
from either version omits the ocean south of 64.5S, the seasonal ice
zones, the enclosed seas the mapping does not reach and the shelves
shallower than the mapping limit, so a comparison against a product
that reaches 89S to 89N, or a heat content scaled up to the global
ocean by an area ratio, carries the coverage difference as if it were
signal. The difference between two "global" means from this product
under two masks is a coverage artifact.

**Correct approach.** A global-mean quantity from this product is
named by its domain: the columns the mapping mask carries to 2000
dbar, the open ocean between 64.5S and 66.5N with the marginal seas
and the Arctic excluded, the mask read from the climatology file and
applied to every extension month. A comparison against another product is
made under one common mask applied to both, and the area the mask
covers is stated beside the mean. A statement about the ocean south of
64.5S, the Arctic or an enclosed sea does not rest on this product.

**Verification.** The latitude axis was read from the August 2026
extension file with netCDF4 on 2026-09-13; the climatology file for
temperature had its header read from the first 4 MB of the archive
and was then downloaded in full the same day, and its two mask
variables were read with netCDF4, the mapping limits counted by
value, by 5 degree latitude band and by 1 degree boxes over the seas
named above.[^rg-extension-202608][^rg-climatology-temperature] The
two area fractions are the sum over the 145 by 360 grid of the cosine
of each cell's latitude, restricted to the columns whose mapping
limit is 2000 dbar (61 percent) or to every column with a mapping
limit (63 percent), divided by the same sum over a full 1 degree
sphere (180 by 360 cells), each cell counted whole; the counts and
fractions are from the file as read and not from any distributed
script.[^rg-climatology-temperature] The
product page's statements on the added seas and on the masked global
average were read the same day.[^rg-page] The WCRP paper's coverage
statements and its Table 2 were read in full from the publisher's PDF
on 2026-09-13 and its Crossref record verified the same
day.[^wcrp-2018] The dataset concept lists the coverage among the
product's known issues.[^dataset]

[^rg-extension-202608]: RG_ArgoClim_202608_2019.nc.gz, downloaded and read 2026-09-13
[^rg-climatology-temperature]: RG_ArgoClim_Temperature_2019.nc.gz, header read from a partial download and then the whole file downloaded and read, 2026-09-13
[^rg-page]: Scripps RG Argo Climatology product page, read 2026-09-13
[^wcrp-2018]: WCRP Global Sea Level Budget Group, 2018, Earth System Science Data, doi:10.5194/essd-10-1551-2018
[^dataset]: This bundle's Roemmich and Gilson dataset concept
