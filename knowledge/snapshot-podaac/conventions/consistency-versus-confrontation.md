---
type: convention
title: "Consistency versus confrontation"
description: "The distinction every claim in this bundle is labelled by: internal consistency (a budget that closes, two computations that agree, an independent implementation that reproduces a number) shows a method agrees with itself; confrontation (an independent observation at a fixed version, with its own uncertainty, not assimilated) shows it agrees with the world; only the second supports a scientific claim, and the acceptable deviation is what the measured comparison and its uncertainty say it is."
tags: [doctrine, attestation, confrontation, consistency, observations, convention]
generated: { by: claude-code/fable-5, at: 2026-09-02T19:00:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-02T22:58:09Z }
status: stable
stale_after: 2027-03-02
sources:
  - id: heat-budget
    resource: ../computations/ecco-heat-budget.md
    title: "The attested heat budget: closure to the residual tolerance, the bundle's first internal-consistency check"
  - id: steric-anchor
    resource: ../computations/ecco-steric-height.md
    title: "The steric height computation and its cross-computation anchor on the sea-level partition, the bundle's first anchor between two of its own methods"
  - id: section-anchor
    resource: ../computations/ecco-section-transport.md
    title: "The section machinery anchored against an independent implementation of the same integral (ecco_v4_py), still internal consistency"
  - id: confrontation
    resource: ../computations/ecco-rapid-amoc-confrontation.md
    title: "The attested confrontation of the overturning at 26.5N with the RAPID array: the bundle's first comparison whose other side is an observation"
  - id: recipe
    resource: ../recipes/ecco-rapid-amoc-26n.md
    title: "The recipe that states the colocation, the representativeness gap and the measured scores of that confrontation"
  - id: mht-spread
    resource: ../recipes/ecco-mht-26n.md
    title: "The heat transport recipe whose comparison to the array is a quoted published spread: a third kind of statement, weaker than either"
  - id: large-scale-domain
    resource: ../validity-domains/ecco-large-scale-statistics.md
    title: "The validity domain that describes the estimate as a synthesis fitted to observations, not an observation"
---

# Consistency versus confrontation

Two kinds of agreement run through this bundle, and they are not the
same kind of evidence.

**Internal consistency shows that a method agrees with itself.** A
heat budget that closes to round-off shows that the four terms were
read with the right signs, weights and partial cells; it cannot show
that the model's heat transport is the ocean's.[^heat-budget] A
steric height that reproduces the sea-level partition's steric term
to four decimals shows that two computations in this repository
integrate the same density the same way; it cannot show that the
density is right.[^steric-anchor] A section transport that reproduces
an independent implementation to 0.002 PW shows that the faces, signs
and topology are right; the independent implementation read the same
fields, so the agreement says nothing about the
fields.[^section-anchor] Every attester in the bundle up to the first
confrontation is of this kind, and each is worth having: a method
that disagrees with itself is wrong before any observation is
consulted, and the anchors catch that class of error at the price of
a receipt. What they attest is the arithmetic, never the ocean.

**Confrontation shows that a method agrees with the world, to a
stated degree.** A comparison earns the name only when the other
side is an observation the model did not see: taken from an
independent record, at a fixed version with its own DOI and terms,
carrying its own measurement uncertainty, and not among the
constraints the estimate was fitted to. The overturning at 26.5N
against the RAPID array is the bundle's first: the array's
transports are not assimilated, the release is pinned to the file
hash, and the scores carry sampling intervals and sit beside the
programme's published measurement error.[^confrontation] The
outcome is a set of numbers, a bias with an interval, a correlation
with an interval, and not a verdict; the recipe states them and what
they support.[^recipe]

**Only the second supports a scientific claim.** "The model's
overturning at 26.5N closes its budget" is a statement about the
code. "The model's overturning at 26.5N is 3.2 Sv below the array's
over 2004 through 2017, with the phase of the variability at three
quarters of its amplitude" is a statement about the model as a
description of the ocean, and it can be wrong in a way the first
cannot: a later release, a different colocation, a revised
observational record can each move it. A claim that rests only on
internal consistency is a claim that the arithmetic was done; a
claim about the ocean needs a confrontation behind it, or it needs
to say that it has none.

**How the bundle labels each.** A computation concept whose attester
checks closure, an anchor or agreement with another implementation
says so in its own words and never uses the word confrontation. A
computation whose other side is an observation carries the
observation's version, DOI, hash, licence, citation and published
uncertainty in its receipt, and its attester refuses a receipt
missing any of them: an unidentified observation is not an
observation the comparison can be held to. A recipe that quotes a
published observed value as a spread, the way the heat transport
recipe quotes the array, is a third and weaker kind of statement:
the observation is cited but not confronted, no colocation is
stated and no score is measured, and such a recipe must not describe
itself as validated against the observation.[^mht-spread] The
estimate itself is a synthesis fitted to observations, and the
validity domain that says so is the reason a confrontation must
also state what the estimate was fitted to.[^large-scale-domain]

**The acceptable deviation is measured, not judged.** Whether a
model number is close enough to an observed one is not a question
for a reviewer. The comparison, with its colocation stated and its
intervals computed, is the answer: a deviation inside the observed
record's published uncertainty is not distinguishable from
measurement; a deviation whose interval excludes zero is a
disagreement of a stated size; a recomputation that lands inside the
receipt's tolerance reproduces the bundle and one that lands outside
it has changed a choice the recipe names. Nobody has to decide what
is acceptable, because the receipt already says how far apart the
two are and how sure that is. A project that queues that question
for a human reviewer has not yet built the comparison.

**Independence is a degree, and it is stated.** No observation is
perfectly independent of a state estimate that fits hydrography,
altimetry and gravimetry over the same decades. The convention does
not demand perfect independence; it demands that the comparison say
what the estimate was constrained by and where the observation might
overlap it, so that the reader knows what the agreement could and
could not be borrowing. The first confrontation does this for the
array's mooring hydrography, and every later one does it for its own
record.

[^heat-budget]: Heat budget closure on the ECCO v4r4 native grid (attested)
[^steric-anchor]: Regional steric height from ECCO v4r4 (attested), the cross-computation anchor
[^section-anchor]: Section transports on the ECCO v4r4 native grid (attested), the ecco_v4_py anchor
[^confrontation]: ECCO overturning against RAPID at 26.5N (attested)
[^recipe]: ECCO overturning at 26.5N confronted with the RAPID array
[^mht-spread]: Meridional heat transport at 26.5N from ECCO v4r4, the RAPID-comparison spread
[^large-scale-domain]: ECCO v4r4 native monthly fields support large-scale statistics over 1992-2017 (validity domain)
