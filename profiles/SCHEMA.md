# Engineering profile — schema v1

A project's conventions live in `engineering/profile.yaml`. Skills read them from there and never hold the values themselves. This is not a Claude Code standard: it is a devFoundry convention. `scripts/resolve-profile.py` of the `project-profile` skill validates a profile and prints the rules in effect.

## Layers

Rules come in layers. When two layers set the same thing, the higher one wins:

1. **Public:** the rules inside the devFoundry skills (`rules.md` of each skill, cited by ID: `CON-2`, `MUNIT-5`).
2. **Packs:** the profiles listed in `extends`, in order. A company pack, a personal pack. Each pack overrides the ones before it.
3. **Project:** `engineering/profile.yaml` itself.

A pack has the same shape as a profile, with `kind: RulesPack` and a version. Personal and company packs live in private repositories and come into the project as a folder under `engineering/packs/<name>/` (git submodule, or a copy pinned to a version). Packs never go into the public repository.

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
    <RULE-ID>: { text: "<the rule as it applies here>", why: "<reason>" }
  disable:
    <RULE-ID>: "<reason>"       # the reason is required
  add:
    - id: <PREFIX-N>            # a new ID with its own prefix; never a public ID
      text: "<the rule>"
      why: "<why it exists>"
      check: "<how to check it>"
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
mulesoft: { naming: {}, components: {} }
```

A pack has no `extends`: the project lists every pack it uses, in order.

## How layers merge

- **`mulesoft.naming`, `mulesoft.precedence`, `mulesoft.components`:** key by key. A higher layer's key replaces a lower layer's, and the report names both.
- **`rules.override`:** replaces the text of a public rule, or of a rule a lower pack added. The ID stays, so reviews still cite it.
- **`rules.disable`:** turns off a rule, with the reason. A higher layer can turn it back on by overriding it.
- **`rules.add`:** a new rule. Its ID must not exist yet in the public rules or in a lower layer; use `override` to change one that exists.
- **Floor rules** are marked `(floor)` in a skill's `rules.md` (for example `FLOOR-1`, `FLOOR-2`, `APISEC-1`). No layer can disable or override them. An attempt is refused: the public rule stays, and the refusal is reported. A layer can still `add` a stricter rule of its own.
- **Errors**, which stop the resolution: an unknown ID in `override` or `disable`, an `add` whose ID exists, a pack folder without `pack.yaml`, or a missing reason in `disable`.

## Schema v0

Profiles with `apiVersion: engineering.poc/v0` are still read. They are v1 profiles with no `extends` and no `rules`.
