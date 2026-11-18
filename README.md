# devFoundry plugins

Claude Code plugins for MuleSoft and API engineering. They make an agent think about integration problems before it writes code: it checks whether a flow needs a pattern, applies it only when the problem is present, and follows the project's own conventions.

| Plugin | What it does |
| --- | --- |
| `integration-patterns` | Finds integration and resilience problems in a flow, even when the developer does not name a pattern, and applies the right one, or says why none is needed. Catalog: **Idempotent Receiver** (no double charges on redelivery) and **Circuit Breaker** (a slow dependency does not bring the app down). Each pattern has a platform-neutral reference and a Mule 4 realization backed by a project that builds and passes its MUnit tests. |
| `engineering-profile` | Applies the project's `engineering/profile.yaml`: naming rules for flows, files, global elements and variables, and how new code relates to legacy code. The same skill gives different names under different profiles, without editing the skill. |

## Install

In Claude Code:

```
/plugin marketplace add brunosouzas/devfoundry-plugins
/plugin install integration-patterns@devfoundry
/plugin install engineering-profile@devfoundry
```

The skills load on their own when the work matches. You can also ask for them by name.

## Project profile

Put the conventions in `engineering/profile.yaml` at the project root. See `profiles/SCHEMA.md` and the examples in `profiles/examples/`. Without a profile, the skills follow the conventions already in the project, and say so.

## What was measured

These plugins come out of a proof of concept with fixed cases, a baseline arm without the plugins, and real Mule builds. `docs/poc-results.md` has the numbers and their limits. In short:

- The profile skill made Opus 5.5 and Sonnet 5.5 follow a project profile in a legacy project in 12/12 runs, against 3/12 without it.
- The Idempotent Receiver was applied in every run where it was needed, and in none of the 18 runs of the negative controls. The generated code built, and its duplicate test passed, in 6/6 projects.
- The Circuit Breaker beat the baseline on Opus 5.5 (3/3 vs 0/3, with 3/3 projects building and passing their tests), but not on Sonnet 5.5. The baselines built a breaker too, but counted client errors as dependency failures.

## Develop

See `AGENTS.md` for the rules that keep the skills correct (verified examples, split references, regression cases), and `tooling/evals/README.md` for the eval runners.

## License

[MIT](LICENSE)
