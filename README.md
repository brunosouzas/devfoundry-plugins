# devFoundry plugins

Claude Code plugins for MuleSoft and API engineering. They make an agent think about integration problems before it writes code: it checks whether a flow needs a pattern, applies it only when the problem is present, starts each endpoint from a spec that describes it, tests it through HTTP, and follows the project's own conventions.

| Plugin | What it does |
| --- | --- |
| `api-first` | The API-first way to implement a change from its requirements: every requirement numbered before code, the contract first, tests that cite the requirement they prove, and a final table that shows anything not done. It takes the requirements from your own process (an OpenSpec change, a design, requirement documents) and calls the other plugins at each step. |
| `integration-patterns` | Finds integration problems in a flow, even when the developer does not name a pattern, and applies the right *Enterprise Integration Pattern* (Hohpe and Woolf), or says why none is needed. Catalog: **Idempotent Receiver** (no double charges on redelivery). |
| `resilience-patterns` | Finds the risk of a slow or failing dependency taking the caller down, and applies a stability pattern, or says why none is needed. Catalog: **Circuit Breaker**, **session renewal**, **bounded fan-out with a time budget**, **retry of transient failures**. |
| `engineering-profile` | Applies the project's `engineering/profile.yaml`: naming rules for flows, files, global elements and variables, and how new code relates to legacy code. The same skill gives different names under different profiles, without editing the skill. |
| `api-contracts` | Makes every endpoint start from a spec that describes it: checks the spec the app actually loads, and writes or extends it in the project when the published one (a template placeholder, an Exchange asset) lacks the operations. Rules for OpenAPI 3 and RAML contracts, the API-led layer an API belongs to (system, process, experience) and the limits its contract states. |
| `mule-engineering` | Mule 4 rules with verified examples: flows, layout, properties, the global error handler (a backend timeout reaches the caller as 504, never 408), structured logs and the build (`mule-app`); DataWeave modules and their tests (`dataweave`); the APIkit router and the spec it loads (`apikit`); MUnit tests that call each endpoint through the HTTP listener, so a route missing from the spec fails a test instead of answering 404 in production (`munit`). |

Each pattern has a platform-neutral reference and a Mule 4 realization backed by a project that builds and passes its MUnit tests.

## Install

In Claude Code:

```
/plugin marketplace add brunosouzas/devfoundry-plugins
/plugin install api-first@devfoundry
/plugin install integration-patterns@devfoundry
/plugin install resilience-patterns@devfoundry
/plugin install engineering-profile@devfoundry
/plugin install api-contracts@devfoundry
/plugin install mule-engineering@devfoundry
```

The skills load on their own when the work matches. You can also ask for them by name.

## Project profile

Put the conventions in `engineering/profile.yaml` at the project root. See `profiles/SCHEMA.md` and the examples in `profiles/examples/`. A profile can extend your company's or your own rules packs, kept in private repositories, and override, disable or add rules by ID. Every rule has a decision class (`auto`: the agent applies it; `propose`: it recommends it, says what it costs, and applies it when the developer agrees or the task already asks for it or implies it; `ask`: it stops and asks), which a profile can change by ID; floor rules (synthetic test data, no secrets in code, a declared security scheme, no payload or personal data in logs) cannot be turned off. `plugins/engineering-profile/skills/project-profile/scripts/resolve-profile.py` shows the rules in effect. Without a profile, the skills follow the conventions already in the project, and say so.

## What was measured

These plugins come out of a proof of concept with fixed cases, a baseline arm without the plugins, and real Mule builds. `docs/poc-results.md` has the numbers and their limits. In short:

- The profile skill made Opus 5.5 and Sonnet 5.5 follow a project profile in a legacy project in 12/12 runs, against 3/12 without it.
- The Idempotent Receiver was applied in every run where it was needed, and in none of the 18 runs of the negative controls. The generated code built, and its duplicate test passed, in 6/6 projects.
- The Circuit Breaker beat the baseline on Opus 5.5 (3/3 vs 0/3, with 3/3 projects building and passing their tests), but not on Sonnet 5.5. The baselines built a breaker too, but counted client errors as dependency failures.

## Scope

`docs/scope.md` says what devFoundry is and is not: public skills here, personal and company rules and agents in private layers on top, MuleSoft first.

## Develop

See `AGENTS.md` for the rules that keep the skills correct (verified examples, split references, regression cases), and `tooling/evals/README.md` for the eval runners.

## License

[MIT](LICENSE)
