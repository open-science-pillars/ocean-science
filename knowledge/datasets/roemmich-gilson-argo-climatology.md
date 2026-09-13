---
type: dataset
spheres: [hydrosphere]
title: "Roemmich and Gilson Argo climatology (Scripps, 2019 release with monthly extensions)"
description: "Argo-only gridded temperature and practical salinity on a 1 degree grid over 58 pressure levels from 2.5 to 1975 dbar, distributed as a 2004 to 2018 mean plus monthly anomalies and extended month by month against that fixed baseline; the organization's steric term, which covers the upper 2000 dbar of the open ocean only."
tags: [argo, roemmich-gilson, climatology, gridded, temperature, salinity, steric, ocean-heat-content, scripps]
generated: { by: knowledge-seeder/claude, at: 2026-09-13T20:20:00Z }
resource: https://sio-argo.ucsd.edu/RG_Climatology.html
version: "2019 release (the product page reads Latest Version 2019, Updated Jan 17, 2020, using Argo data from January 1, 2004 through December 31, 2018), extended by monthly files RG_ArgoClim_YYYYMM_2019.nc.gz through August 2026; product page read and the August 2026 extension file downloaded and inspected 2026-09-13"
sources:
  - id: rg-page
    resource: https://sio-argo.ucsd.edu/RG_Climatology.html
    title: "Scripps RG Argo Climatology product page (read 2026-09-13): version and data window, the method note against the 2009 paper, the download links, the global-average series and its mask note, the early-years note, the not-CF-compliant note and the acknowledgement text"
  - id: rg-extension-202608
    resource: https://sio-argo.ucsd.edu/RG/RG_ArgoClim_202608_2019.nc.gz
    title: "The August 2026 monthly extension file, downloaded and read with netCDF4 on 2026-09-13: dimensions, axes, variables, units, long names and fill value"
  - id: rg-climatology-temperature
    resource: https://sio-argo.ucsd.edu/RG/RG_ArgoClim_Temperature_2019.nc.gz
    title: "The 2004 to 2018 temperature climatology file; its header (dimensions, variables and attributes) read 2026-09-13 from the first 4 MB of the archive"
  - id: roemmich-gilson-2009
    resource: https://doi.org/10.1016/j.pocean.2009.03.004
    title: "Roemmich and Gilson, 2009, The 2004-2008 mean and annual cycle of temperature, salinity, and steric height in the global ocean from the Argo Program, Progress in Oceanography 82(2), 81-100 (the mapping method the product page names; the Crossref registry record was verified 2026-09-13, the publisher's page is unreachable from the drafting environment)"
  - id: argo-doi
    resource: https://doi.org/10.17882/42182
    title: "Argo (2000), Argo float data and metadata from Global Data Assembly Centre (Argo GDAC), SEANOE (the underlying observations; landing page read 2026-09-13)"
  - id: wcrp-2018
    resource: https://doi.org/10.5194/essd-10-1551-2018
    title: "WCRP Global Sea Level Budget Group, 2018, Global sea-level budget 1993-present, Earth System Science Data 10, 1551-1590 (the Scripps product as one of the 0 to 2000 m thermosteric estimates, Table 2 and section 2.3; read in full 2026-09-13)"
  - id: argo-connector
    resource: ../connectors/argo-floats.md
    title: "This bundle's Argo connector concept, which carries the Argo citation and acknowledgement convention"
status: draft
stale_after: 2027-03-13
---

# Roemmich and Gilson Argo climatology

