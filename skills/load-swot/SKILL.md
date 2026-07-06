---
name: load-swot
description: "Load SWOT KaRIn SSH regionally: parse region, cycles, tier; volume gate; flag decoding; swath-aware summary."
---

# load-swot

Bring SWOT KaRIn SSH into the session safely: gated on volume, flags
decoded, swath structure intact. Works by slash command or conversationally
("load SWOT SSH for the Gulf Stream, March 2024").

## Behavior, in order

1. **Parse and show back:** region (bounding box), time range or
   explicit cycles/passes, tier (default Basic; the other tiers per the
   dataset concept's tier inventory, on request), version family and
   current baseline per the dataset concept. Unstated pieces are asked
   about only if they change what gets downloaded (tier and region
   usually do; an open end date rarely does).
2. **Consult the bundle for this load first.** Discover and read the
   SWOT concepts that apply (glob `knowledge/`): the dataset concept for
   structure, tiers, version family, and current baseline, and the
   gotchas the request or downstream intent triggers (the orbit-phase
   and version-family trap whenever the range touches 2023; the
   crossover-calibration issue whenever statistics are the goal; the
   within-collection baseline drift when consistency matters
   downstream). Restate what each changes about the plan and cite it by
   path; do not carry these facts in this skill. A concept added since
   you last ran is found this way.
3. **Search before fetching:** earthaccess granule search (ShortName,
   temporal, bounding box); report granule count and estimated volume
   BEFORE any download.
4. **The volume gate (hard gate).** Threshold from the project local
   config (`ocean-science.local.md`, "maximum ungated download size";
   template default 2 GB). At or below threshold: state count, size, and
   destination, then proceed. Above threshold: STOP and present count,
   total size, destination, and a smaller alternative (fewer cycles,
   tighter box, a lighter tier), and wait for explicit confirmation. The
   gate lives here in the skill body so it fires on every surface. The
   finest-posting tier deserves a size warning even under threshold (its
   fine posting inflates volume fast; the dataset concept records the
   posting).
5. **Load with flags decoded:** open granules; decode the bit-packed
   quality flags per quality-control's rules; mask flagged pixels;
   never drop the swath dimensions or interpolate across the nadir
   gap (loading contract, not analysis).
6. **Swath-aware summary:** cycles and passes loaded (with orbit
   phase); per-swath (left/right) valid-pixel coverage; flagged
   fraction with the dominant flag reasons; processing baselines
   present in the loaded granules; ssha statistics over good pixels
   computed with the crossover correction the dataset concept's
   crossover known issue prescribes (that concept names the correction
   field and its quality gate), stating explicitly that the correction
   was applied; which uncertainty variables came along (per the dataset
   concept's Uncertainty section). This summary is the downstream
   provenance record; name the concepts consulted.

## Must NOT

- Never download above the gate threshold without explicit
  confirmation, on any surface. (Hard refusal: invariant, universal,
  fires without consulting anything.)
- Never present statistics from undecoded or unmasked pixels. (Hard
  refusal.)
- Never flatten swaths into a regular grid or fill the nadir gap as a
  loading step; that is analysis, done deliberately elsewhere. (Loading
  contract, not a dataset fact.)
- Never work from a remembered SWOT dataset rule where a concept exists:
  the version family and current baseline, the within-collection
  baseline drift, the cal/val-to-science orbit transition (surfaced and
  gated per its gotcha), the tier inventory and posting, and the
  crossover correction all live in the swot concepts
  (datasets/swot-karin.md and the swot gotchas) and are read from them
  per load, not restated here. Report what the granules actually
  carried.
