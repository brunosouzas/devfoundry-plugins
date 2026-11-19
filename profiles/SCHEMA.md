# Engineering profile — schema v1

A project's conventions live in `engineering/profile.yaml`. Skills read them from there and never hold the values themselves. This is not a Claude Code standard: it is a devFoundry convention. `scripts/resolve-profile.py` of the `project-profile` skill validates a profile and prints the rules in effect.

## Layers

Rules come in layers. When two layers set the same thing, the higher one wins:

1. **Public:** the rules inside the devFoundry skills (`rules.md` of each skill, cited by ID: `CON-2`, `MUNIT-5`).
2. **Packs:** the profiles listed in `extends`, in order. A company pack, a personal pack. Each pack overrides the ones before it.
3. **Project:** `engineering/profile.yaml` itself.

A pack has the same shape as a profile, with `kind: RulesPack` and a version. Personal and company packs live in private repositories and come into the project as a folder under `engineering/packs/<name>/` (git submodule, or a copy pinned to a version). Packs never go into the public repository; the only exception is the synthetic example `profiles/examples/packs/acme-mule/`, used by the eval cases.

Nothing is overridden silently. Every rule that a pack or the project changes is listed, with its layer, in the agent's report. When a higher layer replaces a value set by a lower one, the report says which won.

## Profile

```yaml
apiVersion: devfoundry/v1
kind: EngineeringProfile
name: <profile name>
extends:                        # packs, lowest precedence first; each entry is a folder that holds pack.yaml
  - engineering/packs/<company pack>
rules:                          # project-level changes to rules, by ID
  override:
    <RULE-ID>: { text: "<the rule as it applies here>", class: <auto | propose | ask>, why: "<reason>" }   # text, class or both
  disable:
    <RULE-ID>: "<reason>"       # the reason is required
  add:
    - id: <PREFIX-N>            # a new ID with its own prefix; never a public ID
      text: "<the rule>"
      why: "<why it exists>"
      check: "<how to check it>"
      class: <auto | propose | ask>   # optional; auto when missing
mulesoft:
  naming:
    flow: <pattern>             # name of each flow; placeholders {resource} {RESOURCE} {operation} {OPERATION}
    implFile: <pattern>         # file that holds the flow
    globalConfigFile: <path>    # file that holds every global element (listener, request and other configs)
    variable: <case or pattern> # flow variable names: camelCase, snake_case, or a pattern such as v_{snake_case}
  precedence:
    newCode: profile            # new code follows naming, even next to legacy code; missing files are created
    legacyCode: keep            # existing code is not renamed, moved or reformatted
    divergence: report          # legacy divergences are reported to the developer, not changed
  components: {}                # approved modules by role, for example circuitBreaker
```

- `{resource}`: plural resource name from the endpoint path (`/products/{id}` → `products`); upper-case form `{RESOURCE}`.
- `{operation}`: `list` (GET collection), `get` (GET by id), `create` (POST), `update` (PUT/PATCH), `delete` (DELETE); upper-case form `{OPERATION}`.
- `precedence` values: `newCode: profile`, `legacyCode: keep`, `divergence: report`. Other values are not defined yet.
- Every section is optional. A profile with only `mulesoft.naming` is valid.

## Pack

```yaml
apiVersion: devfoundry/v1
kind: RulesPack
name: <pack name>
version: <semver>
layer: company                  # company or personal; informative, the order in `extends` decides precedence
rules: { override: {}, disable: {}, add: [] }
mulesoft: { naming: {}, precedence: {}, components: {} }
```

A pack has no `extends`: the project lists every pack it uses, in order.

## How layers merge

In short: settings merge key by key, rules change by ID (`override` of the text, the class or both, `disable` with a reason, `add` with a prefix of your own), one change per rule per layer, and floor rules (`FLOOR-1`, `FLOOR-2`, `APISEC-1`, `MLOG-2`) cannot be disabled or overridden, in their text or their class. The full rules, the errors and what the agent does with each are in `plugins/engineering-profile/skills/project-profile/references/layers.md`, which ships with the plugin.

## Decision classes

Every rule has a class: `auto` (the agent applies it), `propose` (it recommends it, says what it costs, and applies it only when the developer agrees or the task already asks for it or implies it) or `ask` (it stops and asks). A public rule's class is the `Class:` line under it in its `rules.md`. A pack or the project changes it by rule ID with `override: {<RULE-ID>: {class: ask}}`; floor rules keep theirs. The table of classes with examples is in `layers.md`.

## Schema v0

Profiles with `apiVersion: engineering.poc/v0` are still read. They are v1 profiles with no `extends` and no `rules`.
