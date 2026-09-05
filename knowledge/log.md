# ocean-science bundle: change log

Newest first. One line per change: date, concept path, what changed, who.

_Historical note: older entries use build-era shorthand (a "close lint" is a knowledge-linter pass; red/yellow marks are nonconformant/advisory findings; check numbers refer to the linter checks documented in core/agents/knowledge-linter). The decision chains, not the labels, are what teach the standards._

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
