# Connectors: ocean-science

What this plugin talks to over the network, what leaves your machine
when it does, and what happens when it cannot. This file is the
disclosure; `.mcp.json` is the wire.

## NASA Earthdata MCP (`earthdata`)

**What it is.** `.mcp.json` registers NASA's Earthdata MCP server
(github.com/nasa/earthdata-mcp), a streamable-http server in front of
NASA's Common Metadata Repository.

**What leaves your machine.** Search terms only: collection names,
keywords, and the spatial or temporal bounds of a query, sent over
HTTPS to NASA's CMR. No credential is sent, because CMR search is a
public API and this connector needs none. No file, no local path, and
no data you hold ever passes through it.

**What does not go through it.** Downloads. Data retrieval happens
directly between your machine and the archive through earthaccess,
never through this connector, which is why an unreachable connector
cannot block a download.

**When it is unavailable.** Nothing breaks. No ocean workflow requires
this connector: ECCO and SWOT loads go through ecco_access and
earthaccess directly, and discovery falls back to the knowledge bundle
with archive URLs, saying which path it used.

**Where the facts about this service are maintained.** Endpoint,
transport, tool surface, auth boundary and deprecation status are
recorded as a dated concept with a staleness date in the PO.DAAC
knowledge bundle (`connectors/earthdata-mcp.md` in
github.com/open-science-pillars/nasa-daac-knowledge), re-verified on a
schedule. This file deliberately does not restate them, so there is
one place to correct when they change.

**Per-surface.** Claude Code and Cowork read `.mcp.json` from the
installed plugin. Claude Science configures connectors per session;
see marketplace/docs/surface-testing-guide.md.

## Credentials

An Earthdata Login is needed only to retrieve data, never to search.
It is read by earthaccess at download time and is never handled by
this plugin, never sent to the connector above, and never stored in
this repository in any form (SPEC §5.8).
