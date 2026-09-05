---
name: ocean-budget
description: Ocean property budgets on the native ECCO grid only; refuses regridded budgets; budget-auditor auto-run on residuals.
---

# ocean-budget

Compute closed property budgets, or refuse. Works by slash command or conversationally
("heat budget for the subpolar gyre"). The formulation authority is
`knowledge/podaac/conventions/ecco-budget-formulation.md`
(the procedure for applying it is `skills/ecco/references/budget-formulation.md`);
the tolerance authority is the property's attested computation
(`knowledge/podaac/computations/ecco-heat-budget.md` for heat,
which also names the sanctioned code and its attester) or, until a
property's computation reaches stable, its recipe under
`knowledge/podaac/recipes/`; the diagnosis discipline is
budget-closure's.

## The native-grid rule (🔴, non-negotiable)

A budget request on regridded fields is REFUSED: no correct budget
formulation exists there (gotcha ecco-native-vs-regridded, cited in the
refusal), and the refusal always offers the native path with the exact
collections. This rule fires before any computation, whatever the
framing of the request; the ecco skill owns it for the plugin, and this
workflow applies it at its gate.

## Behavior, in order

1. **Parse and show back:** property (heat, salt, volume), domain,
   period, depth range.
2. **Consult the bundle for THIS budget first.** Consult installed
   knowledge concepts first, as the core `consult-knowledge` skill
   sets out, by property, product, and depth range; the ecco skill
   lists the concepts this plugin resolves to. Read the property's
   attested computation under `knowledge/podaac/computations/`
   (its declared parameters, inputs, pass bar, sanctioned code, and
   attester) or, until that computation reaches stable, its recipe
   under `knowledge/podaac/recipes/` (its inputs and measured
   tolerance), and the gotchas that constrain it (for a heat budget,
   the geothermal term; for any budget, the native-grid rule and the
   hFac double count). Restate what applies and cite each by path. If
   the property has neither in the bundle, its tolerance is
   unvalidated and the budget says so.
3. **Inputs check:** the owning concept's exact collections present
   (via load-ecco, gate and all), the snapshot bookends it requires,
   and every ancillary the applicable gotchas name. Missing inputs stop
   the budget with the list of what to fetch; no term is approximated
   silently.
4. **Compute the terms.** Where the property has an attested
   computation, run its sanctioned code from the installed bundle with the
   declared parameters bound (never edited; the attester hashes it)
   and keep the receipt; the executor instructions the concept names
   are the procedure. Otherwise compute exactly per the budget
   formulation convention
   (`knowledge/podaac/conventions/ecco-budget-formulation.md`,
   applied per `skills/ecco/references/budget-formulation.md`); that
   concept is the authority for the term set and the corrections, not
   this skill. Volume element rA * drF * hFacC.
5. **Closure check against the owning concept's bar:** an attested
   receipt goes through the attester and its verdict is reported as
   read; a recipe-owned budget is judged against the recipe's tolerance
   (an absolute, measured tolerance; never a hardcoded relative ratio).
   Domain-integrated closure is asserted only on closed domains;
   open-domain integrals carry boundary transports explicitly (SPEC §6
   distinction).
6. **budget-auditor auto-runs on the result**: every budget, not just
   failing ones; on residual failure it checks the geothermal gotcha
   first, then the formulation traps table, and proposes fixes without
   applying them.
7. **Report:** all four terms with units, the residual against the
   stated bar (with the attester's verdict and the receipt's run id
   where the budget is attested), the domain and period, and the
   concepts consulted. A budget that fails closure is reported as failed
   with the diagnosis, never presented with the residual absorbed into
   a term.

## Must NOT

- Never compute any budget on regridded fields, under any framing.
  (Hard refusal: invariant, universal; the one rule that fires without
  consulting anything.)
- Never absorb a residual into a physical term or average it away.
- Never hardcode the tolerance or restate a gotcha's rule; read them
  from the computation or recipe concept and the gotcha concepts.
- Never edit the sanctioned computation to make a budget pass; the
  attester fails a changed hash by construction.
- Never skip the auditor, even on green residuals.

Dataset-specific rules (geothermal for deep heat budgets, snapshots for
tendencies, the term formulation, the pass bars) are NOT restated
here: they live in the computation and recipe concepts, the gotcha
concepts, and the budget formulation convention, and are consulted per
step 2. That is what lets a corrected tolerance or a new budget gotcha
change this skill's behavior without editing it.
