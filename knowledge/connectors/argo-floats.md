---
type: connector
title: "Argo profiling floats via ERDDAP (observations server)"
description: "Global in-situ temperature and salinity profiles through argo_search and argo_profile; the server returns raw rows, and science use requires the quality-control discipline this concept records."
tags: [connector, argo, erddap, profiles, mcp, observations]
status: draft
generated: { by: claude-code/fable-5, at: 2026-09-01T16:30:00Z }
stale_after: 2026-12-31
sources:
  - id: erddap
    resource: https://erddap.ifremer.fr/erddap/index.html
    title: "Ifremer ERDDAP serving the Argo GDAC"
  - id: live-probe
    resource: "argo_search probe, 2026-09-01: 46 float positions on a 10 by 20 degree box over the prior week, sample float 1902324"
    title: "Live verification of the search and profile paths"
  - id: server
    resource: https://github.com/open-science-pillars/core/blob/main/connectors/observations_mcp.py
    title: "The observations server carrying the argo tools"
---

# Argo profiling floats via ERDDAP

`argo_search` finds float profiles by box and time window;
`argo_profile` returns pressure, temperature, and salinity rows for
one float. Both speak to the Ifremer ERDDAP serving the Argo Global
Data Assembly Centre, anonymous, over HTTPS.[^erddap] Verified live
2026-09-01: 46 float positions from the prior week on a western
Atlantic box.[^live-probe]

**The discipline the server does not do for you.** Rows come back
RAW. Argo data carry per-value quality flags and exist in real-time
and delayed-mode versions; science use requires selecting good flags
and preferring delayed mode, and this connector deliberately does not
filter, because silent filtering is how two studies disagree without
knowing why. Pressure is decibars, not depth. The confrontation
recipes own the method; this connector owns honest retrieval.[^server]

**Composition.** The in-situ temperature and salinity anchor that
model confrontation needs beyond any single benchmark array: modeled
hydrography against the float of record, in one conversation.

[^erddap]: the Ifremer ERDDAP
[^live-probe]: live probe 2026-09-01
[^server]: the observations server source
