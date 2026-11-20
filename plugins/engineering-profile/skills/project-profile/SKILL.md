---
name: project-profile
description: Use before creating, changing or reviewing any Mule 4 flow, flow file, global configuration element or flow variable (endpoints, queue or event consumers, API calls). Applies the project's engineering profile (engineering/profile.yaml) when there is one, with the company or personal rules packs it extends (rules overridden, disabled or added by ID), including projects whose existing code uses other names, and makes the flow's integration decisions explicit (repeated messages, failures) before any XML is written.
---

# Project profile

The project's conventions live in `engineering/profile.yaml` and in the packs it extends, not in this skill. This skill only says how to apply them. The merge rules are in `${CLAUDE_SKILL_DIR}/references/layers.md`; in short: public rules < packs in `extends`, in order < the project profile, and floor rules cannot be changed.

## Steps

0. **Integration decisions (mandatory, before writing or changing any flow).** List, in your answer, the flow's integration decisions:
   - **Repeated message:** can the same message or request reach this flow more than once (broker redelivery, ack timeout, nack, client resend, replay), and what happens to each side effect if it does?
   - **After a failure:** for each step that can fail, what has already happened by then and what the flow does next (retry, redelivery, dead letter, compensation).
   - **A slow or unavailable dependency:** for each synchronous call, what happens to the flow, its callers and the rest of the app when the dependency hangs or fails for minutes.

   Then invoke the `integration-patterns` skill for repeated messages and side effects, and the `resilience-patterns` skill for slow or unavailable dependencies, and follow each one. Apply a pattern only when the problem it solves is present in this flow and none of its "When NOT to use" items applies; otherwise say which item applies and leave the flow without it. Do this whether or not the project has a profile.
   For an API endpoint, also invoke the `api-contract` skill (api-contracts) before writing flows, so the endpoint is in the spec the application loads, the `apikit` skill (mule-engineering) for the router, and the `munit` skill (mule-engineering) for its tests; when those plugins are not installed, check the loaded spec yourself and test each endpoint through the HTTP listener.
   For any Mule code, also invoke the `mule-app` skill (mule-engineering) for flows, configuration, errors and logs, and the `dataweave` skill (mule-engineering) for transforms. The names still come from this profile, never from those skills.
1. **Floor rules, always:** follow `FLOOR-1` and `FLOOR-2` in `${CLAUDE_SKILL_DIR}/rules.md` (synthetic test data, no secret in code or plain configuration), with or without a profile, whatever a pack says.
   Then read `engineering/profile.yaml` at the project root before writing any Mule XML. If it does not exist, say so and follow the conventions already in the project.
2. **Resolve the layers** when the profile has `extends` or `rules`:
   - Read `${CLAUDE_SKILL_DIR}/references/layers.md`. Then read each pack in `extends` (`<folder>/pack.yaml`), in order, then the profile. A later layer wins: key by key for `mulesoft.naming`, `precedence` and `components`; by rule ID for `rules`. The public rule IDs are those in the `rules.md` of the mulesmith skills you use (and `${CLAUDE_SKILL_DIR}/rules.md`).
   - `rules.override` replaces the text or the class of a rule (public or from a lower pack), or both, and keeps its ID; `rules.disable` turns it off, with its reason; `rules.add` brings a new rule (`ACME-LOG-1`), which you follow like a public one.
   - Every rule has a class (its `Class:` line in a `rules.md`, `class` in a pack or the profile, `auto` when an added rule has none): `auto`, apply it; `propose`, recommend it, say what it costs, and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. A class a layer sets wins like its text does.
   - A rule marked `(floor)` in a skill's `rules.md` (`FLOOR-1`, `FLOOR-2`, `APISEC-1`, `MLOG-2`) cannot be disabled or overridden, in its text or its class: keep the public rule, do not follow the layer's change, go on with the work, and report the refusal.
   - An error in the profile or a pack (an unknown rule ID, an `add` whose ID exists, a `disable` without a reason, the full list in `layers.md`): stop before writing code, report it with the file, and ask the developer to fix it.
   - Every other skill you use applies its rules as resolved here: skip a disabled rule, use an overridden rule's text and class, add the packs' new rules.
   - When `uv` and Bash are available, `uv run ${CLAUDE_SKILL_DIR}/scripts/resolve-profile.py <project>` prints the same result (and errors such as an unknown rule ID); without them, resolve it by reading the files.
3. Under `mulesoft.naming` (as resolved), treat every key as a rule that the code must follow. Resolve each pattern by filling its placeholders from the change at hand (for example the resource and the operation of the endpoint). Take placeholder meaning and casing from the profile itself (its comments and examples); never from habit or from another project.
   Every new file or name that a `naming` key covers follows its pattern, also code that serves more than one resource or no single one (a client of a backend, a shared helper or module). Fill a placeholder that has no obvious value in this order: (1) the value the key's comment gives for shared code; (2) otherwise the value of the first endpoint that uses the code, in the order of the spec (its resource; for `{operation}`, that endpoint's operation); never an invented value (the backend's name, `shared`, `common`). Adding to an existing file the pattern resolves to is fine. List each such choice in the answer's "Decisions for you" section (the one api-first AFI-3 defines; without api-first, add the section yourself), naming the file and the other resources it serves. The separation a skill's example shows (a client file, a domain folder) gives way to the profile. A file no key covers (an MUnit suite, the spec, properties) follows the skills' layout (mule-app LAYOUT-2).
4. Apply each rule:
   - `flow`: the `name` of every flow or sub-flow you create, except APIkit implementation flows, whose names the router matches (`get:\resource:config`): keep those names, or name them by the profile and add `apikit:flow-mappings` (see the `apikit` skill).
   - `implFile`: the file that holds the flow.
   - `globalConfigFile`: the file that holds every global element (listener, request and other configs). Put every global element you add there, never inline in the flow file and never in another existing file.
   - `variable`: the name of every flow variable you create (`set-variable`, `target` attributes).
   - Any other key: apply it the way its name and comment say.
5. Under `mulesoft.precedence`, apply how the profile relates to code that already exists in the project:
   - `newCode: profile`: the rules above win over the surrounding code for everything you add, even when the existing flows, files and variables follow other names. Do not copy legacy names into new code. When the profile's file does not exist yet, create it instead of reusing a legacy file.
   - `legacyCode: keep`: do not rename, move or reformat existing code to fit the profile. It does not keep a template's placeholder API spec as the contract of new endpoints: extending or replacing the spec is part of the new code.
   - `divergence: report`: in your answer, say where the existing code diverges from the profile, as a note for the developer, not as a change.
   - If `precedence` is missing, ask nothing and follow the profile for new code; say so in the answer.
6. Before you finish, list each `mulesoft.naming` key with the value you used and the layer it came from, so the reviewer can check it against the profile (skip when there is no profile); each placeholder you filled with a choice (step 3, in "Decisions for you"); every rule a pack or the project overrode (text or class), disabled or added, with its layer, and every change you refused; and the integration decisions of step 0 with the pattern decision for each.

Do not edit `engineering/profile.yaml` or a pack to fit the code. If a rule cannot be applied, say which and why.