**Identity.** An Argo-only objective analysis of temperature and
practical salinity from the Scripps Institution of Oceanography,
produced by Dean Roemmich and John Gilson; the current release (2019)
uses Argo profiles from 2004-01-01 through 2018-12-31 and is described
by the product page as the 2009 method with one modification, the
zonal equatorial correlation scale of the optimal estimation step
scaled by 8 rather than 4.[^rg-page][^roemmich-gilson-2009] The
release added several marginal seas and the Arctic Ocean to the mapped
domain.[^rg-page] Major re-analyses are biennial, and monthly
extension files carry the analysis forward between them; the page
lists extensions from January 2019 through August 2026 as of the
verification date, and states that data from 2019 onward are not used
in the climatology itself.[^rg-page] The product is the Scripps entry
among the eleven in situ thermosteric estimates the WCRP sea level
budget assessment compiled, listed there as a monthly 0 to 2000 m
product covering 2005 to 2016 and referenced to the 2009
paper.[^wcrp-2018] The underlying observations are the Argo array,
which measures the upper 2000 m of the ocean.[^argo-doi]

**Structure.** The files are netCDF, and the product page says they
are not CF compliant.[^rg-page] The August 2026 extension file has
dimensions LONGITUDE 360 (20.5 to 379.5 degrees east, marked as a
modulo axis), LATITUDE 145 (64.5S to 79.5N, 1 degree), PRESSURE 58
(2.5 to 1975 dbar, unevenly spaced: 10 dbar steps to 170 dbar, then
20 dbar steps to 460 dbar, then 50 dbar steps to 1350 dbar, then 100
dbar steps to 1900 dbar, and a last level at 1975 dbar) and TIME 1;
its variables are ARGO_TEMPERATURE_ANOMALY (degrees Celsius, ITS-90)
and ARGO_SALINITY_ANOMALY (Practical Salinity Scale 78), each with the
long name "defined by 2004 - 2018 RG CLIMATOLOGY", missing value and
fill value both minus 999, and no global
attributes.[^rg-extension-202608] The TIME axis carries the unit
"months since 2004-01-01 00:00:00"; the August 2026 file holds the
value 271.5, and xarray (2026.7.0) refuses to decode that unit under
the default calendar, so the axis is read undecoded and converted by
hand from the month count.[^rg-extension-202608] The climatology file
for temperature has TIME 180 (the 180 months of 2004 to 2018) and four
data variables: ARGO_TEMPERATURE_MEAN on (PRESSURE, LATITUDE,
LONGITUDE), ARGO_TEMPERATURE_ANOMALY on (TIME, PRESSURE, LATITUDE,
LONGITUDE), a BATHYMETRY_MASK and a MAPPING_MASK, the last with the
long name "pressure limits of mapping can be shallower than 2000dbar
in marginal seas"; the two masks use minus 9 as their fill
value.[^rg-climatology-temperature] The extension files carry the
anomalies only: an absolute temperature or salinity for any month
after 2018 is the extension anomaly added to the mean field of the
climatology file, and the masks live only in the climatology
files.[^rg-extension-202608][^rg-climatology-temperature] In the
August 2026 file 31,841 of the 52,200 grid cells hold a value at 2.5
dbar and 30,650 at 1975 dbar; the two anomaly variables share one
mask.[^rg-extension-202608]

**Obtaining.** Everything is linked from the product page: the 2004
to 2018 temperature climatology (663 MB gzipped) and salinity
climatology (440 MB), one gzipped netCDF file per extension month
under the RG/ path, named RG_ArgoClim_YYYYMM_2019.nc.gz and about 6.2
MB each, and two higher resolution mean and annual-cycle products fit
to the nearest 33 rather than 100 profiles (a 1/6 degree mean and a
1/2 degree annual cycle).[^rg-page] The acknowledgement the page asks
for is the 2009 paper together with the Argo statement and the Argo
DOI, which this bundle's Argo connector concept carries
verbatim.[^rg-page][^argo-doi][^argo-connector]

**Steric height and heat content from this product.** The product's
own headline series is a 0 to 2000 dbar global-average open-ocean
potential temperature computed under the spatial mask in the netCDF
file, with marginal seas and the Arctic Ocean excluded from the
calculation.[^rg-page] Any steric height, thermosteric sea level or
ocean heat content integrated from these fields is therefore an upper
2000 dbar, open-ocean quantity, defined as an anomaly against the
2004 to 2018 baseline; the three gotchas below own the consequences.

