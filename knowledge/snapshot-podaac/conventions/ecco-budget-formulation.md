---
type: convention
title: "ECCO v4r4 budget formulation on the native grid"
description: "The constants, term definitions, sign conventions and discretization shared by the heat, salt and volume budgets on the llc90 grid, as the ECCO v4 Python tutorial notebooks state them and the sanctioned heat budget code implements them; tolerances and reference residuals are owned by the computations and recipes, not here."
tags: [ecco, budgets, formulation, native-grid, llc90, heat-budget, salt-budget, volume-budget, convention]
generated: { by: claude-code/fable-5, at: 2026-09-04T19:01:47Z }
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
stale_after: 2027-03-04
sources:
  - id: tut-heat
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Heat_budget_closure.html
    title: "ECCO v4 Python tutorial: global heat budget closure notebook (the term definitions, constants, shortwave and geothermal forcing)"
    author: team:ecco-consortium
  - id: tut-salt
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Salt_and_salinity_budget.html
    title: "ECCO v4 Python tutorial: salt, salinity and freshwater budgets notebook"
    author: team:ecco-consortium
  - id: tut-volume
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Volume_budget_closure.html
    title: "ECCO v4 Python tutorial: global volume and sea level budget notebook"
    author: team:ecco-consortium
  - id: sanctioned-heat-code
    resource: ../references/computations/ecco_heat_budget.py
    title: "The sanctioned heat budget computation, sha-bound by its attester; the four terms below are its code"
  - id: heat-computation
    resource: ../computations/ecco-heat-budget.md
    title: "The attested heat budget, owner of the heat pass bar and its baseline residuals"
  - id: salt-recipe
    resource: ../recipes/ecco-salt-budget.md
    title: "The salt budget recipe, owner of the measured salt residuals until the attested computation is extracted"
  - id: volume-recipe
    resource: ../recipes/ecco-volume-budget.md
    title: "The volume budget recipe, owner of the measured volume residuals and of the oceFWflx double-count measurement"
  - id: geothermal-gotcha
    resource: ../gotchas/ecco-geothermal-flux.md
    title: "The geothermal flux is a model input, not a PO.DAAC collection; its omission signature"
  - id: hfac-gotcha
    resource: ../gotchas/ecco-velmass-hfac-double-count.md
    title: "The MASS-suffixed velocities and the flux variables already carry hFac"
  - id: native-gotcha
    resource: ../gotchas/ecco-native-vs-regridded.md
    title: "Budgets close only on the native llc90 grid"
  - id: llc90-grid
    resource: ../fields/ecco-v4r4/geometry.md
    title: "The geometry collection: rA, drF, hFacC, Depth, Z and Zp1 on the native grid"
---

# ECCO v4r4 budget formulation on the native grid

The three closed budgets in this bundle (heat, salt, volume) share one
architecture: a z* tendency from month-boundary snapshots, an advective
and a diffusive convergence of the archived face fluxes, and a forcing
term specific to the tracer, all per grid cell and all divided by the
partial-cell volume. This concept records that shared formulation once,
as the ECCO v4 Python tutorial notebooks state it and as the sanctioned
heat budget code implements it, term by term. The terms below were
verified against the heat budget closure notebook line by line on
2026-07-04, and the sanctioned code carries them verbatim from that
verification.[^tut-heat][^sanctioned-heat-code] Budgets close only on
the native llc90 grid with exactly this formulation; the interpolated
product does not conserve.[^native-gotcha]

What this concept does not own: the pass bars and the measured
residuals. The heat tolerances and the baseline residual statistics
are owned by [the attested heat budget](../computations/ecco-heat-budget.md);
the salt and volume residuals by their recipes until the attested
forms are extracted.[^heat-computation][^salt-recipe][^volume-recipe]

## The budget identity

Per grid cell, in tracer units per second, the tendency equals the sum
of the convergences and the forcing:

```
G_total = G_advection + G_diffusion + G_forcing
```

The residual `G_total - (G_advection + G_diffusion + G_forcing)` is
evaluated pointwise, at every wet cell and every month, and in absolute
terms.[^tut-heat][^sanctioned-heat-code] The archive stores float32, so
the residual of a correct formulation sits at the storage quantization
scale; a residual above the owning computation's tolerance is a
formulation error, never data noise (the heat computation states the
tolerance and the recipe derives the quantization floor).[^heat-computation]

## Constants and the volume element

The Boussinesq reference density and the heat capacity are the MITgcm
values the tutorial uses, and the volume element carries the partial
cells:[^tut-heat][^sanctioned-heat-code]

```python
rhoconst = 1029          # kg m-3, Boussinesq reference density
c_p = 3994               # J kg-1 K-1
vol = rA * drF * hFacC   # m3, partial cells IN
```

`rA`, `drF`, `hFacC`, `Depth`, `Z` and `Zp1` come from the geometry
collection merged into the working dataset.[^llc90-grid]

## Term 1: tendency, snapshots and the z* scale factor

