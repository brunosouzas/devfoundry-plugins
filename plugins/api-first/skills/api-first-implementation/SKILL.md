---
name: api-first-implementation
description: "The API-first way to implement an API change from its requirements - reuse what exists, inventory every requirement, contract before code, code and tests traced to each requirement, and a final check that no requirement was silently left out. Use when asked to implement, build or change endpoints or integration flows \"following the requirements\", a spec, a story or a design (requirement documents in the project, an OpenSpec change, a design.md), in Mule 4 or any spec-driven API. Load it first when the work starts from requirements: it invokes project-profile and api-contract itself. Do NOT use it for a one-line fix with no requirement behind it, for only checking or writing the spec (api-contract), for only applying names or the profile (project-profile), for writing the requirements or the design themselves (that is the team's own process), or for reviewing someone else's change."
---

# API-first implementation

API-first is a public practice (MuleSoft's API-first guidance among others): the contract comes before the code, and the code answers the requirements, one by one. This skill gives the order and the checks. It is not a team's process: it never creates or asks for a design document, a spec-driven change, a review board, an approval, a pull request or a ticket. A team's own process (in its personal or company layer) produces the requirements or the design, runs its own reviews and gates, and calls this skill for the implementation. `${CLAUDE_SKILL_DIR}` is this skill's directory.

## Steps

0. **Reuse first (AFI-4 to AFI-6).** Before creating an API, a spec or a resource, look for what already exists, and say what you searched:
   - the specs in the project (in Mule, `src/main/resources/api/` and the spec `apikit:config` loads; on another stack, the project's spec folder);
   - the Exchange asset the project names: a spec dependency in `pom.xml`, an `apikit:config` that reads `resource::...`, or an asset the requirements name. Read what the project has of it; you cannot browse Exchange from here, so an asset nobody names is not searched for;
   - an existing System API that already reaches the same backend, named in the requirements, the project's documents or its configuration.

   Report each item found and the decision: reused, extended (only what the project itself holds), or not used, and why. When nothing exists, say "nothing found" and what was searched. Whether to call an existing System API or reach the backend directly, when the requirements do not say, is a recommendation with its costs (AFI-6, `propose`). Publishing to Exchange, creating an asset or a new version of one, or changing an API another project owns is the developer's decision: ask, and list it as a follow-up until then (AFI-5, `ask`).
1. **Inventory the requirements (AFI-1).** Before any code, read every source the request points to, whole, including tables, notes and examples. When the request names none, look in this order and read all that apply: the spec-driven change the request names, or the only open one (`openspec/changes/<name>/`: `proposal.md`, the `specs/` scenarios, its `design.md`, and only the implementation items of `tasks.md`; process tasks such as a review, a pull request or a ticket are not requirements); a `design.md` or ADR; then requirement documents (`docs/`, `requirements/`). When a change summarises documents, read the documents too: a one-line rule is easy to drop in a summary. Number every requirement `R1`, `R2`… in your answer, one line each, with its source (file and section). Count as requirements:
   - every operation, parameter, filter, exclusion, mapping and transformation rule, default and edge case;
   - every error the requirements name, and how the caller sees it;
   - every non-functional statement: timeouts, volumes, sessions, caching, security, logging.

   A rule stated once in a note or a table row is a requirement like any other. Where a requirement is ambiguous, write the assumption you take, next to it.
2. **Integration decisions and the project profile.** In Mule 4, invoke `project-profile` (engineering-profile): it applies the profile and its layers, lists the integration decisions of each flow (repeated messages, failures, slow dependencies) with the pattern skills, and for an endpoint calls `api-contract`. On another stack, follow the project's conventions and invoke `integration-patterns` and `resilience-patterns` directly.
3. **Contract first.** Make sure `api-contract` (api-contracts) has run for the operations in the inventory (step 2 calls it in Mule): the spec the application loads describes each of them before a flow is written. When the application routes without a spec and the request does not ask for one, say so and go on.
4. **Code.** Follow the profile and the platform skills (`mule-app`, `dataweave`, `apikit`, `munit` in mule-engineering; `integration-patterns`, `resilience-patterns`). Each requirement is implemented where a reader can find it; a rule that "could change" goes into configuration, not code.
5. **Tests trace to requirements (AFI-2).** Each requirement has at least one test whose name or description cites its ID (`r3-rejects-unknown-status-test`), or a reason in the final table why it has none (for example, a timeout value checked by reading the configuration). Endpoints are tested through the HTTP listener (`munit`, MUNIT-5).
6. **Verify.** Build and run the tests when you can (`mvn clean test` for Mule). When you cannot, say so; never report a build or a test you did not run.
7. **Final check (AFI-3).** Go back to the inventory, line by line, against the code and the tests (not against memory), and end your answer with the table:

   | ID | Requirement | Status | Where | Test |
   | --- | --- | --- | --- | --- |
   | R1 | ... | done and tested / done, not tested / not done | file and flow | test name, or why none |

   Every `not done` and `not tested` has its reason. Fix what you can before you finish; what stays open is listed, never dropped.

   Before the table, give a **"Decisions for you"** section: every question to the developer, in one place. It holds the AFI-5 and AFI-6 questions, each requirement left undone because it waits on the developer (an ambiguity, a doubt about which component owns it, a value the requirements lack), and each assumption the developer must confirm. A reader who reads only that section must see every open decision (AFI-3). It is not the integration decisions of `project-profile`, which say what the flow does about repeated messages and failures. The answer still opens with the reuse line and the inventory (AFI-4, AFI-1) and ends with the table.

## Rules

Read `${CLAUDE_SKILL_DIR}/rules.md` and act on every rule as its `Class:` says: `auto`, apply it; `propose`, recommend it, say what it costs, and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. Cite a rule by its ID and this skill's version, for example "breaks AFI-3 (api-first-implementation 1.0.0)".

If the project has an `engineering/profile.yaml`, apply these rules as the `project-profile` skill (engineering-profile) resolves them: skip a rule a pack or the project disabled, use the text and class of an overridden rule, and follow the rules the packs add.
