# devFoundry plugins

Claude Code plugins for MuleSoft and API engineering. They make an agent think about integration problems before it writes code: it checks whether a flow needs a pattern, applies it only when the problem is present, starts each endpoint from a spec that describes it, tests it through HTTP, and follows the project's own conventions.

| Plugin | What it does |
| --- | --- |
| `api-first` | The API-first way to implement a change from its requirements: every requirement numbered before code, the contract first, tests that cite the requirement they prove, and a final table that shows anything not done. It takes the requirements from your own process (an OpenSpec change, a design, requirement documents) and calls the other plugins at each step. |
| `integration-patterns` | Finds integration problems in a flow, even when the developer does not name a pattern, and applies the right *Enterprise Integration Pattern* (Hohpe and Woolf), or says why none is needed. Catalog: **Idempotent Receiver** (no double charges on redelivery). |
| `resilience-patterns` | Finds the risk of a slow or failing dependency taking the caller down, and applies a stability pattern, or says why none is needed. Catalog: **Circuit Breaker**, **session renewal**, **bounded fan-out with a time budget**, **retry of transient failures**. |
| `engineering-profile` | Applies the project's `engineering/profile.yaml`: naming rules for flows, files, global elements and variables, and how new code relates to legacy code. The same skill gives different names under different profiles, without editing the skill. |
| `api-contracts` | Makes every endpoint start from a spec that describes it: checks the spec the app actually loads, and writes or extends it in the project when the published one (a template placeholder, an Exchange asset) lacks the operations. Rules for OpenAPI 3 and RAML contracts, the API-led layer an API belongs to (system, process, experience) and the limits its contract states. |
| `mule-engineering` | Mule 4 rules with verified examples: flows, layout, properties, the global error handler (a backend timeout reaches the caller as 504, never 408), structured logs and the build (`mule-app`); DataWeave modules and their tests (`dataweave`); the APIkit router and the spec it loads (`apikit`); MUnit tests that call each endpoint through the HTTP listener, so a route missing from the spec fails a test instead of answering 404 in production (`munit`); connectors, shared plugins and DataWeave libraries as assets with a public contract (`mule-sdk`). |

Each pattern has a platform-neutral reference and a Mule 4 realization backed by a project that builds and passes its MUnit tests.

## Requirements

- **Claude Code**, in the terminal, the Code tab of the Claude desktop app, or the VS Code extension. The plugins work in full there: the skills read your project, write the code and run the build.
- **For Mule projects:** what your project already builds with, so the agent can run `mvn clean test`:
  - the JDK your Mule runtime supports (17, which Mule 4.6 and later support);
  - Maven 3.9.x, because Maven 3.10 breaks the Mule Maven plugins;
  - access to MuleSoft's EE Maven repository, which MUnit needs.