The tendency is built from month-boundary snapshots (the SNAPSHOT
collections), never from monthly means, and the tracer is scaled for
the moving z* surface before differencing:[^tut-heat][^sanctioned-heat-code]

```python
s_star  = 1 + ETAN_snp / Depth                    # z* scale factor
G_total = (s_star * THETA_snp).diff('time_snp') / delta_t
```

`delta_t` is the actual spacing between consecutive snapshots in
seconds. The `(1 + ETAN/Depth)` factor is the volume correction of the
z* coordinate; it is part of the tendency, not an optional refinement.

## Term 2: advective convergence

The horizontal convergence is minus the divergence of the archived
horizontal fluxes, differenced with a tile-aware operator (xgcm
`diff_2d_vector` with the llc face connections, or a within-tile
difference on tile-interior cells); the vertical convergence is the
difference of the vertical flux across the cell's faces, with the
bottom face zero-padded:[^tut-heat][^sanctioned-heat-code]

```python
adv_hConv = -(diff_X(ADVx_TH) + diff_Y(ADVy_TH))
adv_vConv = ADVr_TH.diff('k_l')                   # zero-padded at the bottom
G_advection = (adv_hConv + adv_vConv) / vol
```

`ADVr_TH` is masked to zero where `hFacC == 0` before differencing;
dry cells carry fill values otherwise.[^sanctioned-heat-code]

## Term 3: diffusive convergence

The same pattern; the vertical diffusive flux is the explicit part PLUS
the implicit part:[^tut-heat][^sanctioned-heat-code]

```python
dif_hConv = -(diff_X(DFxE_TH) + diff_Y(DFyE_TH))
dif_vConv = (DFrE_TH + DFrI_TH).diff('k_l')       # explicit + implicit
G_diffusion = (dif_hConv + dif_vConv) / vol
```

The tutorial sums both; a budget that reads only the explicit variable
is missing the implicit vertical mixing and does not close where that
mixing acts.[^tut-heat]

## Term 4: forcing (heat)

Surface heat flux with shortwave penetration plus geothermal flux at
the bottom wet cell. `TFLUX` is the total downward heat flux from the
atmosphere (latent, sensible, longwave and shortwave) and `oceQsw` its
shortwave part, both positive into the ocean. Shortwave penetrates with
the two-band double exponential the tutorial takes from Paulson and
Simpson (1977, Table 2), R = 0.62, zeta1 = 0.6 m, zeta2 = 20.0 m, cut
off below 200 m; the fraction absorbed in the top layer is charged to
the surface layer together with the non-solar
flux:[^tut-heat][^sanctioned-heat-code]

```python
q1 = R*exp(RF[:-1]/zeta1) + (1-R)*exp(RF[:-1]/zeta2)   # upper faces
q2 = R*exp(RF[1:]/zeta1)  + (1-R)*exp(RF[1:]/zeta2)    # lower faces
q1[zCut:] = 0; q2[zCut-1:] = 0                          # Z < -200 m cutoff
forcH_subsurf = (q1*(mskC==1) - q2*(mskC.shift(k=-1)==1)) * oceQsw
forcH_surf    = (TFLUX - (1-(q1[0]-q2[0]))*oceQsw) * mskC[0]
forcH = concat([forcH_surf, forcH_subsurf[1:]], dim='k')
```

The geothermal flux is a static model input read from the tutorial's
ancillary file, not a PO.DAAC collection; it enters at the bottom wet
cell of each column through the bottom-cell mask, and the whole forcing
is converted to a tendency with the constants and the partial-cell
thickness:[^tut-heat][^geothermal-gotcha][^sanctioned-heat-code]

```python
mskb   = mskC - mskC.shift(k=-1)                  # bottom-cell mask
GEOFLX = geoflx_llc * mskb                        # W m-2, 3D
G_forcing = ((forcH + GEOFLX) / (rhoconst*c_p)) / (hFacC*drF)
```

## Salt and volume: the same architecture, their own terms

The salt budget uses the salt flux family (`ADVx/y/r_SLT`,
`DFxE/yE/rE_SLT` plus `DFrI_SLT`), the surface salt flux `SFLUX` applied
to the top layer, and the three-dimensional salt plume tendency
`oceSPtnd`, which vertically redistributes the surface salt input; both
are in g m-2 s-1, and dividing by `rhoconst` and `hFacC * drF` gives
g/kg/s. `SFLUX` is nonzero only where sea ice melts or freezes. There
is no shortwave penetration and no geothermal term. The tendency is
`s* * SALT` from the snapshots with the same `s* = 1 + ETAN/Depth`, and
the closure is tendency equals advection plus diffusion plus
forcing:[^tut-salt][^salt-recipe]

```python
sSALT = SALT_snp * (1 + ETAN_snp / Depth)
G_total_Slt = sSALT.diff('time_snp') / delta_t
forcS = concat([SFLUX + oceSPtnd[0], oceSPtnd[1:]], dim='k')
G_forcing_Slt = forcS / rhoconst / (hFacC * drF)
```

