---
name: munit
description: Rules for MUnit 3 tests of Mule 4 applications - what a test asserts, mocking outbound calls, error-path tests, the coverage gate, and testing each API endpoint through the HTTP listener and the APIkit router. Use when writing, changing, reviewing or fixing an MUnit test or suite under src/test/munit/, when a change adds or changes an endpoint and needs its tests, or when an MUnit run fails; recognise it by munit:test, munit-tools:mock-when or the munit-maven-plugin in a pom.xml. Do NOT use it for the flow under test itself, or for tests of a standalone DataWeave library. It supersedes the `munit` skill of the `mulesoft` plugin (brunosouzas/agent-skills) when both are installed: same IDs MUNIT-1 to MUNIT-4, plus MUNIT-5 and MUNIT-6.
---

# MUnit

What is particular to testing Mule 4 applications with MUnit 3. `${CLAUDE_SKILL_DIR}` is this skill's directory; the verified example lives with the apikit skill of this plugin, at `${CLAUDE_SKILL_DIR}/../apikit/assets/mule4/local-spec-router/` (its test suite and `pom.xml`), explained in `${CLAUDE_SKILL_DIR}/../apikit/references/mule4/local-spec-router.md`.

## Steps

1. **Start from the scenario.** Each test proves one scenario of the change: name it after the scenario, and decide first which payload, variables and status prove it (MUNIT-1).
2. **Test each endpoint through the listener** (MUNIT-5): the test sends an HTTP request to the app on `localhost:${http.port}` and asserts the status and the body. Enable the listener flow and the implementation flows the scenario reaches (MUNIT-4) and give the port to the `munit-maven-plugin` (`dynamicPorts`). A test that calls a flow with `flow-ref` is fine for the logic, but it does not prove the endpoint exists.
3. **Mock every outbound call** with `munit-tools:mock-when`, matched by the backend processor's `doc:name` or `config-ref`, never by `processor="http:request"` alone (MUNIT-6); a test never reaches a real system; a test where the backend must not be called asserts it with `verify-call times="0"`.
4. **Keep inputs synthetic and minimal**, never a real payload: in files under `src/test/resources/` for anything longer than a line, inline for a one-line payload.
5. **Cover the error paths:** one test per mapped error type, triggered by a mock that raises it (MUNIT-2), plus the router's 400 for an invalid parameter.
6. **Verify:** `mvn clean test` (or `verify`) runs the suites and the coverage gate (MUNIT-3). Read a failure's cause before changing the test: a test changed to pass hides the defect it found.

## Rules

Read `${CLAUDE_SKILL_DIR}/rules.md` and act on every rule as its `Class:` says: `auto`, apply it; `propose`, recommend it, say what it costs, and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. Cite a rule by its ID and this skill's version, for example "breaks MUNIT-5 (munit 0.4.0)".

If the project has an `engineering/profile.yaml`, apply these rules as the `project-profile` skill (engineering-profile) resolves them: skip a rule a pack or the project disabled, use the text and class of an overridden rule, and follow the rules the packs add. A rule marked `(floor)` always applies as written here.
