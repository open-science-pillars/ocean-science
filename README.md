# ocean-science

Physical oceanography for Open Science Pillars: the ECCO v4r4 state
estimate, SWOT KaRIn SSH, meridional transport, budget closure, water
masses, sea level, and the PO.DAAC knowledge arc.

**Install core first.** This plugin assumes the core plugin is installed
as a peer (its start, discover-data, and report workflows, and its
foundation skills). There is no file dependency between them; core is a
separate install by design (SPECIFICATION.md §0.5).

## Install

```bash
claude plugin marketplace add open-science-pillars/marketplace
claude plugin install core@open-science-pillars
claude plugin install ocean-science@open-science-pillars
```

Cowork and Claude Science: add the marketplace and install from it.

## What's inside

- `skills/`: ECCO and SWOT reference skills, six ocean knowledge skills,
  and eight workflow skills (gated loaders, ocean-budget with the
  native-grid-or-refuse rule, transport-analysis reading validated recipes,
  compare-obs, three analysis workflows).
- `agents/`: ecco-scout (recommends datasets, cites concepts, never
  downloads without approval) and budget-auditor (verifies closure,
  proposes fixes, checks the geothermal gotcha first).
- `knowledge/`: the podaac-arc bundle: four dataset concepts with
  Uncertainty sections, five gotchas with evidence, two validated recipes.
- `verification/`: four marimo golden notebooks on small fixtures.
- `evals/`: gotcha-avoidance and rejection seed cases.
- `ocean-science.local.md.template`: copy into your project and fill in
  data paths, the SWOT block, and the Knowledge block.

Earthdata Login goes in `~/.netrc`, never in a repo. Build status per
surface: marketplace repo, docs/PROGRESS.md. Spec: SPECIFICATION.md §4.
License: Apache-2.0. Cite via CITATION.cff.
