---
type: connector
title: NASA Earthdata MCP server (CMR discovery, no login)
description: "The official CMR MCP server: endpoint, tool surface, and the auth boundary; discovery needs no credentials, downloads go through earthaccess."
tags: [connector, cmr, earthdata, mcp, discovery]
status: draft
generated: { by: claude-code/fable-5, at: 2026-08-31T00:19:55Z }
stale_after: 2026-11-30
sources:
  - id: repo-readme
    resource: https://github.com/nasa/earthdata-mcp
    title: nasa/earthdata-mcp README (endpoint, tools, workflow)
  - id: param-reference
    resource: https://github.com/nasa/earthdata-mcp/blob/main/docs/consumers/SUPPORTED_PARAMETERS.md
    title: Parameter Support Reference (tool inputs to CMR/UMM mapping)
  - id: cmr-api
    resource: https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
    title: CMR Search API documentation (public search, token optional)
  - id: local-smoke
    resource: ../../../tools/mcp_smoke.py
    title: "Tool surface verification (seven tools, parameter schemas), run against a local build 2026-08-29"
  - id: remote-smoke
    resource: https://github.com/open-science-pillars/marketplace/issues/20
    title: "Remote endpoint smoke baseline, 2026-08-30: seven tools listed with schemas over Streamable HTTP; no-login get_collections probe returned the ECCO geometry collection"
---

# NASA Earthdata MCP server

The official ESDIS MCP server exposing CMR to agents over Streamable
HTTP at https://cmr.earthdata.nasa.gov/mcp/v1 (60 second client timeout
recommended).[^repo-readme] CMR collection and granule search is a
public API, so this connector requires no Earthdata Login for any of its
tools; credentials enter only at download, which the server's own
workflow instructions route through the earthaccess library.[^repo-readme][^cmr-api]

## Tool surface

Seven tools, verified by session listing against a local build on
2026-08-29 and against the remote endpoint on 2026-08-30 with no
credentials configured:[^local-smoke][^remote-smoke] `get_keywords`
(KMS vocabulary translation), `get_collections` (dataset search;
accepts short_name, keyword, provider, instrument, platform, spatial
and temporal constraints), `get_granules` (per-file availability within
a collection), `get_services` (OPeNDAP, Harmony, WMS/WMTS endpoints),
`get_tools` (portals and software with deep-link templates),
`get_citations` (publication and DOI records by collection_concept_id
or identifier), `get_variables` (UMM variable records by
collection_concept_id or keyword; scale, offset, fill).
Parameter-level mappings live in the reference.[^param-reference]

## Boundaries

Variable records describe intent; granules are ground truth, so a
Schema row is signed only after a granule load, never from
get_variables alone. OSP gates (verify_cmr, check_fields, attesters)
call CMR REST directly and do not depend on this connector. The
server's legacy embedding pipeline is being deprecated in favor of pure
real-time CMR integration, which is why this concept carries a
near-term stale_after; re-verify the surface with the smoke tool at
each sweep.[^repo-readme]

[^repo-readme]: nasa/earthdata-mcp README
[^param-reference]: Parameter Support Reference
[^cmr-api]: CMR Search API documentation
[^local-smoke]: Tool surface verification, 2026-08-29
[^remote-smoke]: Remote endpoint verification, marketplace issue 20 baseline, 2026-08-30
