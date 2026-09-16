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
   open-domain integrals carry boundary transports explicitly.
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

## Attested runs

Where the budget has an attested computation in the provider bundle,
step 4 runs its sanctioned executor and step 5 runs its attester; this
section is that procedure, with the paths and the parameters bound.
The provider bundle is installed with the nasa-daac-knowledge
dependency; its root is the `installPath` of that entry in
`claude plugin list --json`, or a checkout named by
`NASA_DAAC_KNOWLEDGE` (the way the receipt-figures renderer resolves
it). `$PODAAC` below stands for `<that root>/knowledge/podaac`. Never
edit an executor: its attester hashes it, and a changed hash fails by
construction. Run the named attester on the receipt before quoting any
number from it; a FAIL is reported as a FAIL with the failing field
named, never worked around. These executors take no `--runtime` flag
(their receipts carry no runtime block); record the runtime name
(`claude-code` here) in the report beside the receipt's run id.

Every executor here reads the native granules from `--data-root`
(default `~/ECCO_V4r4`): the 2010 fixture cache (about 2.5 GB, the
geometry granule plus the monthly and snapshot collections the concept
names, fetched with earthaccess under an Earthdata Login; the
repository's goldens tree stages it) or the science record over 1992
to 2017 (`~/ECCO_V4r4_record`). The tree must carry the RECORD.json
stamp the provider's verify tool leaves after checking it against its
manifest (`uv run <root>/tools/science_record_verify.py --manifest
$PODAAC/references/retrieval/fixtures-2010-manifest.json --data-root
~/ECCO_V4r4 --checksum all --exact --stamp`, once after the first
fetch), since every attester refuses a receipt from an unstamped tree.

**Heat budget closure, `ecco-heat-budget`**
(`knowledge/podaac/computations/ecco-heat-budget.md`; executor
`references/computations/ecco_heat_budget.py`, attester
`references/attesters/budget_residual.py`). Binds `year` (required)
and `region` (optional; `tile1-interior` is the default and the one
registered value):

```bash
uv run $PODAAC/references/computations/ecco_heat_budget.py \
  --year 2010 --region tile1-interior --data-root ~/ECCO_V4r4 \
  --receipt /tmp/heat-budget-receipt.json
uv run $PODAAC/references/attesters/budget_residual.py /tmp/heat-budget-receipt.json
```

The receipt carries exactly `run_id`, `code_sha256`, `data` (the tree
and its stamp), `bound_parameters`, `residual_max`, `residual_p999`
and `cells_evaluated`. PASS (exit 0) requires the sanctioned code
hash, a verify-tool stamp in `data.record`, the declared parameter set
exactly, and the residuals within the bars the concept records
(`residual_max <= 1e-10`, `residual_p999 <= 1e-11` degC/s); FAIL
(exit 1) names the field.

**Regional heat, salt and volume budgets, `ecco-regional-heat-budget`,
`ecco-regional-salt-budget` and `ecco-regional-volume-budget`** (one
executor, `references/computations/ecco_regional_budget.py`, under
three contracts; one attester,
`references/attesters/regional_budget_check.py`). Binds `budget`
(`heat`, `salt` or `volume`), the control volume as a registered
`region` (`southeast-atlantic-upper`) or an explicit
`--box LAT0 LAT1 LON0 LON1` with `--depth-m`, and `year` (default
2010):

```bash
uv run $PODAAC/references/computations/ecco_regional_budget.py \
  --budget heat --region southeast-atlantic-upper --year 2010 \
  --data-root ~/ECCO_V4r4 --receipt /tmp/regional-heat-receipt.json
uv run $PODAAC/references/attesters/regional_budget_check.py /tmp/regional-heat-receipt.json
```

The receipt carries `run_id`, `code_sha256`, `data`,
`bound_parameters`, `resolved_volume` (the mask and geometry digests,
the wet and bottom cell counts), `results`, `mutation_evidence` and
`caveats`. The attester recomputes both bars from the results, checks
every mutation's caught flag against its own numbers, and on the
reference configuration (southeast-atlantic-upper, 2010) checks the
wet-cell count, the volume and the residual per volume two-sided. An
explicit box is disclosed by mask digest and carries no anchor; the
report says so.

**Reynolds flux decomposition, `ecco-flux-decomposition`** (executor
`references/computations/ecco_flux_decomposition.py`, attester
`references/attesters/fluxdecomp_check.py`). Binds `region`
(registered, `southeast-atlantic-upper`), `grouping`
(`full-four-term`, `time-mean-eddy` or `anomaly`) and `year` (default
2010):

```bash
uv run $PODAAC/references/computations/ecco_flux_decomposition.py \
  --region southeast-atlantic-upper --grouping full-four-term --year 2010 \
  --data-root ~/ECCO_V4r4 --receipt /tmp/flux-decomposition-receipt.json
uv run $PODAAC/references/attesters/fluxdecomp_check.py /tmp/flux-decomposition-receipt.json
```

All four terms travel in every receipt whatever the grouping; the
attester checks the two oracles (the four-term identity and the
vanishing cross-term means) and that the reported view agrees with
the stored terms.

**Whole-grid salt and volume closure, `ecco-salt-budget` and
`ecco-volume-budget`**: draft contracts with no sanctioned executor
or attester yet (the extraction from the goldens, the way the heat
budget was extracted, has not landed). Until those concepts carry
`computation` and `attester` fields, a salt or volume closure on the
whole grid is a recipe-owned budget under step 5, judged against the
recipe's tolerance and reported as unattested; the regional variants
above are the attested route for a salt or volume budget today.

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
