---
name: sweep
description: "Sweep one parameter an attested computation declares and table the receipts: the sanctioned executor once per value, the attester on every receipt before any field is read, and a CSV, a markdown table and a JSON manifest of the executor's own headline fields, with a refused run as a row carrying its refusal code. Keywords: parameter sweep, window dependence, sensitivity, every window, table of runs, periods, sea level budget closure over many windows."
user-invocable: true
---

# sweep

This skill computes nothing. Every number it puts in a table is a field
of one receipt that the provider bundle's attester passed, copied by
the receipt field path the script records beside each column, and the
computation that owns those numbers is the concept the sweep names
(for the sea level budget closure,
`knowledge/podaac/computations/sea-level-budget.md`). The script fits
nothing, averages nothing and carries no expected value of its own.
What the sweep adds is arrangement: a concept states its boundaries in
prose from a handful of runs someone made by hand, and a sweep turns
that sentence into a measured table by running the sanctioned executor
once per value of one parameter the concept declares.

Use it when the question is how an answer moves with a parameter the
concept declares: every window of a stated length stepping through the
record, the same period with and without a bridge citation, the same
question asked of a family of values rather than one. Use the wrapping
skill (`sea-level-budget` for the closure) when the question is about
one run, which is also the only thing a reader may quote as a number.

The runs it drives are the wrapping skill's runs, so read that skill
first: it states the parameters, the refusal codes, the receipt fields
and the caveats that travel with every number. The sweep changes none
of that. It runs the same executor with the same flags, one value at a
time.

## Where the executor, the attester and the concept are

The provider bundle is installed with the nasa-daac-knowledge
dependency; its root is the `installPath` of that entry in
`claude plugin list --json`, or a checkout named by
`NASA_DAAC_KNOWLEDGE`. The script resolves it that way, exactly as the
wrapping skill and the receipt-figures renderer do, and copies nothing
into this repository. `$PODAAC` below stands for
`<that root>/knowledge/podaac`:

- concept: `$PODAAC/computations/sea-level-budget.md` (it declares the
  parameters, and the script reads the declared set from its
  frontmatter rather than from a list of its own)
- executor: `$PODAAC/references/computations/sea_level_budget.py`
- attester: `$PODAAC/references/attesters/sea_level_budget_check.py`
- the committed data root:
  `$PODAAC/references/retrieval/sea-level-budget-root`

## The command line

Every run states the parameter swept, its values, and the fixed value
of every other parameter the concept declares. A declared parameter
that is neither swept nor fixed is a refusal, so the table always says
what every run was bound to.

```bash
uv run skills/sweep/scripts/sweep.py \
  --computation sea-level-budget --parameter period \
  --windows 60:12 --span 2005-01:2026-07 \
  --fixed bridge=unbound \
  --input data-root --data-root $PODAAC/references/retrieval/sea-level-budget-root \
  --runtime claude-code --capability-root . \
  --out-dir /tmp/sweep-sea-level-budget
```

- `--parameter NAME` is swept; `--values A,B,C` states the values one
  by one, or `--windows LENGTH:STEP --span FIRST:LAST` states a window
  rule in months that expands to explicit values, which the manifest
  and every row then carry.
- `--fixed NAME=VALUE` states another declared parameter;
  `--fixed bridge=unbound` says in the table that no bridge was bound
  on any run, which is why the runs across the inter-mission gap
  refuse.
- `--input fixture [--seed N] [--fixture-offset MM]` rehearses on the
  executor's synthetic record; `--input data-root DIR` is a real run on
  a stamped tree. One input for the whole sweep: a table is one method
  on one root.
- `--runtime NAME` is passed to every run (from Claude Code, pass
  `--runtime claude-code`), and `--capability-root DIR` names the
  package the runs are evidence for.
