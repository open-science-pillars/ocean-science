# Regional sea level briefing: <REGION> (<PERIOD>)

**Plain summary.** Over <PERIOD>, sea level near <REGION> <rose/fell> by
<X.X> cm (<trend> mm per year, <uncertainty>).[^r1] About <NN> percent of
the change came from added water mass and <NN> percent from expansion and
contraction of the water column (rounded shares of the fitted total; they
need not sum to exactly 100, and the small rounding overlap is the same
residual the attester checks).[^r1][^c1] <One sentence of situational
meaning drawn only from signed concept text, in reader-facing words; no
project jargon.>[^c2]

**How this period compares.** <One or two sentences placing the figure
against known variability for this region, drawn ONLY from a signed
context concept cited here by path. If no signed context concept exists
for this region and period, state that plainly instead; never fill this
from literature or memory.>

**What this means for planning.** <Two sentences max, restricted to
signed-concept language about interpretation and caveats; no new
claims.> Figures here are ocean water-level changes from the estimate;
relative sea level at a specific shoreline additionally involves
vertical land motion and glacial isostatic adjustment bookkeeping,
which are outside this briefing's scope.[^c1]

**The numbers.**
| Quantity | Value | Receipt |
|---|---|---|
| Total change | <val> | [^r1] |
| Mass component (manometric: added or removed water) | <val> | [^r1] |
| Steric component (expansion or contraction) | <val> | [^r1] |
| Partition residual | <val> (within tolerance) | [^r1] |

**Method and provenance.** Computed by the sanctioned regional sea level
partition (attested computation <concept link>), run <run_id>, attester
verdict PASS at the recorded tolerance; an area-weighted mean
(native-grid cell areas) over <N> ocean cells; the SSH variant stated
in words per the signed variants concept (for example: `SSH`, the
IB-corrected, GIA-free model sea level).[^r1][^c1] Definitions and
caveats per the signed concepts cited. Data: <collections list>
(citations below, per-DOI).[^cite]

**Boundaries.** This estimate ends at <DATA_END>; it is a retrospective
analysis, not a forecast. <Independent checks: the list, or this
sentence verbatim: "No comparison against tide gauges or altimetry was
performed for this briefing; every check above is internal
consistency."> Produced by Open Science Pillars (personal-hat open
source), not a NASA or JPL product. Questions and corrections: <named
steward>, via <public channel>.

[^r1]: Attested run <run_id>: receipt (code sha <12>, residuals, cells) at <receipt link>.
[^c1]: <concept path at commit>: sea-level-budget-closure convention.
[^c2]: <concept path at commit>: <dataset or gotcha cited>.
[^cite]: <ecco_cite output block>
