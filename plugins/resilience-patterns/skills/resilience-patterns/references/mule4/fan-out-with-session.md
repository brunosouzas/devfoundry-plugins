# Session renewal, bounded fan-out and retries — Mule 4 realization

The why of each piece is in `../session-renewal.md`, `../bounded-fan-out.md` and `../retry.md`. This file is how to build them in Mule 4. The three often come together (a backend with a login, a search, then one read per result), so one example shows all three; a flow that needs only one takes only that part.

## Native options first

- **OAuth 2.0:** when the dependency speaks OAuth, the HTTP connector's authentication with the OAuth module's client-credentials grant caches the token and gets a new one on a condition you set. Use it instead of building session renewal (not built in this example).
- **Reconnection strategies** (`reconnect`, `reconnect-forever`) on a connector retry the *connection*, not a failed request: they do not replace a retry of a `503`.
- **`until-successful`** retries a block with a **fixed** delay (`millisBetweenRetries`); Mule has no exponential backoff in the flow. Keep the attempts few on a request path.

## The example

A complete, built and tested project is in `${CLAUDE_SKILL_DIR}/assets/mule4/fan-out-with-session/` (this skill's directory). `scripts/verify-examples.sh` builds it and runs its 11 MUnit tests. Its domain is synthetic: `GET /api/shipments?date=` logs in to a carrier, searches the day's shipment ids, then reads each shipment. Adapt the names, the values and the error contract to the flow at hand; do not copy its domain. The split into files (`impl/carrier-client.xml` next to `impl/shipments-impl.xml`) is the example's own choice: in a project with a profile, the files, folders and names come from the profile (`project-profile`), also for the client of a backend.

| File | What it shows |
| --- | --- |
| `src/main/mule/common/global-config.xml` | The request config with `responseTimeout` from a property, and the session store: in memory, `entryTtl` below the dependency's session life, one entry |
| `src/main/mule/impl/carrier-client.xml` | **Session renewal** (`call-carrier-with-session`: on `CARRIER:SESSION_REJECTED`, reuse a newer cached session or drop the rejected one and log in, then repeat once); the cached session or a login (`get-carrier-session`); **retries** (`until-successful` around a `try` that checks the deadline, rethrows only transient errors and keeps a permanent one, then raises a defined error: a timeout after the last attempt is `504`, other transient failures `503`) |
| `src/main/mule/impl/shipments-impl.xml` | **The bounded fan-out:** the deadline set once (or taken from an outer one), the bound on N checked before any detail call, `parallel-foreach` with `maxConcurrency`, each route's failure caught and mapped to one defined error |
| `src/main/mule/common/common-error.xml` | `422` for too many results, `504` for the spent budget or a timeout, `503` for an unavailable carrier, `502` for a rejected session or a bad answer, each with a fixed body |
| `src/main/resources/properties/config.yaml` | Every value with the reason for it: timeout, session cache, attempts and delay, `maxItems`, budget, concurrency |
| `src/test/munit/shipments-test-suite.xml` | The 11 tests: the happy path through HTTP; the cached session is reused; a rejected session is renewed once (against a stub of the carrier); a second rejection fails without a loop; too many results is `422` with no detail call; a spent budget starts no call; a deadline stops the retries; a transient failure is tried `maxRetries + 1` times then `503`; a timeout after its retries is the carrier timeout; a `404` is not retried; a login timeout is `504` |

## How each part is built

- **Session renewal.** Keep the call in a `try` whose `on-error-continue type="CARRIER:SESSION_REJECTED"` replaces the session and makes the call once more. To replace it, read the cache again: a newer session than the rejected one (another request renewed it) is reused; otherwise remove it (`os:remove`, in its own `try` that ignores `OS:KEY_NOT_FOUND`) and log in. An error inside the handler propagates, so a second rejection reaches the caller: no loop. Map the dependency's expiry signal to the app's type with `error-mapping` (`HTTP:UNAUTHORIZED` to `CARRIER:SESSION_REJECTED`). A SOAP dependency signals expiry with a fault (Web Service Consumer `WSC:SOAP_FAULT`) or an error field in the answer: catch it, check the fault code the dependency documents, and raise the session type only for that code (not built in this example).
- **Retries.** `until-successful maxRetries=... millisBetweenRetries=...` around a `try` that first checks the deadline. Its `on-error-propagate` lists the transient types (`HTTP:TIMEOUT, HTTP:CONNECTIVITY, HTTP:BAD_GATEWAY, HTTP:SERVICE_UNAVAILABLE, HTTP:GATEWAY_TIMEOUT`), which `until-successful` then retries, and keeps the last one. Its `on-error-continue` keeps any other error (a spent budget included) in a variable, which ends the attempts. After the block, raise the kept error as a defined type. Exhausted retries arrive as `MULE:RETRY_EXHAUSTED`: raise the app's timeout type when the last attempt timed out, its "unavailable" type otherwise.
- **The bound and the budget.** Set `vars.deadlineMillis` once (`now() as Number {unit: 'milliseconds'}` plus the budget). Raise the "too many" type before the fan-out. Check the deadline in one sub-flow, called before every attempt and every login, and at the start of each `parallel-foreach` route. Catch the route's failure with `on-error-continue` and return `{ ok: false, errorType }`. After the scope, `payload map $.payload` gives the routes' results; raise one defined error from the failure types, most telling first.

## Pitfalls the build caught

- **A dynamic `flow-ref` (`name="#[vars.x]"`) fails in MUnit** with `No flow/sub-flow with name ... found`, even for a `flow`: with MUnit's lazy initialization (its default), what only a dynamic reference reaches is never created. Use static references (a `choice` on the name).
- **`os:retrieve` does not accept a null `default-value`** (`ObjectDoesNotExistException`): use an empty string and test it with `isEmpty`.
- **In DataWeave, `not a and b` is `not (a and b)`.** Write `(not isEmpty(x)) and y`. The build caught a renewal that never logged in again because of it.
- **An error raised in a `then-call` flow of a mock reaches the flow as `MULE:UNKNOWN`,** not as the type raised. To make a dependency answer differently per request (the old session rejected, the new one accepted), run a stub of it: a listener in the test suite on a free port (`dynamicPorts` in `pom.xml` for the property the request config reads), enabled with `munit:enable-flow-sources`. The real `401` then goes through the request's own `error-mapping`.
- **A failure inside `parallel-foreach` surfaces as `MULE:COMPOSITE_ROUTING`,** whose message carries the dependency's own text. Catch it in each route instead, and map the results.
- **`until-successful` retries every error** unless the block inside it decides: without the `on-error-continue` for permanent errors, a `404` is asked `maxRetries + 1` times.

## Mutation checks

Each part's test fails when the part is removed: no repeat after renewal (the two session tests fail), no bound (the `422` test fails), no deadline check (the two budget tests fail), retrying every error (the `404`, the retries' deadline and the session tests fail), a timeout after its retries treated as unavailable (the carrier timeout test fails).
