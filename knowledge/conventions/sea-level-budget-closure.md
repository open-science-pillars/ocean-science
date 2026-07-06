---
type: convention
title: "Sea level budget closure: a correction-consistency problem first"
description: "The altimetry = ocean-mass + steric budget closes only under consistent GIA, reference-frame, atmospheric-pressure, smoothing, and period bookkeeping; the deep-steric term below the Argo sampling floor is nonzero and must be acknowledged."
tags: [sea-level, budget, steric, manometric, gia, closure, altimetry, grace, argo]
timestamp: 2026-07-05
status: verified
verified: 2026-07-06
verified_by: OSP steward review
evidence:
  - https://doi.org/10.5194/essd-10-1551-2018
---

# Sea level budget closure: a correction-consistency problem first

**The budget.** Regional and global sea level closes as altimetry
(geocentric sea surface height) equals the manometric (ocean-mass) piece
from gravimetry plus the steric piece from hydrography. The identity
holds within uncertainties ONLY when the three estimates are bookkept
consistently; apparent non-closure is a correction-consistency finding
before it is a missing-physics finding, so the corrections table is
worked first.

**Consistency requirements.** For the budget to close:

- **GIA.** The same glacial isostatic adjustment treatment is applied
  compatibly to altimetry and gravimetry. GRACE mascon products arrive
  with a specific GIA model already subtracted (see
  [grace-gia-correction](../gotchas/grace-gia-correction.md)); altimetry
  trends carry their own GIA convention. Comparing across products under
  inconsistent GIA attributes the model difference to the ocean.
- **Reference frame and atmospheric pressure.** Compatible reference
  frames, and compatible atmospheric-pressure (inverse-barometer)
  conventions between the altimetry product and the mass estimate.
- **Effective smoothing.** Comparable effective resolution: gravimetry's
  coarse footprint against pointwise altimetry (nearshore, coastal
  leakage also enters, see
  [grace-coastal-leakage](../gotchas/grace-coastal-leakage.md)).
- **Matching periods.** The same time window for every term; the
  GRACE-to-GRACE-FO gap and era-dependent altimetry trends are honored.
- **The deep-steric term.** Argo-era hydrography samples steric height
  over its sampled depth range only (the upper ocean); the steric
  contribution below the Argo sampling floor is not measured by it and
  is NOT zero. A budget that treats Argo-era steric as full-depth steric
  omits a real term.

**Wrong-result mode.** A budget assembled from mismatched corrections
shows apparent non-closure that is an artifact of the bookkeeping, not
the ocean, and tempts a spurious missing-physics conclusion; or it
closes only by accident when two inconsistencies cancel.

**Correct approach.** State every correction each term carries, align
them across products (or quote the correction spread as a systematic
term), acknowledge the deep-steric contribution explicitly, and audit
the corrections table before ever declaring non-closure. For ECCO
specifically, the SSH-variant IB convention
([ecco-ssh-ib-variants](../gotchas/ecco-ssh-ib-variants.md)) and the
Boussinesq global-mean correction
([ecco-boussinesq-global-steric](../gotchas/ecco-boussinesq-global-steric.md))
enter the same bookkeeping.
