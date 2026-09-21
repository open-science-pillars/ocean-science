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

How it is organized: its knowledge is the PO.DAAC provider bundle,
reviewed by its maintainers and confirmed by the provider where a
contact has confirmed it, consulted in place, plus the local
conventions, connectors and attested computations here; its behavior is
the skills, each computation's executor and attester beside the skill
that runs them; its verification is the golden notebooks here, which
prove the scripts those computations name; its connectors are declared
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
Runtime support for ocean-science 0.9.0 (release lock `sha256:de135f0aa0f8`), rendered by build-kit's `osp.py advertise` from `.osp/surfaces.yaml` and the qualification records; edit those, not this block.

| Runtime | Role | Declared status | Qualification |
|---|---|---|---|
| Claude Code | development and runtime, required | tested | Not qualified, waived for this release (Claude Code is not qualified for this release because the release environment could not produce a record that would be evidence. Two runs of the same candidate disagreed with each other: the first was contaminated by a concurrent qualification sharing the same plugin cache, and the second, run alone, had the shell tool denied part way through, so the runtime could not execute the computation it was asked to. Tool denials varied between runs, so neither result is a statement about the capability. What was established, deterministically and by hand from the installed 0.9.0 package rather than from the checkout, is that the attested sea level budget runs and attests at the new script paths: PASS, run sha256:c1031ce03a2eb00c, every check ok. This waiver first recorded one further finding as a defect in the package, that the skill does real work but its output never names the capability. That was wrong and is withdrawn. The expectation was the harness default, which asked a domain skill to print its own package name, and a skill that closes a sea level budget has no reason to write one into output a scientist reads. The same expectation was later found to match a reply from an environment where this capability was not installed at all, so it was not testing the capability. The probe now names what the skill must state to have done the work, the sanctioned computation and the attester whose verdict clears it, and it matched nineteen runs of the installed package across both invocation forms and did not match the uninstalled control. The surface is not advertised until a run passes on a machine that can run it.; human:PaulMRamirez, 2026-09-21) |
| Claude Cowork | runtime, required | tested | Not qualified, waived for this release (Claude Cowork is not qualified for this release. A Cowork record is a run by a person with Cowork in front of them, installing from the catalog, and no such run has been made for 0.9.0; the runtime cannot be driven headlessly, so the coordinator carrying this release on the maintainer's behalf cannot make one either. This repeats the decision recorded for land-ice 0.1.0 on 2026-09-19 for the same reason. Nothing about the capability is known to fail there: its projection renders and validates in the gate. The surface is not advertised until a run exists.; human:PaulMRamirez, 2026-09-20) |
| OpenAI Codex | runtime, required | planned | Not qualified, waived for this release (OpenAI Codex is not qualified for this release. No release in this organization has been qualified on Codex: the Agent Plugins projection renders and passes plugin-check in the gate, but the Codex leg has never been exercised, so there is no procedure to run and nothing to record. This repeats the decision recorded for land-ice 0.1.0 on 2026-09-19 for the same reason. The surface is not advertised, and the projection is published as conformant rather than as tested.; human:PaulMRamirez, 2026-09-20) |
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
  `cite-ecco`, `receipt-figures`, `briefing-generator`, `sweep`, and
  the attested runs `argo-ohc` (this plugin's own computation) and
  `sea-level-budget` (the provider bundle's). `sweep` runs one
  attested computation once per value of a parameter its concept
  declares and tables the attested receipts, computing nothing of its
  own. Each attested computation
  in the provider bundle is wrapped by the workflow skill that covers
  it, which names the executor it runs and the attester to run on the
  receipt before a number is quoted. The loaders
  show the download size and ask before fetching; `ocean-budget`
  refuses to compute on regridded data (it never closes).
- **Agents** (`agents/`): `ecco-scout` recommends datasets and cites the
  knowledge it relied on, never downloading on its own; `budget-auditor`
  checks that a computed budget closed and diagnoses it if not.
- **Knowledge** (`knowledge/`): the plugin's own conventions (the
  climate indices, the mixed layer criteria), its three observational
  connector concepts and its attested computations under
  `knowledge/computations/`, each beside the skill whose scripts run it.
  The PO.DAAC provider bundle (dataset concepts with uncertainty
  structure, gotchas with evidence, recipes with expected numbers) lives
  at `knowledge/podaac/` in
  [nasa-daac-knowledge](https://github.com/open-science-pillars/nasa-daac-knowledge)
  and is installed as the dependency; skills cite it by bundle path and
  nothing is copied here.
- **Verification** (`verification/`): `load_ecco.py`, `load_swot.py`,
  `transport_analysis.py`, `ocean_budget.py`, `salt_budget.py` and
  `volume_budget.py`, golden notebooks that re-check each workflow on
  small cached data. The heat-budget closure is additionally attested
  against the sanctioned computation and steward-signed tolerances by
  the attester in this package,
  `skills/ocean-budget/scripts/budget_residual.py`.
  `sea_level_budget.py` runs this package's attested sea level budget
  closure on its synthetic fixture (no download, no NASA host) and
  proves the gap refusal; it is the golden and the prove step of the
  release qualification.
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
