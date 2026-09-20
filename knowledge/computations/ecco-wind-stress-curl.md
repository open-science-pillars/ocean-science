---
type: Attested Computation
spheres: [hydrosphere]
title: "Wind-stress curl and Ekman pumping from ECCO v4r4 (attested)"
description: "Sanctioned curl computed entirely in the local tile frame (curl is rotation-invariant, so the rotation trap cannot occur), with Ekman pumping validated against the model's own vertical velocity; the method caveat is a required receipt field."
tags: [ecco, wind-stress, curl, ekman, attested, native-grid]
runtime: python
parameters:
  - { name: month, type: "YYYY-MM string", required: true }
computation: skills/ecco/scripts/ecco_curl_ekman.py
executor:
  resource: skills/ecco/scripts/ecco_curl_ekman.py
  receipt: [run_id, code_sha256, data, bound_parameters, results, method_caveat, fields]
attester:
  resource: skills/ecco/scripts/curl_check.py
generated: { by: claude-code/fable-5, at: 2026-09-01T05:35:00Z }
verified:
  - { by: human:PaulMRamirez, at: 2026-09-05T16:14:15Z }
  - { by: human:PaulMRamirez, at: 2026-09-16T05:51:09Z, role: maintainer, source: https://github.com/open-science-pillars/nasa-daac-knowledge/pull/183 }
status: draft
stale_after: 2027-01-04
sources:
  - id: gradients-curl
    resource: knowledge/podaac/tutorial/gradients-and-curl.md
    title: "Gradients and curl on the native grid: the staggered-point locations (oceTAUX at west faces, oceTAUY at south faces) and metric handling this computation uses"
  - id: vector-orientation
    resource: knowledge/podaac/gotchas/ecco-vector-orientation.md
    title: "The vector-orientation gotcha: native UVEL and VVEL are tile-local components, the trap the local-frame formulation sidesteps"
  - id: ecco-skills-corroboration
    resource: https://github.com/podaac/ecco-skills
    title: "podaac/ecco-skills curl and Ekman acceptance record: an independent implementation validating Ekman pumping against model vertical velocity at correlation 0.74"
---

# Wind-stress curl and Ekman pumping from ECCO v4r4 (attested)

**Placement, 2026-09-20 (ADR E, a computation is a skill).** This
concept came from the nasa-daac-knowledge bundle at
`knowledge/podaac/computations/ecco-wind-stress-curl.md`, and the
executor and the attester it names now ship in this package under
`skills/ecco/scripts/`. The golden `verification/ecco_dynamics.py` names
every script it does. The executor
`skills/ecco/scripts/ecco_curl_ekman.py` is byte for byte the file that
was under the bundle, so its sha256 8fbfd0e34099d764 and every receipt
that names it stand. The reference run `curl-ekman` reads the ECCO 2010
fixture cache, which this environment does not hold, so it was not
re-run here; the golden runs it where the cache is present. The
signature block is the one the maintainer left; the concept sits at
`status: draft` with no verified event added, and the maintainer
re-signs it after merge.

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

**Per-cell fields, on request.** The scalars say whether Ekman pumping
tracks the model's vertical velocity; a map says where the wind drives
surface water down (w_ek negative, the subtropical gyres) and where it
draws it up (w_ek positive, the subpolar gyres and the Southern Ocean).
Run with `--fields PATH` and the executor also writes the per-cell
arrays behind the scalars to a NumPy `.npz` (XC, YC, CS, SN, Depth; the
cell-centered stresses in the tile frame; curl, w_ek and the model WVEL
at the compared interface; and the exact mask the scalars were computed
over) and records, under `fields` in the receipt, the file's path and
SHA-256 plus each array's shape, dtype and SHA-256. The attester then
requires the file to exist and hash as recorded, so a figure drawn from
it can only show what the receipt vouches for; a receipt without the
block is attested as before. curl, w_ek and WVEL are scalars and need no
rotation; the stress components do.

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^gradients-curl]: knowledge/podaac/tutorial/gradients-and-curl.md, staggered locations and metrics
[^vector-orientation]: knowledge/podaac/gotchas/ecco-vector-orientation.md, tile-local components
[^ecco-skills-corroboration]: podaac/ecco-skills curl and Ekman acceptance record
