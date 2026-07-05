# Connectors: ocean-science

## NASA Earthdata MCP (`earthdata`)

`.mcp.json` registers the NASA Earthdata MCP server (github.com/nasa/earthdata-mcp), a streamable-http server over NASA's Common Metadata Repository. Entry verified against the repository README at authoring time (per the connector guide, entries are verified against the provider repository and never trusted from earlier drafts).

**Known state as of 2026-07-04:** the hosted endpoint `https://cmr.earthdata.nasa.gov/mcp/v1` was documented in the README but unreachable (301 to `/search/mcp/v1`, then a CMR error page). Alternatives documented in the same README: run locally with `uv run server.py http` (serves `http://127.0.0.1:5001/mcp/v1`; point the URL in `.mcp.json` there) or via the repo's Docker image.

**Graceful degradation:** No ocean workflow requires this connector. ECCO and SWOT loads go through ecco_access and earthaccess directly (Earthdata Login via ~/.netrc); discovery falls back to the knowledge bundle with archive URLs when the server is unreachable.

**Per-surface:** Claude Code and Cowork read `.mcp.json` from the installed plugin. Claude Science configures connectors per session; see marketplace/docs/surface-testing-guide.md.

## Credentials

Earthdata Login credentials live in `~/.netrc` (machine `urs.earthdata.nasa.gov`, chmod 600) or in connector configuration. Credentials never appear in any repo (SPEC §5.8).
