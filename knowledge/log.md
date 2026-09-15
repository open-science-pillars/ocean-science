# ocean-science bundle: change log

Newest first. One line per change: date, concept path, what changed, who.

_Historical note: older entries use build-era shorthand (a "close lint" is a knowledge-linter pass; red/yellow marks are nonconformant/advisory findings; check numbers refer to the linter checks documented in core/agents/knowledge-linter). The decision chains, not the labels, are what teach the standards._

- 2026-09-15 · SEEDED, status draft: the regional sea level trend
  recipe and two gotchas for issue 55.
  recipes/regional-sea-level-trend.md (the NASA-SSH altimetry trend
  in a box against the coast, the GIA correction named with its model
  and with the right one of its two rates applied to each quantity,
  the land motion at the gauge from gnss_vertical_velocity with its
  frame beside the SONEL solutions PSMSL prints and the laboratory's
  own tide gauge estimate, the PSMSL RLR relative trend over the same
  window, the identity geocentric equals relative plus uplift with a
  residual read against the combined uncertainty and the two
  differences of place; the Brest land motion term worked from the
  printed values, no trend computed for any site);
  gotchas/coastal-heights-ellipsoidal-versus-orthometric.md (high; a
  GNSS height is above the ellipsoid, a gauge series is above a local
  or orthometric datum and an SSHA is an anomaly against a mean sea
  surface, three surfaces tens of metres apart at one site, with
  nothing in the files naming the surface; eval case
  coastal-heights-ellipsoidal-versus-orthometric proposed in
  agent-evals on branch claude/r3-regional-sea-level under
  ecco/cases; qualifies the PSMSL connector);
  gotchas/velocity-reference-frame.md (medium; a vertical velocity is
  a number in a frame, IGS20, IGS14, ITRF2014 or a plate frame, and a
  difference across frames or solutions reads the frame as land
  motion; medium because the tool returns the frame with every answer
  and the recorded IGS14 to IGS20 effect at one station sits below
  the stated uncertainty, so the trap is a recoverable provenance
  omission; qualifies the GNSS vertical velocity connector). The
  connector concept for the tool (connectors/gnss-vertical-velocity.md,
  merged in PR 57) and the five tide gauge gotchas are linked, not
  repeated. Registration of the eval case in the evals repository's
  manifest is the coordinator's follow-up. Sources read 2026-09-15:
  geodesy.unr.edu (the home page, the reference frames page, the
  vertical land motion at tide gauges page and its README, the
  GipsyX-2.3/IGS20 analysis strategy summary, the MIDAS README, the
  velocities directory README, the tenv3 README, the BRST station
  page, and from the laboratory's publications directory Blewitt 2004
  in full, the abstract and introduction of Blewitt 2003 and sections
  1 to 3 and 5 of Hammond and others 2021); psmsl.org (the ellipsoidal
  links page, the Brest RLR diagram page, the GIA page and the Peltier
  GIA data sets page; the ellipsoidal station list page returned not
  found); podaac.jpl.nasa.gov (the NASA_SSH_REF_SIMPLE_GRID_V11 dataset
  page) and the NASA-SSH V1.1 User Guide it links on
  archive.podaac.earthdata.nasa.gov, read anonymously through the
  signed redirect; api.crossref.org for Blewitt, Hammond and Kreemer
  2018 (doi 10.1029/2018EO104623), Blewitt and others 2016 (doi
  10.1002/2015JB012552), Hammond and others 2021 (doi
  10.1029/2021JB022355) and Peltier 2004 (doi
  10.1146/annurev.earth.32.082503.144359), whose publisher page was
  not fetched. The CO-OPS facts are taken from this bundle's signed
  CO-OPS gotchas and not re-read. Every claim carries a footnote to
  one of these; no data file was downloaded. (knowledge-seeder)

