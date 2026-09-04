---
type: dataset-gotcha
title: "Curl on the native grid needs a SECOND rotation: the derivative vectors rotate too"
description: "Rotating UVEL and VVEL to east and north is not enough for curl or any derivative-of-vector quantity; the derivative components are themselves grid-relative vectors and need the same CS and SN rotation, or the curl is silently wrong on the rotated faces."
tags: [ecco, llc90, curl, rotation, vectors]
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: ecco-curl-second-rotation
# eval id reserved for the eval-commons seed.
generated: { by: claude-code/fable-5, at: 2026-09-01T05:11:19Z }
verified: { by: human:PaulMRamirez, at: 2026-09-01T05:53:24Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: ecco-skills-eval
    resource: https://github.com/podaac/ecco-skills/blob/main/docs/eval2.md
    title: "podaac/ecco-skills evaluation round 2: after the first rotation fix, curl was still wrong until the derivative vectors were also rotated; fixed and verified against the tutorial"
  - id: vector-orientation
    resource: ecco-vector-orientation.md
    title: "The base rule this extends: native UVEL and VVEL are grid-relative, rotation via CS and SN"
  - id: tutorial-curl
    resource: ../tutorial/gradients-and-curl.md
    title: "Tutorial companion: gradients and curl on the native grid"
---

# Curl on the native grid needs a SECOND rotation

The base vector-orientation rule says native UVEL and VVEL are
grid-relative and rotate to east and north via CS and
SN.[^vector-orientation] The trap this concept adds: for curl, Ekman
pumping, or any quantity built from DERIVATIVES of a vector field, one
rotation is not enough. The derivative components are themselves a
vector pair in grid coordinates, and they need the same CS and SN
rotation before combining; skip it and the curl is silently wrong
wherever tiles are rotated, which on llc90 includes the Arctic cap and
the rotated faces.[^tutorial-curl]

This is not hypothetical. An independent PO.DAAC skills project fixed
the first rotation, was adversarially evaluated, and the evaluation
found the curl still wrong because the second rotation was missing;
only after rotating the derivative vectors did their implementation
match the tutorial bit-for-bit.[^ecco-skills-eval] A trap that
survives one fix by careful builders is exactly the kind worth a
concept of its own.

[^ecco-skills-eval]: podaac/ecco-skills eval round 2, the caught second-rotation omission
[^vector-orientation]: gotchas/ecco-vector-orientation.md
[^tutorial-curl]: tutorial/gradients-and-curl.md
