---
name: cite-ecco
description: "Emit the exact ECCO Consortium citation block with per-collection DOIs (PO.DAAC template) for the ECCO collections an analysis touched. Keywords: cite, citation, DOI, ECCO, acknowledge, references."
---

# cite-ecco

Every ECCO V4r4 collection carries its own DOI, and PO.DAAC prescribes
the exact ECCO Consortium citation. This skill emits that block for
exactly the collections a session touched. The DOI facts live in the
knowledge layer (each fields concept's Variants carries its harvested
DOIs); this skill is the behavior that assembles the block, and it
never composes citation text freehand.

The tool and the pinned DOI mapping ship beside this skill
(`scripts/ecco_cite.py`, `scripts/ecco_v4r4_dois.yaml`), copies of
nasa-daac-knowledge `tools/ecco_cite.py` and `tools/ecco_v4r4_dois.yaml`
pinned to one commit of that repository: the tool's header carries a
`pinned_from:` line naming the source path and the commit it copies
(the copy differs from the source only by that header and by the
usage paths in its docstring). They refresh at plugin releases when
the canonical files change. The tool's `--selftest` cross-checks the
mapping against the canonical fields concepts and runs in the
canonical repository; here only `cite` is used.

## Behavior

1. Collect the ECCO ShortNames the session actually loaded (from the
   load steps' provenance summaries). Show the list back before
   emitting; add or drop only on the user's say.
2. Determine the access date (the date the data was fetched in this
   analysis, not today's date, when the two differ).
3. Run the tool, from the plugin root:

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/cite-ecco/scripts/ecco_cite.py cite \
     --dois ${CLAUDE_PLUGIN_ROOT}/skills/cite-ecco/scripts/ecco_v4r4_dois.yaml \
     SHORTNAME [SHORTNAME ...] --accessed YYYY-MM-DD
   ```

4. Append the emitted block verbatim to the report or output the user
   is producing, under a References or Acknowledgments heading, and say
   which collections it covers.

## Must NOT

- Never compose, edit, or abbreviate citation text freehand; the tool's
  output is the citation, byte for byte.
- Never guess or reconstruct a DOI. A ShortName missing from the
  mapping is reported as a harvest gap (it goes to the fields tracking
  issue), not improvised.
- Never alter the Consortium author list or the template ordering.
- Never substitute today's date for the actual access date without
  saying so.
