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
   that exact receipt. Show them back.
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
   - Uncertainty language follows the cited concepts: ECCO ships no
     formal error fields, so the briefing states the receipt's
     partition-consistency bound and the single-period caveat rather
     than inventing a confidence interval.
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
