# SWOT KaRIn L2 SSH products

Reference for the swot skill, per SPEC §4.3.
**ShortNames and version families verified against live CMR 2026-07-04**
(earthaccess, netrc auth); granule-level evidence quoted below comes
from the same session's probes. The current processing baseline is
recorded in `knowledge/datasets/swot-karin.md` with its verification
date, never hardcoded here or in skills.

## Product tiers (Low Rate / oceanography)

Each tier exists in two version families in CMR as of 2026-07-04:
`*_2.0` collections (titled Version C) and `*_D` collections (Version
D, the full-mission reprocessing):

| Tier | ShortNames | Contents |
|---|---|---|
| Basic | `SWOT_L2_LR_SSH_BASIC_2.0` / `SWOT_L2_LR_SSH_BASIC_D` | ssha_karin plus core flags on the 2 km swath grid; the starting point for most SSH work |
| Expert | `..._EXPERT_2.0` / `..._EXPERT_D` | Basic plus the full correction and uncertainty variable set (for reprocessing corrections yourself) |
| WindWave | `..._WINDWAVE_2.0` / `..._WINDWAVE_D` | wind speed and significant wave height variables |
| Unsmoothed | `..._UNSMOOTHED_2.0` / `..._UNSMOOTHED_D` | 250 m native posting, no along-track smoothing; large granules |

Umbrella collections `SWOT_L2_LR_SSH_2.0` / `SWOT_L2_LR_SSH_D` group
the tiers. Nadir altimeter products are separate collections
(`SWOT_L2_NALT_GDR_*` families: GDR/SGDR/IGDR at versions 1.0/2.0/D),
conventional altimetry from the nadir instrument.

**Version-family caveat (probed 2026-07-04):** the cal/val phase
exists ONLY in the `_D` collections; `_2.0` (Version C) collections
return zero granules for cal/val-era dates (verified: BASIC_2.0 empty
for 2023-04, BASIC_D returns cycle-477 granules). A "no data" result
on early-mission dates is a version-family symptom before it is a
coverage fact.

## Granule anatomy and cycle/pass naming

```
SWOT_L2_LR_SSH_Basic_011_424_20240229T234642_20240301T003728_PIC0_01.nc
                      ^^^ ^^^ start           end             ^^^^ counter
                    cycle pass                                baseline
```

- One granule is one pass (half-orbit), about 9.5 minutes of swath.
- **Processing baseline codes** (PGC0, PIC0, PGD0 observed 2026-07-04)
  vary between granules WITHIN one collection as forward processing
  and reprocessing interleave; filter or at least record the baseline
  when consistency matters (the dataset concept carries the current
  state).

## Orbit phases (the first-class gotcha)

- **Cal/val phase:** 1-day repeat orbit, roughly 2023-01 through
  2023-07; dense temporal sampling of a sparse fixed track set; cycle
  numbers in the 400-500s (cycle 477 = April 2023, probed).
- **Science phase:** 21-day repeat, from late July 2023; global
  coverage each cycle; cycle numbers restart at 001 (cycle 001 = late
  July 2023, probed).

Date ranges spanning the July 2023 transition mix two incompatible
sampling regimes and two cycle-numbering schemes; time series and
crossover analyses treat the phases separately. Details and evidence in
`knowledge/gotchas/swot-calval-orbit-phases.md`.

## Two-swath geometry

KaRIn measures two 50 km swaths separated by a roughly 20 km nadir
gap (the nadir altimeter fills the gap at conventional-altimetry
resolution only). Swath data dims are along-track lines by cross-track
pixels PER SIDE; gridding must respect the gap (no interpolation
across it), and swath-crossover comparisons are the calibration
currency. Cross-track distance is signed; left and right swaths carry
distinct systematic error profiles (Expert tier exposes the
cross-track-dependent corrections).

## Access

earthaccess with Earthdata login: `search_data(short_name=...,
temporal=..., bounding_box=...)` then download or stream; granules are
per-pass, so regional work filters spatially and then trims to the
region. Quality flags are bit-packed integers (decode per
quality-control's rules; the swot-karin dataset concept lists the flag
and uncertainty variables). Hydrology products (river and lake vector
products, raster inundation) are separate SWOT collections, deferred
to the hydrology plugin (Phase 2).
