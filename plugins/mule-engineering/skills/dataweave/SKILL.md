---
name: dataweave
description: Rules for DataWeave 2 - scripts and modules, null and missing fields, typed pure functions, match with an else, explicit date and number formats, indexing large collections, and tests of each function with its edge cases. Use when writing, changing, reviewing or explaining a DataWeave transform, a .dwl script or module, or a snippet; recognise it by .dwl files, %dw 2.0 headers or ee:transform elements. Do NOT use it for the Mule flow around the transform, its connectors or error handling (mule-app), the structure of an MUnit suite (munit), or the names of .dwl files (the project's conventions or a private pack). It supersedes the `dataweave` skill of brunosouzas/agent-skills when both are installed, keeping its rule IDs.
metadata:
  aliases: "dataweave 2, dwl"
---

# DataWeave

What is particular to DataWeave 2 work, inside a Mule application or on its own. `${CLAUDE_SKILL_DIR}` is this skill's directory. When the transform sits in a flow, the flow follows `mule-app`. A verified module with its MUnit tests lives in the mule-app example: `${CLAUDE_SKILL_DIR}/../mule-app/assets/mule4/error-handling/src/main/resources/dwl/` and its test suite, explained in `${CLAUDE_SKILL_DIR}/../mule-app/references/mule4/error-handling.md`.

## Steps

1. **Know the inputs and the output.** Read the input's MIME type and shape (an example, the spec's type, the connector's metadata) and the output the contract asks for. With no example, write a minimal synthetic one (FLOOR-1).
2. **Write small, pure functions** (DW-5), typed when they are public (DW-6), in a module when they are reused or longer than a few lines (DW-1).
3. **Handle absence and the unexpected on purpose:** every optional field gets `default` or a null-safe selector (DW-2), every `match` an `else`, with the type checked before literal cases (DW-7), every date and number an explicit format (DW-8).
4. **Test** each function and each transform with its edge cases: a missing field, an empty array, null, an unknown value, and a literal as the wrong type (DWTEST-1).
5. **Report** what you ran. A snippet you could not run against the real input is reported as not verified, with what would prove it.

## Rules

Read `${CLAUDE_SKILL_DIR}/rules.md` and act on every rule as its `Class:` says: `auto`, apply it; `propose`, recommend it, say what it costs, and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. Cite a rule by its ID and this skill's version, for example "breaks DW-7 (dataweave 1.1.0)".

If the project has an `engineering/profile.yaml`, apply these rules as the `project-profile` skill (engineering-profile) resolves them: skip a rule a pack or the project disabled, use the text and class of an overridden rule, and follow the rules the packs add. A rule marked `(floor)` always applies as written here.
