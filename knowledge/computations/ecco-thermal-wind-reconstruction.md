---
type: Attested Computation
spheres: [hydrosphere]
title: "Thermal-wind reconstruction from a level of no motion in ECCO v4r4 (attested)"
description: "Sanctioned reconstruction of the current from density alone: thermal-wind shear integrated from a 3000 m level of no motion, scored against the model's actual current (absolute) and against the model's current minus its own current at the reference level (relative); both scores, every depth band and the model's speed at the reference level are REQUIRED receipt fields, so a receipt quoting only the flattering relative score fails attestation."
tags: [ecco, thermal-wind, geostrophy, level-of-no-motion, attested, native-grid]
runtime: python
parameters:
  - { name: month, type: "YYYY-MM string", required: true }
  - { name: reference_depth_m, type: "level of no motion, default 3000", required: false }
  - { name: map_depth_m, type: "depth of the per-cell map arrays, default 350", required: false }
computation: skills/ecco/scripts/ecco_thermal_wind_reconstruction.py
executor:
  resource: skills/ecco/scripts/ecco_thermal_wind_reconstruction.py
  receipt: [run_id, code_sha256, data, bound_parameters, reference, bands, by_level, level_of_no_motion_caveat, frame_note, fields]
attester:
  resource: skills/ecco/scripts/thermal_wind_check.py
