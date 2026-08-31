# Connectors: ocean-science

## NASA Earthdata MCP (`earthdata`)

`.mcp.json` registers the NASA Earthdata MCP server (github.com/nasa/earthdata-mcp), a streamable-http server over NASA's Common Metadata Repository. Entry verified against the repository README at authoring time (per the connector guide, entries are verified against the provider repository and never trusted from earlier drafts).

**Verified 2026-08-31:** the hosted endpoint `https://cmr.earthdata.nasa.gov/mcp/v1` is reachable and serving. A session over streamable HTTP lists all seven documented tools with their parameter schemas, and an unauthenticated `get_collections` probe returns results, because CMR search is a public API. An earlier note here recorded the endpoint as unreachable on 2026-07-04 (a 301 to `/search/mcp/v1` and a CMR error page); that has since been fixed upstream, and running a local server is no longer necessary. If it is ever wanted, the repository documents `uv run server.py http` (serving `http://127.0.0.1:5001/mcp/v1`; point the URL in `.mcp.json` there) and a Docker image.

**Graceful degradation:** No ocean workflow requires this connector. ECCO and SWOT loads go through ecco_access and earthaccess directly (an Earthdata Login from the environment or ~/.netrc); discovery falls back to the knowledge bundle with archive URLs when the server is unreachable.

**Per-surface:** Claude Code and Cowork read `.mcp.json` from the installed plugin. Claude Science configures connectors per session; see marketplace/docs/surface-testing-guide.md.

## Credentials

An Earthdata Login is needed only to retrieve data; searching CMR through this connector needs no account. earthaccess looks for the credential in the environment first (an `EARTHDATA_TOKEN`, or username and password variables), then `~/.netrc` (machine `urs.earthdata.nasa.gov`, chmod 600), then an interactive prompt. Credentials never appear in any repo, in any of those forms (SPEC §5.8).
