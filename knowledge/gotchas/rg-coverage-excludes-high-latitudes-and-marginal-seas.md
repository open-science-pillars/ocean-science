---
type: dataset-gotcha
spheres: [hydrosphere]
title: "The Roemmich and Gilson grid starts at 64.5S and its global average masks out the marginal seas and the Arctic: a global mean from this product is an open-ocean mean over that domain"
description: "The gridded Argo climatology has no cells south of 64.5S, its 2019 release maps some marginal seas and part of the Arctic but the product's own global-average series excludes them by a mask carried only in the climatology files, several enclosed seas hold no values at all, and the mapped fraction of cells falls off sharply north of about 45N. A mean labelled global from these fields is a mean over the mapped, masked, ice-free open ocean, and it differs from a truly global product or from the same product averaged under a different mask by the coverage, not by the ocean."
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
    title: "The 2004 to 2018 temperature climatology file; its header, read 2026-09-13, names the BATHYMETRY_MASK and MAPPING_MASK variables and the mapping mask's shallower limit in marginal seas"
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
BATHYMETRY_MASK and a MAPPING_MASK, the latter with the long name
"pressure limits of mapping can be shallower than 2000dbar in
marginal seas", while an extension file carries the two anomaly
fields and their axes only.[^rg-climatology-temperature][^rg-extension-202608]
In the August 2026 extension file the fraction of cells holding a
value at 2.5 dbar is above nine tenths in every 5 degree band from
64.5S to 40S, between six and eight tenths through the tropics, about
one half between 25N and 40N, one third between 45N and 50N, and
below one tenth in every band north of 65N; 1 degree boxes over the
Red Sea, the Black Sea, the Baltic, Hudson Bay and the Persian Gulf
hold no values at all, while the Mediterranean, the Gulf of Mexico,
the Sea of Japan, the Nordic seas and the Bering Sea hold mapped
cells (these counts are of grid cells in latitude and longitude boxes,
land included, so they measure where the mapping reaches and not the
fraction of sea area mapped).[^rg-extension-202608] The observing
system behind the product samples the ice-free ocean, with
quasi-global coverage between 60S and 60N, and the WCRP assessment's
compilation of thermosteric products records latitude ranges from
60S to 60N and 65S to 65N for the Argo-era products against 89S to
89N for the products that fill the gaps with a model or a
climatology.[^wcrp-2018]

**Wrong-result mode.** A mean over every mapped cell in the grid is
not the product's own global average: it includes the marginal seas
and the Arctic cells the product masks out. A mean labelled "global"
from either version omits the ocean south of 64.5S, the seasonal ice
zones, the enclosed seas the mapping does not reach and the shelves
shallower than the mapping limit, so a comparison against a product
that reaches 89S to 89N, or a heat content scaled up to the global
ocean by an area ratio, carries the coverage difference as if it were
signal. The difference between two "global" means from this product
under two masks is a coverage artifact.

**Correct approach.** A global-mean quantity from this product is
named by its domain: the mapped open ocean between 64.5S and the
mask's northern limit, marginal seas and the Arctic excluded, under
the climatology file's mask, which is read from that file and applied
to every extension month. A comparison against another product is
made under one common mask applied to both, and the area the mask
covers is stated beside the mean. A statement about the ocean south of
64.5S, the Arctic or an enclosed sea does not rest on this product.

**Verification.** The latitude axis and the cell counts by band and
by region were read from the August 2026 extension file with netCDF4
on 2026-09-13; the climatology file's header, read the same day from
the first 4 MB of the archive, carries the two mask variables and the
mapping mask's long name.[^rg-extension-202608][^rg-climatology-temperature]
The product page's statements on the added seas and on the masked
global average were read the same day.[^rg-page] The WCRP paper's
coverage statements and its Table 2 were read in full from the
publisher's PDF on 2026-09-13 and its Crossref record verified the
same day.[^wcrp-2018] The dataset concept lists the coverage among
the product's known issues.[^dataset]

[^rg-extension-202608]: RG_ArgoClim_202608_2019.nc.gz, downloaded and read 2026-09-13
[^rg-climatology-temperature]: RG_ArgoClim_Temperature_2019.nc.gz, header read 2026-09-13
[^rg-page]: Scripps RG Argo Climatology product page, read 2026-09-13
[^wcrp-2018]: WCRP Global Sea Level Budget Group, 2018, Earth System Science Data, doi:10.5194/essd-10-1551-2018
[^dataset]: This bundle's Roemmich and Gilson dataset concept