- `--out-dir DIR` receives `sweep.csv` (every column at the receipts'
  full precision), `sweep.md` (the same columns, floats shown to four
  decimals, with the provenance line above the table), `sweep.json`
  (the manifest: the command, the one executor digest, the one input
  identity, the column-to-receipt-field map, and every row with its
  receipt path, run id and the attester's own verdict line) and
  `receipts/` (every receipt and its attestation).
- `--selftest` runs the whole discipline on the executor's synthetic
  fixture and exercises every refusal below.

## Behavior, in order

1. **Name the concept first, then show the sweep back.** State the
   concept by bundle path (`knowledge/podaac/computations/sea-level-budget.md`
   for the closure), the parameter to be swept as that concept declares
   it, the values, the fixed value of every other declared parameter,
   and the input (the fixture as a rehearsal, or the stamped data root
   for a real run). Consult the wrapping skill and the concepts it
   names before running.
2. **Run the sweep.** One executor run per value, each writing its own
   receipt. A run the executor refuses (exit 3) is a row carrying its
   reason code, never a skipped row and never retried with a different
   binding to get a number out of it: the refusal is part of what the
   sweep measures. For the closure, a window whose months straddle the
   GRACE to GRACE-FO gap refuses with `gap-without-bridge` unless a
   bridge citation the user supplies is fixed on the sweep.
3. **The attester runs on every receipt before any field is read.**
   The script attests each receipt and only then copies fields out of
   it. A receipt that does not pass is a failed row carrying the
   attester's own line and no number, and the script exits nonzero so
   the failure cannot pass for a table. Do not work around it; report
   it.
4. **Read the table.** The columns are the receipt fields the concept's
   reference run names: the months used of the months in the period,
   the trend of each term and of the residual, the residual's interval,
   the closure gap against the bar, and the verdict. The manifest maps
   every column to its receipt field path and every row to its receipt
   and run id.
5. **Report the table with its provenance and the concept's caveats.**
   Hand over the markdown table together with the provenance line the
   script writes above it (the executor digest, the attester, the
   concept, the input identity, the runtime), the run identifiers of
   the rows discussed, and the caveats the concept states, beside the
   numbers and not after them. Say how many rows the executor refused
   and why. A fixture sweep proves the chain, not the ocean, and says
   so.
6. **Answer the aggregate question with a row.** A reader who sees a
   table of windows asks for one number across it. Give the row that
   answers the question as asked (the longest window, or the window
   the question names), quote it with its interval and its run id, and
   say that the spread across the rows is what the table shows and not
   a quantity any receipt carries. The script refuses `--aggregate`
   with that reason, and the reason is the answer to give.

## Reading a sweep of the closure

- A short window is not a small version of a long one. The interval
  widens, the months dropped at the gap grow as a share of the period,
  and the bar the verdict is measured against moves with them. Compare
  a row against its own bar, which the table carries, never against
  another row's.
- A refused row and a row that fails to close are different findings.
  The first says the run was not licensed; the second is a
  correction-consistency finding before it is a missing-physics one,
  as the closure convention
  (`knowledge/podaac/conventions/sea-level-budget-closure.md`) and the
  `sea-level` skill state.
- The deep-steric systematic sits beside the combined uncertainty in
  every row, never inside it.

## Must NOT

- Never state the headline number a reader will ask for first: the
  overall trend across the rows, the mean residual over the windows,
  the average closure gap, or the fraction of windows that closed read
  as a rate. No receipt carries any of them and no concept owns them;
  a capability that computes one is computing a number of its own,
  which is domain expansion under ADR D of the marketplace decisions
  and waits on the ablation. The script refuses them; do not do by hand
  what it refuses.
- Never compare or table rows whose receipts carry different executor
  digests or different input identities. The script refuses that too:
  a table is one method on one root.
- Never quote a number from a receipt the attester did not pass, and
  never drop a failed row to make the table look complete.
- Never drop a refused row, and never rerun it with an invented
  binding (a bridge phrase nobody supplied) to fill the cell.
- Never sweep something the concept does not declare (a seed, an output
  path, a knob invented for the occasion); the script reads the
  declared set from the concept and refuses the rest.
- Never present a table without the run identifiers, the executor
  digest and the concept's caveats, and never commit a receipt, an
  attestation or a generated table to the bundle.
