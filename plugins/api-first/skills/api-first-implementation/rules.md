# API-first implementation: rules

Rules for implementing an API change from its requirements. New in devFoundry. A team's own process may add to them or override them through its rules pack (`project-profile`, `references/layers.md`).

How to change this file: add a rule with the next number; edit a rule in place and keep its ID; retire a rule by keeping its ID with `(retired in <version>: <reason>)`, never reusing the number.

Every rule has a `Class:` line that says how the agent acts on it: `auto`, apply it; `propose`, recommend it with what it costs and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. A new rule gets a class; a profile can change it by ID (`project-profile`, `references/layers.md`), except on a floor rule.

## API-first implementation (AFI)

- **AFI-1** Before writing code, list every requirement of the change, numbered, with its source: operations, parameters, filters, exclusions, mappings, errors and non-functional statements, including those stated once in a note or a table row.
  Why: a requirement that is never written down is the one that gets lost, and a rule stated once in a note or a table row is the easiest to miss.
  Check: the answer opens with the reuse line (AFI-4), then the numbered inventory; each item names its file and section.
  Class: auto

- **AFI-2** Each requirement has at least one test that cites its ID, or a stated reason why it has none.
  Why: a test named after the requirement shows the reviewer what is proven and what is not.
  Check: every inventory ID appears in a test name or description, or in the final table with a reason.
  Class: auto

- **AFI-3** The answer ends with the final table of every requirement: done and tested, done but not tested, or not done, each with where it is and its test, and a reason for anything not done or not tested. A requirement not done because it waits on the developer (an ambiguity, a doubt about which component owns it, a value the requirements lack), or done on an assumption the developer must confirm, is also a question in the answer's "Decisions for you" section, not only a row of the table.
  Why: a requirement left out silently looks done; the table turns a gap into a decision the developer can see, and a reader who reads only the "Decisions for you" section must still see it.
  Check: the table has one row per inventory ID, checked against the code and the tests, not against memory; every `not done` that waits on the developer, and every assumption the developer must confirm, also appears in "Decisions for you".
  Class: auto

- **AFI-4** Before creating an API, a spec or a resource, look for what already exists: the specs in the project, the Exchange asset the project names (a spec dependency in `pom.xml`, an `apikit:config` that reads `resource::...`, an asset named in the requirements), and an existing System API that already reaches the same backend (named in the requirements, the project's documents or its configuration). Report what you found and whether the change reuses it, extends it or does not use it, and why; when nothing exists, say so.
  Why: a second API or spec for the same backend or resource is two contracts that drift apart, two sets of credentials and two places to fix each defect; the search is cheap, the duplicate is not.
  Check: the answer has a reuse line before the requirements inventory: what was searched, what was found (or "nothing found") and the decision for each item.
  Class: auto

- **AFI-5** Publishing to Exchange, creating an Exchange asset or a new version of one, and changing an API or asset that another project owns are the developer's decision; until the developer has decided, each one is a follow-up in the answer. Extending what the project itself holds (its own spec in `src/main/resources/api/`, its own flows) is part of the change.
  Why: a published asset or a change to another team's API reaches consumers outside this change, and cannot be taken back with a revert.
  Check: the change publishes nothing and creates no asset that the developer did not ask for or agree to; each such step appears in the answer as a question or a follow-up.
  Class: ask

- **AFI-6** When an existing System API reaches the backend the change needs and the requirements or the design do not say whether to use it, recommend calling it or reaching the backend directly, with what each costs (a dependency on that API, its limits and its credentials; or a second integration with the backend to keep), and build the one the developer agrees to.
  Why: going through a System API or around it is a layering decision of API-led connectivity (api-contracts LAYER-5 is the same decision: give it once), with costs on both sides; it belongs to the developer, and the recommendation makes it quick.
  Check: when AFI-4 found such an API, the answer gives the recommendation with both costs and says which way the developer chose, or that the requirements decided it.
  Class: propose
