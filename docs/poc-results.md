# Proof-of-concept results (2026-11-17 to 2026-11-18)

The plugins come from a local proof of concept (not published). It ran headless `claude -p` runs (Claude Code 2.1.308) against synthetic Mule 4 fixtures. Every case had 3 runs per model and was compared with a baseline arm without the plugins, under the same isolation flags. A case passes when the plugin arm passes 3/3 **and** the baseline is clearly worse. The fixed cases are in `tooling/evals/cases/`.

| Hypothesis | Cases | Result |
| --- | --- | --- |
| H1, policy isolation: the same skill gives different naming when only the profile changes | T3, T3b | **T3** (small project): a tie, 6/6 vs 6/6. **T3b** (legacy project): plugin 12/12 vs baseline 3/12. Caveat: the profiles also gained a `precedence` rule. |
| H2, proactive pattern: the right pattern without being named, and none when it is not needed | T1b, T2, T5, T6 | **Idempotent Receiver (T1b):** Sonnet 3/3 vs 0/3; Opus 3/3 vs 3/3 (a tie). **Negative control T2:** 6/6, no dedup added. **Circuit Breaker (T5):** Opus 3/3 vs 0/3; Sonnet 2/3 vs 0/3 (one run wrote no code). **Negative control T6:** 12/12 in both arms, no breaker added. **Regression after adding the second pattern:** T1b 6/6, T2 6/6. |
| H3, real code: the generated project builds and the pattern's test passes | T4, T7 | **T4** (Idempotent Receiver): 6/6 with the verified example; 5/6 in the regression. **T7** (Circuit Breaker): plugin Opus 3/3, Sonnet 0/3; baseline 0/6 (no tests written, 2 schema errors). |

## Lessons that became rules (`AGENTS.md`)

- **Prove every dependency of a test before a counted run.** Three rounds were lost to defects of the harness, the fixture and the skill's own code snippet.
- **Code examples must be complete projects that build.** A partial MUnit snippet in a reference was copied verbatim by every run and broke every test.
- **A mutation check shows a test discriminates.** Remove the pattern, and its key test must fail.
- **Graders:** scripts where an item can be checked; a blind, independent reviewer for judgment items.

## Known limits

- The runs could not execute Bash, so no agent compiled its own code. Letting them run `mvn` would need a new baseline.
- Graders and runs come from the same model family.
- In the Circuit Breaker case, the arms differ mainly on one rubric item: the baselines count client errors as dependency failures.