- 2026-09-15 · STEWARD SIGNING of knowledge/computations/argo-ohc.md,
  knowledge/recipes/argo-ohc.md,
  knowledge/references/skills/run-argo-ohc.md: Maintainer review of the
  attested Argo ocean heat content computation merged in PR #56 after
  the coordinator's review and fix round (the attester now verifies the
  data root, the run ids reproduce, the endpoint bar carries the
  autocorrelation inflation); the computation concept and the recipe
  promoted to stable, the run skill stays a draft reference as the sea
  level budget's does; the golden runs in CI from this commit. The
  verified event is written on the steward's word. (steward)

- 2026-09-15 · SEEDED, status draft: the attested ocean heat content
  computation on the Roemmich and Gilson gridded Argo product, issue
  54. computations/argo-ohc.md (type Attested Computation: the 0 to
  700 and 0 to 2000 dbar heat content change over a window as a rate
  with the sanctioned interval, the change the rate implies, the
  endpoint change, the residual and the combined uncertainty, the
  deep ocean below 2000 m as a stated omission with its published
  rate, the rates per unit area, and the anchor distance; a fixture
  with a planted change recovered, a refusal for a window outside the
  coverage, and a real-data run on the stamped root anchored to the
  published 2006 to 2020 rates); recipes/argo-ohc.md (the layer, the
  domain, the baseline and the deep term); references/skills/run-argo-ohc.md;
  the executor references/computations/argo_ohc.py, the attester
  references/attesters/argo_ohc_check.py, the loader
  references/loaders/ohc_rg_loader.py and the data-root tool
  references/loaders/ohc_data_root.py, the stamped root
  references/retrieval/argo-ohc-root (two CSVs, two stamps,
  SOURCES.json, RECORD.json; no product file), and the golden
  verification/argo_ohc.py. Sources read: the Scripps product page
  and the 2019 climatology and extension files through 2026-08
  (downloaded by the loader, hashed in the stamps and SOURCES.json);
  the TEOS-10 manual sections 3.3 and A.18 (cp0 and Conservative
  Temperature as the heat content variable); von Schuckmann and
  others 2023 in full on the journal's site (Table 1 layer rates, the
  deep ocean rate); the Crossref records of Roemmich and Gilson 2009,
  Roemmich and others 2015, Purkey and Johnson 2010, Desbruyeres and
  others 2016 and von Schuckmann and others 2023; the Nature abstract
  of Roemmich and others 2015. The dataset concept and its three
  gotchas are linked, not repeated. (knowledge-seeder)
- 2026-09-15 · knowledge/connectors/gnss-vertical-velocity.md drafted
  for the ocean tool of the observations server's round three
  (gnss_vertical_velocity; core issue 43): the Nevada Geodetic
  Laboratory's MIDAS README, the IGS20 and IGS14 tables and the home
  page read live, both citation DOIs verified on Crossref, the P224
  and TIBB values recorded with their frames; status draft pending
  steward review (drafting session, connector seed)

- 2026-09-14 · STEWARD RE-SIGNING of
  knowledge/gotchas/psmsl-rlr-versus-metric.md,
  knowledge/gotchas/tide-gauge-relative-sea-level-and-land-motion.md,
  knowledge/gotchas/rg-sampled-depth-floor.md: second maintainer review
  recorded on the maintainer's explicit instruction in the coordinator
  session, the maintainer having reviewed the concept; promoted to
  stable under the two-review rule for high severity, with the
  playbook's preference for a different second reviewer noted, and a
  provider confirmation still invited The new verified event is appended
  on the steward's word, the earlier events kept as history. (steward)

- 2026-09-14 · STEWARD SIGNING of
  knowledge/gotchas/coops-datum-and-epoch.md,
  knowledge/gotchas/tide-gauge-gia-is-modelled.md,
  knowledge/gotchas/tide-gauge-record-length-and-gaps.md,
  knowledge/gotchas/psmsl-rlr-versus-metric.md,
  knowledge/gotchas/tide-gauge-relative-sea-level-and-land-motion.md:
  maintainer's review of PR 51 recorded on the maintainer's standing
  instruction for round two of seeding; the three medium gotchas
  promoted to stable; psmsl-rlr-versus-metric and
  tide-gauge-relative-sea-level-and-land-motion (high severity) keep
  draft with this first review until a second human review, per the
  two-review rule. The verified event is written on the steward's word.
  The verified event is written on the steward's word. (steward)

