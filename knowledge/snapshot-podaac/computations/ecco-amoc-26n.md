---
type: Attested Computation
title: "Atlantic overturning at 26.5N from ECCO v4r4 (attested)"
description: "The meridional overturning across the Atlantic at the RAPID latitude, month by month on the native grid: Atlantic-only section faces from the signed section machinery and ECCO's own basin codes, three streamfunction conventions with the mass-balanced one primary and the per-level transports in every receipt, an enforced anchor on ecco_v4_py for 2010, two structural sabotages caught and two scope choices measured."
tags: [ecco, amoc, overturning, transport, section, "26n", attested, native-grid]
runtime: python
parameters:
  - { name: period, type: "YYYY-MM:YYYY-MM within 1992-01..2017-12", required: true }
  - { name: scope, type: "atlantic (the array's section) or atlantic-with-gulf-of-mexico", required: true }
computation: references/computations/ecco_amoc_26n.py
executor:
  resource: references/computations/ecco_amoc_26n.py
  receipt: [run_id, computation, code_sha256, section_code_sha256, basin_codes_sha256, data, generated_utc, bound_parameters, resolved_section, anchor, results, mutation_evidence, caveats]
attester:
  resource: references/attesters/rapid_confrontation_check.py
generated: { by: claude-code/fable-5, at: 2026-09-02T18:50:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T02:40:20Z }
status: stable
stale_after: 2027-03-02
sources:
  - id: section-transport
    resource: ecco-section-transport.md
    title: "The attested section machinery this computation imports and names by hash: indicator-gradient faces over the budget-verified tile topology, the weighting rule, the five sabotages"
  - id: basin-codes
    resource: ../references/derivations/llc90_basin_codes.py
    title: "The derivation that converted ECCO's own basins.data (ECCOv4-py binary_data, pinned commit) into the hashed mask this computation restricts by"
  - id: ecco-v4-py
    resource: https://github.com/ECCO-GROUP/ECCOv4-py
    title: "ecco_v4_py 1.8.1, calc_meridional_stf: the independent implementation the 2010 anchor is measured against, on both integration directions"
  - id: confrontation
    resource: ecco-rapid-amoc-confrontation.md
    title: "The attested confrontation that consumes this receipt and whose attester recomputes it"
  - id: recipe
    resource: ../recipes/ecco-rapid-amoc-26n.md
    title: "The recipe that states the colocation choices these conventions and scopes are the numbers for"
---

# Atlantic overturning at 26.5N from ECCO v4r4 (attested)

The quantity the RAPID-MOCHA-WBTS array observes, computed from the
model: the zonal integral of meridional volume transport per level
across the Atlantic at 26.5N, cumulative in depth, maximum over
depth, one value per month. The faces are the signed section
machinery's, the closed 26.5N circle by the indicator-gradient method
over the budget-verified tile topology, then restricted to the
Atlantic by the basin code of the cell owning each stored face; the
codes are ECCO's own, pinned and hashed, and `atl` alone is the
array's section from Florida to Africa.[^section-transport][^basin-codes]
The resolved section is 66 faces (42 west faces on the rotated tile,
24 south faces on the other, no seam faces) along the grid's face row
at 26.1N between 80.5W and 14.5W, with an open area of 2.98e10 m2.
The Gulf of Mexico, which the latitude circle also crosses and the
array does not observe, is a registered second scope and a recorded
disclosure, never a silent inclusion. Weighting is the section
computation's: mass-weighted velocity times face length times layer
thickness, no partial-cell factor.

