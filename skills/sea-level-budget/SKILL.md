---
name: sea-level-budget
description: "Run the attested global sea level budget closure (altimetry against Argo steric plus GRACE-FO mass) through the provider bundle's sanctioned executor and attest the receipt before quoting a number. Keywords: sea level budget, budget closure, altimetry, steric, ocean mass, GRACE-FO, mascons, inter-mission gap, bridge."
user-invocable: true
---

# sea-level-budget

Run instructions for the attested computation
`knowledge/computations/sea-level-budget.md` in this package: over one stated period, the three monthly global-mean series
in millimeters (altimetric sea level from NASA-SSH, steric sea level
from Argo-era hydrography with its sampled depth floor stated, ocean
mass from the GRACE-FO mascons), the residual, the trend of every
term and of the residual with the interval the bundle's one
sanctioned trend method states, the combined uncertainty, the verdict
`closed_within_uncertainty`, and the corrections table the closure
convention (`knowledge/podaac/conventions/sea-level-budget-closure.md`)
demands as a bookkeeping block. The contract (parameters, receipt
fields, refusal codes) is the concept and the executor's own usage
text; this skill is the procedure an agent follows to run it. The
sea-level skill carries the discipline (the decomposition, the three
observing systems, the corrections-first rule); consult it and the
convention before running.

A runner binds VALUES for `period` and, across the inter-mission gap,
`bridge`, names the runtime that ran it, and never edits the
computation; the attester hashes it. Receipts and verdicts are runtime
artifacts, never committed to this package; nothing is committed under a
fixtures directory either, since the fixture is generated at run time.

The executor and the attester of every computation below ship in this
package, in the scripts directory of the skill that runs them, and the
concept each one answers to is under `knowledge/computations/`.
`${CLAUDE_PLUGIN_ROOT}` below is this package's root, which the runtime
sets:

- executor: `${CLAUDE_PLUGIN_ROOT}/skills/sea-level-budget/scripts/sea_level_budget.py`
- attester: `${CLAUDE_PLUGIN_ROOT}/skills/sea-level-budget/scripts/sea_level_budget_check.py`
- loaders: `${CLAUDE_PLUGIN_ROOT}/skills/sea-level-budget/scripts/slb_altimetry_nasa_ssh.py`,
  `slb_steric_rg.py`, `slb_mass_mascons.py` and `slb_data_root.py`
- the committed data root: `${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/sea-level-budget-root`

Parameters bound on every run: `--period YYYY-MM:YYYY-MM` (the
declared `period`) and, for a period that crosses the GRACE to
GRACE-FO gap, `--bridge TEXT` (the declared `bridge`, a citation of
the independent continuity evidence). The runtime name is passed with
`--runtime`; from Claude Code pass `--runtime claude-code`, from
another runtime its own name (`--runtime-version V` optionally).
`--fixture` or `--data-root DIR` selects the input; `--receipt PATH`
names the receipt.

## Behavior, in order

1. **Parse and show back:** the period, whether it crosses the
   inter-mission gap (mass months on both sides of 2017-07 through
   2018-05) and so needs a bridge, and whether the run is a rehearsal
   on the fixture or a real run on the committed data root. Consult
   the concept, the closure convention and the sea-level skill's
   concepts (the GRACE leakage and GIA gotchas, the NASA-SSH dataset
   concept, the Roemmich and Gilson depth-floor gotcha), restating
   what each fixes about the bookkeeping and citing each by path.
2. **The fixture run** (the reference, and the rehearsal):

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/sea-level-budget/scripts/sea_level_budget.py \
     --fixture --seed 7 --period 2005-01:2016-12 --runtime claude-code \
     --receipt /tmp/sea-level-budget-receipt.json
   ```

   The fixture is regenerated deterministically from the seed (a
   hash-based Gaussian stream, no numeric library in the path); its
   digest is in the receipt and the attester regenerates it. Knobs:
   `--seed N` (default 7), `--fixture-offset MM` (an inter-mission
   offset injected into the mass series after the gap, zero by
   default, so a bridged run across the gap has something to fail
   on), and `--capability-root DIR` for a capability whose golden
   invokes this executor and whose release the receipt is evidence
   for (the `bundle` block names the package the executor ships in,
   which is this one). The
   headline line prints the residual trend, the closure gap against
   the bar, and the verdict; the receipt carries exactly the declared
   fields, with the three series, their uncertainties and the
   residual at full precision, the four trend blocks, the combined
   uncertainty, the verdict and the bookkeeping table.
3. **The refusal rule.** A period that crosses the gap refuses
   without `--bridge TEXT`, and a refusal is never a number:

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/sea-level-budget/scripts/sea_level_budget.py \
     --fixture --period 2016-01:2019-12 --runtime claude-code \
     --receipt /tmp/refusal.json
   echo $?   # 3, and the receipt says refused: true with the reason
   ```

   The other refusals are a term with fewer than 24 months in the
   period, a period outside the record, and a term whose interval the
   chain refuses to state. A refusal receipt attests PASS as a refusal
   (the verdict line carries the word refusal). Report the refusal
   and its reason; a bridge is a citation the user supplies or
   confirms, never a phrase invented to get past the refusal.
