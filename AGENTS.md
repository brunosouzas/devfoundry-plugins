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
- **Test in proportion to the change.** Decide what the change can break, then run the smallest check that would catch it. Write the pass criterion down before running.

  | What changed | What to run |
  | --- | --- |
  | Manifests, docs, layout only | `claude plugin validate`; a smoke run that reads the moved files |
  | A verified example | `scripts/verify-examples.sh` plus the mutation check for that pattern |
  | A realization (`references/<platform>/`) or how the skill reaches it | the verified examples, plus **1 run** of that pattern's positive case on the weakest supported model: the realization was read, the rubric passes, the generated project builds |
  | When to use / When NOT to use, or the catalog signals | 1 run each of that pattern's positive and negative cases, on the weakest supported model |
  | A new pattern, or a claim about the skill's value | the full fixed cases with a baseline arm (3 runs per model), which is the only case that needs it |

  A failed check gets its cause found and fixed; it does not get another round of the same runs. Report what was run, what was not, and why.
- **Never** write credentials, real customer data, real URLs or organisation IDs into fixtures or examples. Synthetic data only.

## Working conventions

- Artifacts (code, skills, docs, commits, pull requests) are in English. Talk to the maintainer in Brazilian Portuguese.
- Every change goes through a branch and a pull request into `main`, squash-merged.
- Agents write on GitHub as `brunosouzas-agent`; the maintainer (`brunosouzas`) approves and merges.
- The agent's token has no `workflow` scope, so changes under `.github/workflows/` are pushed by the maintainer.
