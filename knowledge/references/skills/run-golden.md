---
type: Reference
title: "Run instructions: attested ECCO heat budget"
description: "Executor instructions for the attested heat budget: stage the fixture cache, run the sanctioned computation for a receipt, attest the receipt."
generated: { by: claude-code/fable-5, at: 2026-08-30T19:20:00Z }
status: draft
---

# Run instructions: attested ECCO heat budget

The executor contract for
[the heat-budget computation](../../computations/ecco-heat-budget.md)
(spec 10.2): a runner, human or agent, follows these steps exactly. The
runner binds VALUES for the declared parameters and never edits the
computation file; the attester hashes it (spec 10.3). Receipts and
verdicts are runtime artifacts, never committed to the bundle (spec 10.5).

## 1. Stage the data

The computation reads the scripted 2010 ECCO fixture cache (about 2.5 GB
at `~/ECCO_V4r4`; an Earthdata Login is needed on the first fetch,
from the environment or `~/.netrc`):

```bash
uv run --with marimo,numpy,xarray,netcdf4,earthaccess,ecco_access,ecco_v4_py \
  python ocean-science/verification/fixtures/fetch_ecco_2010.py
```

An already-populated cache is used as-is; nothing is re-downloaded.

## 2. Run the sanctioned computation

From the bundle root (`podaac/`), bind the declared parameters (`year`
required, `region` optional, default `tile1-interior`) and write the
receipt:

```bash
uv run references/computations/ecco_heat_budget.py \
  --year 2010 --receipt /tmp/heat-budget-receipt.json
```

The receipt carries exactly the declared fields: `run_id`, `code_sha256`,
`bound_parameters`, `residual_max`, `residual_p999`, `cells_evaluated`.

## 3. Attest the receipt

```bash
uv run references/attesters/budget_residual.py /tmp/heat-budget-receipt.json
```

Exit 0 prints `PASS` with the run id and residuals; exit 1 prints `FAIL`
naming the failing field. A consumer refuses to display a value whose
receipt fails attestation, and surfaces the verdict either way
(spec 10.5). PASS requires the receipt's `code_sha256` to match the
sanctioned computation file, the bound parameters to match the declared
set, and the residuals to sit within the recipe tolerances
(`residual_max <= 1e-10`, `residual_p999 <= 1e-11` degC/s).
