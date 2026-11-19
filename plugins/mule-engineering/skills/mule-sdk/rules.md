# Mule SDK and shared assets: rules

Rules for Mule 4 connectors, shared Mule plugins and DataWeave libraries, from the Mule SDK documentation and semantic versioning. Ported from the `mule-sdk` skill of brunosouzas/agent-skills, with the same IDs. In an existing asset, follow the conventions it already uses and report a difference instead of renaming.

How to change this file: add a rule with the next number; edit a rule in place and keep its ID; retire a rule by keeping its ID with `(retired in <version>: <reason>)`, never reusing the number.

Every rule has a `Class:` line that says how the agent acts on it: `auto`, apply it; `propose`, recommend it with what it costs and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. A new rule gets a class; a profile can change it by ID (`project-profile`, `references/layers.md`), except on a floor rule.

## Shared assets (ASSET)

- **ASSET-1** Treat exported operations, functions and their parameters as a public contract: a breaking change bumps the major version.
  Why: every application that depends on the asset breaks on upgrade.
  Check: changed signatures come with a version bump in `pom.xml`.
  Class: auto

- **ASSET-2** A connector built with the Mule SDK keeps connection management in its connection provider and exposes only the operations it needs.
  Why: connection handling in operations leaks connections and cannot be pooled.
  Check: operations receive the connection as a parameter.
  Class: auto
