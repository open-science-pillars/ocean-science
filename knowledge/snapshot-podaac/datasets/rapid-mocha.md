---
type: dataset
title: RAPID-MOCHA transports at 26.5N (observational reference)
description: "The moored-array AMOC and heat-transport observations at 26.5N; the canonical scriptable download is the dataset DOI, not the project pages."
tags: [rapid, mocha, amoc, mht, observations, "26n"]
generated: { by: knowledge-seeder/claude, at: 2026-07-04T00:00:00Z }
resource: https://doi.org/10.17604/3nfq-va20
version: "MOCHA MHT v.2020 via dataset DOI 10.17604/3nfq-va20; RAPID AMOC series v2024.1a, DOI 10.5285/48d0bf43-0598-ceb2-e063-7086abc062f1, BODC (retrieved from rapid.ac.uk and verified against the file attributes 2026-09-02; earlier access verified 2026-07-04)"
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T02:40:20Z }
stale_after: 2027-01-04
---

# RAPID-MOCHA transports at 26.5N (observational reference)

**Identity.** The RAPID-MOCHA-WBTS moored array at 26.5N in the
Atlantic: continuous overturning (AMOC, Sv) and meridional heat
transport (PW) observations since April 2004; the standard ground truth
for Atlantic transport comparisons (the ecco-mht-26n recipe's
expected-uncertainty is defined against it).

**Access peculiarity (discovered during the end-to-end test,
2026-07-04).** The MOCHA heat-transport product's official project page
links a SharePoint share that scripted workflows cannot fetch. The
canonical scriptable path is the dataset DOI
(https://doi.org/10.17604/3nfq-va20, Johns et al., MHT time series
v.2020); the AMOCatlas community registry
(github.com/AMOCcommunity/AMOCatlas) indexes this and sibling
array-product DOIs. RAPID's own AMOC series downloads directly from
rapid.ac.uk. Comparisons cite the dataset DOI and carry the RAPID-MOCHA
funding acknowledgment the product requests.

**The overturning release on record (added 2026-09-02).** The AMOC
series has its own DOI and version, separate from the MOCHA heat
transport product: release v2024.1a, DOI
10.5285/48d0bf43-0598-ceb2-e063-7086abc062f1 (NERC EDS British
Oceanographic Data Centre NOC, 2026), Open Government Licence v3. The
release identifies itself inside the delivered netCDF files (global
attributes `version` and `DOI`), which is where the bundle reads it
from. The retrieved tree, its manifest, the live checks on the files,
the overlap with the ECCO record (2004-04 through 2017-12, 165 months)
and the terms of use are recorded in
[docs/rapid-26n-record.md](../../../docs/rapid-26n-record.md); a
computation that reads the tree carries its stamp in the receipt.
The confrontation the bundle builds on this release, with its
colocation choices, representativeness gap and measured scores, is
[the overturning recipe](../recipes/ecco-rapid-amoc-26n.md).

## Uncertainty

The published MHT uncertainty is about +/-0.2 PW on 10-day values
(Johns et al. 2011), with temporal variability (monthly std around
0.3 to 0.4 PW) dominating comparison spreads; the recipe concept
records the ECCO-comparison framing. Array-based transports carry
structural terms (boundary-wedge and mid-ocean interpolation choices)
that do not appear in the formal error; sub-0.1 PW distinctions
against any model are beyond the method's resolution.

## Known issues

- Product versions update the record end-date and can revise earlier
  values; comparisons cite the version and DOI actually used (v.2020
  verified 2026-07-04).
- The rapid.ac.uk direct files are refreshed in place (server
  Last-Modified on the retrieval day against a January creation date
  inside the file), so a retrieval is identified by its hashes and
  the version attribute, never by its URL; a later retrieval that
  hashes differently is a new record beside the old one.
- The 10-day meridional_transports.nc file in v2024.1a writes its
  version as v2024-1a and its citation year as 2025, while the
  transport files, README and DOI record say v2024.1a and 2026; the
  manifest tool normalises the hyphen and refuses if the files
  disagree on the release.
- The 10-day-averaged native cadence requires explicit averaging-chain
  statements when compared against monthly model output (per the
  compare-obs alignment discipline).
