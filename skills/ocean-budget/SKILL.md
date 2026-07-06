---
name: ocean-budget
description: Ocean property budgets on the native ECCO grid only; refuses regridded budgets; budget-auditor auto-run on residuals.
---

# ocean-budget

Compute closed property budgets, or refuse. Works by slash command or conversationally
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
   period, depth range.
2. **Consult the bundle for THIS budget first.** Discover and read the
   concepts that apply, do not restate them from memory: search
   `knowledge/recipes/` for the property's budget recipe (its inputs
   and its measured tolerance), and `knowledge/gotchas/` for the
   gotchas that constrain it (for a heat budget, the geothermal term;
   for any budget, the native-grid rule). Restate what applies and cite
   each by path. If the property has no recipe in the bundle, its
   tolerance is unvalidated and the budget says so.
3. **Inputs check:** the recipe's exact collections present (via
   load-ecco, gate and all), the snapshot bookends the recipe requires,
   and every ancillary the applicable gotchas name. Missing inputs stop
   the budget with the list of what to fetch; no term is approximated
   silently.
4. **Compute the terms** exactly per the budget-formulation reference
   (`skills/ecco/references/budget-formulation.md`); that reference is
   the authority for the term set and the corrections, not this skill.
   Volume element rA * drF * hFacC.
5. **Closure check against the recipe's tolerance,** read from the
   recipe concept (it is an absolute, measured tolerance; never a
   hardcoded relative ratio). Domain-integrated closure is asserted
   only on closed domains; open-domain integrals carry boundary
   transports explicitly (SPEC §6 distinction).
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
  (Hard refusal: invariant, universal; the one rule that fires without
  consulting anything.)
- Never absorb a residual into a physical term or average it away.
- Never hardcode the tolerance or restate a gotcha's rule; read them
  from the recipe and the gotcha concepts.
- Never skip the auditor, even on green residuals.

Dataset-specific rules (geothermal for deep heat budgets, snapshots for
tendencies, the term formulation) are NOT restated here: they live in
the recipe, the gotcha concepts, and the budget-formulation reference,
and are consulted per step 2. That is what lets a corrected tolerance or
a new budget gotcha change this skill's behavior without editing it.
