# Circuit Breaker — Mule 4 realization

The why of each piece is in `../circuit-breaker.md`. This file is how to build it in Mule 4.

## Native options first

- **Anypoint MQ consumer:** the subscriber has a native `circuitBreaker` (`onErrorTypes`, `errorsThreshold`, `tripTimeout`, `tripTimeoutUnit`; Anypoint MQ connector 2.1.0 and later). Use it instead of building one.
- **Behind Flex Gateway:** check whether the outbound circuit breaker policy already covers the dependency.

## In the flow

Mule 4 has no in-flow circuit breaker component for a synchronous HTTP call, so the state machine is built with an Object Store. A complete, built and tested project is in `${CLAUDE_SKILL_DIR}/assets/mule4/circuit-breaker/` (this skill's directory). `scripts/verify-examples.sh` builds it and runs its 5 MUnit tests. Its domain is a freight quote (`GET /quotes`, a carrier rates API). Adapt the names, the thresholds and the fallback to the flow at hand; do not copy its domain.

Its file names and layout are the example's own; in a project with a profile, they come from the profile (`project-profile`).

Read these files before writing the flow:

| File | What it shows |
| --- | --- |
| `pom.xml` | The `mule-objectstore-connector` dependency (classifier `mule-plugin`) |
| `src/main/mule/global.xml` | `responseTimeout` on the request config, and the state store (in memory, per worker, with the trade-off stated) |
| `src/main/mule/quotes.xml` | The API flow that maps `BREAKER:OPEN` to `503` + `Retry-After`, and the breaker flow without a source: read the state, fail fast or start a trial, call, then count or reset |
| `src/test/munit/circuit-breaker-test-suite.xml` | The 5 tests: open does not call, the threshold opens, a 4xx does not trip, the trial's success closes, the trial's failure reopens |
| `src/main/resources/config.yaml` | `failureThreshold`, `openSeconds` and the timeout, with the reasons for their values |

Keep the breaker logic in a flow without a source, so that MUnit can call it directly and other flows can reuse it for the same dependency. Use one state entry per dependency (the key is the dependency, not the request).

## Where the state lives (Mule)

- **In memory (`persistent="false"`), per worker:** no network call per request; each worker opens its own circuit after its own failures. This is enough in most cases.
- **Shared (persistent, Object Store v2 on CloudHub):** every worker opens together. It costs a store call on every request, and OSv2 has rate limits. Use it only when per-worker circuits are not enough.

Either way, the count and the trial are **approximate under concurrency**: two requests can read the same state at the same time, so a few extra calls can slip through while the circuit is opening or half-open. That is acceptable for a breaker, which is about load, not correctness. State this limit in the answer.

## Pitfalls the build catches

- A custom error type such as `BREAKER:OPEN` exists only if some `raise-error` raises it. An `on-error-*` handler for a type that is never raised fails to compile ("Could not find error").
- `<` inside an XML attribute must be written `&lt;` (for example in a `choice` `when` expression).
- The epoch comes from `now() as Number`, which gives seconds. Compare it with the stored `openedAt` in the same unit.
- `os:retrieve` with `<os:default-value>` returns the default when no state is stored yet, so a fresh app starts CLOSED.
- The pitfalls of the Idempotent Receiver reference also apply (`doc:name` needs `xmlns:doc`; MUnit payloads as serialized JSON; `--` is not allowed in XML comments).

## Failures that count, in Mule error types

`HTTP:TIMEOUT`, `HTTP:CONNECTIVITY`, `HTTP:INTERNAL_SERVER_ERROR`, `HTTP:BAD_GATEWAY`, `HTTP:SERVICE_UNAVAILABLE` and `HTTP:GATEWAY_TIMEOUT`. A `4xx` is handled by a separate `on-error-propagate` that does not count it, and on the trial call it closes the circuit. Set `responseTimeout` on the request config.

## The breaker test in MUnit

Use `assets/mule4/circuit-breaker/src/test/munit/circuit-breaker-test-suite.xml` as the model:

- **Open does not call:** store an `OPEN` state with a recent `openedAt` (`os:store` in the test). Call the breaker flow and catch the error. Check `verify-call ... times="0"` and that the error is the breaker's.
- **The threshold opens:** the mock raises `HTTP:SERVICE_UNAVAILABLE`. Call `threshold + 1` times, in a `foreach` with a `try` around each call. Check `times="<threshold>"` and that the stored state is `OPEN`.
- **A 4xx does not trip:** the mock raises `HTTP:NOT_FOUND`. Every call reaches the dependency.
- **The trial's success closes, and its failure reopens:** store `OPEN` with an `openedAt` in the past. Then check `CLOSED`, or `OPEN` with a fresh `openedAt`.
- **Pitfall seen in generated tests:** calling a listener flow in a loop loses `attributes` (such as `uriParams`) after the first mocked `http:request`, because the mock's response replaces them. Loop over the breaker flow, which has no source, or set the attributes again on each pass.

Run the tests with `mvn clean test` when the environment allows it.
