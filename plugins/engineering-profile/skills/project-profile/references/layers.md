# Layers: how a profile and its packs merge

The owner of the merge rules. `docs/profile-schema.md` in the devFoundry repository describes the file formats and points here; `scripts/resolve-profile.py` implements these rules.

## Order

1. **Public:** the rules in the `rules.md` of every devFoundry skill, cited by ID (`CON-2`, `MUNIT-5`, `FLOOR-1`).
2. **Packs:** each folder in the profile's `extends`, in the order listed. A later pack wins over an earlier one.
3. **Project:** `engineering/profile.yaml` itself wins over every pack.

## Settings (`mulesoft.naming`, `mulesoft.precedence`, `mulesoft.components`)

- Merged key by key, one level deep: a higher layer's key replaces the lower layer's value whole (a nested map such as `components.circuitBreaker: {module, version}` is replaced, not merged).
- When a key is replaced, the report names both values and both layers.

## Classes

Every rule has a decision class, which says how the agent acts on it:

| Class | The agent | Examples |
| --- | --- | --- |
| `auto` | applies the rule: it is technical and can be checked | a backend timeout reaches the caller as 504 (MERR-3); every test cites its requirement (AFI-2) |
| `propose` | recommends it, says what it costs, and applies it only when the developer agrees or the task already asks for it or implies it | calling an existing System API instead of the backend (AFI-6); a layer of API-led connectivity; a pattern that adds a component the task does not show a need for |
| `ask` | stops and asks the developer before acting on it | publishing to Exchange or creating an asset (AFI-5); a breaking change to a spec consumers use (CON-5); a conflict with a company rule |

- A public rule's class is the `Class:` line under it in its `rules.md`; a rule a layer adds has `class` (`auto` when it has none).
- A layer changes a rule's class with `override` (below), by rule ID, like its text. The class of the highest layer wins.
- The pattern skills (`integration-patterns`, `resilience-patterns`) decide with their own "When to use" and "When NOT to use": when the problem a pattern solves is present in the flow, the task implies the pattern, and the skill applies it without asking.
- The rule's text says what; its class says how. A rule's text does not repeat its class, so an override of the class alone changes how the agent acts.
- Floor rules keep their class: an override of their class is refused like any other override.
- When two rules conflict (a pack's rule against a public one, or a rule against the task), that is an `ask`: name both and ask, unless a layer already decided it with `override` or `disable`.

## Rules

- **`override`:** `<ID>: "<text>"`, or `<ID>: {text: "<text>", class: auto | propose | ask, why: "<reason>"}`, with `text`, `class` or both (`why` is optional and only reported). It replaces the text or the class of a public rule, or of a rule a lower layer added, and keeps the ID; what it does not give stays as it was. Overriding a rule a lower layer disabled turns it back on.
- **`disable`:** `<ID>: "<reason>"`. The reason is a required string.
- **`add`:** a list of `{id, text, why, check, class}`; the first four are required, and `class` is `auto` when it is missing. The ID has the form `PREFIX-N` (`ACME-LOG-1`), must not exist yet, and its prefix must not be a public prefix (`CON`, `MUNIT`...), so a future public rule cannot collide with it. To change a rule that exists, use `override`.
- **One change per rule per layer:** the same ID in two of `add`, `override` and `disable` of one layer is an error.
- **Floor rules**, marked `(floor)` in a `rules.md` (`FLOOR-1`, `FLOOR-2`, `APISEC-1`, `MLOG-2`): no layer can disable or override them, in their text or their class. The attempt is **refused**: the public rule stays, and the refusal is reported. It is not an error: the rest of the profile still applies. A layer can `add` a stricter rule of its own.

## Packs

- A pack is a folder inside the project (`engineering/packs/<name>/`) that holds `pack.yaml` with `kind: RulesPack`, a `name` and a `version`. A folder outside the project is refused.
- A pack has no `extends`, and is listed once.
- A pack with the wrong `kind` or `apiVersion` is not applied.

## Errors

Any of these is an error: the profile must be fixed before its rules are used.

- a missing or invalid `apiVersion` or `kind`; `extends` or `rules` in a v0 profile;
- `extends` that is not a list; a pack folder outside the project, listed twice, or without `pack.yaml`; a pack without a name or a version, or with its own `extends`;
- a section of the wrong type (`rules`, `mulesoft` and its sections, `override` and `disable` are mappings; `add` is a list);
- `override` or `disable` of an unknown ID; `override` with neither text nor class; `disable` without a reason;
- a `class` that is not `auto`, `propose` or `ask`;
- an `add` with a malformed ID, an ID that exists, a public prefix, or a missing field;
- one ID changed twice in one layer.

## What the agent does

- **An error:** stop before writing code, report the error and the file, and ask the developer to fix the profile or the pack. Do not guess what was meant.
- **A refusal:** keep the floor rule, go on with the work, and report the refusal.
- **A rule of class `propose` or `ask`:** act on it as its class says; `resolve-profile.py` lists them under "Rules of class ask" and "Rules of class propose".
- **At the end:** list every rule a pack or the project changed (text or class), with its layer; every refusal; and every setting a higher layer replaced.
