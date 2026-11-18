# Verified example: an APIkit router on a spec kept in the project

Project: `${CLAUDE_SKILL_DIR}/assets/mule4/local-spec-router/` (Mule 4.9.5, APIkit 1.13.3, HTTP 1.10.3, MUnit 3.4.0). `scripts/verify-examples.sh` builds it and runs its 4 tests. A synthetic orders API: `GET /orders?status=` and `GET /orders/{orderId}`, both calling a backend over HTTP.

## What the example leaves out on purpose

It shows routing and testing, nothing else. A real spec also follows the api-contract rules the example skips: a security scheme on each operation (APISEC-1), examples (CON-3), a major version in the base path (CON-4), a bound or paging on `GET /orders` (RES-3), and every error status on each operation (CON-2). A real listener flow also maps `APIKIT:NOT_ACCEPTABLE` 406, `APIKIT:UNSUPPORTED_MEDIA_TYPE` 415 and `APIKIT:NOT_IMPLEMENTED` 501, with a test for each mapped error (MUNIT-2). Copy the syntax, not the scope.

## Files and why each piece is there

| File | What it shows |
| --- | --- |
| `src/main/resources/api/orders-api.yaml` | The API's own OAS 3 spec in the project: parameters with enum and pattern, the shared `Error` type, one response per status the API returns. |
| `src/main/resources/config.yaml` | `api.spec: "orders-api.yaml"`: the router reads the spec through a property, so moving to the Exchange dependency later changes one value (`resource::<groupId>:<assetId>:<version>:oas:zip:orders-api.yaml`, APIKIT-1). |
| `src/main/mule/global.xml` | `apikit:config api="${api.spec}"`, the listener config, and the backend request config with a `responseTimeout` from properties. |
| `src/main/mule/orders-api.xml` | The listener flow (router plus the APIKIT error responses), one thin implementation flow per operation (APIKIT-3), the private flows that call the backend, and an `error-mapping` from `HTTP:NOT_FOUND` to the app's `ORDERS:NOT_FOUND`. |
| `src/test/munit/orders-api-test-suite.xml` | Every test sends an HTTP request to the listener (MUNIT-5): 200 for each operation, 400 for an invalid enum (the backend is never called), 404 when the backend has no such order. |
| `pom.xml` | `dynamicPorts` in the `munit-maven-plugin` configuration: a free port for `http.port` during tests. |

## What the tests prove (mutation checks)

- Remove `/orders/{orderId}` from the spec: the build still compiles, and the get-order test fails with `Expected: 200 but: 404`. A test that called the implementation flow with `flow-ref` would still pass: this is how an API ships with routes that answer 404.
- Remove the `doc:name` filter from the backend mock: the mock also catches the test's own HTTP request, and the test fails with a `null` status. Mocks of `http:request` must be matched by `doc:name` (or `config-ref`) of the backend call.

## Pitfalls the build caught

- In `http:request`, the `error-mapping` element comes first, without an `error-mappings` wrapper, before `http:uri-params` and `http:query-params`. Any other order fails the XML schema at `process-classes`.
- `munit:dynamic-ports` does not exist in MUnit 3.4: the free port goes in the `munit-maven-plugin` configuration (`<dynamicPorts><dynamicPort>http.port</dynamicPort></dynamicPorts>`).
- The test's `http:request` needs `http:response-validator` with `success-status-code-validator values="100..599"`; without it, a 4xx answer raises an error in the test instead of letting it assert the status.
- Each test enables, with `munit:enable-flow-sources`, the listener flow and the implementation flows it reaches (MUNIT-4). Without the listener flow the request gets `Connection refused`; without the implementation flows the router raises `APIKIT:NOT_IMPLEMENTED` (500). Removing a flow from one test only can still pass when another test of the suite enables it, so check each test.
