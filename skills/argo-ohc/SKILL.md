---
name: argo-ohc
description: "Run the attested Argo ocean heat content change (0 to 700 and 0 to 2000 dbar) from the Roemmich and Gilson gridded product through this plugin's sanctioned executor and attest the receipt before quoting a number. Keywords: ocean heat content, OHC, Argo, Roemmich Gilson, heat uptake, zettajoules, Earth heat inventory."
user-invocable: true
---

# argo-ohc

Run instructions for the attested computation
`knowledge/computations/argo-ohc.md` (this plugin's own bundle): how
much heat the upper ocean gained over a window from the Roemmich and
Gilson gridded Argo product, for the 0 to 700 dbar and 0 to 2000 dbar
layers, with the interval, the endpoint change, the residual and the
verdict the concept declares. The contract (parameters, receipt
fields, refusal codes) is the concept and the executor's own usage
text; this skill is the procedure an agent follows to run it. A
runner binds VALUES for `window` and `depth`, names the runtime that
ran it, and never edits the computation; the attester hashes it.
Receipts and verdicts are runtime artifacts, never committed to the
bundle; nothing is committed under a fixtures directory either, since
the fixture is generated at run time.

The executor, the attester, the loaders and the stamped data root all
sit under this plugin's bundle, reached through the installed plugin
root:

- executor: `${CLAUDE_PLUGIN_ROOT}/knowledge/references/computations/argo_ohc.py`
- attester: `${CLAUDE_PLUGIN_ROOT}/knowledge/references/attesters/argo_ohc_check.py`
- loaders: `${CLAUDE_PLUGIN_ROOT}/knowledge/references/loaders/ohc_rg_loader.py` and `ohc_data_root.py`
- the committed data root: `${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/argo-ohc-root`

Parameters bound on every run: `--window YYYY-MM:YYYY-MM` (the
declared `window`) and `--depth 700|2000` (the declared `depth`, the
layer floor in dbar). The runtime name is passed with `--runtime`;
from Claude Code pass `--runtime claude-code`, from another runtime
its own name. `--fixture` or `--data-root DIR` selects the input;
`--receipt PATH` names the receipt.

## Behavior, in order

1. **Parse and show back:** the window, the layer (700 or 2000 dbar)
   and whether the run is a rehearsal on the fixture or a real run on
   the committed data root. Consult the concept and the recipe
   (`knowledge/recipes/argo-ohc.md`) and the four Roemmich and Gilson
   gotchas the concept cites, restating what each fixes about the
   answer (the layer, the domain, the fixed 2004 to 2018 baseline, the
   deep ocean as a separate term) and citing each by path.
2. **The fixture run** (the rehearsal, and the reference every
   attester selftest reproduces):

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/knowledge/references/computations/argo_ohc.py \
     --fixture --seed 7 --window 2005-01:2016-12 --depth 2000 --runtime claude-code \
     --receipt /tmp/argo-ohc-receipt.json
   ```

   The fixture is regenerated deterministically from the seed and the
   depth (a hash-based Gaussian stream, no numeric library in the
   path); its digest is in the receipt and the attester regenerates
   it. Knobs: `--seed N` (default 7), `--depth 700|2000`, and
   `--capability-root DIR` for a package whose golden invokes this
   executor and whose release the receipt is evidence for (the
   `bundle` block always names this plugin's package). The headline
   line prints the trend with its interval, the change from the first
   year of the window to the last, the endpoint change read directly,
   the residual against the bar and the verdict; the receipt carries
   exactly the declared fields, with the series at full precision, the
   four terms, the residual, the combined uncertainty, the verdict,
   the rates per unit area, the bookkeeping table, and on a fixture
   the planted truth beside what was recovered.
3. **The refusal rule.** A window that leaves the record's coverage
   refuses, and a refusal is never a number:

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/knowledge/references/computations/argo_ohc.py \
     --fixture --window 2001-01:2016-12 --depth 700 --runtime claude-code \
     --receipt /tmp/refusal.json
   echo $?   # 3, and the receipt says refused: true with the reason
   ```

   The other refusals are fewer than 24 months in the window, fewer
   than twelve values in the first or last year of it (the endpoint
   means need all twelve), and a trend whose interval cannot be
   stated. A refusal receipt attests PASS as a refusal (the verdict
   line reads `PASS refusal`). Report the refusal and its reason; do
   not narrow the window silently to get a number.
4. **A real run on the committed data root.** The tree at
   `knowledge/references/retrieval/argo-ohc-root` is built by the
   loader `ohc_rg_loader.py` (the Roemmich and Gilson product, with
   `--selftest` on a synthetic grid and `--fetch` for the downloads)
   and stamped by `ohc_data_root.py`, which writes RECORD.json with
   the bookkeeping table from the loader's stamps; SOURCES.json
   records every product file read with its URL, hash and time. This
   is the layout the computation reads, `--data-root DIR` in place of
   `--fixture`:

   ```
   DIR/
     RECORD.json          the stamp: record name, the manifest of every file,
                          manifest_sha256, verified_utc, the loader's stamps,
                          and the bookkeeping table under "bookkeeping"
     ohc-700.csv          month,value_ZJ,uncertainty_ZJ   one row per calendar month
     ohc-2000.csv         month,value_ZJ,uncertainty_ZJ
     ohc-700-stamp.json   what the loader read and how: product, version, grid,
     ohc-2000-stamp.json  method, climatology, mask, aggregation, coverage with
                          the domain area, the uncertainty basis, the sha256 of
                          every product file read
     SOURCES.json         every product file read, its URL, sha256 and the time
   ```

   Months are `YYYY-MM`, unique and in order; values are heat content
   anomalies of the layer over the mapped open-ocean domain in
   zettajoules against the product's 2004 to 2018 mean (the change
   between two months does not care about the baseline, and the
   receipt records the values as read). `bookkeeping` must carry
   `climatology.statement`, `anomaly_convention.statement`,
   `coverage.statement`, `coverage.domain_area_m2`,
   `deep_omission.statement` and `uncertainty.basis`, each a statement
   in words read from the product and the loader at loading time; the
   executor refuses a record that lacks any of them, and refuses a
   tree whose files do not hash to the record's manifest. Where the
   record carries `anchor.ohc-DEPTH` (a published rate in watts per
   square meter of the Earth's surface with its uncertainty, period,
   ocean-area fraction and source), the receipt states the run's
   distance from it. The receipt copies the stamp, the two file
   digests and the record's digest, and records the tree's path
   relative to the plugin when the tree sits under it (absolute
   otherwise). The receipt's `run_id` digests the receipt without its
   timestamp, so it is bound to the runtime name and to that recorded
   path: the same runtime name on the committed root reproduces the
   id on any machine.

   Rebuilding the tree, from a cache of the product files outside it
   (only when the user asks for a refresh; the committed root is the
   record a real run reads):

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/knowledge/references/loaders/ohc_rg_loader.py --rg-dir ~/rg --fetch   # downloads what ~/rg lacks
   uv run ${CLAUDE_PLUGIN_ROOT}/knowledge/references/loaders/ohc_rg_loader.py --rg-dir ~/rg \
     --out-dir ${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/argo-ohc-root
   uv run ${CLAUDE_PLUGIN_ROOT}/knowledge/references/loaders/ohc_data_root.py \
     --root ${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/argo-ohc-root --record argo-ohc-root-YYYY-MM-DD
   uv run ${CLAUDE_PLUGIN_ROOT}/knowledge/references/loaders/ohc_data_root.py \
     --root ${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/argo-ohc-root --check
   ```

   The real run on the committed root:

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/knowledge/references/computations/argo_ohc.py \
     --data-root ${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/argo-ohc-root \
     --window 2006-01:2020-12 --depth 2000 --runtime claude-code \
     --receipt /tmp/argo-ohc-record.json
   ```

5. **Attest the receipt before quoting anything from it.** Every
   number quoted from a receipt comes after the attester says PASS on
   that exact receipt:

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/knowledge/references/attesters/argo_ohc_check.py /tmp/argo-ohc-receipt.json \
     [--out /tmp/attestation.json]
   uv run ${CLAUDE_PLUGIN_ROOT}/knowledge/references/attesters/argo_ohc_check.py /tmp/argo-ohc-record.json \
     --data-root ${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/argo-ohc-root [--out /tmp/attestation.json]
   ```

   A data-root receipt is attested with `--data-root DIR`: the
   attester rehashes RECORD.json, the CSV and the stamp in that tree
   against the receipt's digests and reproduces a refusal from the
   tree's stamp and series. Without the tree the digests are reported
   as not verified, and a data-root refusal is taken on the executor's
   word and fails. PASS requires every declared field, the sanctioned
   code hash, this plugin's package name, version and release lock
   digest in the `bundle` block and a well-formed `capability` block,
   a named runtime, the fixture regenerated at the receipt's seed and
   depth hashing to the receipt's digest (or the record's name,
   digest, files and stamp for a data root), the months used and
   missing partitioning the window and the series as the regenerated
   fixture yields it, the trend, its interval, the change, the
   endpoint change, the residual, the combined uncertainty, the
   verdict, the rates per unit area and the anchor distance recomputed
   from the series, the bookkeeping statements complete with the
   sanctioned deep-omission statement and the window handling agreeing
   with the months, and the stated plausibility bounds (on the
   fixture, the known truth). One `PASS name` or `FAIL name: reason`
   line per check, `PASS refusal` for a refusal receipt, exit nonzero
   on any FAIL. `--out` writes the attestation (verdict, refusal flag,
   digests, the capability, bundle and runtime blocks, every check)
   for a qualification record. `--selftest` runs the pass on both
   layers, the tampers, the wrong release, the tampered computation,
   the refusals, a forged refusal, and a data root built in a
   temporary directory with its own refusal and an edited-tree
   rejection.
6. **Report** the trend with its interval and the window, the change
   and the endpoint change with the residual against the bar, the
   verdict, the layer and the domain as the bookkeeping states them,
   the deep-ocean omission with its published rate, the run id, the
   attester's verdict and the concepts consulted. A figure of the
   series goes through the receipt-figures skill, never a hand-drawn
   plot.

## Must NOT

- Never quote a number from a receipt the attester has not passed,
  and never edit the sanctioned computation; the attester fails a
  changed hash by construction.
- Never present a refusal as a number, and never trim the window to
  dodge a refusal without saying so.
- Never label the 0 to 2000 dbar change as full-depth; the deep ocean
  is the separate term the receipt's bookkeeping states.
- Never quote the absolute anomaly as a heat content; the change over
  the window is the quantity, and the baseline is the product's.
- Never commit a receipt, a verdict or a generated fixture to the
  bundle.
