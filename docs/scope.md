# Scope

What devFoundry is, what it is not, and the order of the next pieces. Agreed with the maintainer on 2026-11-18. A change to this scope is a pull request to this file.

## The idea in one paragraph

devFoundry is a public set of **skills**, packaged as Claude Code plugins. The skills are reusable by anyone: each one says what to do, holds the rules, and backs its code with examples that build and pass their tests. People and companies put their **own rules and agents** on top, in their own private layer, without editing the public skills. The first domain is MuleSoft: API-first implementation (contract, code, unit tests), API design, and integration patterns.

## Three layers

| Layer | Where it lives | What it holds |
| --- | --- | --- |
| **Public** | this repository, `devfoundry-plugins` | Skills and their verified examples: the public practices MuleSoft itself publishes (API-first, API-led), API contracts, Mule code, MUnit, API design, integration and resilience patterns. The profile mechanism that lets the other layers override rules. |
| **Personal** | the maintainer's own kit or a private repository | His agents (developer, reviewer), his MuleSoft rules as a rules pack, his own end-to-end process: spec-driven development, design reviews, approvals and delivery. |
| **Company** | the company's private repository or marketplace | The company's agents, process and corporate rules (logger, error handler, project template, approved modules), named by the project's `engineering/profile.yaml`. |

The public layer never holds personal or company material, and never client data. The private layers never fork a public skill: they add or override rules by ID, through the profile.

## Skills public, agents private

- **Skills are public.** A skill is a capability: a procedure, rules with IDs, and verified examples. It does not decide who approves, which tools an agent may use, the branch model, the tracker or where a pull request goes.
- **Agents are private.** An agent carries the process and policy of whoever runs it: model, tools, permissions, gates, delivery. That differs per person and per company, so agents live in the personal or company layer and compose the public skills.
- **Public practices, private processes.** API-first (contract before code, code traced to requirements) and API-led (system, process and experience layers) are practices MuleSoft publishes: they belong in the public skills. How a person or a company runs a change end to end is a process: spec-driven development (proposal, design, scenarios), design reviews, approvals, pull requests and the board. That lives in the personal or company layer, which calls the public skills at each step.
- **API-first is a public skill.** `api-first-implementation` (plugin `api-first`) gives the order (requirements → contract → code → tests → verification) and a final check of every requirement. It takes the requirements from wherever the team's process put them (a spec-driven change, a `design.md`, requirement documents) and never creates or asks for them. Without it, someone who installs the plugins with no process of their own has no flow; the full-API test showed what goes missing without that final check.

## Repository

- One monorepo for every devFoundry skill that becomes a plugin: one plugin per domain, technical names with no brand (`api-contracts`, `mule-engineering`).
- Platform-neutral skills (`integration-patterns`, `resilience-patterns`, `api-contracts`) keep the platform in a subfolder (`references/mule4/`, `assets/mule4/`). Another stack adds its own subfolder, or its own plugin, in this repository.
- MuleSoft first. Other domains join only after the MuleSoft set is complete and measured.

## In scope (MuleSoft first)

| Area | Plugin | Today | Missing |
| --- | --- | --- | --- |
| API-first implementation | `api-first` | `api-first-implementation`: requirements inventory, contract first, tests traced to requirements, final check (AFI-1 to AFI-3) | measured on the full-API case |
| API contract (spec) | `api-contracts` | contract first, RES, CON, APISEC | spec validation with real tooling |
| Mule code | `mule-engineering` | `apikit` | flows, layout, error handling, logging, properties, build, DataWeave (ported from the maintainer's `mulesoft` and `dataweave` skills) |
| Unit tests | `mule-engineering` | `munit` (endpoints through HTTP, mocks, error paths) | small gaps only |
| API design (architecture) | to be decided | none | API-led layers (system, process, experience), resource modelling, non-functional requirements, API design review rules |
| Integration patterns | `integration-patterns` | Idempotent Receiver | Content-Based Router, Scatter-Gather, Aggregator, Dead Letter Channel |
| Resilience patterns | `resilience-patterns` | Circuit Breaker | retry with backoff, fan-out bounds and a total time budget for N+1 calls, re-login when a session expires |
| Layers and overrides | `engineering-profile` | schema v1: packs in `extends`, rules overridden, disabled or added by ID, floor rules (`references/layers.md`) | a personal preference layer above the project |
| Measurement | `tooling/evals` | fixed cases T1b, T2, T3b, T5, T6 | the full-API case as a benchmark, CI for `verify-examples.sh` |

## Out of scope

- **Agents and processes.** They belong to the personal or company layer (see above): spec-driven development, design reviews, approvals and boards included.
- **Delivery, pipelines and deployment.** They are covered by the `delivery` plugin of brunosouzas/agent-skills and by each company's own process.
- **Company rules packs and client material.** They live in private repositories.
- **Hosts other than Claude Code.** No other host for now.

## Next pieces, in order

1. **Layers and overrides.** Extend the profile beyond naming:
   - a precedence order (public < company < project < preference). Done in schema v1 for public < packs < project; a personal pack sits in `extends` below the project, and a preference layer above the project is left for later;
   - a rules pack that adds or overrides public rules by ID, kept in a private repository the profile names;
   - a report when a company rule conflicts with a public rule, instead of a silent override.

   Without this, every new rule ends up in the public layer for lack of another place.
2. **API-first implementation.** The ordered flow and the final requirements check (`api-first`).
3. **The rest of `mule-engineering`.** Port the remaining Mule and DataWeave rules, with verified examples. A Niche timeout that reaches the caller as 408 is one of the gaps this closes.
4. **API design**, including the API-led layers.

After steps 1 and 2: measure again with the full-API case (1 run per arm), so the public layer is shown to work before private layers are put on top.

## Open decision

The maintainer's existing `mulesoft` and `api` skill families (brunosouzas/agent-skills) overlap with this repository. Each rule there goes one of two ways: into the public layer here, or into his personal rules pack. The old repositories are deleted once that split is done.
