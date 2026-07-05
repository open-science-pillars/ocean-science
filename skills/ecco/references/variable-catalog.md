# ECCO v4r4 variable catalog (llc90 native grid)

Reference for the ecco skill, per SPEC §4.2.

**ShortName verification: 2026-07-04**, against live CMR via earthaccess
(netrc-authenticated `search_datasets`, one collection returned per name
below; full llc90 sweep returned 51 V4R4* collections). Re-verify and
update this date whenever a row is added or PO.DAAC announces a
reprocessing. Variable names are granule-verified only where the row
says so; others follow the ECCO v4r4 user guide and must be
granule-verified at first load.

## Grid geometry (load first, always)

| ShortName | Contents |
|---|---|
| `ECCO_L4_GEOMETRY_LLC0090GRID_V4R4` | one static granule (`GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc`, ~8.6 MB), granule-verified 2026-07-04: areas rA, rAw, rAs, rAz; edges dxG, dyG, dxC, dyC; vertical drF, drC; partial cells hFacC/W/S; land masks maskC/W/S; rotation CS, SN; Depth, PHrefC/F. XC, YC, XG, YG, Z, Zl, Zu, Zp1 arrive as coordinates, not data variables. Merged into every native-grid dataset before analysis. |

## Monthly means (the workhorse rows)

| ShortName | Key variables | Purpose |
|---|---|---|
| `ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4` | THETA, SALT | potential temperature (degree_C), salinity; granule-verified 2026-07-04 (12 granules loaded live, dims time/k/tile/j/i = 12/50/13/90/90) |
| `ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4` | UVEL, VVEL, WVELMASS | ocean velocity. NOTE: this is the velocity ShortName; OBP below is bottom pressure, a different product (the v0.1 confusion this row exists to prevent) |
| `ECCO_L4_OBP_LLC0090GRID_MONTHLY_V4R4` | OBP, OBPGMAP | ocean bottom pressure |
| `ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4` | SSH, SSHIBC, SSHNOIBC, ETAN | sea surface height family |
| `ECCO_L4_HEAT_FLUX_LLC0090GRID_MONTHLY_V4R4` | TFLUX, oceQsw, oceQnet, EXF* components | surface heat fluxes; TFLUX and oceQsw are the heat-budget forcing terms |
| `ECCO_L4_FRESH_FLUX_LLC0090GRID_MONTHLY_V4R4` | SFLUX, oceFWflx, EXF* components | surface freshwater and salt fluxes |
| `ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4` | ADVx_TH, ADVy_TH, ADVr_TH, DFxE_TH, DFyE_TH, DFrE_TH, DFrI_TH | advective and diffusive heat-budget fluxes |
| `ECCO_L4_OCEAN_3D_SALINITY_FLUX_LLC0090GRID_MONTHLY_V4R4` | ADV*_SLT, DF*_SLT, oceSPtnd | salt-budget fluxes |
| `ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4` | UVELMASS, VVELMASS, WVELMASS | mass-weighted transports; the transport-analysis inputs |
| `ECCO_L4_BOLUS_LLC0090GRID_MONTHLY_V4R4` | UVELSTAR, VVELSTAR, WVELSTAR | GM bolus velocity (added to Eulerian velocity for tracer transport) |
| `ECCO_L4_MIXED_LAYER_DEPTH_LLC0090GRID_MONTHLY_V4R4` | MXLDEPTH | mixed layer depth |
| `ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4` | RHOAnoma, DRHODR, PHIHYD | density, stratification, pressure |
| `ECCO_L4_STRESS_LLC0090GRID_MONTHLY_V4R4` | EXFtaux, EXFtauy, oceTAUX, oceTAUY | surface stress |
| `ECCO_L4_SEA_ICE_CONC_THICKNESS_LLC0090GRID_MONTHLY_V4R4` | SIarea, SIheff, SIhsnow | sea-ice state |
| `ECCO_L4_ATM_STATE_LLC0090GRID_MONTHLY_V4R4` | EXFatemp, EXFaqh, EXFuwind, EXFvwind, EXFpress | atmosphere forcing state |

## Snapshots (budget bookends)

Monthly-mean budgets need state snapshots at month boundaries for the
tendency term; these collections carry them:

| ShortName | Key variables |
|---|---|
| `ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4` | THETA, SALT |
| `ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4` | ETAN (for the z* scale factor in budgets) |
| `ECCO_L4_OBP_LLC0090GRID_SNAPSHOT_V4R4` | OBP |
| `ECCO_L4_SEA_ICE_CONC_THICKNESS_LLC0090GRID_SNAPSHOT_V4R4` | SIarea, SIheff |

## Variants and special rows

- **Daily means** exist for most monthly rows above (same ShortName with
  `MONTHLY` replaced by `DAILY`); confirmed in the 2026-07-04 sweep.
- **`V4R4B` rows:** `ECCO_L4_SSH_LLC0090GRID_{MONTHLY,DAILY}_V4R4B` and
  `ECCO_L4_OBP_LLC0090GRID_{MONTHLY,DAILY}_V4R4B` are a corrected
  B-release for SSH and OBP only. Never mix V4R4 and V4R4B rows in one
  analysis without saying so; when starting fresh with SSH or OBP,
  check the PO.DAAC landing pages for which release is recommended.
- **Mixing coefficients:** `ECCO_L4_OCEAN_3D_MIX_COEFFS_LLC0090GRID_V4R4`
  (static, one granule).
- **Momentum tendencies:** `ECCO_L4_OCEAN_3D_MOMENTUM_TEND_LLC0090GRID_{MONTHLY,DAILY}_V4R4`.
- **Bolus streamfunction:** `ECCO_L4_OCEAN_BOLUS_STREAMFUNCTION_LLC0090GRID_{MONTHLY,DAILY}_V4R4`.
- **Sea-ice fluxes:** `ECCO_L4_SEA_ICE_{HORIZ_VOLUME_FLUX,SALT_PLUME_FLUX,VELOCITY}_LLC0090GRID_{MONTHLY,DAILY}_V4R4`.
- **Geothermal flux is not a PO.DAAC collection.** It is a static model
  input (`geothermalFlux.bin` in the ECCO v4 ancillary inputs); deep
  heat budgets need it and it must be fetched from the ECCO ancillary
  data, not CMR. The `ecco-geothermal-flux` gotcha carries the details.

## Access pattern

`ecco_access.ecco_podaac_to_xrdataset(query, version='v4r4', StartDate=,
EndDate=, mode=)` accepts ShortNames or variable names for TIME-RANGED
collections (call pattern per the ECCO v4 Python tutorial).

**Static-collection quirk (observed 2026-07-04, ecco_access 0.3.1):**
given a static collection (GEOMETRY; likely MIX_COEFFS too) with no date
range, ecco_access synthesized a dated granule filename
(`GRID_1992-01-01_...`) that does not exist (archive 404) and estimated
a 75.8 GB download for a single-granule collection. Fetch static
collections via `earthaccess.search_data(short_name=...)` plus
`earthaccess.download` instead: granule names come from CMR, never
guessed. Grid geometry then merges via `xarray.merge` with the data
granules.
