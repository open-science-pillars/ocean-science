---
type: connector
title: "NOAA CO-OPS tide and water-level stations (observations server)"
description: "Coastal water level from the station of record, minutes fresh, through the coops_data tool; the datum is the trap: series on different datums differ by feet and must never be compared unconverted."
tags: [connector, coops, tides, water-level, mcp, observations]
verified: { by: human:PaulMRamirez, at: 2026-09-01T16:55:00Z }
status: stable
generated: { by: claude-code/fable-5, at: 2026-09-01T16:30:00Z }
stale_after: 2026-12-31
sources:
  - id: coops-api
    resource: https://api.tidesandcurrents.noaa.gov/api/prod/
    title: "CO-OPS Data API documentation (products, datums, formats)"
  - id: live-probe
    resource: "coops_data probes, 2026-09-01: Boston 8443970 water level timestamped minutes prior; 24 hours of Providence 8454000 predictions"
    title: "Live verification of observations and predictions"
  - id: server
    resource: https://github.com/open-science-pillars/core/blob/main/connectors/observations_mcp.py
    title: "The observations server carrying the coops_data tool"
---

# NOAA CO-OPS tide and water-level stations

The `coops_data` tool of the observations server fetches from NOAA
CO-OPS, the agency of record for United States coastal water level:
observations, predictions, and meteorology per station, anonymous,
over HTTPS.[^coops-api] Verified live 2026-09-01: a Boston water
level timestamped minutes before the request, and a day of Providence
tide predictions.[^live-probe]

**The datum is the trap.** Every water level is relative to a declared
datum, and MLLW, MSL, NAVD, and station datum differ by feet at the
same gauge. The tool requires the datum explicitly and returns it in
every response; never compare series across datums without a
conversion, and never quote a level without its datum. Units are
metric and times GMT by the tool's contract, so the classic
feet-and-local-time confusions cannot enter through this
connector.[^coops-api]

**Composition.** The regional sea-level partition and its briefings
gain the observed coastal record beside the model attribution; a
confrontation of modeled coastal sea level against the gauge of
record starts here.[^server]

[^coops-api]: CO-OPS Data API documentation
[^live-probe]: live probes 2026-09-01
[^server]: the observations server source
