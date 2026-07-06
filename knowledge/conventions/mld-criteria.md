---
type: convention
title: "Mixed layer depth criteria: definitions, thresholds, and comparability"
description: "MLD is a criterion, not an observable; the density and temperature thresholds, reference depth, and input averaging that must match before two MLD values are comparable, plus the workflow default."
tags: [mixed-layer, mld, criterion, density-threshold, comparability, ocean]
timestamp: 2026-07-05
status: draft
evidence:
  - "internal: skills/mixed-layer/SKILL.md (the mixed-layer discipline authority the mixed-layer-analysis workflow cites)"
  - "internal: relocated from ocean-science/skills/mixed-layer-analysis/SKILL.md during the knowledge-coupling migration, needs a steward evidence link"
---

# Mixed layer depth criteria: definitions, thresholds, and comparability

**MLD is a criterion, not an observable.** Every MLD number embeds a
definition, and two numbers are the same physical quantity only when
the definition matches. State the full criterion block (criterion
family, threshold, reference depth, input averaging) with every MLD
value.

## Criterion families and the numbers

- **Density threshold:** depth where potential density exceeds its
  value at a reference depth (commonly 10 m) by a threshold. Two
  widespread choices, 0.03 kg/m3 (de Boyer Montegut-style) and 0.125
  kg/m3 (Levitus-style), can differ by tens of meters in weak
  stratification and by over 100 m in winter deep-mixing regions.
- **Temperature threshold:** 0.2 C or 0.5 C from the 10 m value; fails
  where salinity stratifies (barrier layers), reporting a mixed layer
  deeper than the density-mixed layer. Check a temperature criterion
  against a density criterion wherever barrier layers are plausible
  (tropics, subpolar fresh regions).
- **Gradient and hybrid criteria:** thresholds on the vertical
  derivative; sensitive to vertical resolution.

## The workflow default

When no criterion is supplied, the mixed-layer-analysis workflow
proposes the density threshold 0.03 kg/m3 with a 10 m reference depth,
confirmed with the user, never silently assumed. It is a proposal, not
an imposition; any of the families above is valid once pinned and
stated.

## Comparability rule

MLD values are comparable only under the SAME criterion, reference
depth, threshold, AND input averaging. When comparing products,
recompute under one criterion rather than mixing definitions.

## Input averaging: the monthly-mean shallow bias

MLD computed from monthly-mean profiles is biased shallow against the
monthly mean of daily MLD: the mixing events average out before the
depth is diagnosed, and the winter bias reaches tens of meters. When
only monthly-mean inputs are available, state the averaging chain and
carry the shallow-bias caveat; recompute from daily fields when they
exist. This is why input averaging is part of the criterion block, not
an afterthought.

## Sensitivity is the uncertainty statement

There is no instrument error bar for a definition. The uncertainty on
an MLD conclusion is the threshold-sensitivity check: recompute under at
least one alternative threshold or criterion family and report whether
the conclusion survives. The magnitude of the spread accompanies every
headline MLD.
