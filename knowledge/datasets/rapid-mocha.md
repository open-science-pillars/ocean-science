---
type: dataset
title: RAPID-MOCHA transports at 26.5N (observational reference)
description: "The moored-array AMOC and heat-transport observations at 26.5N; the canonical scriptable download is the dataset DOI, not the project pages."
tags: [rapid, mocha, amoc, mht, observations, "26n"]
timestamp: 2026-07-04
resource: https://doi.org/10.17604/3nfq-va20
version: "MOCHA MHT v.2020 via dataset DOI 10.17604/3nfq-va20; RAPID AMOC series via rapid.ac.uk (access verified 2026-07-04)"
status: verified
verified: 2026-07-04
verified_by: Paul Ramirez (steward pro tem)
---

# RAPID-MOCHA transports at 26.5N (observational reference)

**Identity.** The RAPID-MOCHA-WBTS moored array at 26.5N in the
Atlantic: continuous overturning (AMOC, Sv) and meridional heat
transport (PW) observations since April 2004; the standard ground truth
for Atlantic transport comparisons (the ecco-mht-26n recipe's
expected-uncertainty is defined against it).

**Access peculiarity (discovered during the Session 10 end-to-end,
2026-07-04).** The MOCHA heat-transport product's official project page
links a SharePoint share that scripted workflows cannot fetch. The
canonical scriptable path is the dataset DOI
(https://doi.org/10.17604/3nfq-va20, Johns et al., MHT time series
v.2020); the AMOCatlas community registry
(github.com/AMOCcommunity/AMOCatlas) indexes this and sibling
array-product DOIs. RAPID's own AMOC series downloads directly from
rapid.ac.uk. Comparisons cite the dataset DOI and carry the RAPID-MOCHA
funding acknowledgment the product requests.

## Uncertainty

The published MHT uncertainty is about +/-0.2 PW on 10-day values
(Johns et al. 2011), with temporal variability (monthly std around
0.3 to 0.4 PW) dominating comparison spreads; the recipe concept
records the ECCO-comparison framing. Array-based transports carry
structural terms (boundary-wedge and mid-ocean interpolation choices)
that do not appear in the formal error; treat sub-0.1 PW distinctions
against any model as beyond the method's resolution.

## Known issues

- Product versions update the record end-date and can revise earlier
  values; cite the version and DOI actually used (v.2020 verified
  2026-07-04).
- The 10-day-averaged native cadence requires explicit averaging-chain
  statements when compared against monthly model output (per the
  compare-obs alignment discipline).
