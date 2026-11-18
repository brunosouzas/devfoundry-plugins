# AGENTS.md — devFoundry plugins

Claude Code plugins for MuleSoft and API engineering. This file is for agents working **on** this repository. Users of the plugins read `README.md`.

## Layout

- `plugins/<plugin>/`: one plugin each, in the Claude Code layout (`.claude-plugin/plugin.json`, `skills/<skill>/SKILL.md`, and `references/`, `assets/`, `scripts/` next to the skill). `.claude-plugin/marketplace.json` lists them.
- `profiles/`: the `engineering/profile.yaml` schema (`SCHEMA.md`) and example profiles.
- `tooling/evals/`: the fixed eval cases (`cases/<id>/`: prompt, fixture, rubric, graders) and their runners. See `tooling/evals/README.md`.
- `docs/`: architecture, decisions, and the results of the proof of concept these plugins came from.

## Rules for changing a skill

- **Names are fixed slugs.** Plugin and skill names are technical and carry no brand. A plugin `name` never changes once published.
- **The description is the trigger.** Write the when-to-use cases there, with concrete wording, and a "Do NOT use" clause for the near misses. The body is the procedure; keep it under 500 lines.
- **References are split.** A pattern has a platform-neutral `references/<pattern>.md` (the why, when and when NOT to use it, failures, limits, the test) and one realization per platform, `references/<platform>/<pattern>.md`. Refer to skill files as `${CLAUDE_SKILL_DIR}/...`.
- **Every code example is a verified project**, in `assets/<platform>/<pattern>/`. It builds and its tests pass (`scripts/verify-examples.sh`), and its key test fails when the pattern is removed (a mutation check). No code snippet goes into a reference without a project that proves it. Pitfalls the build caught go into the realization.
- **A new pattern** comes with its neutral reference, its realization, its verified example, a catalog row in `SKILL.md`, and two fixed cases in `tooling/evals/cases/`: one where the pattern is needed and one where it is not.
- **Before a change merges:** `claude plugin validate plugins/<plugin>`, `scripts/verify-examples.sh`, and, when a skill's text changes, the fixed cases of that skill (`tooling/evals/run-suite.sh plugin ...`), graded as their `grading.md` says. These are regression checks, not a gate before every step. Report what was run and what was not.
- **Never** write credentials, real customer data, real URLs or organisation IDs into fixtures or examples. Synthetic data only.

## Working conventions

- Artifacts (code, skills, docs, commits, pull requests) are in English. Talk to the maintainer in Brazilian Portuguese.
- Every change goes through a branch and a pull request into `main`, squash-merged.
- Agents write on GitHub as `brunosouzas-agent`; the maintainer (`brunosouzas`) approves and merges.
- The agent's token has no `workflow` scope, so changes under `.github/workflows/` are pushed by the maintainer.