4. **A real run on a data root.** The first real run's tree is
   committed at `${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/sea-level-budget-root`,
   built by the loaders (`slb_altimetry_nasa_ssh.py` for the NASA-SSH
   grids, `slb_steric_rg.py` for the Roemmich and Gilson product,
   `slb_mass_mascons.py` for the mascon grid, each with `--selftest`)
   and stamped by `slb_data_root.py`, which writes RECORD.json with
   the corrections table from the loaders' stamps; SOURCES.json
   records the downloads. This is the layout the computation reads,
   `--data-root DIR` in place of `--fixture`:

   ```
   DIR/
     RECORD.json      the stamp: record name, manifest_sha256, verified_utc,
                      and the corrections table under "bookkeeping"
     altimetry.csv    month,value_mm,uncertainty_mm   one row per calendar month
     steric.csv       month,value_mm,uncertainty_mm
     mass.csv         month,value_mm,uncertainty_mm   missing months absent, never filled
   ```

   Months are `YYYY-MM`, unique and in order; values are global means
   in millimeters against each product's own baseline (the trend does
   not care about the baseline, and the receipt records the values as
   read). `bookkeeping` must carry `gia.altimetry`, `gia.mass`,
   `inverse_barometer.altimetry`, `inverse_barometer.mass`,
   `reference_frame.altimetry`, `reference_frame.mass`,
   `effective_smoothing.altimetry`, `effective_smoothing.mass`,
   `low_degree.mass`, `deep_steric.sampled_depth_floor_m` and
   `deep_steric.steric_source`, each a statement in words read from
   the product documentation at loading time; the executor refuses a
   stamp that lacks any of them. The receipt copies the stamp and the
   three file digests.

   Which loader produces each file:

   - `altimetry.csv`: the global mean per calendar month of the
     NASA-SSH simple grids in the stamped record
     (`knowledge/podaac/datasets/nasa-ssh.md` and the record note it
     cites), the grids of a month averaged (they share passes), the
     dynamic atmospheric correction as the product applies it.
   - `steric.csv`: the ocean mean of a gridded Argo steric height
     (Roemmich and Gilson, or a successor) over its sampled depth
     range, the floor written into `deep_steric.sampled_depth_floor_m`.
     Regionally, from profiles through core's observations connector
     (`argo_search`, then `argo_profile` for each float and cycle):
     that loader lives outside the gate, since a gate never depends on
     a connector, and its output is the same CSV.
   - `mass.csv`: the CRI-filtered mascon grids summed over the ocean
     mascons with their true areas and converted to millimeters of
     sea level equivalent per
     `knowledge/podaac/recipes/grace-mass-to-sea-level.md`, the
     product's formal uncertainty combined per its guidance on
     correlated mascon errors; the months the product lacks are absent
     from the file.

   The real run on the committed root:

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/sea-level-budget/scripts/sea_level_budget.py \
     --data-root ${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/sea-level-budget-root \
     --period 2005-01:2016-12 --runtime claude-code \
     --receipt /tmp/sea-level-budget-record.json
   ```

5. **Attest the receipt before quoting anything from it.** Every
   number quoted from a receipt comes after the attester says PASS on
   that exact receipt:

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/sea-level-budget/scripts/sea_level_budget_check.py /tmp/sea-level-budget-receipt.json \
     [--out /tmp/attestation.json]
   ```

   PASS requires every declared field, the sanctioned code hash, this
   package's name, version and release lock digest in
   the `bundle` block and a well-formed `capability` block, a named
   runtime, the fixture regenerated at the receipt's seed hashing to
   the receipt's digest (or the stamp for a data root), the series and
   the months used and missing as the regenerated fixture yields them,
   every trend, interval, formal error, the combined uncertainty and
   the verdict recomputed from the series, the corrections table
   complete with the gap handling agreeing with the months (a bridge
   where the period crosses the gap), and on the fixture the known
   truth. `--out` writes the attestation (verdict, refusal flag,
   digests, the capability, bundle and runtime blocks, every check)
   for a qualification record. `--selftest` runs the pass, the
   tampers, the wrong release, the refusals and the stripped bridge.
6. **Report** the residual trend against the combined uncertainty and
   the verdict as the receipt states them, the trend of each term
   with its interval and the period, the months dropped at the gap,
   the corrections table as the bookkeeping states it (the
   deep-steric systematic beside the combined uncertainty, never
   inside it), the run id, the attester's verdict and the concepts
   consulted. Apparent non-closure is a correction-consistency finding
   before it is a missing-physics finding: the sea-level skill's hard
   refusal applies to the reading of the receipt.

## Must NOT

- Never quote a number from a receipt the attester has not passed,
  and never edit the sanctioned computation; the attester fails a
  changed hash by construction.
- Never present a refusal as a number, and never invent a bridge; a
  period across the gap runs only with a citation the user supplies
  or confirms.
- Never fill a missing mass month or fit the terms over different
  epochs; the executor drops a month with no mass solution from every
  term, and the receipt says which.
- Never declare non-closure before auditing correction consistency
  (the sea-level skill's rule), and never present the deep-steric
  systematic as part of the combined uncertainty.
- Never commit a receipt, a verdict or a generated fixture to the
  bundle.