- 2026-09-14 · SEEDED, status draft: five tide gauge datum and vertical
  land motion gotchas on the two tide gauge connector concepts
  (connectors/psmsl-gauges.md and connectors/coops-tides.md; no new
  dataset concept, and each gotcha's dataset field names the
  connector concept it qualifies because no dataset concept exists
  for either service, accepted by design), issue 50.
  gotchas/psmsl-rlr-versus-metric.md
  (high; a metric record is the means as received with datum
  continuity only within a year, an RLR record is reduced to one
  station datum, and a trend from a metric file carries the datum
  history silently; eval case psmsl-rlr-versus-metric proposed in
  agent-evals pull request 16, branch claude/seed-tide-gauge-datums,
  under ecco/cases); gotchas/coops-datum-and-epoch.md (medium; the
  datum choice and the 1983 to 2001 National Tidal Datum Epoch, with
  the 2002 to 2020 epoch due in 2029, the Boston datum collection as
  the worked offsets; medium because the tool returns the datum in
  every response so the error is visible);
  gotchas/tide-gauge-relative-sea-level-and-land-motion.md (high; a
  gauge series is relative sea level and carries the land motion, and
  a comparison with altimetry without the land motion stated is
  silently a comparison of different quantities; eval case
  tide-gauge-relative-sea-level-and-land-motion proposed in the same
  agent-evals pull request under ecco/cases);
  gotchas/tide-gauge-gia-is-modelled.md (medium; the GIA correction
  is a model prediction named by its ice and Earth model, the PSMSL
  set being ICE-5G v1.3 VM2 with a 90 km lithosphere from 2012;
  medium because the trap is a provenance omission, a corrected trend
  with no model named, rather than a wrong value: the model and the
  rate applied are recoverable from the analysis that used them, and
  the uncorrected relative trend is unaffected); and gotchas/tide-gauge-record-length-and-gaps.md (medium; the
  30-year minimum and the published confidence widths of CO-OPS, the
  PSMSL padding, missing days and flags). Registration of the two
  eval cases in the evals repository's manifest is the coordinator's
  follow-up. Sources read 2026-09-14: psmsl.org (the RLR definition,
  the help file, the notes on data and formats, the metric-only
  station list, the referencing page, the ellipsoidal links page, the
  GIA page and the Peltier GIA data sets page, the Brest station page
  and its RLR diagram page with the SONEL GNSS rates);
  tidesandcurrents.noaa.gov (the tidal datums page, the NTDE page and
  its FAQ, the sea level trends page, its FAQ and the Boston station
  trend page) and api.tidesandcurrents.noaa.gov (the data API
  documentation for the datum parameter, the metadata API
  documentation and the Boston datum collection); api.crossref.org
  for Holgate and others 2013 (doi 10.2112/JCOASTRES-D-12-00175.1,
  whose registry record carries no author list, the authors taken
  from PSMSL's referencing page) and Peltier 2004 (doi
  10.1146/annurev.earth.32.082503.144359, abstract read there); the
  publisher pages of both, reached through doi.org, were refused by
  the drafting environment's proxy and are cited on their registry
  records. Every claim carries a footnote to one of these; no data
  file was downloaded. (knowledge-seeder)

- 2026-09-13 · STEWARD SIGNING of
  knowledge/datasets/roemmich-gilson-argo-climatology.md,
  knowledge/gotchas/rg-coverage-excludes-high-latitudes-and-marginal-seas.md,
  knowledge/gotchas/rg-anomaly-against-a-fixed-climatology.md,
  knowledge/gotchas/rg-sampled-depth-floor.md: maintainer's review of PR
  47 recorded on the maintainer's instruction; the dataset concept and
  the two medium gotchas promoted to stable; rg-sampled-depth-floor
  (high severity) keeps draft with this first review until a second
  human review, per the two-review rule The verified event is written on
  the steward's word. (steward)

