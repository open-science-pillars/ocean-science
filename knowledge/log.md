# podaac-arc bundle: change log

Newest first. One line per change: date, concept path, what changed, who.

- 2026-07-04 · recipes/ecco-heat-budget.md tolerance RE-GROUNDED on
  measurement (steward-approved): the relative-1e-6 criterion replaced by
  absolute max 1e-10 degC/s pointwise (p99.9 1e-11). The ocean_budget
  golden's first run showed relative ratios up to 9e-2 on a CORRECT
  formulation because float32 storage quantization exceeds quiescent-cell
  term magnitudes; measured residuals: max 4.95e-11, median 5.7e-14
  degC/s over 3.34M cell-months. budget-formulation.md aligned · Session 9
- 2026-07-04 · Session 8b full-bundle lint: zero 🔴; the Session-6
  standing check-8 pair CLOSED (all four high gotchas now match real
  eval cases); three check-11 rewordings applied on steward decision
  (ghrsst-mur house-rule phrasing, ecco-v4r4 never-mix imperative,
  swot-karin crid imperative). All 14 external URLs 200 this run · Session 8b
- 2026-07-04 · six arc concepts authored and steward-verified
  (verified_by Paul Ramirez): swot-karin (granule-verified structure,
  crid attribute, 39% valid-fraction normalization), swot-calval-orbit-phases
  (reproducible C-vs-D probes), grace-fo-mascons (RL06.3 v4), both GRACE
  gotchas (GIA severity medium per recorded rationale, steward-confirmed),
  ghrsst-mur (analysis-error framing) · Session 8b
- 2026-07-04 · Session 7 close lint (incremental): zero 🔴, three new 🟡
  resolved on steward decision: heat-budget recipe reworded to the
  owned-by pattern (check 11), inputs expanded to exact ShortNames
  (check 12), and the residual-threshold contradiction reconciled
  (budget-formulation's unsupported 1e-9-relative claim corrected to
  round-off/epsilon framing; recipe's 1e-6 relabeled as conservative
  pass tolerance). Standing check-8 pair unchanged (Session 8b) · Session 7
- 2026-07-04 · recipes/ecco-mht-26n.md, recipes/ecco-heat-budget.md
  authored with the live 2010 reproducing run (MHT 26.5N mean 1.098 PW,
  monthly series recorded) and tutorial provenance; steward review
  passed, both verified (verified_by Paul Ramirez) · Session 7
- 2026-07-04 · steward review passed: all three ECCO concepts verified
  (verified_by Paul Ramirez). Linter run first: zero 🔴, four 🟡; the two
  check-11 findings resolved by applying the linter's rewordings (policy
  phrasing moved out of concept bodies; refusal owned by ocean-budget);
  the two check-8 findings (eval cases native-grid-refusal and
  geothermal-omission are placeholders) stand until Session 8b authors
  the cases · Session 6
- 2026-07-04 · datasets/ecco-v4r4.md, gotchas/ecco-native-vs-regridded.md,
  gotchas/ecco-geothermal-flux.md drafted with evidence from the Session 6
  ShortName audit (51 collections, CMR), live access tests (geometry +
  THETA 2010, 208.75 MB), and the tutorial-verified budget formulation;
  status draft pending steward review · Session 6 (drafted by build
  assistant; steward pro tem: Paul Ramirez)
