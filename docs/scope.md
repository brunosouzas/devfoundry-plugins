# Scope

What Mulesmith is, what it is not, and what is left. Agreed with the maintainer on 2026-11-18. A change to this scope is a pull request to this file.

## The idea in one paragraph

Mulesmith is a public set of **skills**, packaged as Claude Code plugins, for **MuleSoft only**. The skills are reusable by anyone: each one says what to do, holds the rules, and backs its code with examples that build and pass their tests. People and companies put their **own rules and agents** on top, in their own private layer, without editing the public skills. It covers: API-first implementation (contract, code, unit tests), API design, and integration patterns.

## Three layers

| Layer | Where it lives | What it holds |
| --- | --- | --- |
| **Public** | this repository, `mulesmith` | Skills and their verified examples: the public practices MuleSoft itself publishes (API-first, API-led), API contracts, Mule code, MUnit, API design, integration and resilience patterns. The profile mechanism that lets the other layers override rules. |
| **Personal** | the maintainer's own kit or a private repository | His agents (developer, reviewer), his MuleSoft rules as a rules pack, his own end-to-end process: spec-driven development, design reviews, approvals and delivery. |
| **Company** | the company's private repository or marketplace | The company's agents, process and corporate rules (logger, error handler, project template, approved modules), named by the project's `engineering/profile.yaml`. |

The public layer never holds personal or company material, and never client data. The private layers never fork a public skill: they add or override rules by ID, through the profile.

## Skills public, agents private

- **Skills are public.** A skill is a capability: a procedure, rules with IDs, and verified examples. It does not decide who approves, which tools an agent may use, the branch model, the tracker or where a pull request goes.
- **Agents are private.** An agent carries the process and policy of whoever runs it: model, tools, permissions, gates, delivery. That differs per person and per company, so agents live in the personal or company layer and compose the public skills.
- **Public practices, private processes.** API-first (contract before code, code traced to requirements) and API-led (system, process and experience layers) are practices MuleSoft publishes: they belong in the public skills. How a person or a company runs a change end to end is a process: spec-driven development (proposal, design, scenarios), design reviews, approvals, pull requests and the board. That lives in the personal or company layer, which calls the public skills at each step.
- **API-first is a public skill.** `api-first-implementation` (plugin `api-first`) gives the order (requirements → contract → code → tests → verification) and a final check of every requirement. It takes the requirements from wherever the team's process put them (a spec-driven change, a `design.md`, requirement documents) and never creates or asks for them. Without it, someone who installs the plugins with no process of their own has no flow; the full-API test showed what goes missing without that final check.

## Repository

- One monorepo for every mulesmith skill that becomes a plugin: one plugin per domain, technical names with no brand (`api-contracts`, `mule-engineering`).
- Platform-neutral skills (`integration-patterns`, `resilience-patterns`, `api-contracts`) keep the platform in a subfolder (`references/mule4/`, `assets/mule4/`).
- MuleSoft only. Other languages do not join this repository: they go to a separate public repository, `devfoundry`, which promises **rules only** (rules with IDs and no verified examples, no profile and no measurement). Mulesmith keeps the profile mechanism, the verified examples and the measurement.

## In scope (MuleSoft only)

| Area | Plugin | Today | Missing |
| --- | --- | --- | --- |
| API-first implementation | `api-first` | `api-first-implementation`: reuse first, requirements inventory, contract first, tests traced to requirements, final check (AFI-1 to AFI-6) | nothing open: measured on the full-API case (TAPI, `tooling/evals`) |
| API contract (spec) | `api-contracts` | contract first, RES, CON, APISEC | spec validation with real tooling |
| Mule code | `mule-engineering` | `mule-app` (flows, layout, properties, errors, logs, build), `dataweave`, `apikit`, `mule-sdk` (shared assets) | deploy and platform configuration stays out (delivery); naming conventions stay in profiles and private packs |
| Unit tests | `mule-engineering` | `munit` (endpoints through HTTP, mocks, error paths) | small gaps only |
| API design | `api-contracts` | API-led layers as rules (LAYER-1 to LAYER-5: what a system, process and experience API holds; a new or skipped layer is proposed), limits in the contract (NFR-1); resources and versioning in RES and CON | solution architecture stays out (platform, topology, integration strategy, design documents and reviews belong to the team's process, which calls these rules) |
| Integration patterns | `integration-patterns` | Idempotent Receiver | Content-Based Router, Scatter-Gather, Aggregator, Dead Letter Channel, Correlation Identifier, Publish-Subscribe (source rules in `docs/backlog/eip-from-agent-skills.md`) |
| Resilience patterns | `resilience-patterns` | Circuit Breaker, session renewal, a bounded fan-out with a time budget, retry of transient failures | bulkheads beyond the fan-out's concurrency bound |
| Layers and overrides | `engineering-profile` | schema v1: packs in `extends`, rules overridden, disabled or added by ID, floor rules (`references/layers.md`) | a personal preference layer above the project |
| Measurement | `tooling/evals` | fixed cases T1b, T2, T3b, T5, T6, T8, T9, and the full-API benchmark TAPI (synthetic) | MUnit of the examples in CI (it needs MuleSoft's EE repository; CI packages them) |

## Out of scope

- **Agents and processes.** They belong to the personal or company layer (see above): spec-driven development, design reviews, approvals and boards included.
- **Delivery, pipelines and deployment.** They are covered by the `delivery` plugin of brunosouzas/agent-skills and by each company's own process.
- **Company rules packs and client material.** They live in private repositories.
- **Hosts other than Claude Code.** No other host for now.

## Done

The pieces planned on 2026-11-18 are all in place: layers and overrides (`engineering-profile`, schema v1), `api-first`, the rest of `mule-engineering`, and API design as rules in `api-contracts`. The full-API case (TAPI) measured the public layer before private layers were put on top.

## Open items

- The rest of the integration-pattern catalog (see the `integration-patterns` row above), one pattern at a time, when a real project needs it.
- Spec validation with Anypoint Governance, only if it runs without an Anypoint login.
- A personal preference layer above the project profile.

## Where the rest went

The maintainer's earlier `mulesoft` and `api` skill families (brunosouzas/agent-skills) were split: the public MuleSoft rules are here, and his personal rules moved to a private pack. Skills for other languages go to `devfoundry`, a separate public repository (rules only).