- 2026-09-13 · SEEDED, status draft: the Scripps Roemmich and Gilson
  Argo climatology, 2019 release with monthly extensions, the gridded
  Argo product whose steric height and heat content cover the upper
  2000 dbar of the open ocean (the product the PO.DAAC bundle's
  attested sea level budget reads as its steric term, through the
  loader knowledge/podaac/references/loaders/slb_steric_rg.py of
  nasa-daac-knowledge pull request 127).
  datasets/roemmich-gilson-argo-climatology.md and three gotchas:
  gotchas/rg-sampled-depth-floor.md (high; the product ends at 1975
  dbar and a budget that carries it as the whole steric term omits
  the deep term; its eval case rg-sampled-depth-floor lives in the
  agent-evals repository under ecco/cases, opened there as pull
  request 12, and the evals repository's ocean-science manifest
  already registers it at that path);
  gotchas/rg-coverage-excludes-high-latitudes-and-marginal-seas.md
  (medium: the coverage is visible in the files, the grid's latitude
  axis and the fill values show where the product stops, so a wrong
  global mean is a labelling error the reader can catch rather than a
  silently wrong number); and
  gotchas/rg-anomaly-against-a-fixed-climatology.md (medium: the
  baseline is written into every anomaly variable's long name and the
  file name carries the release, so a mixed-release series or a
  mis-baselined comparison is detectable from the files, and a
  single-release trend over whole years is unaffected). This index
  gains a datasets and a gotchas section. Sources read 2026-09-13:
  the Scripps product page (sio-argo.ucsd.edu/RG_Climatology.html);
  the August 2026 extension file RG_ArgoClim_202608_2019.nc.gz
  downloaded and read with netCDF4; RG_ArgoClim_Temperature_2019.nc.gz,
  its header first from the first 4 MB of the archive and then the
  whole file downloaded for its mean field and its bathymetry and
  mapping masks; the WCRP Global Sea Level Budget Group 2018 paper
  (doi 10.5194/essd-10-1551-2018) in full from the publisher's PDF;
  the SEANOE landing page of the Argo DOI 10.17882/42182; the
  Crossref registry records of that paper, of Purkey and Johnson
  2010 (doi 10.1175/2010JCLI3682.1, abstract read there) and of
  Roemmich and Gilson 2009 (doi 10.1016/j.pocean.2009.03.004, whose
  publisher page the drafting environment's proxy refused). Every
  claim carries a footnote to one of these. Same day, later: the
  coordinator's lint applied (the steric-term claim reworded to what
  the product is, the CF time statement and the mapping-error
  statement made plain, the four cell counts defined, the whole-years
  qualification on the slope, the climatology file's provenance
  stated the same way everywhere, the area-fraction computation
  written out, the gotcha titles shortened to the trap).
  (knowledge-seeder, coordinator review pending)
- 2026-09-12 · the five conventions: `spheres` added to the
  frontmatter, hydrosphere on the AMO, PDO and mixed-layer
  conventions, hydrosphere with atmosphere on the ENSO indices and
  atmosphere with hydrosphere on the NAO index. Classification by
  Earth science sphere (ADR A in the marketplace repository), outside
  the signed text; no claim changed. (claude-code)
- 2026-09-04 · THE PLUGIN'S COPY OF THE OCEAN EVAL CASES IS RETIRED:
  evals/ (nine case files, the schema pointer, the seed grades and the
  tutorial checkpoint fixtures) deleted. The cases have one home, the
  ecco-agent-evals repository, which already declared itself their
  authority; its case headers now carry the `targets` the copy alone
  recorded, and the seed grades of 2026-07-04 are its first results
  entry. The one file that guarded this plugin's own output rather
  than a case, the briefing 001 regression fixture, moves to
  verification/fixtures/briefings/ with a provenance row. This index
  and the README point at the one home. No concept text changed.
  (build assistant, steward review at merge)
