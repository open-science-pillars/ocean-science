---
name: ocean-budget
description: Ocean property budgets on the native ECCO grid only; refuses regridded budgets; budget-auditor auto-run on residuals.
---

# ocean-budget

Compute closed property budgets, or refuse. Authored in Session 9 per
SPECIFICATION.md v0.5.1 §4.4. Works by slash command or conversationally
("heat budget for the subpolar gyre"). The formulation authority is
`skills/ecco/references/budget-formulation.md`; the tolerance authority
is `knowledge/recipes/ecco-heat-budget.md`; the diagnosis discipline is
budget-closure's.

## The native-grid rule (🔴, non-negotiable)

A budget request on regridded fields is REFUSED: no correct budget
formulation exists there (gotcha ecco-native-vs-regridded, cited in the
refusal), and the refusal always offers the native path with the exact
collections. This rule fires before any computation, whatever the
framing of the request.

## Behavior, in order

1. **Parse and show back:** property (heat, salt, volume), domain,
   period, depth range (full-depth vs upper-ocean changes the
   geothermal and shortwave handling).
2. **Knowledge first, restated:** the heat-budget recipe (inputs,
   tolerance), the geothermal gotcha for heat budgets (the term is a
   static ancillary, not a PO.DAAC collection), snapshots for
   tendencies, and the native-grid rule above.
3. **Inputs check:** the recipe's exact collections present (via
   load-ecco, gate and all), snapshot bookends covering the period,
   the geothermal file for heat. Missing inputs stop the budget with
   the list of what to fetch; no term gets approximated silently.
4. **Compute the four terms** exactly per the budget-formulation
   reference: z*-corrected tendency from snapshots; tile-aware
   advective and diffusive convergences (explicit plus implicit
   vertical); forcing with shortwave penetration and geothermal at the
   bottom wet cell. Volume element rA * drF * hFacC.
5. **Closure check against the recipe tolerance** (relative residual
   at or below 1e-6 pointwise on wet cells). Domain-integrated closure
   is asserted only on closed domains; open-domain integrals carry
   boundary transports explicitly (SPEC §6 distinction).
6. **budget-auditor auto-runs on the result**: every budget, not just
   failing ones; on residual failure it checks the geothermal gotcha
   first, then the formulation traps table, and proposes fixes without
   applying them.
7. **Report:** all four terms with units, the residual against the
   stated tolerance, the domain and period, and the concepts and
   recipe consulted. A budget that fails closure is reported as failed
   with the diagnosis, never presented with the residual absorbed into
   a term.

## Must NOT

- Never compute any budget on regridded fields, under any framing.
- Never substitute monthly means for snapshot bookends.
- Never omit geothermal from full-depth or deep heat budgets.
- Never absorb a residual into a physical term or average it away.
- Never hardcode the tolerance; read the recipe.
- Never skip the auditor, even on green residuals.
