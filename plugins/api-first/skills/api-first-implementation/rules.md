# API-first implementation: rules

Rules for implementing an API change from its requirements. New in devFoundry. A team's own process may add to them or override them through its rules pack (`project-profile`, `references/layers.md`).

How to change this file: add a rule with the next number; edit a rule in place and keep its ID; retire a rule by keeping its ID with `(retired in <version>: <reason>)`, never reusing the number.

## API-first implementation (AFI)

- **AFI-1** Before writing code, list every requirement of the change, numbered, with its source: operations, parameters, filters, exclusions, mappings, errors and non-functional statements, including those stated once in a note or a table row.
  Why: a requirement that is never written down is the one that gets lost, and a rule stated once in a note or a table row is the easiest to miss.
  Check: the answer opens with the numbered inventory; each item names its file and section.

- **AFI-2** Each requirement has at least one test that cites its ID, or a stated reason why it has none.
  Why: a test named after the requirement shows the reviewer what is proven and what is not.
  Check: every inventory ID appears in a test name or description, or in the final table with a reason.

- **AFI-3** The answer ends with the final table of every requirement: done and tested, done but not tested, or not done, each with where it is and its test, and a reason for anything not done or not tested.
  Why: a requirement left out silently looks done; the table turns a gap into a decision the developer can see.
  Check: the table has one row per inventory ID, checked against the code and the tests, not against memory.
