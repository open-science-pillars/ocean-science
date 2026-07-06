---
name: budget-closure
description: "Closed property budgets on native model grids: tendency, advection, diffusion, forcing terms; machine-precision residual expectations."
user-invocable: false
---

# budget-closure

Background expertise for property budgets that actually close. This skill
carries the architecture and the diagnosis discipline; the exact terms,
constants, and expected residuals are dataset knowledge and live in the
bundle's recipe and gotcha concepts and in the ECCO budget-formulation
reference, consulted per the step below, never carried here.

## Consult the bundle for this budget

Before diagnosing or blessing any budget, DISCOVER and read the applicable
concepts; do not work from a remembered list or carry a number here. Glob and
grep `knowledge/recipes/` for the property's budget recipe (heat, salt, or
volume) and take the expected residual, its tolerance, and its provenance from
there, restating and citing by path. Glob and grep `knowledge/gotchas/` for
the gotchas that constrain the property (for heat, the geothermal term; for any
budget, the native-vs-regridded rule) and restate what each changes about the
plan. The exact term formulation, the z* correction, shortwave penetration, and
the traps table are quoted in `skills/ecco/references/budget-formulation.md`;
consult it for the terms. A concept or tolerance added or corrected since you
last ran is found this way, which is what lets it change this skill's behavior
without editing this file. A residual above the recipe's stated expectation is
a formulation error to diagnose, never noise to average away, and "small
compared to the terms" is not a closure criterion.

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
   geothermal at the bottom wet cell (heat budgets only). The dataset
   specifics of each term are read from the concepts per the step above.

## Diagnosing non-closure by signature

Work the signature, not guesswork; the property's recipe and the traps
table in the budget-formulation reference map these in dataset-specific
detail, consulted per the step above:

- Residual grows with depth, concentrates at the seafloor: missing
  bottom forcing (for heat, the geothermal term; consult its gotcha).
- Residual surface-intensified and tracking sea level variability:
  missing free-surface (z*) correction in the tendency.
- Residual only along tile or fold seams: index-space differencing
  where topology-aware operators were needed (see ocean-grids).
- Residual proportional to a term near topography: partial cells
  (hFac) applied twice or not at all.
- Residual roughly the within-month evolution: monthly means used as
  tendency bookends instead of snapshots.
- Residual everywhere, same order as the terms: fields were regridded;
  consult the native-vs-regridded gotcha (refusing regridded budgets is
  the ocean-budget workflow's job).

## Pointwise vs domain-integrated

Pointwise closure (every cell balances) is valid on ANY spatial subset,
which is why golden-notebook fixtures can assert it on small regions.
Domain-integrated closure (tendency of the integral balances boundary
fluxes plus interior forcing) holds only on closed domains; asserting
it on an open subset without the boundary transport term is a made-up
test. SPEC §6 encodes this for verification.

## Discipline

Budget results report all terms plus the residual against the recipe's
stated expectation, and the budget-auditor agent reviews any budget
after computation (consulting the applicable gotchas first, the
geothermal term first on heat-budget failures); it proposes fixes,
never applies them.

## Hard refusals

These fire regardless of dataset; they are invariant, refusal-shaped,
and universal, not dataset facts:

- Never bless a budget computed on regridded fields; no correct
  formulation exists there. (Consult the native-vs-regridded gotcha for
  the mechanism; the outright refusal of such a request is the
  ocean-budget workflow's.)
- Never accept "residual is small relative to the terms" as closure.
- Never compute tendencies from consecutive monthly means; tendency
  comes from state snapshots at the interval boundaries.
- Never omit the implicit vertical diffusion term.
- Never assert domain-integrated closure on an open domain without the
  boundary transport term.
- Never hardcode an expected residual; read it from the recipe concept.

Dataset-specific rules (the geothermal term, the exact term formulation
and constants, the z* and shortwave corrections, the measured residual
tolerances) are NOT restated here: they live in the recipe concepts, the
ECCO gotchas, and `skills/ecco/references/budget-formulation.md`,
consulted per the step above. That is what lets a corrected tolerance or
a new budget gotcha change this skill's behavior without editing it.
