# Regional sea level briefing: US Northeast coastal waters (2010)

Briefing 001. Region: the registered `us-northeast-coast` box (35N to
45N, 75W to 65W, ocean cells on the native ECCO grid, 102 cells).
Period: January through December 2010.

**Plain summary.** Over 2010, sea level in the US Northeast coastal box
rose by about 14.7 cm (a linear fit of 146.7 mm per year across the 12
monthly values; a single-year figure with the seasonal cycle included,
not a long-term rate).[^r1] About 8 percent of the fitted change came
from added water mass and about 93 percent from expansion of the water
column (steric change); the rounded shares need not sum to exactly
100, and the small rounding overlap is the same residual the attester
checks.[^r1][^c1] All three pieces come from one physically consistent
ocean estimate, so their sum can be checked against the total rather
than taken on trust.[^c2]

**How this period compares.** No signed context concept for this
region and period is cited yet, so the single-year figure stands
without an anchor against known regional variability; it should not be
read as a long-term rate.

**What this means for planning.** This is a retrospective, single-year
figure from a 1992-2017 ocean state estimate: single-period figures
carry a wider envelope than multi-year rates, and ECCO provides no
formal error field for any quantity here, so the stated internal check
is the attested partition consistency below.[^c2][^c3] Figures here
are ocean water-level changes from the estimate; relative sea level at
a specific shoreline additionally involves vertical land motion and
glacial isostatic adjustment bookkeeping, which are outside this
briefing's scope.[^c2]

**The numbers.**

| Quantity | Value | Receipt |
|---|---|---|
| Total change, 2010 (linear fit) | +14.7 cm (146.7 mm/yr) | [^r1] |
| Mass component (manometric: added or removed water) | +1.2 cm (11.8 mm/yr) | [^r1] |
| Steric component (expansion of the water column) | +13.6 cm (135.8 mm/yr) | [^r1] |
| Partition residual | max 0.51 mm in any month (within the 1.0 mm tolerance) | [^r1] |

**Method and provenance.** Computed by the sanctioned regional sea
level partition (attested computation
`podaac/computations/ecco-regional-sea-level.md` at nasa-daac-knowledge
commit fc9733a), run `20260830T223624Z-40849f17`, attester verdict PASS
at the recorded tolerance; an area-weighted mean (native-grid cell
areas) over the 102 ocean cells; the SSH variant is `SSH`, the
IB-corrected, GIA-free model sea level per the signed variants
concept, and the steric piece is the model's own density integrated
over depth.[^r1][^c1][^c4] Definitions and caveats per the signed concepts
cited. Data: ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4,
ECCO_L4_OBP_LLC0090GRID_MONTHLY_V4R4,
ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4, and the geometry
granule (citations below, per-DOI).[^cite]

**Boundaries.** This estimate covers 2010 and the underlying data end
at 2017-12; it is a retrospective analysis, not a forecast, and the
operational cadence story arrives with V4r5. No comparison against
tide gauges or altimetry was performed for this briefing; every check
above is internal consistency. Produced by Open Science Pillars
(personal-hat open source), not a NASA or JPL product. Questions and
corrections: Paul Ramirez (@PaulMRamirez), via the
open-science-pillars/marketplace issues.

[^r1]: Attested run 20260830T223624Z-40849f17: receipt (code sha 9a3da0e37068, partition residual max 5.085e-04 m, 12 months, 102 cells) attached to open-science-pillars/marketplace#18; percentages and centimeter changes are arithmetic restatements of the receipt's trends (trend times the one-year period; component share of the total trend).
[^c1]: podaac/computations/ecco-regional-sea-level.md at nasa-daac-knowledge fc9733a: the sanctioned partition, its A1-A5 attester criterion, and the measured 1.0e-3 m tolerance.
[^c2]: knowledge/conventions/sea-level-budget-closure.md (steward-verified 2026-07-06): sea level budget closure as a correction-consistency discipline; single-product consistency is what v1 attests.
[^c3]: podaac/datasets/ecco-v4r4.md at nasa-daac-knowledge fc9733a: ECCO ships no formal error or uncertainty fields; recipe-style expectations and attested checks stand in.
[^c4]: knowledge/gotchas/ecco-ssh-ib-variants.md: the SSH variant family (SSH is the IB-corrected, GIA-free model sea level; the variants are distinct quantities, never mixed).
[^cite]: ECCO Consortium, Fukumori, I., Wang, O., Fenty, I., Forget, G., Heimbach, P., & Ponte, R. M. (2021). ECCO Sea Surface Height - Monthly Mean llc90 Grid (Version 4 Release 4) [Data set]. NASA PO.DAAC. https://doi.org/10.5067/ECL5M-SSH44 Dataset accessed 2026-08-30. | ECCO Consortium, Fukumori, I., Wang, O., Fenty, I., Forget, G., Heimbach, P., & Ponte, R. M. (2021). ECCO Ocean Bottom Pressure - Monthly Mean llc90 Grid (Version 4 Release 4) [Data set]. NASA PO.DAAC. https://doi.org/10.5067/ECL5M-OBP44 Dataset accessed 2026-08-30. | ECCO Consortium, Fukumori, I., Wang, O., Fenty, I., Forget, G., Heimbach, P., & Ponte, R. M. (2021). ECCO Ocean Density, Stratification, and Hydrostatic Pressure - Monthly Mean llc90 Grid (Version 4 Release 4) [Data set]. NASA PO.DAAC. https://doi.org/10.5067/ECL5M-ODE44 Dataset accessed 2026-08-30. | ECCO Consortium, Fukumori, I., Wang, O., Fenty, I., Forget, G., Heimbach, P., & Ponte, R. M. (2021). ECCO Geometry Parameters for the Lat-Lon-Cap 90 (llc90) Native Model Grid (Version 4 Release 4) [Data set]. NASA PO.DAAC. https://doi.org/10.5067/ECL5A-GRD44 Dataset accessed 2026-08-30.
