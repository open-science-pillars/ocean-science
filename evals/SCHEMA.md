# Eval case schema (ocean-science)

The case format, field by field, is the org's eval authoring guide,
`marketplace/docs/eval-authoring-guide.md`; this file points there and
records what is local. Cases live here beside verification/, versioned
with the skills and knowledge they test, and the org evals repository
(ecco-agent-evals) is the declared authority for the cases it carries.
Evals test AGENT SCIENTIFIC JUDGMENT with the plugin installed (the
verification scripts test code; the surface harness tests packaging).

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

The fields (`id`, `type`, `targets`, `prompt`, `fixtures`, `graders`,
`trials`, `pass_threshold`, `notes`, and the org repository's
`concept_basis`) are defined in the authoring guide; a case here
carries the same fields. `fixtures` names files under this plugin's
`verification/fixtures/`, or under the org evals repository's
`fixtures/` when the fixture lives there.

Seed discipline: cases are drafted here, run
ONCE each manually on Claude Code, and rubric-graded by hand into
`RESULTS-seed.md` with the model version and date recorded. The
programmatic grader ids name predicates the shared runner (the org
evals repo) implements; until then they document grading intent.
Prompts must state the task only; naming the expected behavior in the
prompt invalidates the case (same rule as the behavior-test prompt
corpus in marketplace/docs/prompts/).
