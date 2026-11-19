---
name: mule-sdk
description: Rules for shared Mule 4 assets that other applications depend on - connectors built with the Mule SDK (Java SDK), shared Mule plugins (mule-plugin packaging) and DataWeave libraries published to Exchange or a Maven repository - covering the public contract of exported operations and functions, semantic versioning of the asset, and connection management in connectors. Use when writing, changing or reviewing such an asset; recognise it by a pom.xml with mule-extension, mule-plugin or dw-library packaging, or @Extension and @Operations classes. Do NOT use it for a Mule application (mule-app), the DataWeave code inside a library (dataweave), publishing or deploying the asset (the team's delivery process), or a plain Java library with no Mule packaging. It supersedes the `mule-sdk` skill of brunosouzas/agent-skills when both are installed, keeping its rule IDs.
---

# Mule SDK and shared assets

What is particular to Mule 4 assets that applications depend on: connectors (Mule SDK), shared Mule plugins and DataWeave libraries. What makes them different from an application is that their exported surface is a contract: every consumer breaks when it changes. The DataWeave code of a library follows `dataweave`, and the build toolchain follows `mule-app` BUILD-1. `${CLAUDE_SKILL_DIR}` is this skill's directory.

## Steps

1. **Know the asset and its consumers.** Read the packaging and the current version in `pom.xml`, and find which applications depend on it before changing an exported operation, function or parameter.
2. **Decide the version first** (ASSET-1): a removed or changed exported signature is a new major version; a new operation or function is a minor one.
3. **Keep connections in the provider** (ASSET-2): an operation receives the connection as a parameter and never opens one.
4. **Build with the toolchain the Mule plugins support** (mule-app BUILD-1): Maven 3.9.x and the JDK of the target runtime. Maven 3.10 breaks `mule-extensions-maven-plugin` with `NoSuchMethodError`.
5. **Verify:** `mvn clean verify` on the asset, then build one consumer against the new version. Publishing it is the developer's decision (api-first AFI-5).

## Rules

Read `${CLAUDE_SKILL_DIR}/rules.md` and act on every rule as its `Class:` says: `auto`, apply it; `propose`, recommend it, say what it costs, and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. Cite a rule by its ID and this skill's version, for example "breaks ASSET-1 (mule-sdk 0.5.0)".

If the project has an `engineering/profile.yaml`, apply these rules as the `project-profile` skill (engineering-profile) resolves them: skip a rule a pack or the project disabled, use the text and class of an overridden rule, and follow the rules the packs add.
