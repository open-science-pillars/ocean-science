---
type: Attested Computation
title: "Wind-stress curl and Ekman pumping from ECCO v4r4 (attested)"
description: "Sanctioned curl computed entirely in the local tile frame (curl is rotation-invariant, so the rotation trap cannot occur), with Ekman pumping validated against the model's own vertical velocity; the method caveat is a required receipt field."
tags: [ecco, wind-stress, curl, ekman, attested, native-grid]
runtime: python
parameters:
  - { name: month, type: "YYYY-MM string", required: true }
computation: references/computations/ecco_curl_ekman.py
executor:
  resource: references/computations/ecco_curl_ekman.py
  receipt: [run_id, code_sha256, data, bound_parameters, results, method_caveat]
attester:
  resource: references/attesters/curl_check.py
generated: { by: claude-code/fable-5, at: 2026-09-01T05:35:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T02:58:02Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: gradients-curl
    resource: ../tutorial/gradients-and-curl.md
    title: "Gradients and curl on the native grid: the staggered-point locations (oceTAUX at west faces, oceTAUY at south faces) and metric handling this computation uses"
  - id: vector-orientation
    resource: ../gotchas/ecco-vector-orientation.md
    title: "The vector-orientation gotcha: native UVEL and VVEL are tile-local components, the trap the local-frame formulation sidesteps"
  - id: ecco-skills-corroboration
    resource: https://github.com/podaac/ecco-skills
    title: "podaac/ecco-skills curl and Ekman acceptance record: an independent implementation validating Ekman pumping against model vertical velocity at correlation 0.74"
---

# Wind-stress curl and Ekman pumping from ECCO v4r4 (attested)

Curl of the ocean-surface stress at tracer points, computed ENTIRELY
in each tile's local grid frame: average the staggered oceTAUX (west
faces) and oceTAUY (south faces) to cell centers, then d(tau_y)/dx
minus d(tau_x)/dy with the local metrics.[^gradients-curl] The curl of
a horizontal vector field is invariant under local orthogonal
rotation, so no component rotation is performed or needed; the
rotation trap the curl gotcha records (differencing components in a
frame they no longer match) cannot occur in this
formulation.[^vector-orientation] Ekman pumping follows as one over
rho0 times curl of tau over f, and is validated against the model's
own WVEL at the 70 m interface over the open-ocean interior (10 to 55
degrees latitude, seafloor deeper than 3000 m; the equatorial band is
excluded because f approaches zero).

**Attestation contract.** A run passes only when the receipt's
code_sha256 matches the sanctioned computation, the bound parameters
are exactly the contract set, and the METHOD CAVEAT is present in the
receipt: WVEL contains all vertical motion, so the correlation
validates sign and pattern, not equality. A receipt that drops the
caveat fails, whatever its numbers. The reference month (2009-12)
must land r within 0.02 of the measured value TWO-SIDED, so an
inflated claim fails the same as a broken one.

**Reference run (2026-09-01, cached native granules, month 2009-12).**
Ekman pumping vs model WVEL at 70 m: r = 0.8225 over 20,751 cells,
median absolute difference 2.97E-07 m per s, median absolute curl
9.25E-08 N m-3. Attester PASS on the run; FAIL demonstrated on a
dropped caveat and on a one-line code tamper. The independent PO.DAAC
implementation of the same comparison records correlation
0.74.[^ecco-skills-corroboration]

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^gradients-curl]: tutorial/gradients-and-curl.md, staggered locations and metrics
[^vector-orientation]: gotchas/ecco-vector-orientation.md, tile-local components
[^ecco-skills-corroboration]: podaac/ecco-skills curl and Ekman acceptance record
