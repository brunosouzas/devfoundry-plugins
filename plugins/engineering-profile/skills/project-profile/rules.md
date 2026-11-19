# Project profile: rules

Floor rules: the public minimum that no pack or project profile can disable or override (`profiles/SCHEMA.md`, "How layers merge"). A layer can add a stricter rule of its own.

How to change this file: add a rule with the next number; edit a rule in place and keep its ID; retire a rule by keeping its ID with `(retired in <version>: <reason>)`, never reusing the number. Marking a rule `(floor)`, or removing the mark, is a MAJOR version.

Every rule has a `Class:` line that says how the agent acts on it: `auto`, apply it; `propose`, recommend it with what it costs and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. A new rule gets a class; a profile can change it by ID (`project-profile`, `references/layers.md`), except on a floor rule.

## Floor (FLOOR)

- **FLOOR-1** (floor) Test data, fixtures and examples are synthetic: no real customer data, names, documents, phone numbers, e-mails or production identifiers.
  Why: test files are copied, committed and shared far more widely than the systems they stand for.
  Check: test resources and examples hold no value that came from a real system; identifiers and contacts use reserved ranges (`example.test`, `07700 900xxx`).
  Class: auto

- **FLOOR-2** (floor) No secret in code or in plain configuration: passwords, keys and tokens come from the platform's secure store (in Mule, `${secure::...}` properties or the runtime's secrets) and never appear as a literal in the repository.
  Why: a secret in a repository is a leaked secret; rotating it is the only fix.
  Check: no literal password, key or token in `src/` or in properties files; secure properties hold only encrypted values or placeholders.
  Class: auto