- **Optional:** [`uv`](https://docs.astral.sh/uv/), to print the rules a project profile puts in effect (see [Check what is in effect](#check-what-is-in-effect)).

## Install

The marketplace is named `devfoundry`. Add it once, then install the plugins you want. Most Mule API work uses all six: `api-first` calls the others at each step.

### Claude Code, in the terminal

In a Claude Code session (each `/plugin install` opens the plugin's panel, where you pick the scope and confirm):

```
/plugin marketplace add brunosouzas/devfoundry-plugins
/plugin install api-first@devfoundry
/plugin install integration-patterns@devfoundry
/plugin install resilience-patterns@devfoundry
/plugin install engineering-profile@devfoundry
/plugin install api-contracts@devfoundry
/plugin install mule-engineering@devfoundry
```

Or from a shell, with a scope (`user` for every project, `project` to record it in this repository's settings, `local` for this repository only on your machine):

```bash
claude plugin marketplace add brunosouzas/devfoundry-plugins
for p in api-first integration-patterns resilience-patterns engineering-profile api-contracts mule-engineering; do
  claude plugin install "$p@devfoundry" --scope user
done
```

A plugin installed from a shell loads the next time Claude Code starts, or after `/reload-plugins`.

### The Code tab of the Claude desktop app

The desktop app's Code tab, the terminal and the VS Code extension read the same settings on one computer, so a plugin installed at user scope in one is there in the others.

1. Add the marketplace once from a terminal: `claude plugin marketplace add brunosouzas/devfoundry-plugins`.
2. Click **+** next to the prompt box, then **Add plugins** (or **Plugins > Browse plugins**), pick a devFoundry plugin and its scope.
3. **Plugins > Manage plugins** enables, disables or uninstalls them.

Cloud sessions of the desktop app do not get these plugins.

### VS Code

Type `/plugins` in the Claude Code panel to open **Manage plugins**, add `brunosouzas/devfoundry-plugins` on its **Marketplaces** tab, then install each plugin with a scope.

### claude.ai and Cowork

On a paid plan, **Customize > Plugins > Add > Add marketplace**, then `brunosouzas/devfoundry-plugins`. Cowork takes its plugins from the same claude.ai account.

- **In chat** the skills guide the answer, but chat cannot open your project or run its build.
- **In Cowork** we have not tried a Mule build.
- The work these plugins are for (code that builds and tests that pass) belongs in Claude Code.
- Plugins turned on in claude.ai also reach Claude Code sessions in the terminal, as `<plugin>@synced`. Install them in one place, or you get two copies.

### A whole team

A project can offer the plugins to everyone who opens it. Add to its `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "devfoundry": {
      "source": { "source": "github", "repo": "brunosouzas/devfoundry-plugins" }
    }
  },
  "enabledPlugins": {
    "api-first@devfoundry": true,
    "integration-patterns@devfoundry": true,
    "resilience-patterns@devfoundry": true,
    "engineering-profile@devfoundry": true,
    "api-contracts@devfoundry": true,
    "mule-engineering@devfoundry": true
  }
}
```

Claude Code registers the marketplace when a contributor trusts the folder. Each contributor still installs the plugins once per clone (`claude plugin install <plugin>@devfoundry --scope project`). To install them for everyone without that step, an organisation uses its managed settings, which take the same two keys.

### Update and remove

```bash
claude plugin marketplace update devfoundry                 # read the latest versions
claude plugin update mule-engineering@devfoundry            # then restart, or /reload-plugins
claude plugin uninstall mule-engineering@devfoundry         # add --scope project if it was installed that way
claude plugin marketplace remove devfoundry                 # removes the marketplace and all its plugins
```

Auto-update is off by default for a marketplace like this one; turn it on in `/plugin` > **Marketplaces**. What changed in each version is in [CHANGELOG.md](CHANGELOG.md).

## Use

There is no command to learn. Describe the work as you would to a colleague, in a Mule project, and the skills load when the work matches:

> Implement `GET /orders/{orderId}` following `docs/order-status/requirements.md`.

With the plugins, the agent:

1. **Looks for what exists** (a spec in the project, an Exchange asset the project names, a System API) and says what it reused.
2. **Numbers every requirement** (R1, R2...) before it writes code.
3. **Writes or extends the spec** the app loads, then the flows, following the project's profile or its existing conventions.
4. **Decides the integration patterns** the flow needs, even when you named none: a client that can resend the request, a backend that can hang, one call per item of a list.
5. **Tests each endpoint through HTTP** with MUnit, at least one test per requirement or the reason it has none, and runs `mvn clean test` when it can (it says so when it cannot).
6. **Ends with what you must decide and a table of every requirement** (done and tested, done and not tested, or not done, with the reason), and one line per pattern considered: `applied` or `not applied`, and why.

Smaller asks work too: "review this flow", "this API hangs when the scoring service is slow", "write the MUnit tests for this endpoint". To ask for a skill by name, use its full name, for example `/mule-engineering:munit`; `+ > Slash commands` in the desktop app lists them.

### If a skill does not load

- Check that the plugin is installed and enabled: `claude plugin list`, or `/plugin`. Load failures show on the **Errors** tab of `/plugin`.
- After an install or update from a shell, restart Claude Code or run `/reload-plugins`.
- Ask for it by name: type `/` and look for `/<plugin>:<skill>`, such as `/api-first:api-first-implementation`.
- The skills are for Mule 4 projects and API specs. In another stack only the platform-neutral ones apply: `api-first`, `integration-patterns`, `resilience-patterns`, `api-contracts`.

## Your own layer: rules, agents and process

devFoundry is the public layer: skills that hold practices, each rule with an ID (`MERR-3`, `MUNIT-5`, `CON-2`), and examples that build. What is yours, or your company's, goes in a **private layer on top**, without forking or editing a public skill:

| Piece | What it is | Where it lives | How it uses devFoundry |
| --- | --- | --- | --- |
| **Rules** | your conventions: names, rules of your own, public rules changed or turned off | a rules pack in your private repository, brought into each project as `engineering/packs/<name>/` | the project's `engineering/profile.yaml` lists the pack; the skills that hold rules read the result |
| **Agents** | who does the work: a developer, a reviewer, with their model, tools and permissions | `.claude/agents/` of a project, `~/.claude/agents/`, or a private plugin | each agent preloads the devFoundry skills it needs |
| **Process** | how a change runs end to end: proposal, design review, approvals, pull requests, delivery | a skill in a private plugin, or your team's `AGENTS.md` and `CLAUDE.md` | it calls the devFoundry skills at each step |

Skills are public because they are capabilities; agents, process and company rules are private because they differ per person and per company. [`docs/scope.md`](docs/scope.md) gives the reasons.

### Rules

Rules have three levels of precedence, and a higher one wins. Personal and company packs both sit at the Packs level:

| Layer | Where | Holds |
| --- | --- | --- |
| Public | the skills of this repository | the practices |
| Packs | `engineering/packs/<name>/pack.yaml` in the project, copied from your private repository (a git submodule, or a copy pinned to a version) | the company's or your own conventions |
| Project | `engineering/profile.yaml` | what this one project or team decides, over its packs |

#### A pack

A company pack, `engineering/packs/acme-mule/pack.yaml`:

```yaml
apiVersion: devfoundry/v1
kind: RulesPack
name: acme-mule
version: 1.0.0
layer: company
mulesoft:
  naming:
    flow: "acme-{resource}-{operation}-flow"        # acme-customers-get-flow
    implFile: "src/main/mule/acme/{resource}.xml"
    globalConfigFile: "src/main/mule/acme/acme-global.xml"
    variable: "snake_case"
rules:
  add:
    - id: ACME-LOG-1
      text: "Every new endpoint flow logs one line on entry and one on exit, with category com.acme.api.<resource>."
      why: "ACME's log routing and audit dashboards select API traffic by that category."
      check: "each new endpoint flow has two loggers with category com.acme.api.<resource>"
  override:
    BUILD-1: { class: auto, why: "every ACME build pins Maven 3.9 and Java 17; no need to ask" }
  disable:
    LAYOUT-2: "our project template has its own folder layout"
```

- **`add`** a rule of your own. Its ID takes a prefix of yours (`ACME-`), never a public one, so it cannot collide with a future public rule.
- **`override`** a public rule by ID: its text, its decision class, or both.
- **`disable`** a public rule by ID, with the reason.

#### The project profile

The project lists its packs in order (a later one wins) and adds its own choices:

```yaml
apiVersion: devfoundry/v1
kind: EngineeringProfile
name: catalog-team
extends:
  - engineering/packs/acme-mule
mulesoft:
  naming:
    variable: "camelCase"   # this team keeps camelCase, over the company's snake_case
```

Without a profile, the skills follow the conventions already in the project, and say so.

#### Decision classes

Every rule has one, and a pack or the project can change it by ID:

- `auto`: the agent applies it;
- `propose`: it recommends it, says what it costs, and applies it when you agree or the task already asks for it or implies it;
- `ask`: it stops and asks you first.

#### What cannot be turned off

Floor rules: synthetic test data, no secrets in code, a declared security scheme, and never a full payload or personal data in logs at INFO or above. A pack or the project that tries to disable or override one is refused and the refusal is reported; the rest of the profile still applies. A pack can add a stricter rule of its own.

#### Check what is in effect

Ask the agent which rules are in effect, or run the resolver from a clone of this repository (it needs `uv`):

```bash
uv run plugins/engineering-profile/skills/project-profile/scripts/resolve-profile.py path/to/your-project
```

It prints the layers, every rule a pack or the project changed, the rules of class `ask` and `propose`, and the naming in effect. An error in a profile or a pack stops the agent before it writes code. The file formats are in [`profiles/SCHEMA.md`](profiles/SCHEMA.md), and the merge rules in [`layers.md`](plugins/engineering-profile/skills/project-profile/references/layers.md). [`profiles/examples/`](profiles/examples/) has the synthetic ACME pack and two naming-only profiles in the older v0 schema, which cannot use `extends` or `rules`; start from the v1 examples above.

### Agents

An agent is a Markdown file with its instructions, and its `skills:` list loads devFoundry skills at start. A synthetic company developer, `.claude/agents/acme-mule-developer.md`:

```markdown
---
name: acme-mule-developer
description: Implements a change in an ACME Mule 4 API, from its approved design to green MUnit tests. Does not merge or deploy.
model: sonnet
skills:
  - engineering-profile:project-profile
  - api-first:api-first-implementation
  - api-contracts:api-contract
  - mule-engineering:mule-app
  - mule-engineering:dataweave
  - mule-engineering:apikit
  - mule-engineering:munit
  - integration-patterns:integration-patterns
  - resilience-patterns:resilience-patterns
---

You implement one change from its approved design. Read the project's AGENTS.md first.
Build with `mvn clean test` and report every requirement, as api-first-implementation says.
Open the pull request with ACME's template; never merge it.
```

The skills bring the practices and the project's rules; the agent adds what is yours: the model, its tools, and where its work stops.

- **devFoundry must be installed too.** A skill missing from `skills:` is skipped with only a warning in the debug log, so the agent would run without the practices.
- **The prompt is not a gate.** "Never merge" in the prompt is an instruction, not a block. To enforce it, give the agent a `tools` list, or use permissions and branch protection.
- **Agents from a plugin have limits.** They ignore `permissionMode`, `hooks` and `mcpServers`; keep the agent in `.claude/agents/` when it needs those.

### Process

A process is the order of a change and its gates, for example: proposal, design review, implementation, code review, approval, merge, delivery. Write it as a skill of your own (`acme-change-flow`), and at each step name the devFoundry skill or the agent that does it: implementation is the `acme-mule-developer` agent (`acme-engineering:acme-mule-developer` when it comes from a plugin), the contract is `api-contracts:api-contract`, the design review checks the patterns with `integration-patterns` and `resilience-patterns`. devFoundry takes its requirements from wherever your process puts them (a spec-driven change, a `design.md`, requirement documents) and never asks for a process of its own.

### Where the private layer lives

Keep the agents and the process in a private repository with the same layout as this one: a `.claude-plugin/marketplace.json` and a plugin with `skills/` (the process) and `agents/`. Install it like devFoundry; the part after `@` is the `name` in your `marketplace.json`:

```bash
claude plugin marketplace add your-company/engineering-private
claude plugin install acme-engineering@acme
```

Claude Code reads a private repository with the git credentials already on the machine and never prompts:

- **Over SSH:** the key must be loaded in `ssh-agent` and the host already in `known_hosts`.
- **Over HTTPS:** a stored credential is needed. On GitHub, run `gh auth login`, then `gh auth setup-git`.

Installing the plugin does not bring the rules into a project. Keep each rules pack in a repository (or folder) of its own, with `pack.yaml` at its root. Each project brings it in as `engineering/packs/<name>/`, by git submodule or by a copy pinned to a version, and lists it in its profile. The resolver refuses a pack outside the project.

## Stack names

A process that loads one skill per technology named on a repository's `Stack:` line (in its `AGENTS.md`) matches a name against each skill's `name` and its `metadata.aliases`, ignoring case:

| Name on the `Stack:` line | Skill |
| --- | --- |
| MuleSoft, Mule, Mule 4, Anypoint, CloudHub | `mule-engineering:mule-app` |
| APIkit | `mule-engineering:apikit` |
| DataWeave, DataWeave 2, DWL | `mule-engineering:dataweave` |
| MUnit, MUnit 3, MUnit Tools | `mule-engineering:munit` |
| Mule SDK, Mule extension, Mule connector, mule-plugin, dw-library | `mule-engineering:mule-sdk` |
| RAML, OpenAPI, OAS, Swagger, API spec | `api-contracts:api-contract` |

The other skills are not technologies: `project-profile`, `api-first-implementation` and the pattern skills load from their descriptions, or because another skill invokes them.

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