## Uncertainty

- **No error field ships with the product.** The extension file holds
  the two anomaly variables and their axes and nothing else, and the
  temperature climatology file's header lists the mean, the anomalies
  and the two masks with no uncertainty
  variable.[^rg-extension-202608][^rg-climatology-temperature] The
  mapping's formal error, if the method produces one, is not
  distributed; the 2009 paper's description of the method could not
  be read from the drafting environment (its registry record was
  verified instead).[^roemmich-gilson-2009]
- **Mapping smoothing.** The mean field is a weighted least-squares
  fit to the nearest 100 Argo profiles within a month, so features
  smaller than the span of those profiles are muted; the page's
  higher-resolution variants fit the nearest 33 profiles instead and
  retain smaller scales at the cost of larger uncertainties, which the
  page states without quantifying.[^rg-page]
- **Sparse early years.** The array reached its 3,000 float target in
  2008, and the page notes that in the early years it was too sparse
  to "cool" the monthly estimates away from the warmer 2004 to 2018
  mean-plus-annual field used as the first guess; early-year anomalies
  therefore lean toward the baseline.[^rg-page] The WCRP assessment
  dates quasi-global coverage of the ice-free ocean to the start of
  2006, with more than 80 percent of the planned array deployed
  during 2005, and reports a larger spread between in situ estimates
  before the Argo era than after it.[^wcrp-2018]
- **Marginal seas and shelves.** The mapping mask records that the
  mapping's pressure limit can be shallower than 2000 dbar in marginal
  seas, and the product's global-average series excludes marginal
  seas and the Arctic by
  mask.[^rg-climatology-temperature][^rg-page] The Argo array samples
  the ice-free ocean, with quasi-global coverage between 60S and 60N,
  so the mapped values poleward of that and over shelves rest on fewer
  profiles.[^wcrp-2018]
- **Spread among products as the practical uncertainty.** The WCRP
  assessment treats the spread of the 0 to 2000 m estimates (nine in
  the Argo era, this product among them) as the error bar of the
  ensemble mean, and quotes a full-depth thermosteric trend of 1.3
  plus or minus 0.4 mm per year over 2005 to 2015 on that
  basis.[^wcrp-2018]

## Known issues

- [rg-sampled-depth-floor](../gotchas/rg-sampled-depth-floor.md):
  the product stops at 1975 dbar, so a steric or heat content
  integral from it is an upper 2000 dbar term and the deep ocean below
  it is a separate term of the budget.
- [rg-coverage-excludes-high-latitudes-and-marginal-seas](../gotchas/rg-coverage-excludes-high-latitudes-and-marginal-seas.md):
  the grid begins at 64.5S, the product's global average masks out
  marginal seas and the Arctic, and a "global" mean from it is an
  open-ocean mean over that domain.
- [rg-anomaly-against-a-fixed-climatology](../gotchas/rg-anomaly-against-a-fixed-climatology.md):
  the anomalies are departures from the 2004 to 2018 mean and annual
  cycle, the extension files keep that reference, and a series that
  joins releases or re-baselines moves its intercept and any
  comparison against another product.

[^rg-page]: Scripps RG Argo Climatology product page, read 2026-09-13
[^rg-extension-202608]: RG_ArgoClim_202608_2019.nc.gz, downloaded and read 2026-09-13
[^rg-climatology-temperature]: RG_ArgoClim_Temperature_2019.nc.gz, header read 2026-09-13
[^roemmich-gilson-2009]: Roemmich and Gilson, 2009, Progress in Oceanography, doi:10.1016/j.pocean.2009.03.004 (registry record)
[^argo-doi]: Argo (2000), SEANOE, doi:10.17882/42182
[^wcrp-2018]: WCRP Global Sea Level Budget Group, 2018, Earth System Science Data, doi:10.5194/essd-10-1551-2018
[^argo-connector]: This bundle's Argo connector concept
