---
type: dataset-gotcha
title: "Daily ECCO granules overlap at midnight the way monthlies do at month edges"
description: "A temporal query keyed to day boundaries can match two adjacent daily granules; selecting daily granules needs a mid-day query time plus filename filtering, the daily twin of the month-edge rule."
tags: [ecco, granules, daily, temporal-query, access]
severity: medium
dataset: ../datasets/ecco-v4r4.md
generated: { by: claude-code/fable-5, at: 2026-09-01T05:11:19Z }
verified: { by: human:PaulMRamirez, at: 2026-09-01T05:53:24Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: ecco-skills-eval
    resource: https://github.com/podaac/ecco-skills/blob/main/docs/eval3.md
    title: "podaac/ecco-skills evaluation round 3: daily granules overlap at midnight like monthly at month edges; the day selector was fixed to query mid-day and filter by filename"
---

# Daily ECCO granules overlap at midnight

Daily-mean ECCO granules abut at midnight, so a CMR temporal query
pinned to a day boundary can match the granule on either side, the
same trap the monthly collections have at month edges. The selection
that works: query a mid-day instant for the wanted day, then confirm
by filename, which carries the date unambiguously.[^ecco-skills-eval]
An independent PO.DAAC skills project hit this while adding daily
support and fixed it exactly that way; recording it here keeps the
next loader from rediscovering it.

[^ecco-skills-eval]: podaac/ecco-skills eval round 3, the daily-selector fix
