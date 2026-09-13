# ocean-science

Physical oceanography for Open Science Pillars: load the ECCO v4r4 state
estimate and SWOT KaRIn sea surface height through a size gate, compute
meridional transports, close property budgets on the native grid,
identify water masses, attribute sea level, and compare the result with
observations, with an uncertainty on every headline number and the
knowledge concept behind every choice cited. It is a Hydrosphere
capability, discipline Ocean Physics (`kind: capability` in
`.osp/repository.yaml`); the words used on this page (capability,
plugin, sphere, knowledge bundle, runtime) are defined in the
[glossary](https://github.com/open-science-pillars/marketplace/blob/main/GLOSSARY.md).

How it is organized: its knowledge (KNOW) is the PO.DAAC provider bundle,
signed by that provider's stewards and consulted in place, plus the local
conventions and connectors here; its behavior (ACT) is the skills; its
verification (PROVE) is the golden notebooks here and the attested
computations in the provider bundle; its connectors (REACH) are declared
in `.osp/package.yaml`, from which the Claude package files are rendered.

## Install

On Claude Code:

```bash
claude plugin marketplace add open-science-pillars/marketplace
claude plugin install ocean-science@open-science-pillars
```

What comes with it: `core` (the foundation skills and the start,
discover-data and report workflows) and `nasa-daac-knowledge` (the
PO.DAAC provider bundle), both declared as dependencies, so the one
install brings them with it. An install stays at the release it was
installed from: `claude plugin update ocean-science@open-science-pillars`
moves this plugin and only this plugin; a dependency moves by its own
update command (`claude plugin update core@open-science-pillars`,
`claude plugin update nasa-daac-knowledge@open-science-pillars`), and a
release that raises a floor says so in its notes. `claude plugin list`
shows what you have.

On Claude Cowork: add the marketplace by repository
(`open-science-pillars/marketplace`) under Customize > Plugins > Add
marketplace, then install the same capability from it; the shell commands
on this page are for Claude Code.

Local requirements: [uv](https://docs.astral.sh/uv/getting-started/installation/).
The observations connector and every script here (the verification
notebooks, the fixture fetch, the figure renderer) declare their
dependencies in a PEP 723 header and run as `uv run <script>`; uv builds
the environment on first run, so nothing is installed by hand. Never
`python script.py`: it skips the header and fails at the first import.
`uv run <nasa-daac-knowledge>/tools/doctor.py --warm .` builds every
environment ahead of a first or offline run.

Downloading NASA data needs an Earthdata Login; nothing else here does,
so you can install the plugin, read the knowledge bundle and search
collections before you have an account. earthaccess finds the credential
on its own: set `EARTHDATA_TOKEN` (the easy path in CI and cloud
notebooks), or put a username and password in `~/.netrc` (machine
`urs.earthdata.nasa.gov`, `chmod 600`), or let it prompt you. Never
commit either to a repository. PO.DAAC, where the ECCO and SWOT
products live, needs no further authorization on the account.

## Runtimes

Which runtimes this release is qualified on is the table below, rendered
from the qualification records; what each word asserts is in the
marketplace repository's
[docs/runtime-distribution.md](https://github.com/open-science-pillars/marketplace/blob/main/docs/runtime-distribution.md).

<!-- osp-runtimes:start -->
Runtime support for ocean-science 0.8.2 (release lock `sha256:dba92d2233f7`), rendered by build-kit's `osp.py advertise` from `.osp/surfaces.yaml` and the qualification records; edit those, not this block.

| Runtime | Role | Declared status | Qualification |
|---|---|---|---|
| Claude Code | development and runtime, required | supported | Supported (development environment) |
| Claude Cowork | runtime, required | tested | Not qualified |
| OpenAI Codex | runtime, required | planned | Not qualified |
| Claude Science | future runtime | limited-release | Outside the required matrix |

A runtime is advertised as supported only on a qualified record for this exact release; a release stays valid when a runtime is not qualified, and that runtime is simply not advertised.
<!-- osp-runtimes:end -->

## First result

[tutorials/quickstart.md](tutorials/quickstart.md) in this repository is
the short form: configure the project, plan the data, load ECCO through
the gate, compute the Atlantic meridional heat transport at 26.5N
against the recipe, compare it with RAPID and report. It assumes core
and ocean-science are installed and an Earthdata Login reachable by
earthaccess, since it downloads data. The long form is
[Tutorial 2, ECCO Heat Transport](https://github.com/open-science-pillars/tutorials/blob/main/tutorial-2-ecco-mht.qmd)
in the tutorials repository (measured at 15.0 minutes on a fresh install
including downloads, about 1.3 GB cached).

## What's inside

- **Skills** (`skills/`, one `SKILL.md` each): background on `ecco`,
  `swot`, `ocean-grids`, `budget-closure`, `meridional-transport`,
  `water-masses`, `mixed-layer`, `sea-level` and `ocean-indices`; the
  gated loaders `load-ecco` and `load-swot`; the workflows
  `transport-analysis`, `ocean-budget`, `water-mass-analysis`,
  `mixed-layer-analysis`, `sea-level-analysis`, `compare-obs`,
  `cite-ecco`, `receipt-figures` and `briefing-generator`. The loaders
  show the download size and ask before fetching; `ocean-budget`
  refuses to compute on regridded data (it never closes).
- **Agents** (`agents/`): `ecco-scout` recommends datasets and cites the
  knowledge it relied on, never downloading on its own; `budget-auditor`
  checks that a computed budget closed and diagnoses it if not.
- **Knowledge** (`knowledge/`): the plugin's own conventions (the
  climate indices, the mixed layer criteria) and its three observational
  connector concepts. The PO.DAAC provider bundle (dataset concepts with
  uncertainty structure, gotchas with evidence, recipes with expected
  numbers, attested computations with their receipts) lives at
  `knowledge/podaac/` in
  [nasa-daac-knowledge](https://github.com/open-science-pillars/nasa-daac-knowledge)
  and is installed as the dependency; skills cite it by bundle path and
  nothing is copied here.
- **Verification** (`verification/`): `load_ecco.py`, `load_swot.py`,
  `transport_analysis.py`, `ocean_budget.py`, `salt_budget.py` and
  `volume_budget.py`, golden notebooks that re-check each workflow on
  small cached data. The heat-budget closure is additionally attested
  against the sanctioned computation and steward-signed tolerances by
  the attester in nasa-daac-knowledge.
- **Evals**: the agent-judgment cases (does an agent with this plugin
  avoid the documented ECCO and SWOT traps?) have one home, the ECCO set
  of [agent-evals](https://github.com/open-science-pillars/agent-evals)
  (`ecco/cases/`); each release is run against the tagged case set.

## Configuration

Copy [`ocean-science.local.md.template`](ocean-science.local.md.template)
into your project as `ocean-science.local.md`. Region, period, the ECCO
release and data directories, the compute label, the SWOT defaults and
the download gate (2 GB unless you change it) live there, and every
loader reads them at the start of ocean work.

## Connectors and credentials

The NASA Earthdata connector serves data discovery when it is reachable,
with knowledge-based discovery as the fallback; the observations
connector fetches tide gauge, Argo and PSMSL records from public agency
sources. What leaves your machine, which credential is read where, and
what happens when a connector is unavailable is in
[CONNECTORS.md](CONNECTORS.md).

## Contributing

Start with the marketplace repository's
[CONTRIBUTING.md](https://github.com/open-science-pillars/marketplace/blob/main/CONTRIBUTING.md)
and the guides under its `docs/` (contributing a skill, contributing
knowledge, testing, the package authoring guide).

## License and citation

Apache-2.0. Cite via [CITATION.cff](CITATION.cff).
