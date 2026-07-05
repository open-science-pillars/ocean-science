---
name: budget-closure
description: "Closed property budgets on native model grids: tendency, advection, diffusion, forcing terms; machine-precision residual expectations."
user-invocable: false
---

# budget-closure

Background expertise for property budgets that actually close. The ECCO heat
budget's exact terms live in `skills/ecco/references/budget-formulation.md`;
expected residuals live in recipe concepts; this skill carries the
architecture and the diagnosis discipline.

## What closure means

A closed budget is an identity, not a regression:

```
tendency = advective convergence + diffusive convergence + forcing
```

per grid cell, per time step, in the property's units. It holds exactly
in a dynamically consistent product (a free-running model, a state
estimate fit through adjusted controls) because the model integrated
exactly these terms. It does NOT hold in sequential data-assimilation
products (reanalyses with increments): the increment is a budget term
the product usually does not ship. Know which kind of product is in
hand before promising closure.

## The four terms, generically

1. **Tendency** comes from state SNAPSHOTS at interval boundaries,
   never from consecutive monthly means; free-surface models (z*) also
   need the layer-thickness or scale-factor correction in the tendency.
2. **Advective convergence** differences face fluxes (topology-aware
   operators; see ocean-grids), with the vertical flux zero-padded at
   the bottom.
3. **Diffusive convergence** includes explicit AND implicit vertical
   contributions; the implicit part carries most vertical mixing in
   most models.
4. **Forcing** enters where physics put it: penetrating shortwave
   distributed over depth, other surface fluxes in the top layer,
   geothermal at the bottom wet cell (heat budgets only).

## Residual expectations come from recipes

The expected residual for a validated budget is stated in its recipe
concept (for ECCO heat: `knowledge/recipes/ecco-heat-budget.md`), with
provenance. Consult the recipe and compare against its stated
expectation; a residual above it is a formulation error to diagnose,
never noise to average away, and "small compared to the terms" is not a
closure criterion.

## Diagnosing non-closure by signature

Work the signature, not guesswork (the ECCO-specific traps table in
budget-formulation.md maps these):

- Residual grows with depth, concentrates at the seafloor: missing
  bottom forcing (geothermal, for heat).
- Residual surface-intensified and tracking sea level variability:
  missing free-surface (z*) correction in the tendency.
- Residual only along tile or fold seams: index-space differencing
  where topology-aware operators were needed.
- Residual proportional to a term near topography: partial cells
  (hFac) applied twice or not at all.
- Residual roughly the within-month evolution: monthly means used as
  tendency bookends instead of snapshots.
- Residual everywhere, same order as the terms: computed on regridded
  fields; no correct formulation exists there (the
  ecco-native-vs-regridded gotcha; refusal is the ocean-budget
  workflow's job).

## Pointwise vs domain-integrated

Pointwise closure (every cell balances) is valid on ANY spatial subset,
which is why golden-notebook fixtures can assert it on small regions.
Domain-integrated closure (tendency of the integral balances boundary
fluxes plus interior forcing) holds only on closed domains; asserting
it on an open subset without the boundary transport term is a made-up
test. SPEC §6 encodes this for verification.

## Discipline

Budget results report all terms plus the residual against the recipe
expectation, and the budget-auditor agent reviews any budget after
computation (checking the geothermal gotcha first on heat-budget
failures); it proposes fixes, never applies them.

## Must NOT

- Never hardcode an expected residual; read the recipe concept.
- Never accept "residual is small relative to terms" as closure.
- Never compute tendencies from monthly means.
- Never omit the implicit vertical diffusion term.
- Never assert domain-integrated closure on an open domain without
  boundary fluxes.
- Never attempt a budget on regridded fields.
