# ECCO v4r4 heat budget formulation (native grid)

Reference for the ecco skill, per SPECIFICATION.md v0.5.1 §4.2.
**Verified term by term against the ECCO v4 Python tutorial's
`ECCO_v4_Heat_budget_closure.ipynb`** (github.com/ECCO-GROUP/
ECCO-v4-Python-Tutorial, master branch, source fetched and code cells
extracted 2026-07-04); each term below quotes the tutorial's own code.
Budgets close ONLY on the native llc90 grid with exactly this
formulation; the regridded product does not conserve (see the
ecco-native-vs-regridded gotcha).

## The budget identity

Per grid cell, in degC/s:

```
G_total = G_advection + G_diffusion + G_forcing
```

Residual expectation: machine precision pointwise (float32 fields;
relative residuals around 1e-9 of term magnitude), at every cell, every
month. A residual above that is a formulation error, not noise; check
the traps table before blaming the data.

## Constants and the volume element (tutorial values)

```python
rhoconst = 1029          # kg m-3, Boussinesq reference density
c_p = 3994               # J kg-1 K-1
vol = ecco_grid.rA * ecco_grid.drF * ecco_grid.hFacC   # m3, partial cells IN
```

## Term 1: tendency (G_total), snapshots and the z* scale factor

Month-boundary snapshots (SNAPSHOT collections), not monthly means, and
THETA scaled for the moving z* surface:

```python
sTHETA = THETA_snp * (1 + ETAN_snp / Depth)       # s* scale factor
G_total = sTHETA.diff('time_snp') / delta_t        # degC s-1
```

The `(1 + ETAN/Depth)` factor is the z* volume correction; omitting it
leaves a surface-intensified residual that looks like a mixing error but
is bookkeeping. `delta_t` comes from the actual snapshot spacing.

## Term 2: advective convergence

Horizontal from the 3D temperature-flux product, differenced with the
tile-aware operator (xgcm `diff_2d_vector` with llc face connections, or
the tutorial's equivalent workaround):

```python
ADVxy_diff = grid.diff_2d_vector({'X': ADVx_TH, 'Y': ADVy_TH}, boundary='fill')
adv_hConvH = -(ADVxy_diff['X'] + ADVxy_diff['Y'])
adv_vConvH = ADVr_TH.diff('k_l')                   # zero-padded at bottom
G_advection = (adv_hConvH + adv_vConvH) / vol
```

`ADVr_TH` is masked to zero where `hFacC == 0` first (dry cells carry
fill garbage otherwise).

## Term 3: diffusive convergence

Same pattern; vertical diffusion is explicit PLUS implicit:

```python
DFxyE_diff = grid.diff_2d_vector({'X': DFxE_TH, 'Y': DFyE_TH}, boundary='fill')
dif_hConvH = -(DFxyE_diff['X'] + DFxyE_diff['Y'])
dif_vConvH = (DFrE_TH + DFrI_TH).diff('k_l')       # explicit + implicit
G_diffusion = (dif_hConvH + dif_vConvH) / vol
```

Forgetting `DFrI_TH` (the implicit part, where most vertical mixing
lives) is a classic near-surface closure failure.

## Term 4: forcing, shortwave penetration plus geothermal

Shortwave penetrates with the two-band double exponential
(R = 0.62, zeta1 = 0.6 m, zeta2 = 20.0 m), cut off below 200 m:

```python
q1 = R*exp(RF[:-1]/zeta1) + (1-R)*exp(RF[:-1]/zeta2)   # at upper faces
q2 = R*exp(RF[1:]/zeta1)  + (1-R)*exp(RF[1:]/zeta2)    # at lower faces
q1[zCut:] = 0; q2[zCut-1:] = 0                          # Z < -200 m cutoff
forcH_subsurf = (q1*(mskC==1) - q2*(mskC.shift(k=-1)==1)) * oceQsw
forcH_surf = (TFLUX - (1-(q1[0]-q2[0]))*oceQsw) * mskC[0]   # k=0 layer
forcH = concat([forcH_surf, forcH_subsurf[:, :, 1:]], dim='k')
```

Geothermal flux enters at the BOTTOM wet cell of each column, from the
static ancillary file (not a PO.DAAC collection; the tutorial reads
`geothermalFlux.bin` from its `misc/` directory via
`ecco.read_llc_to_tiles`):

```python
mskb = mskC - mskC.shift(k=-1)                      # bottom-cell mask
GEOFLX = geoflx_llc * mskb                          # W m-2, 3D
G_forcing = ((forcH + GEOFLX) / (rhoconst*c_p)) / (hFacC*drF)
```

## The traps table (each verified against the formulation above)

| Omission or error | Signature |
|---|---|
| geothermal flux left out | deep and bottom cells fail closure by order 10 to 100 mW m-2 equivalent; column integrals off everywhere the seafloor is warm (the ecco-geothermal-flux gotcha) |
| z* scale factor left off the tendency | surface-intensified residual tracking ETAN variability |
| DFrI_TH forgotten | near-surface closure failure where implicit mixing dominates |
| hFac applied to *MASS or *_TH flux variables again | double-counted partial cells; the MASS/flux variables already include hFac |
| monthly means used as bookends instead of snapshots | tendency term wrong by the within-month evolution |
| shortwave penetration skipped (all TFLUX at k=0) | vertical structure of the top 200 m wrong; column integral still closes, which hides the error from lazy checks |
| naive np.diff instead of tile-aware differencing | closure fails along tile seams only (see llc90-grid.md) |
| computed on regridded fields | closure fails everywhere, by construction |

## Salt, salinity, and volume budgets

Same architecture with their own products: salt uses `ADV*_SLT`,
`DF*_SLT`, plus the salt-plume term `oceSPtnd` and surface `SFLUX`;
volume uses `UVELMASS/VVELMASS/WVELMASS` convergence against the
z*-corrected layer thickness tendency (ETAN snapshots). The tutorial
repository carries dedicated notebooks for both
(`ECCO_v4_Salt_and_salinity_budget.ipynb`,
`ECCO_v4_Volume_budget_closure.ipynb`); Session 7's recipes pin their
expected residuals.
