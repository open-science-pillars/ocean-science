---
name: briefing-generator
description: "Generate a receipted regional sea level briefing: fills the template strictly from a PASS attested-run receipt and signed concept text, with per-DOI citations. Keywords: briefing, sea level, coastal, receipt, attested, report."
---

# briefing-generator

Produces a regional sea level briefing where every number carries a
receipt. The plain story is readable on its own; every quantitative
claim footnotes either a signed concept (definitions, caveats) or an
attested-run receipt (the computed numbers, with run id and residual).
The template ships beside this skill (`briefing-template.md`); the
sanctioned computation and its attester live in the knowledge bundle
(`knowledge/computations/ecco-regional-sea-level.md`).

## Behavior

1. Collect the inputs: the region and period, the receipt JSON from a
   run of the sanctioned computation, and the attester's verdict for
   that exact receipt. Show them back. Then read the knowledge bundle's
   index for its findings section and check whether any finding's
   question covers this region, this period and this quantity; a
   finding for a different period or a different box does not count,
   however close.
2. **The gate (hard refusal): no briefing without a PASS.** If there is
   no receipt, or the attester verdict is FAIL, or the receipt's
   parameters do not match the requested region and period, stop and
   say which; never draft "provisional" numbers.
3. Fill `briefing-template.md`:
   - Every number in the briefing comes from the receipt (trends,
     residual, months, cells) or is an arithmetic restatement of
     receipt values with the derivation stated (a change over the
     period from its linear trend, a percentage partition of the
     trend). **A number from anywhere else is a bug**, including
     memory, the literature, or other runs.
   - Every definitional or interpretive sentence comes from signed
     concept text, cited by concept path with its commit; the
     situational-meaning and planning sentences are restricted to that
     language.
   - The "How this period compares" slot fills only from a signed
     context concept cited by path; when none exists for the region and
     period, it states that absence plainly (never from literature,
     never from memory).
   - Uncertainty language follows the cited concepts: ECCO ships no
     formal error fields, so the briefing states the receipt's
     partition-consistency bound and the single-period caveat rather
     than inventing a confidence interval.
   - **Findings before receipts.** Once a finding exists for the claim,
     the briefing cites the finding in preference to the raw receipt:
     the numbers it claims are quoted through it (the table row cites
     the finding; the finding's own `claim.from` names the receipt
     field, so the reader's provenance runs quoted number, finding,
     receipt field, attested computation, manifested data tree), and
     its position on the ladder is voiced in the "Findings this
     briefing rests on" slot the way the template says: a draft as an
     unverified statement of what the numbers show, under review with
     its URL, stable with the signature, superseded by naming the
     replacement, retracted only as history with the reason. The
     briefing says whether the finding is confronted and against which
     record; a confronted finding's confrontation is the briefing's
     independent check, and the Boundaries footer then names the record
     instead of the "no comparison" sentence. The finding's limitations
     are inherited: they appear in Boundaries in the finding's words,
     never softened. When no finding covers the claim, the slot carries
     the template's verbatim absence sentence and the receipt route
     above applies unchanged.
4. Append the citation block emitted by the cite-ecco skill for exactly
   the collections the computation consumed, with the real access date.
5. Keep the footer verbatim from the template: the data-end boundary
   (retrospective, not a forecast) and the personal-hat provenance
   line.

## Must NOT

- Never produce a briefing from a missing or FAIL receipt, or edit a
  receipt.
- Never introduce a number that is not in the receipt or a cited
  concept; never quote literature values, remembered rates, or other
  regions' numbers.
- Never soften the boundaries footer or drop the not-a-NASA/JPL line.
- Never compose citations freehand (the cite-ecco tool's output is the
  citation, byte for byte).
- Never restate a finding's numbers as the briefing's own: a number a
  finding claims is quoted through the finding, with the finding cited.
- Never cite a retracted finding as a result, a superseded finding
  without its replacement, or a draft finding as if it were signed; the
  position is voiced every time.
- Never fill the findings slot from a finding whose region, period or
  quantity differs from the briefing's, and never drop or soften a
  cited finding's limitations.