**Three conventions, one primary, all recomputable.** The maximum of
the streamfunction depends on where the integral starts, because the
model's net transport across the section is not zero (about 1.2 Sv
southward over the record: the Bering Strait throughflow and Arctic
storage), while the array enforces zero net transport by
construction. The receipt carries the per-level transports for every
month so that all three are recomputable from it: mass-balanced
(primary; the net removed uniformly over the section's open area,
then integrated from the surface and maximised), surface-down (no
balance), and bottom-up (integrated from the bottom and negated,
ecco_v4_py's doFlip). Over 1992-01 through 2017-12 the three means
are 14.47, 14.25 and 15.44 Sv; the maximum is taken of the
streamfunction of the monthly-mean velocity field, never the monthly
mean of an instantaneous maximum, and the receipt says so in its
caveats.

**The anchor, enforced.** Any run that covers 2010 must reproduce
ecco_v4_py 1.8.1 `calc_meridional_stf` at 26.5N over `atl` on the
same granules, 11.7709 Sv surface-down and 12.8615 Sv bottom-up,
within 0.01 Sv; the reference run measures 11.7709 and 12.8615, and
a run outside the tolerance aborts receiptless.[^ecco-v4-py] This is
internal consistency: two implementations of the same integral over
the same fields agree, which says the faces, signs and weights are
right and nothing about the ocean.

**Mutation evidence, in every receipt.** Two structural sabotages
must be caught or the run aborts: the rotated tile's face signs
flipped (delta on the mean 14.33 Sv, at most 23.09 Sv in a month) and
the south faces dropped (7.49 Sv, at most 12.36). Two scope choices
are measured and disclosed with `applicable: false`: the Gulf of
Mexico included (+0.15 Sv on the mean, at most 0.97 Sv in a month)
and the path moved to the next face row north at 27.0N (0.21 Sv, at
most 0.93). The disclosures are the numbers a comparison quotes when
it says how much its own scope and path choices could move it.

**Receipt.** `run_id`, `computation`, `code_sha256`, the section
machinery's hash and the basin codes' hash, the verified-tree stamp
under `data`, `bound_parameters` (period, scope, basins, latitude,
convention, collection, sign convention), `resolved_section` (face
counts, tiles, extents, mask and geometry hashes, the open area
profile by level and its total, level bottom depths), `anchor`,
`results` (months, the primary series, the depth of its maximum, the
net transport, the mean, all three conventions' series, and the
per-level transports by month to six decimals), `mutation_evidence`
and `caveats`.

**Attestation.** This computation has no attester of its own. Its
receipt is attested through the confrontation that cites it: the
confrontation attester hashes the model receipt against the citation,
checks the sanctioned code hash, recomputes the mass-balanced maximum
and the net transport for every month from the per-level transports
(tolerance 1e-4 Sv), checks that every confronted value is the model
receipt's, checks the anchor when 2010 is inside the period, and
checks that both structural sabotages were
caught.[^confrontation] A model receipt no confrontation cites is a
consistent number, not an attested one; the distinction is the point
of the recipe this computation serves.[^recipe]

**Reference run.** `exhibit-amoc-26n-record.json` under
references/retrieval/: period 1992-01:2017-12, scope atlantic, 312
months, primary mean 14.4702 Sv, depth of the mean maximum 880 m,
anchor held on both conventions, both structural sabotages caught,
run 2026-09-02 on the verified v4r4 record tree.

    uv run knowledge/podaac/references/computations/ecco_amoc_26n.py \
        --period 1992-01:2017-12 --scope atlantic \
        --data-root ~/ECCO_V4r4_record --receipt amoc.json

[^section-transport]: Section transports on the ECCO v4r4 native grid (attested), the machinery imported and hashed
[^basin-codes]: references/derivations/llc90_basin_codes.py and the hashed masks under references/masks/
[^ecco-v4-py]: ecco_v4_py 1.8.1 calc_meridional_stf, lat_vals 26.5, basin_name atl, doFlip False and True, xgcm 0.8, same granules, measured 2026-09-02
[^confrontation]: ECCO overturning against RAPID at 26.5N (attested), the consumer and the attester
[^recipe]: ECCO overturning at 26.5N confronted with the RAPID array, the recipe