- 2026-09-04 · THE PINNED COPY OF THE PO.DAAC BUNDLE IS RETIRED:
  snapshot-podaac/ (135 files at pin b6ac8fc0d5c1) and snapshot.yaml
  deleted. The bundle now reaches an install only as the
  nasa-daac-knowledge dependency (declared 2026-09-04, floor
  >=2026.9.1), and every skill, agent, reference and verification
  script that cited `knowledge/snapshot-podaac/...` cites the bundle
  path `knowledge/podaac/...` instead, which consult-knowledge resolves
  through the installer's record. The heat-budget smoke
  (verification/ocean_budget.py) reads the provider plugin's
  installPath from `claude plugin list --json` (NASA_DAAC_KNOWLEDGE
  overrides it with a checkout) and runs the same sanctioned code: the
  computation and attester blobs are identical at the old pin and at
  the 2026.9.1 release. The cite-ecco tool copies now cite the release
  tag rather than the pin. This index loses its snapshot section for a
  short account of the dependency. No concept text changed; the three
  local connectors and four local conventions are untouched. (build
  assistant, steward review at merge)
- 2026-09-04 · STEWARD RE-SIGNING of the three connector concepts
  (connectors/argo-floats.md, coops-tides.md, psmsl-gauges.md). Each
  had gained its citation block on 2026-09-01 after the steward's
  signature of that day, so each owed a signature under the
  merge-then-sign rule (SPEC 5.4); the canonical repository's new
  tools/signature_check.py found the debt by the signing commit, the
  steward read the three diffs (the citation block is the whole
  change) and signed again at 2026-09-05T00:17:00Z, the earlier event
  kept as history. The check now runs in the canonical gate for this
  bundle too. Same day, earlier: the PO.DAAC copy refreshed from pin
  24b27927c387 to b6ac8fc0d5c1 (the signing commit of the trend
  family: computations/ecco-trend-ci.md and recipes/ecco-trend-ci.md,
  gotchas/ecco-trend-deseasonalize-jointly.md and
  ecco-trend-without-effective-n.md promoted to stable and signed, and
  computations/ecco-regional-sea-level.md re-signed); five files
  rewritten, none removed, sync_check OK. (steward)
