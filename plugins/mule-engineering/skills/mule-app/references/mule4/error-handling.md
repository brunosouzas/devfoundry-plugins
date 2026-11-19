# Verified example: global error handling, properties, logs and a DataWeave module

Project: `${CLAUDE_SKILL_DIR}/assets/mule4/error-handling/` (Mule 4.9.5, HTTP 1.10.3, MUnit 3.4.0). `scripts/verify-examples.sh` builds it and runs its 7 tests. A synthetic customers API: `GET /api/customers/{customerId}` reads a customer from a backend over HTTP and maps it with a DataWeave module.

## What the example leaves out on purpose

It shows how errors reach the caller, where configuration lives, how a log entry is built and how a module is tested. It routes with a plain listener, so the spec and the router are not here (`apikit` skill and its example), and the error bodies are fixed text where a real API uses the spec's error type (api-contract CON-2). Secure properties need the Secure Properties module and a key the deploy supplies (FLOOR-2); a real project adds them. The names (flows, files, variables) are placeholders: the project profile or the project's conventions win. The log messages are JSON objects, so they are structured once the project's `log4j2.xml` gives the core logger a JSON layout (MLOG-1); the example ships no `log4j2.xml`, and its build does not check a layout. The module coerces `id` and `createdAt` without a default: a row without them fails the transform (500), which is what this API wants; another API decides it under DW-2. Copy the syntax, not the scope. Its file names and layout are the example's own; in a project with a profile, they come from the profile (`project-profile`).

## Files and why each piece is there

| File | What it shows |
| --- | --- |
| `src/main/mule/common/global-config.xml` | Every global element once (FLOW-3): the property files, `configuration defaultErrorHandler-ref` (MERR-1), the listener, and the backend request config with `responseTimeout` and a connection timeout (`sockets:tcp-client-socket-properties connectionTimeout`, namespace `sockets`, no extra dependency) from properties (MERR-3, CFG-1). The `env` global property defaults to `local`; the deploy sets `-Denv=<name>`. |
| `src/main/mule/common/common-error.xml` | The global error handler: `CUSTOMERS:NOT_FOUND` 404, `HTTP:TIMEOUT` 504, `HTTP:CONNECTIVITY` 503, anything else 500, each with a fixed body and never `error.description` (MERR-2, MERR-3), and one sub-flow that logs the failure with the correlation id and the error type (MLOG-1, MLOG-2). |
| `src/main/mule/customers-api.xml` | The entry flow: the listener answers with `vars.httpStatus`, set by the handler, and logs the request at entry and exit as JSON objects with the correlation id, never the payload (MLOG-1, MLOG-2). |
| `src/main/mule/impl/customers-impl.xml` | The work, in a sub-flow: the backend call with an `error-mapping` from `HTTP:NOT_FOUND` to the app's `CUSTOMERS:NOT_FOUND`, then the mapping through the module. |
| `src/main/resources/dwl/customer/CustomerMapping.dwl` | A module with a type and typed, pure functions (DW-5, DW-6), a `match` whose `else` fails with the unknown value (DW-7), and explicit date formats in and out (DW-8). |
| `src/main/resources/properties/` | `config.yaml` for what every environment shares, and one `config-<env>.yaml` per environment, the backend's protocol included (CFG-3). |
| `src/test/munit/customers-api-test-suite.xml` | Five tests through the listener (MUNIT-5): 200, and one per mapped error type, raised by a mock of the backend call (MUNIT-2, MUNIT-6). Three tests of the module alone: a missing field, an unknown status, a status sent as a number (DWTEST-1; the module takes one row, so there is no collection to test empty). |

## What the tests prove (mutation checks)

- Remove the `HTTP:TIMEOUT` case from the handler: the timeout falls into `ANY`, and `backend-timeout-gives-504-test` fails (500 instead of 504).
- Remove `defaultErrorHandler-ref`: the 404, 503 and 504 tests fail, and the 500 test errors. No handler means Mule's default answer, whatever the error.
- Put `error.description` in the timeout body: `backend-timeout-gives-504-test` fails on the message. The test pins the body's text, so a raw error message cannot slip in unseen.

## Pitfalls the build caught

- A mock that returns `readUrl(..., 'application/json')` hands the flow a Java map labelled JSON, and the next transform fails with `requires a Stream Compatible content`. Return the file as text (`MunitTools::getResourceAsString('backend-customer.json')`) with `mediaType="application/json"`.
- A test with `expectedErrorType` and nothing to assert has no `munit:validation`: an empty one fails the XML schema.
- The listener flow is the only flow source a test through HTTP needs to enable (MUNIT-4) when the work is in sub-flows, which have no source.
- Mule loads the XML files in the subfolders of `src/main/mule/` (`common/`, `impl/`) with no list in `mule-artifact.json`.
