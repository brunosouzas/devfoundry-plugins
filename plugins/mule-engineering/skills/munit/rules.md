# MUnit: rules

Rules for MUnit tests of Mule 4 applications. MUNIT-1 to MUNIT-4 are ported from the `munit` skill of brunosouzas/agent-skills; MUNIT-5 and MUNIT-6 are new. In an existing project, follow the conventions it already uses and report a difference instead of renaming.

How to change this file: add a rule with the next number; edit a rule in place and keep its ID; retire a rule by keeping its ID with `(retired in <version>: <reason>)`, never reusing the number.

## MUnit (MUNIT)

- **MUNIT-1** Every flow change has an MUnit test that asserts the payload and the status the scenario specifies, with external calls mocked.
  Why: a test that only checks that the flow ran proves nothing.
  Check: each test has `assert-that` on the payload, the status or variables, and `mock-when` for each outbound call.

- **MUNIT-2** Test the error paths: each mapped error type has a test that triggers it.
  Why: error handling is the part nobody exercises by hand.
  Check: tests use `mock-when` with an error to trigger each handler.

- **MUNIT-3** Keep the coverage gate in `pom.xml` and never lower it to pass a build.
  Why: lowering the gate hides untested code.
  Check: the diff does not change the coverage settings.

- **MUNIT-4** A test that calls the application through HTTP lists in `munit:enable-flow-sources` the listener flow and every APIkit implementation flow the scenario reaches.
  Why: without the listener flow the request gets `Connection refused`; without the implementation flows the router answers `NOT_IMPLEMENTED`, and the test fails for a reason that is not in the code under test.
  Check: each test that sends an HTTP request to the app enables the listener flow and the implementation flows of its operations.

- **MUNIT-5** Every endpoint the change adds or changes has at least one test that sends an HTTP request to the application's listener and asserts the status and the body; an APIkit API also has a test for the router's 400 on an invalid parameter.
  Why: only a request through the listener exercises the router and the spec. A test that calls the implementation flow with `flow-ref` passes even when the spec has no such route, and the endpoint answers 404 in production.
  Check: for each new operation, a test whose execution is an `http:request` to `localhost:${http.port}` with the operation's method and path, and an `assert-that` on `attributes.statusCode`.

- **MUNIT-6** Mocks of an outbound connector operation are matched by the call's `doc:name` or `config-ref`, not by the processor type alone.
  Why: a mock of `http:request` with no attribute also catches the test's own HTTP request to the listener, and the test asserts on the mock's answer instead of the app's.
  Check: each `mock-when` of `http:request` has `with-attributes`.