- 2026-09-04 · the PO.DAAC snapshot moves from the flat layout to
  snapshot-podaac/ and becomes a full mirror declared in snapshot.yaml
  (the whole canonical bundle except tutorial/; 135 files at pin
  24b27927c387, the steward's signing commit of that day): the 33
  flat copies of the old snapshot retired (pinned to 41d5ffadd1aa,
  listed in no manifest, and behind canonical's re-sourcing and
  signing since) and 97 files arrive that the old copy never carried
  (14 attested computations, 9 recipes, 8 gotchas, 3 validity
  domains, the finding, the earthdata-mcp connector, the sanctioned
  code, attesters, masks and retrieval receipts they cite). Five
  plugin-local ECCO concepts that were upstreamed to canonical and
  migrated there (ecco-ssh-ib-variants, ecco-boussinesq-global-
  steric, ecco-native-density-eos, ecco-mxldepth-criterion,
  sea-level-budget-closure) are deleted here and return as copies.
  index.md rewritten around the two parts (local conventions and
  connectors; the copy with its pin, scope and contents); skills,
  agents, verification comments, fixtures and the cite-ecco copies
  repointed. Checked by tools/sync_check.py in the canonical
  repository: OK at the pin. (build assistant; the steward's merge is
  the review)
- 2026-09-01 · the three connector concepts gain citation blocks
  (required text, DOI where one exists, whether the source mandates an
  access date, each claim verified against the authority's own page
  this day: PSMSL's Holgate-plus-dataset pairing, Argo's required
  acknowledgment and GDAC DOI with the monthly snapshot mechanism,
  NOS's attribution request with no mandated format). Added after the
  concepts' verification events; the steward's merge is the review of
  this addition. (drafted by build assistant)
- 2026-09-01 · steward review passed: the three connector concepts
  (coops-tides, argo-floats, psmsl-gauges) verified (verified_by
  human:PaulMRamirez) and promoted draft to stable
- 2026-09-01 · the v0.2 event-shape migration this bundle was missed
  by is completed on the steward's direction, original signatures
  carried across: the ten concepts holding v0.1-form verification
  (status verified with a bare date and verified_by line) now carry
  the v0.2 verified event with the ORIGINAL steward date (2026-07-06
  per file frontmatter and the log entry of that day) and status
  stable. No verification is new here; the record's shape changed,
  never its facts
- 2026-09-01 · three connector concepts land with the observations
  MCP server (core repo): CO-OPS tide stations (the datum trap), Argo
  floats (the quality-control discipline the server deliberately does
  not do), PSMSL gauges (the RLR datum that makes absolutes
  meaningless). Every capability claim probed live 2026-09-01; the
  root CONNECTORS.md gains the disclosure section and .mcp.json runs
  the server from a commit-pinned URL. (drafted by build assistant;
  steward review pending)
- 2026-09-01 · The volume budget golden now DEMONSTRATES the oceFWflx
  double-count its header always claimed. It loaded the freshwater flux
  collection and never used it, while three concepts asserted that adding
  a separate oceFWflx forcing term drives the surface residual to order
  1e-8. Measured now, as a shipped assertion with teeth: k=0 residual
  4.27e-12 per s correct against 3.47e-08 per s with the spurious term,
  8135 times worse, and the golden fails if that gap ever closes. The
  heat budget recipe's quantization statement was also corrected to
  measured values; see the podaac-arc log for the derivation.
  (fixed by build assistant; steward review)
- 2026-08-30 · SNAPSHOT extended with the fields layer (ECCO fields
  open-science-pillars/marketplace#10): fields/ecco-v4r4/
  copied byte-identical from canonical at 41d5ffadd1aa (ten stable
  demo-family concepts plus the fields index); sync_check green. The
  ecco variable catalog slimmed to load behavior plus deferral per the
  knowledge-vs-skills doctrine; the catalog's OCEAN_VEL row error
  (WVELMASS for WVEL) leaves with the tables, corrected in the bundle.

- 2026-08-30 · snapshot follow-up: computations/ecco-heat-budget.md
  re-copied byte-identical after the steward sign-off on canonical
  (verified event, status stable); sync_check stays green.

- 2026-08-30 · SNAPSHOT REFRESHED from canonical at de6ef2e6c066 (OKF v0.2
  migration, open-science-pillars/marketplace#6): the 17
  migrated concepts copied byte-identical; the 4 attested-computation
  concepts and references/skills/run-golden.md snapshotted alongside;
  sync_check green (22 files). This CLOSES the declared sync_check red.
  Plugin-local concepts (4 gotchas, 6 conventions) remain v0.1-form
  pending their own migration; the canonical concept wins on conflict.

- 2026-07-06 · steward addition: re-synced grace-fo-mascons and ecco-v4r4 snapshots from canonical (mascon-resolution caveat; THETA/SALT flavor; double-hFac trap). Byte-identical.

- 2026-07-06 · steward review PASSED: the 10 migration-draft concepts (mld-criteria, sea-level-budget-closure, enso/nao/pdo/amo indices, ecco-ssh-ib-variants, ecco-boussinesq-global-steric, ecco-mxldepth-criterion, ecco-native-density-eos) promoted draft to status: verified (verified_by OSP steward review); placeholder evidence replaced with resolving sources (NOAA CPC/NCEI/PSL for indices, published DOIs, TEOS-10, USGS, DataCite, pymannkendall, GRACE JPL, the ECCO variable catalog).

- 2026-07-05 · knowledge-coupling migration (PARKING #14): the ocean skills
  were slimmed to procedure + hard refusals and their dataset knowledge moved
  to concepts. 10 new DRAFT concepts authored by the migration workflow (6
  conventions: mld-criteria, sea-level-budget-closure, enso/nao/pdo/amo indices;
  4 ECCO gotchas: ssh-ib-variants, boussinesq-global-steric, mxldepth-criterion,
  native-density-eos), reconciled from workflow duplicates. Drafts need steward
  review: real evidence links (some carry a relocated-from-skill placeholder),
  severity calibration + eval cases for any promoted to high, and four facts to
  add to protected concepts (GRACE ~300km resolution, THETA/SALT flavor gloss,
  double-hFac). Byte-identity of the podaac mirror preserved.

- 2026-07-05 · steward review PASSED: five concepts
  (recipes/ecco-salt-budget.md, recipes/ecco-volume-budget.md, and gotchas/
  ecco-release-mixing.md, ecco-mht-basin-scope.md, swot-crossover-unapplied.md)
  promoted draft to status: verified (verified_by OSP steward review); datasets
  ecco-v4r4.md and swot-karin.md cross-linked to the new gotchas.

- 2026-07-05 · SPEC §10.5 completion: authored recipes/ecco-salt-budget.md
  and ecco-volume-budget.md with MEASURED round-off tolerances (salt max
  7.2e-11 g/kg/s, volume max 4.6e-12 1/s; 2010 tile-1 interior) and green
  goldens. Volume budget: discovered WVELMASS already carries the surface
  freshwater flux, so a separate oceFWflx forcing term double-counts
  (surface residual jumps to ~1e-8); recorded in the recipe and the
  budget-formulation reference. Drafted for steward review.

- 2026-07-05 · SPEC §10.5 completion: promoted three embedded facts to
  standalone high-severity gotchas with matching eval cases in the
  ocean-science plugin: ecco-release-mixing (V4R4 vs V4R4B), ecco-mht-basin-scope
  (no basin mask = full circle), swot-crossover-unapplied (height_cor_xover
  not pre-applied). Drafted for steward review.

- 2026-07-05 · This bundle is now a PINNED SNAPSHOT: canonical home
  established at open-science-pillars/nasa-daac-knowledge@a0c84fff959f
  (§5.7); files unchanged and byte-identical (sync_check green);
  concept edits happen in the canonical repo first from here on ·
  a later session
- 2026-07-05 · close lint: zero 🔴, three 🟡 applied on steward
  decision: swot-karin verification stamp bumped to cover the ingested
  items; load-swot and swot skills updated to ACCOMMODATE the crossover
  fact (restate lists route through Known issues; loader summary applies
  height_cor_xover and says so; flags-not-sufficient rule; new Must
  NOT). Promotion to a high gotcha deferred
- 2026-07-05 · datasets/swot-karin.md Known issues extended via the
  operational ingest loop (Tutorial 2 fresh walkthrough): crossover
  calibration arrives unapplied in ssha_karin (spurious +/-2.9 m
  cross-track ramp until height_cor_xover is added, observed PGD0
  Expert cycle 011), and CMR spatial matches can be whole passes with
  zero in-box pixels. Steward review passed
- 2026-07-04 · close lint: zero 🔴, one 🟡 (two imperative
  phrases in rapid-mocha.md), reworded to the declarative pattern per
  standing steward precedent; cross-checks vs the MHT recipe and
  compare-obs confirmed complementary, no contradictions
- 2026-07-04 · datasets/rapid-mocha.md LIVE-INGESTED via the operational
  loop: the end-to-end discovered the MOCHA official page
  links a non-scriptable SharePoint share and the canonical scriptable
  path is the dataset DOI (10.17604/3nfq-va20, AMOCatlas-indexed);
  drafted immediately, steward review passed same session (verified_by
  OSP steward review). First ingest-loop concept of the build
- 2026-07-04 · close lint: zero 🔴, four 🟡. Applied (implementing
  already-approved decisions): the relative-1e-6 remnant in
  ecco-heat-budget expected_uncertainty replaced with the approved
  absolute criterion (T1); meridional-transport's carries-no-numbers
  claim reworded after the scope-trap addition (T3); budget-formulation's
  claim of nonexistent salt/volume recipes corrected, recipes parked
 . AMS DOI 403-to-fetchers stands as accepted context
- 2026-07-04 · recipes/ecco-mht-26n.md SCOPE-CORRECTED (steward-approved):
  the earlier anchor 1.098 PW was the GLOBAL latitude circle (bare
  calc_meridional_heat_trsp), not the RAPID-comparable Atlantic section.
  Discovered by a skill-following test agent during a spot
  test, independently verified by basin decomposition (atl 0.666 + pac
  0.430 + ind 0.002 = 1.098). Recipe now carries both anchors with
  scopes; the 0.8-1.4 band is Atlantic multi-year; transport golden
  asserts both anchors and the basin-sum identity;
  meridional-transport skill gained the scope trap
- 2026-07-04 · recipes/ecco-heat-budget.md tolerance RE-GROUNDED on
  measurement (steward-approved): the relative-1e-6 criterion replaced by
  absolute max 1e-10 degC/s pointwise (p99.9 1e-11). The ocean_budget
  golden's first run showed relative ratios up to 9e-2 on a CORRECT
  formulation because float32 storage quantization exceeds quiescent-cell
  term magnitudes; measured residuals: max 4.95e-11, median 5.7e-14
  degC/s over 3.34M cell-months. budget-formulation.md aligned
- 2026-07-04 · full-bundle lint: zero 🔴; the an earlier session
  standing check-8 pair CLOSED (all four high gotchas now match real
  eval cases); three check-11 rewordings applied on steward decision
  (ghrsst-mur house-rule phrasing, ecco-v4r4 never-mix imperative,
  swot-karin crid imperative). All 14 external URLs 200 this run
- 2026-07-04 · six arc concepts authored and steward-verified
  (verified_by OSP steward review): swot-karin (granule-verified structure,
  crid attribute, 39% valid-fraction normalization), swot-calval-orbit-phases
  (reproducible C-vs-D probes), grace-fo-mascons (RL06.3 v4), both GRACE
  gotchas (GIA severity medium per recorded rationale, steward-confirmed),
  ghrsst-mur (analysis-error framing)
- 2026-07-04 · close lint (incremental): zero 🔴, three new 🟡
  resolved on steward decision: heat-budget recipe reworded to the
  owned-by pattern (check 11), inputs expanded to exact ShortNames
  (check 12), and the residual-threshold contradiction reconciled
  (budget-formulation's unsupported 1e-9-relative claim corrected to
  round-off/epsilon framing; recipe's 1e-6 relabeled as conservative
  pass tolerance). Standing check-8 pair unchanged (then pending)
- 2026-07-04 · recipes/ecco-mht-26n.md, recipes/ecco-heat-budget.md
  authored with the live 2010 reproducing run (MHT 26.5N mean 1.098 PW,
  monthly series recorded) and tutorial provenance; steward review
  passed, both verified (verified_by OSP steward review)
- 2026-07-04 · steward review passed: all three ECCO concepts verified
  (verified_by OSP steward review). Linter run first: zero 🔴, four 🟡; the two
  check-11 findings resolved by applying the linter's rewordings (policy
  phrasing moved out of concept bodies; refusal owned by ocean-budget);
  the two check-8 findings (eval cases native-grid-refusal and
  geothermal-omission are placeholders) stand until a later session authors
  the cases
- 2026-07-04 · datasets/ecco-v4r4.md, gotchas/ecco-native-vs-regridded.md,
  gotchas/ecco-geothermal-flux.md drafted with evidence from the earlier
  ShortName audit (51 collections, CMR), live access tests (geometry +
  THETA 2010, 208.75 MB), and the tutorial-verified budget formulation;
  status draft pending steward review (drafted by build
  assistant; steward review)
