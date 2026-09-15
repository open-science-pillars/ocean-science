---
type: Reference
spheres: [hydrosphere]
title: "Run instructions: attested Argo ocean heat content change"
description: "Executor instructions for the Argo ocean heat content change: the fixture command, the data-root layout for real inputs and which loader produces each file, the refusal rule, the attester command."
generated: { by: knowledge-seeder/claude, at: 2026-09-15T16:00:00Z }
status: draft
stale_after: 2027-03-15
---

# Run instructions: attested Argo ocean heat content change

The executor contract for
[the Argo ocean heat content computation](../../computations/argo-ohc.md):
a runner binds VALUES for `window` and `depth`, names the runtime that
ran it, and never edits the computation; the attester hashes it.
Receipts and verdicts are runtime artifacts, never committed to the
bundle; nothing is committed under a fixtures directory either, since
the fixture is generated at run time.

## 1. The fixture run

```bash
uv run knowledge/references/computations/argo_ohc.py \
  --fixture --seed 7 --window 2005-01:2016-12 --depth 2000 --runtime claude-code \
  --receipt /tmp/argo-ohc-receipt.json
```

The fixture is regenerated deterministically from the seed and the
depth (a hash-based Gaussian stream, no numeric library in the path);
its digest is in the receipt and the attester regenerates it. Knobs:
`--seed N` (default 7), `--depth 700|2000` (the layer floor in dbar),
and `--capability-root DIR` for a package whose golden invokes this
executor and whose release the receipt is evidence for (the `bundle`
block always names this repository's package). The headline line
prints the trend with its interval, the change from the first year of
the window to the last, the endpoint change read directly, the
residual against the bar and the verdict; the receipt carries exactly
the declared fields, with the series at full precision, the four
terms, the residual, the combined uncertainty, the verdict, the rates
per unit area, the bookkeeping table, and on a fixture the planted
truth beside what was recovered.

## 2. The refusal rule

A window that leaves the record's coverage refuses:

```bash
uv run knowledge/references/computations/argo_ohc.py \
  --fixture --window 2001-01:2016-12 --depth 700 --runtime claude-code \
  --receipt /tmp/refusal.json
echo $?   # 3, and the receipt says refused: true with the reason
```

The other refusals are fewer than 24 months in the window, fewer than
twelve values in the first or last year of it (the endpoint means need
all twelve), and a trend whose interval cannot be stated. A refusal
receipt attests PASS as a refusal (the verdict line reads `PASS
refusal`) and is never a number.

## 3. A data root, for a real run

The real run's tree is committed at
references/retrieval/argo-ohc-root, built by the loader under
references/loaders (ohc_rg_loader.py for the Roemmich and Gilson
product, with `--selftest` on a synthetic grid and `--fetch` for the
downloads) and stamped by ohc_data_root.py, which writes RECORD.json
with the bookkeeping table from the loader's stamps; SOURCES.json
records every product file read with its URL, hash and time. This is
the layout the computation reads. `--data-root DIR` in place of
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
between two months does not care about the baseline, and the receipt
records the values as read). `bookkeeping` must carry
`climatology.statement`, `anomaly_convention.statement`,
`coverage.statement`, `coverage.domain_area_m2`,
`deep_omission.statement` and `uncertainty.basis`, each a statement in
words read from the product and the loader at loading time; the
executor refuses a record that lacks any of them, and refuses a tree
whose files do not hash to the record's manifest. Where the record
carries `anchor.ohc-DEPTH` (a published rate in watts per square meter
of the Earth's surface with its uncertainty, period, ocean-area
fraction and source), the receipt states the run's distance from it.
The receipt copies the stamp, the two file digests and the record's
digest.

The loader, from a cache of the product files outside the tree:

```bash
uv run knowledge/references/loaders/ohc_rg_loader.py --rg-dir ~/rg --fetch   # downloads what ~/rg lacks
uv run knowledge/references/loaders/ohc_rg_loader.py --rg-dir ~/rg \
  --out-dir knowledge/references/retrieval/argo-ohc-root
uv run knowledge/references/loaders/ohc_data_root.py \
  --root knowledge/references/retrieval/argo-ohc-root --record argo-ohc-root-YYYY-MM-DD
uv run knowledge/references/loaders/ohc_data_root.py \
  --root knowledge/references/retrieval/argo-ohc-root --check
```

The real run on the committed root:

```bash
uv run knowledge/references/computations/argo_ohc.py \
  --data-root knowledge/references/retrieval/argo-ohc-root \
  --window 2006-01:2020-12 --depth 2000 --runtime claude-code \
  --receipt /tmp/argo-ohc-record.json
```

## 4. Attest the receipt

```bash
uv run knowledge/references/attesters/argo_ohc_check.py /tmp/argo-ohc-receipt.json \
  [--out /tmp/attestation.json]
```

PASS requires every declared field, the sanctioned code hash, this
repository's package name, version and release lock digest in the
`bundle` block and a well-formed `capability` block, a named runtime,
the fixture regenerated at the receipt's seed and depth hashing to the
receipt's digest (or the record's name, digest, files and stamp for a
data root), the months used and missing partitioning the window and
the series as the regenerated fixture yields it, the trend, its
interval, the change, the endpoint change, the residual, the combined
uncertainty, the verdict, the rates per unit area and the anchor
distance recomputed from the series, the bookkeeping statements
complete with the sanctioned deep-omission statement and the window
handling agreeing with the months, and the stated plausibility bounds
(on the fixture, the known truth). One `PASS name` or `FAIL name:
reason` line per check, `PASS refusal` for a refusal receipt, exit
nonzero on any FAIL. `--out` writes the attestation (verdict, refusal
flag, digests, the capability, bundle and runtime blocks, every check)
for a qualification record. `--selftest` runs the pass on both layers,
the tampers, the wrong release, the tampered computation, the
refusals, a forged refusal, and a data root built in a temporary
directory with its own refusal and an edited-tree rejection. The
repository's golden, verification/argo_ohc.py, runs the fixture chain,
the refusal and the record run on the committed root and asserts the
recorded numbers.
