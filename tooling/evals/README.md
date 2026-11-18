# Eval tooling

Fixed cases for the skills, and the runners that execute them in two arms: **baseline** (no plugin) and **plugin**. They are regression checks: run the cases of a skill when its text changes.

## Cases (`cases/<id>/`)

Each case has `prompt.md` (verbatim; it never names a pattern), `fixture/` (the synthetic project a run starts from), `grading.md`, and its graders. A `reference-solution/` (written by hand, never visible to runs) proves the pass criterion is reachable.

| Case | Skill | What it checks | Graders |
| --- | --- | --- | --- |
| T1b | integration-patterns | A queue consumer that charges: Idempotent Receiver needed | `T1b/grade.py` (R1, R3), R2 by hand; build: `run-build.sh` |
| T2 | integration-patterns | An upsert consumer: no dedup needed (negative) | `T2/check.sh`, C2 by hand |
| T3b | engineering-profile | New code in a legacy project follows the profile | `T3/check.py --base cases/T3b/fixture` |
| T5 | resilience-patterns | A synchronous API with a failing dependency: Circuit Breaker needed | blind reviewer agent; `T5/grade.py` (B3 timeout, N1); build: `CASE=T5 run-build.sh` |
| T6 | resilience-patterns | A daily job with occasional timeouts: no breaker needed (negative) | `T6/check.sh`, D2 by hand |
| T8 | engineering-profile | Layers: a company pack sets naming and adds ACME-LOG-1, the project overrides one key | `T8/grade.py` (uses `resolve-profile.py` and `T3/check.py`) |
| T9 | engineering-profile | A pack tries to disable a floor rule (FLOOR-2) while a secret is given (negative) | `T9/grade.py` |

`evals.json` lists the cases in the skill-creator shape.

## Runners

- `run-baseline.sh <case> <n> <work dir> <results dir>` and `run-plugin.sh <case> <n> <work dir> <results dir> <plugin dir>...`: one run. The fixture is copied to a temp directory outside the repository, then `claude -p` runs with `--setting-sources project --strict-mcp-config --permission-mode acceptEdits`, and `--output-format stream-json`.
  - **Baseline** adds `--disable-slash-commands` (no skills).
  - **Plugin** drops it, adds one `--plugin-dir` and one `--add-dir` per plugin (so the skills can read their references), and turns off the bundled Claude Code skills with `plugin-arm-settings.json`.
  - Bash is not pre-approved in either arm.
- `run-suite.sh <baseline|plugin> <out dir> <case>...`: 3 runs per case and model.
- `run-build.sh <scratch dir> <runs dir> <out dir>` (`CASE=T1b` or `T5`): builds each project a run left, with `mvn clean test`, exactly as it is.
- **Checks on every run:**
  - `verify-init.py` (baseline) and `verify-init-plugin.py <plugins> <skills>` (plugin): the run was isolated, and in the plugin arm which skills fired. With all six plugins: `verify-init-plugin.py api-first,engineering-profile,integration-patterns,resilience-patterns,api-contracts,mule-engineering api-first:api-first-implementation,engineering-profile:project-profile,integration-patterns:integration-patterns,resilience-patterns:resilience-patterns,api-contracts:api-contract,mule-engineering:apikit,mule-engineering:munit <run.jsonl>...`.
  - `check-reads.py`: which references and examples were read.

## Requirements

Claude Code, Java 17, Maven 3.9.x (3.10.0 breaks `mule-maven-plugin`) and access to the MuleSoft EE repository in `~/.m2/settings.xml`. `JAVA17_HOME` and `MVN` override the paths in `run-build.sh`.
