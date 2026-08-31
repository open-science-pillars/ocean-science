# Eval case schema (ocean-science)

Case format per SPEC §8. Cases
live here beside verification/, versioned with the skills and knowledge
they test. Evals test AGENT SCIENTIFIC JUDGMENT with the plugin
installed (golden notebooks test code; the surface harness tests
packaging).

## Case types

- `gotcha-avoidance`: one per high-severity gotcha (mandatory, harness
  rule 9): does the agent surface and act on the trap unprompted?
- `rejection`: the 🔴 rules and gates hold (native-grid refusal, volume
  gate).
- `methodology`: correct method chosen (area weighting, trend method,
  uncertainty statement); core's cases are of this type.
- `recipe-fidelity`: an end-to-end result lands inside the recipe
  concept's expected range and spread.

## Fields

```yaml
id: native-grid-refusal        # matches the gotcha's eval_case field
type: rejection                # one of the four types above
targets: [ocean-budget, gotchas/ecco-native-vs-regridded]
prompt: >                      # verbatim; no coaching on the tested behavior
  ...
fixtures: [verification/fixtures/...]   # empty list if none needed
graders:
  - programmatic: <checker id>          # transcript/output predicate
  - rubric: <rubric file>               # rubric-eval judge (shared runner)
trials: 5                      # seed runs; 20 under the shared runner
pass_threshold: 0.8
notes: >                       # grading guidance for the manual seed pass
  ...
```

Seed discipline: cases are drafted here, run
ONCE each manually on Claude Code, and rubric-graded by hand into
`RESULTS-seed.md` with the model version and date recorded. The
programmatic grader ids name predicates the shared runner (the org
evals repo) implements; until then they document grading intent.
Prompts must state the task only; naming the expected behavior in the
prompt invalidates the case (same rule as the behavior-test prompt
corpus in marketplace/docs/prompts/).
