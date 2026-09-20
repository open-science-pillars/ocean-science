---
name: transport-analysis
description: "Meridional transport analysis: MHT at chosen latitudes, overturning streamfunction, expected range and spread from the recipe concept."
---

# transport-analysis

Compute meridional transports and judge them against validated
expectations.
Works by slash command or conversationally ("what's the heat transport
at 26.5N?"). The method authority is the meridional-transport skill;
the dataset knowledge (expected values, scope, caveats) is the knowledge
bundle, discovered per analysis. This skill carries no dataset facts of
its own.

## Behavior, in order

1. **Parse and show back:** quantity (heat, volume, freshwater,
   overturning streamfunction), latitude or named section, period,
   basin scope.
2. **Consult the knowledge bundle for this section and dataset FIRST.**
   Consult installed knowledge concepts first, as the core
   `consult-knowledge` skill sets out, by section, latitude, quantity,
   and product; the ecco skill lists the concepts this plugin resolves
   to (the gotchas that constrain this section, the recipe or attested
   computation that pins its expected values and spread, the dataset
   concept's uncertainty framing). Read them, restate what applies to
   the request, and cite each by bundle path. If the ecco-scout agent
   is available, its plan already carries these citations; otherwise do
   the discovery here. A section whose scope, expected range, or
   comparison discipline is not found in the bundle is flagged as
   unvalidated, not guessed.
3. **Inputs via load-ecco** (gated): 3D temperature fluxes for heat,
   volume fluxes for volume and streamfunction, geometry merged.
4. **Compute natively:** section masks over faces (ecco_v4_py section
   machinery), transports summed over masked faces, streamfunction by
   vertical cumulation; no regridding anywhere in the path.
5. **Judge against the recipe:** the computed mean against the
   expected range; variability against the expected-uncertainty
   spread; time-sampling discipline applied (a single-year mean gets
   the wider single-year envelope, and any RAPID comparison matches
   overlap periods or says it cannot). Out-of-range results are
   reported as out-of-range with the recipe cited, then diagnosed
   (period mismatch, wrong fluxes, mask errors) rather than accepted
   quietly.
6. **Report:** the transport with its uncertainty statement (recipe
   spread, or the explicit ECCO no-formal-uncertainty line), the
   period, the method one-liner, and the concepts consulted. Where the
   comparison against observations is the point, hand off to
   compare-obs rather than improvising one here.

## Attested runs

Where the section has an attested computation in this package,
step 4 runs its sanctioned executor and step 5 reads the attester's
verdict; this section is that procedure, with the paths and the
parameters bound.
The executor and the attester of every computation below ship in this
package, in the scripts directory of the skill that runs them, and the
concept each one answers to is under `knowledge/computations/`.
`${CLAUDE_PLUGIN_ROOT}` below is this package's root, which the runtime
sets. Never
edit an executor: its attester hashes it, and a changed hash fails by
construction. Run the named attester on the receipt before quoting any
number from it; a FAIL is reported as a FAIL with the failing field
named, never worked around. These executors take no `--runtime` flag
(their receipts carry no runtime block); record the runtime name
(`claude-code` here) in the report beside the receipt's run id.

Every executor here reads the native granules from `--data-root`
(default `~/ECCO_V4r4`): the 2010 fixture cache (about 2.5 GB, the
geometry granule plus the monthly and snapshot collections the concept
names, fetched with earthaccess under an Earthdata Login; the
repository's goldens tree stages it) or the science record over 1992
to 2017 (`~/ECCO_V4r4_record`). The tree must carry the RECORD.json
stamp the provider's verify tool leaves after checking it against its
manifest (`uv run <root>/tools/science_record_verify.py --manifest
${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/fixtures-2010-manifest.json --data-root
~/ECCO_V4r4 --checksum all --exact --stamp`, once after the first
fetch), since every attester refuses a receipt from an unstamped tree.

**Section transports, `ecco-section-transport`**
(`knowledge/computations/ecco-section-transport.md`; executor
`skills/transport-analysis/scripts/ecco_section_transport.py`, attester
`skills/transport-analysis/scripts/section_transport_check.py`). Binds `section`
(registered: `global-26.5n`, the closed latitude circle with the
anchor; `fifteen-s-southeast-atlantic`, an interior segment with no
anchor by design) and `year` (default 2010):

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/transport-analysis/scripts/ecco_section_transport.py \
  --section global-26.5n --year 2010 --data-root ~/ECCO_V4r4 \
  --receipt /tmp/section-transport-receipt.json
uv run ${CLAUDE_PLUGIN_ROOT}/skills/transport-analysis/scripts/section_transport_check.py /tmp/section-transport-receipt.json
```

The receipt carries `run_id`, `code_sha256`, `data`,
`bound_parameters`, `resolved_section` (face counts, extent, mask and
geometry digests), `results`, `mutation_evidence` (the five named
sabotages) and `caveats`. The anchored section is checked against the
independent implementation's band and the measured value two-sided;
an unanchored section's receipt must say it is unanchored, and the
report says the same.

**Atlantic overturning at 26.5N, `ecco-amoc-26n`**
(`knowledge/computations/ecco-amoc-26n.md`; executor
`skills/transport-analysis/scripts/ecco_amoc_26n.py`; attester
`skills/compare-obs/scripts/rapid_confrontation_check.py`, through the
confrontation that cites the receipt). Binds `period`
(`YYYY-MM:YYYY-MM` within 1992-01 to 2017-12) and `scope` (`atlantic`,
the array's section from Florida to Africa; `atlantic-with-gulf-of-mexico`,
the registered second scope and a recorded sabotage, never a silent
inclusion):

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/transport-analysis/scripts/ecco_amoc_26n.py \
  --period 1992-01:2017-12 --scope atlantic \
  --data-root ~/ECCO_V4r4_record --receipt /tmp/amoc-receipt.json
```

The receipt carries the per-level transports for every month and all
three streamfunction conventions with the mass-balanced one primary;
a run covering 2010 must reproduce the ecco_v4_py anchor or it writes
no receipt. This computation has no attester of its own: its receipt
is attested through the RAPID confrontation that cites it (the
compare-obs skill's attested run), whose attester hashes the model
receipt against the citation, checks the sanctioned code hash,
recomputes the mass-balanced maximum and the net transport for every
month from the per-level transports, checks the 2010 anchor, and
checks that both structural sabotages were caught. A model receipt no
confrontation cites is a consistent number, not an attested one: say
so when quoting it, or run the confrontation first.

**Meridional heat transport at 26.5N, `ecco-mht-26n`**: a draft
contract with no sanctioned executor yet. The heat transport across
`global-26.5n` in the section transport receipt above is the attested
route today (its `results` carry the heat transport with the anchor);
the MHT concept is cited as a draft and voiced as such.

## Must NOT

- Never hardcode an expected transport or spread; the recipe is the
  authority and gets cited.
- Never regrid anything in a transport computation.
- Never present a single-year mean against a multi-year expectation
  without the envelope caveat.
- Never quote heat transport across a mass-unbalanced section without
  the reference-temperature statement.
- Never accept an out-of-range result without diagnosis.
