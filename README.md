# ocean-science

![ecco heat budget](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/open-science-pillars/ecco-budget-badge/main/.badges/ecco-budget.json)

Physical oceanography for Open Science Pillars: the ECCO v4r4 state
estimate, SWOT KaRIn SSH, meridional transport, budget closure, water
masses, sea level, and the PO.DAAC knowledge arc.

**Install core first.** This plugin builds on core's foundation skills and
its start / discover-data / report workflows. They install as peers (no
shared files), so you add core alongside this one.

## Install

```bash
claude plugin marketplace add open-science-pillars/marketplace
claude plugin install core@open-science-pillars
claude plugin install ocean-science@open-science-pillars
```

Cowork and Claude Science: add the marketplace and install from it.

## Your first run

Do the 20-minute [ECCO Heat Transport tutorial](https://github.com/open-science-pillars/tutorials/blob/main/tutorial-2-ecco-mht.qmd):
it plans the data, loads ECCO through a size gate, computes the Atlantic
meridional heat transport at 26.5N, and compares it against the RAPID
observations, with every number carrying its uncertainty. New terms are in
the [glossary](https://github.com/open-science-pillars/marketplace/blob/main/GLOSSARY.md).

## What's inside

- **Skills** for ECCO and SWOT, ocean methods (grids, budgets, transports,
  water masses, sea level), and workflows: data loaders that show you the
  download size and ask before fetching, an ocean-budget workflow that
  refuses to compute on regridded data (it never closes), and transport and
  comparison workflows that read validated recipes.
- **Agents**: a scout that recommends datasets and cites the knowledge it
  relied on (never downloading on its own), and a budget auditor that checks
  a computed budget closed and diagnoses it if not.
- **A knowledge bundle** for the PO.DAAC datasets: dataset concepts with
  uncertainty structure, documented gotchas with evidence, and validated
  recipes with expected numbers.
- **Verification**: automated notebooks that re-check each workflow on small
  cached data. The heat-budget closure is additionally attested: a receipt
  from the sanctioned computation is checked against the code hash and the
  steward-signed tolerances by
  [ecco-budget-badge](https://github.com/open-science-pillars/ecco-budget-badge)
  (pin tag v1), and the badge above is machine-written from that verdict;
  it says "does not close" the moment either check fails. Salt, volume,
  and MHT attach as their computations reach stable.
- **A project config template** (`ocean-science.local.md.template`): copy it
  into your project and fill in your data paths, region, and download limit.

Downloading NASA data needs an Earthdata Login; nothing else here does,
so you can install the plugin, read the knowledge bundle, and search
collections before you have an account. earthaccess finds the
credential on its own: set `EARTHDATA_TOKEN` (the easy path in CI and
cloud notebooks), or put a username and password in `~/.netrc`
(machine `urs.earthdata.nasa.gov`, `chmod 600`), or let it prompt you.
Never commit either to a repo. The
[glossary](https://github.com/open-science-pillars/marketplace/blob/main/GLOSSARY.md)
has the netrc format. License: Apache-2.0. Cite via CITATION.cff.