The volume budget is the tracer set to one: the tendency is `d(s*)/dt`
from the ETAN snapshots, the same fractional volume change for every
layer of a column, and the convergence is of the mass-weighted
transports, volume flux in +x equal to `UVELMASS * drF * dyG`, in +y to
`VVELMASS * drF * dxG`, and in the vertical to `WVELMASS * rA`, divided
by the partial-cell volume. There is no separate forcing term:
`WVELMASS` at the top of the surface cell is the liquid volume flux out
of the ocean surface and is proportional to `oceFWflx` (the net
freshwater flux into the ocean, kg m-2 s-1, positive where salinity
decreases), so the interior volume budget closes on transport
convergence alone and adding `oceFWflx` as a forcing double-counts
it.[^tut-volume][^volume-recipe] (The tutorial's own chapter closes
the sea level budget, a different identity in which `oceFWflx` appears
explicitly; both are true of the same model.)

## Sign and placement conventions

- Horizontal fluxes sit on the west face (`i_g`) and the south face
  (`j_g`) and are positive toward increasing `i` and `j`; the
  horizontal convergence of a cell is minus the divergence, the flux
  at its west and south faces minus the flux at its east and north
  faces.[^tut-volume][^sanctioned-heat-code]
- Vertical fluxes sit on the upper face (`k_l`); the vertical
  convergence is the difference along `k_l` with the bottom face
  zero-padded, the flux at the cell's lower face minus the flux at its
  upper face.[^tut-heat][^sanctioned-heat-code]
- Surface fluxes are positive into the ocean: `TFLUX` and `oceQsw` as
  downward heat flux, `oceFWflx` as net freshwater flux into the ocean.
  They are applied to the `k = 0` layer, except the penetrating
  shortwave fraction distributed by `q1` and `q2` and the salt plume
  tendency `oceSPtnd`, which is three-dimensional.[^tut-heat][^tut-salt][^tut-volume]
- The `*MASS` velocities already include the partial-cell factor, and
  the `ADV*` and `DF*` fluxes are archived already integrated over the
  cell face (degC m3/s for heat), which is why the convergences are
  divided by the volume directly; `hFac` is applied once, in the
  volume element, and never to those variables
  again.[^hfac-gotcha][^tut-heat]
- Convergences are divided by `rA * drF * hFacC`; the forcing is
  divided by `hFacC * drF` after the `rhoconst * c_p` conversion, which
  is the same volume normalisation with `rA` cancelled against the
  per-area flux.[^sanctioned-heat-code]

## Formulation traps and their signatures

Each signature is where the omitted or misapplied term acts, read off
the term definitions above; the geothermal and oceFWflx rows are also
measured, by the tutorial and by the volume recipe.

| Omission or error | Signature |
|---|---|
| geothermal flux left out | closure degrades with depth and fails at the seafloor; the tutorial's own recomputation without the term sits three orders above the closure residual[^tut-heat][^geothermal-gotcha] |
| z* scale factor left off the tendency | surface-intensified residual tracking ETAN variability[^tut-heat] |
| DFrI forgotten | near-surface closure failure where implicit mixing dominates[^tut-heat] |
| hFac applied to *MASS or flux variables again | double-counted partial cells[^hfac-gotcha][^tut-heat] |
| monthly means used as bookends instead of snapshots | tendency wrong by the within-month evolution[^tut-heat] |
| shortwave penetration skipped (all TFLUX at k=0) | vertical structure of the top 200 m wrong; the column integral still closes, which hides the error from column-only checks[^tut-heat] |
| naive difference instead of tile-aware differencing | closure fails along tile seams only[^tut-heat] |
| oceFWflx added to the volume budget as forcing | surface-layer residual six orders above round-off, all at k = 0[^volume-recipe] |
| computed on regridded fields | closure fails everywhere, by construction[^native-gotcha] |

[^tut-heat]: ECCO v4 Python tutorial: global heat budget closure notebook (the term definitions, constants, shortwave and geothermal forcing)
[^tut-salt]: ECCO v4 Python tutorial: salt, salinity and freshwater budgets notebook
[^tut-volume]: ECCO v4 Python tutorial: global volume and sea level budget notebook
[^sanctioned-heat-code]: The sanctioned heat budget computation, sha-bound by its attester; the four terms above are its code
[^heat-computation]: The attested heat budget, owner of the heat pass bar and its baseline residuals
[^salt-recipe]: The salt budget recipe, owner of the measured salt residuals until the attested computation is extracted
[^volume-recipe]: The volume budget recipe, owner of the measured volume residuals and of the oceFWflx double-count measurement
[^geothermal-gotcha]: The geothermal flux is a model input, not a PO.DAAC collection; its omission signature
[^hfac-gotcha]: The MASS-suffixed velocities and the flux variables already carry hFac
[^native-gotcha]: Budgets close only on the native llc90 grid
[^llc90-grid]: The geometry collection: rA, drF, hFacC, Depth, Z and Zp1 on the native grid