generated: { by: claude-code/fable-5, at: 2026-09-05T15:50:00Z }
verified:
  - { by: human:PaulMRamirez, at: 2026-09-05T16:14:15Z }
  - { by: human:PaulMRamirez, at: 2026-09-16T05:51:09Z, role: maintainer, source: https://github.com/open-science-pillars/nasa-daac-knowledge/pull/183 }
status: draft
stale_after: 2027-03-05
sources:
  - id: tutorial-thermal-wind
    resource: https://ecco-v4-python-tutorial.readthedocs.io/Thermal_wind.html
    title: "ECCO v4 tutorial, thermal wind: the reference formulation, the 3000 m level of no motion, the separate upward and downward integrations, and the 26N Atlantic transect it validates on"
  - id: geostrophic-balance
    resource: ecco-geostrophic-balance.md
    title: "Attested computation, geostrophic balance: the density factor and the interior validation domain this computation inherits"
  - id: density-factor
    resource: knowledge/podaac/gotchas/ecco-geostrophic-density-factor.md
    title: "The density-factor gotcha: the local density rho0 plus RHOAnoma divides the shear, not rho0"
  - id: vector-orientation
    resource: knowledge/podaac/gotchas/ecco-vector-orientation.md
    title: "The vector-orientation gotcha: reconstructed and model components are tile-frame, and a map to east and north needs the CS and SN rotation"
  - id: ecco-skills-corroboration
    resource: https://github.com/podaac/ecco-skills
    title: "podaac/ecco-skills thermal-wind skill: an independent implementation that also integrates from 3000 m and excludes the equatorial band, read for conventions and not for code"
---

# Thermal-wind reconstruction from a level of no motion in ECCO v4r4 (attested)

**Placement, 2026-09-20 (ADR E, a computation is a skill).** This
concept came from the nasa-daac-knowledge bundle at
`knowledge/podaac/computations/ecco-thermal-wind-reconstruction.md`, and
the executor and the attester it names now ship in this package under
`skills/ecco/scripts/`. The golden `verification/ecco_dynamics.py` names
every script it does. The executor
`skills/ecco/scripts/ecco_thermal_wind_reconstruction.py` is byte for
byte the file that was under the bundle, so its sha256 6de42bc425a2cefb
and every receipt that names it stand. The reference run `thermal-wind`
reads the ECCO 2010 fixture cache, which this environment does not hold,
so it was not re-run here; the golden runs it where the cache is
present. The signature block is the one the maintainer left; the concept
sits at `status: draft` with no verified event added, and the maintainer
re-signs it after merge.

The question this answers is the one density alone can be asked: if
the ocean's density field were all you knew, how well could you
reconstruct its currents? Thermal wind gives the vertical shear of the
geostrophic current from the horizontal density gradient, du/dz equals
g over f rho times drho/dy and dv/dz equals minus g over f rho times
drho/dx, with rho the local density rho0 plus RHOAnoma per the
density-factor gotcha.[^density-factor] Shear alone fixes the current
only up to a constant per column, so the reconstruction sets the
current to zero at a reference level, the level of no motion, 3000 m
as in the tutorial, and integrates the shear upward and downward from
it on the model's own level spacing.[^tutorial-thermal-wind] Gradients
are centered differences at tracer points in each tile's local frame,
the model's UVEL and VVEL are averaged to tracer points with their own
face masks, and everything is compared in that frame; a map to east
and north needs the rotation the vector-orientation gotcha
describes.[^vector-orientation]

**Two scores, because the assumption has a cost.** The model's current
at 3000 m is not zero (median 3.6E-03 m per s, 90th percentile
1.1E-02 m per s over the validation columns in the reference month),
and the reconstruction is exactly wrong by that amount at every depth
in the column. The receipt therefore scores every depth band twice:
the ABSOLUTE score compares the reconstruction with the model's actual
current, and answers the question as asked; the RELATIVE score
compares it with the model's current minus the model's own current at
the reference level, and isolates how well the shear was recovered.
The gap between them is the level-of-no-motion assumption's cost, and
the receipt's caveat field says which may be quoted as what. Both
travel in the receipt for all four bands (0 to 100 m, 100 to 1000 m,
1000 m to the reference, below the reference), with the correlation
and the RMS error as a fraction of the model's RMS current, plus the
correlation of the thermal-wind shear itself with the model's shear.

**Attestation contract.** A run passes only when the receipt's
code_sha256 matches the sanctioned computation, the bound parameters
are exactly the contract set (the two collections, rho0 1029, g,
omega, the 3000 m reference, the validation domain 10 to 55 degrees
over a seafloor deeper than 3000 m and wet at the reference level),
the domain holds its geometry-determined 19,315 columns, all four
bands carry both scores, the model's speed at the reference level is
disclosed, and the caveat is present with its wording intact. A
receipt that keeps the relative score and drops the absolute one,
or drops the deep band where the absolute skill collapses, fails
whatever its headline number. The reference-month anchors are
TWO-SIDED, so an inflated claim fails the same as a broken one; other
months attest against provisional bands measured across the 1992 to
2017 record, including a ceiling on the below-reference absolute
correlation and on the surface-layer shear correlation, so a receipt
claiming skill where this method has none is not this method.

**Reference run (2026-09-05, cached native granules, month 2009-12).**
Over the 19,315 validation columns, 100 to 1000 m: absolute r =
0.9900 with RMS error 15 percent of the model's RMS current; relative
r = 0.9989 with RMS error 5 percent; shear r = 0.9757. From 1000 m
down to the reference: absolute r = 0.897 (RMS error 47 percent),
relative r = 0.997. Below the reference level: absolute r = 0.152 with
RMS error 108 percent, that is, no skill, while relative r = 0.978;
the deep current is almost entirely the barotropic part the level of
no motion throws away. In the top 100 m the shear correlation is
0.03: geostrophy does not govern the surface layer, so that band is
reported and not validated. So the answer to the question as asked is
that density alone recovers the thermocline current to within about
15 percent RMS and the deep current not at all, and the second half of
that answer is the required part. Attester PASS on the run; FAIL
demonstrated on a code tamper, a dropped deep band, a dropped absolute
score, a reworded caveat, an inflated below-reference r of 0.95, an
inflated 100 to 1000 m r of 0.999, a receipt for another month claiming
surface-layer shear skill, an unverified data tree, a column count off
by one, an altered fields file and a missing one. The tutorial
validates the same construction on the Atlantic 26N transect and
names the level-of-no-motion assumption the potentially more
problematic one and the top 100 m the systematic
failure;[^tutorial-thermal-wind] the PO.DAAC ecco-skills project
reached the same conventions independently.[^ecco-skills-corroboration]

**Where the shear is density-controlled.** The per-column shear skill
over 100 to 1000 m (one minus the shear error energy over the model's
shear energy) is near one across the subtropical gyres and the whole
summer hemisphere, and drops to zero in a coherent band across the
winter North Pacific and North Atlantic near 30 to 45 degrees. That
band is the deep winter mixed layer: in the reference month, no
validation column with a mixed layer shallower than 50 m
(ECCO_L4_MIXED_LAYER_DEPTH, MXLDEPTH) has skill under 0.5, 3 percent
of those between 50 and 100 m do, 27 percent between 100 and 200 m,
and 58 percent deeper than 300 m; 15.5 percent of Northern Hemisphere
columns score under 0.5 against 0.4 percent of Southern Hemisphere
columns. The surface-layer failure the tutorial names is a
mixed-layer failure: where wind-driven and convective shear reach
below 100 m, density stops controlling the shear there, and the map
says where that is in a given month.

**Across the record.** Five further months spanning 2000 to 2017
attest PASS on the provisional bands: 100 to 1000 m absolute r 0.987
to 0.991, relative r 0.9985 to 0.9989, shear r 0.92 to 0.98; below
the reference absolute r 0.06 to 0.15 against relative r 0.97 to
0.98; top 100 m shear |r| under 0.04 in every month. The method's
skill and its failure are both stationary.

**Per-cell fields, on request.** Run with `--fields PATH` and the
executor also writes the per-cell arrays to a NumPy `.npz` (XC, YC,
CS, SN, Depth; a per-column shear skill over 100 to 1000 m, one minus
the shear error energy over the model's shear energy; the model's
speed at the reference level; the reconstructed and model components
and the absolute and relative errors at the map depth, tile frame;
and the exact masks) and records the file's path and SHA-256 plus each
array's shape, dtype and SHA-256 under `fields` in the receipt. The
attester requires the file to exist and hash as recorded, so a map of
where density controls the shear can only show what the receipt
vouches for. Scalar maps need no rotation; a vector map to east and
north needs the CS and SN rotation shipped in the file.

**Data provenance.** The receipt carries a `data` block: the data root
and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest. The attester refuses a receipt whose
`data.record` is not that stamp. The two trees and the rule are in
docs/science-record.md. The loader turns every granule fill value into
NaN before arithmetic and masks UVEL with hFacW and VVEL with hFacS,
their own face masks: a first run that masked the face velocities with
the cell mask let the 9.97E+36 fill into the model shear and read a
shear correlation near zero where the clean run reads 0.98.

[^tutorial-thermal-wind]: ECCO v4 tutorial thermal wind chapter, the 3000 m level of no motion and the 26N transect validation
[^density-factor]: knowledge/podaac/gotchas/ecco-geostrophic-density-factor.md
[^vector-orientation]: knowledge/podaac/gotchas/ecco-vector-orientation.md
[^ecco-skills-corroboration]: podaac/ecco-skills thermal-wind skill, an independent implementation reaching the same conventions
