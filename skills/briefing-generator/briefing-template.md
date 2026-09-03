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

**The numbers.** <Each row cites the receipt the value came from, or
the finding it is quoted through when one covers the claim.>
| Quantity | Value | Receipt |
|---|---|---|
| Total change | <val> | [^r1] or [^f1] |
| Mass component (manometric: added or removed water) | <val> | [^r1] or [^f1] |
| Steric component (expansion or contraction) | <val> | [^r1] or [^f1] |
| Partition residual | <val> (within tolerance) | [^r1] |

**Method and provenance.** Computed by the sanctioned regional sea level
partition (attested computation <concept link>), run <run_id>, attester
verdict PASS at the recorded tolerance; an area-weighted mean
(native-grid cell areas) over <N> ocean cells; the SSH variant stated
in words per the signed variants concept (for example: `SSH`, the
IB-corrected, GIA-free model sea level).[^r1][^c1] Definitions and
caveats per the signed concepts cited. Data: <collections list>
(citations below, per-DOI).[^cite]

**Findings this briefing rests on.** <If the knowledge bundle holds a
finding whose question covers this region, this period and this
quantity, cite it here by path at commit and voice its position, never
its numbers: a draft as an unverified statement of what the numbers
show; under review with its review URL; stable with the steward's
signature and date; superseded by naming the replacement and saying
so; retracted only as history, with the reason, never as a result.
Say whether the finding is confronted against an independent
observational record and name the record and its version, or say that
it is not confronted and why; a confronted finding is the stronger
object and the reader is told which kind this is. The numbers above
that the finding claims are then quoted through it (the table's
receipt column cites the finding, whose own `claim.from` names the
receipt field), and its limitations are carried into Boundaries below
in the finding's words. If no finding covers this claim, this sentence
verbatim: "No finding in the knowledge bundle covers this region,
period and quantity; every number above is quoted from the receipt
directly.">[^f1]

**Boundaries.** This estimate ends at <DATA_END>; it is a retrospective
analysis, not a forecast. <Independent checks: the confrontation a
cited finding carries, named by record and version and quoting no
score the finding does not state; or this sentence verbatim: "No
comparison against tide gauges or altimetry was performed for this
briefing; every check above is internal consistency."> <The
limitations of every cited finding, in the finding's words.> Produced
by Open Science Pillars (personal-hat open source), not a NASA or JPL
product. Questions and corrections: <named steward>, via <public
channel>.

[^r1]: Attested run <run_id>: receipt (code sha <12>, residuals, cells) at <receipt link>.
[^c1]: <concept path at commit>: sea-level-budget-closure convention.
[^c2]: <concept path at commit>: <dataset or gotcha cited>.
[^f1]: <finding path at commit>: <finding title>; position <draft, unsigned | under review, <URL> | stable, signed by <steward> on <date> | superseded by <finding path> | retracted, <reason>>; <confronted against <observational record, version> | not confronted: <reason>>. Omit this footnote when no finding covers the claim.
[^cite]: <ecco_cite output block>
