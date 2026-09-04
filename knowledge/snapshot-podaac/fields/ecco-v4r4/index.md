# ECCO V4r4 fields layer

The layer that makes "all the ECCO model fields" a machine-checked
claim: one Data Collection concept per collection family, 26 families
covering the 90 ECCO_L4_*V4R4* collections at PO.DAAC. Concepts are
drafted only from the family manifest (tools/ecco_v4r4_families.yaml,
the single source of truth for family membership), machine-confirmed by
the live CMR verifier (tools/verify_cmr.py, whose --sign is the only
writer of process events), and steward-signed after granule
verification; tools/check_fields.py reconciles this directory against
the manifest and its coverage meter is the completeness claim.

## families

Ten demo-critical families authored; the remaining sixteen arrive via
good-first issues at the community handoff. The coverage meter in
tools/check_fields.py tracks progress toward 26/26 families and 90/90
ShortNames.

- [Grid geometry parameters](geometry.md): areas, edges, partial cells, masks, rotation, bathymetry; the static granule merged into every native-grid analysis.
- [Ocean potential temperature and salinity](temp-salinity.md): the tracer state, with the snapshot bookends budgets need.
- [Ocean velocity](ocean-vel.md): UVEL, VVEL, and the vertical velocity WVEL.
- [Ocean three-dimensional volume fluxes](volume-flux-3d.md): the mass-weighted transports; transport-analysis and volume-budget inputs.
- [Ocean three-dimensional potential temperature fluxes](temperature-flux-3d.md): the advective and diffusive heat-budget fluxes.
- [Ocean three-dimensional salinity fluxes](salinity-flux-3d.md): the salt-budget fluxes plus the salt-plume tendency.
- [Ocean and sea-ice surface heat fluxes](heat-flux.md): TFLUX and the shortwave component that force the heat budget.
- [Ocean and sea-ice surface freshwater fluxes](fresh-flux.md): SFLUX and oceFWflx; the salt-budget surface forcing.
- [Sea surface height](ssh.md): dynamic SSH and model sea level anomaly, with the corrected V4R4B re-release.
- [Ocean bottom pressure](obp.md): OBP and its anomaly, with the corrected V4R4B re-release.
