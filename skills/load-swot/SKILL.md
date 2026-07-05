---
name: load-swot
description: Load SWOT KaRIn SSH regionally: parse region, cycles, tier; volume gate; flag decoding; swath-aware summary.
---

# load-swot

Bring SWOT KaRIn SSH into the session safely: gated on volume, flags
decoded, swath structure intact. Authored in Session 8b per
SPECIFICATION.md v0.5.1 §4.4. Works by slash command or conversationally
("load SWOT SSH for the Gulf Stream, March 2024").

## Behavior, in order

1. **Parse and show back:** region (bounding box), time range or
   explicit cycles/passes, tier (default Basic; Expert, WindWave,
   Unsmoothed on request), version family per the swot-karin dataset
   concept's current-baseline note. Unstated pieces are asked about
   only if they change what gets downloaded (tier and region usually
   do; an open end date rarely does).
2. **Knowledge first, restated:** consult the bundle and state what
   applies before searching: the orbit-phase gotcha whenever the range
   touches 2023 (spanning ranges get split or narrowed, with the user
   deciding); the version-family note (cal/val dates need the D
   family); the baseline-varies-within-collection caveat when
   consistency matters downstream; the crossover-calibration known
   issue (ssha_karin/ssh_karin arrive without height_cor_xover
   applied; swath or regional statistics on the raw field are
   silently wrong) whenever statistics are the goal.
3. **Search before fetching:** earthaccess granule search (ShortName,
   temporal, bounding box); report granule count and estimated volume
   BEFORE any download.
4. **The volume gate.** Threshold from the project local config
   (`ocean-science.local.md`, "maximum ungated download size"; template
   default 2 GB). At or below threshold: state count, size, and
   destination, then proceed. Above threshold: STOP and present count,
   total size, destination, and a smaller alternative (fewer cycles,
   tighter box, Basic instead of Unsmoothed), and wait for explicit
   confirmation. The gate lives here in the skill body so it fires on
   every surface. Unsmoothed-tier requests deserve a size warning even
   under threshold (250 m posting inflates fast).
5. **Load with flags decoded:** open granules; decode the bit-packed
   quality flags per quality-control's rules; mask flagged pixels;
   never drop the swath dimensions or interpolate across the nadir
   gap.
6. **Swath-aware summary:** cycles and passes loaded (with orbit
   phase); per-swath (left/right) valid-pixel coverage; flagged
   fraction with the dominant flag reasons; processing baselines
   present in the loaded granules; ssha statistics over good pixels
   with height_cor_xover added (gated by height_cor_xover_qual, per
   the dataset concept's crossover known issue), stating explicitly
   that the correction was applied;
   which uncertainty variables came along (per the dataset concept's
   Uncertainty section). This summary is the downstream provenance
   record; name the concepts consulted.

## Must NOT

- Never download above the gate threshold without explicit
  confirmation, on any surface.
- Never present statistics from undecoded or unmasked pixels.
- Never flatten swaths into a regular grid or fill the nadir gap as a
  loading step; that is analysis, done deliberately elsewhere.
- Never silently span the cal/val-to-science transition; surface the
  gotcha and let the user choose.
- Never assume a version family or baseline; read the dataset concept
  and report what the granules actually carried.
