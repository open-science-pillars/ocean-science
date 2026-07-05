# ocean-science quickstart

From installed to a validated ocean number. Assumes core AND
ocean-science are installed plus Earthdata Login in `~/.netrc`; the
full walkthrough with real downloads is
[Tutorial 2](https://github.com/open-science-pillars/tutorials)
(measured at 15.0 minutes fresh, ~1.3 GB cached).

## 1. Configure the project

Copy `ocean-science.local.md.template` to your project as
`ocean-science.local.md`: region, period, and the download gate
(default 2 GB) live there, and every loader reads them.

## 2. Plan before touching data

Ask: "How did the Atlantic's meridional heat transport at 26.5N
compare with RAPID during 2010? Plan the data first." The ecco-scout
agent (or the skills conversationally) returns a plan citing the
knowledge concepts that constrain it: exact ShortNames, volumes, the
native-grid rule, snapshot bookends.

## 3. Load through the gate

load-ecco restates the applicable gotchas, shows granule counts and
sizes BEFORE fetching, and stops for confirmation above your gate.
Geometry loads first and merges with everything.

## 4. Compute against the recipe

transport-analysis reads `knowledge/recipes/ecco-mht-26n.md` for the
method and the expected value (0.666 PW Atlantic 2010, with its
scope stated: the full-circle number is a different quantity). Basin
scope is named on every number.

## 5. Compare and report

compare-obs fetches RAPID by DOI, aligns windows and conventions, and
judges differences against the recipe's comparison spread (no
disagreement declared inside it). The report gate then writes the
provenance-complete summary with uncertainty on every headline.

The budget path (ocean-budget + budget-auditor, geothermal included,
absolute closure tolerance from the recipe) is the same shape: plan,
gate, compute against knowledge, audit, report.
