# Layers: how a profile and its packs merge

The owner of the merge rules. `profiles/SCHEMA.md` in the devFoundry repository describes the file formats and points here; `scripts/resolve-profile.py` implements these rules.

## Order

1. **Public:** the rules in the `rules.md` of every devFoundry skill, cited by ID (`CON-2`, `MUNIT-5`, `FLOOR-1`).
2. **Packs:** each folder in the profile's `extends`, in the order listed. A later pack wins over an earlier one.
3. **Project:** `engineering/profile.yaml` itself wins over every pack.

## Settings (`mulesoft.naming`, `mulesoft.precedence`, `mulesoft.components`)

- Merged key by key, one level deep: a higher layer's key replaces the lower layer's value whole (a nested map such as `components.circuitBreaker: {module, version}` is replaced, not merged).
- When a key is replaced, the report names both values and both layers.

## Rules

- **`override`:** `<ID>: "<text>"`, or `<ID>: {text: "<text>", why: "<reason>"}` (`why` is optional and only reported). It replaces the text of a public rule, or of a rule a lower layer added, and keeps the ID. Overriding a rule a lower layer disabled turns it back on.
- **`disable`:** `<ID>: "<reason>"`. The reason is a required string.
- **`add`:** a list of `{id, text, why, check}`, all four required. The ID has the form `PREFIX-N` (`ACME-LOG-1`), must not exist yet, and its prefix must not be a public prefix (`CON`, `MUNIT`...), so a future public rule cannot collide with it. To change a rule that exists, use `override`.
- **One change per rule per layer:** the same ID in two of `add`, `override` and `disable` of one layer is an error.
- **Floor rules**, marked `(floor)` in a `rules.md` (`FLOOR-1`, `FLOOR-2`, `APISEC-1`, `MLOG-2`): no layer can disable or override them. The attempt is **refused**: the public rule stays, and the refusal is reported. It is not an error: the rest of the profile still applies. A layer can `add` a stricter rule of its own.

## Packs

- A pack is a folder inside the project (`engineering/packs/<name>/`) that holds `pack.yaml` with `kind: RulesPack`, a `name` and a `version`. A folder outside the project is refused.
- A pack has no `extends`, and is listed once.
- A pack with the wrong `kind` or `apiVersion` is not applied.

## Errors

Any of these is an error: the profile must be fixed before its rules are used.

- a missing or invalid `apiVersion` or `kind`; `extends` or `rules` in a v0 profile;
- `extends` that is not a list; a pack folder outside the project, listed twice, or without `pack.yaml`; a pack without a name or a version, or with its own `extends`;
- a section of the wrong type (`rules`, `mulesoft` and its sections, `override` and `disable` are mappings; `add` is a list);
- `override` or `disable` of an unknown ID; `override` without text; `disable` without a reason;
- an `add` with a malformed ID, an ID that exists, a public prefix, or a missing field;
- one ID changed twice in one layer.

## What the agent does

- **An error:** stop before writing code, report the error and the file, and ask the developer to fix the profile or the pack. Do not guess what was meant.
- **A refusal:** keep the floor rule, go on with the work, and report the refusal.
- **At the end:** list every rule a pack or the project changed, with its layer; every refusal; and every setting a higher layer replaced.
