---
type: connector
title: "PSMSL long-record tide gauges (observations server)"
description: "Two centuries of monthly mean sea level through psmsl_monthly; values sit on the Revised Local Reference datum, roughly 7000 mm below mean sea level, so absolute numbers are meaningless and only differences and trends carry science."
tags: [connector, psmsl, sea-level, tide-gauge, mcp, observations]
verified: { by: human:PaulMRamirez, at: 2026-09-01T16:55:00Z }
status: stable
generated: { by: claude-code/fable-5, at: 2026-09-01T16:30:00Z }
stale_after: 2026-12-31
sources:
  - id: psmsl
    resource: https://psmsl.org/data/obtaining/
    title: "PSMSL data obtaining pages (RLR definition, station catalogue)"
  - id: live-probe
    resource: "psmsl_monthly probe, 2026-09-01: Brest (station 1) monthly series back to 1807 over stable URLs"
    title: "Live verification of the RLR monthly path"
  - id: server
    resource: https://github.com/open-science-pillars/core/blob/main/connectors/observations_mcp.py
    title: "The observations server carrying the psmsl_monthly tool"
---

# PSMSL long-record tide gauges

`psmsl_monthly` fetches monthly mean sea level from the Permanent
Service for Mean Sea Level, the authority for long-record gauge data,
over stable anonymous URLs.[^psmsl] Verified live 2026-09-01: the
Brest series back to 1807.[^live-probe]

**The datum is deliberate and absolute values are meaningless.**
Revised Local Reference places each station's datum roughly 7000 mm
below mean sea level precisely so that nobody mistakes the numbers
for elevations; use differences and trends only. Missing months carry
the -99999 sentinel, which the tool drops and counts, so a series
with gaps discloses them.[^psmsl] PSMSL has no API and no wrapper
ecosystem, and it belongs in this connector anyway: authority
outranks convenience.

**Composition.** Sea-level trends with honest error bars, anchored to
the record of record: the observed centuries beside the modeled
decades, and the attested trend machinery applies to both.[^server]

[^psmsl]: PSMSL data obtaining pages
[^live-probe]: live probe 2026-09-01
[^server]: the observations server source
