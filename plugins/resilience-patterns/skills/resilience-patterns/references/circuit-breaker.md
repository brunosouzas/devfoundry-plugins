# Circuit Breaker

## The problem

A flow calls a dependency synchronously. When that dependency is healthy it answers in milliseconds. When it is overloaded it does something worse than failing: it hangs for tens of seconds, then fails. Every request that waits on it holds a thread, so the app runs out of threads, and endpoints that never touch the dependency stop answering too. The callers keep sending requests at full rate, so the dependency gets no room to recover, and the outage lasts longer than the dependency's own problem.

A Circuit Breaker stops making the call for a while once the dependency is clearly failing. The flow answers at once instead: a fallback, or a defined error. After a cool-down it lets one trial call through to see whether the dependency is back. This protects the app's own threads and gives the dependency time to recover.

Timeouts alone do not solve it. They shorten the wait, but every request still goes out and still fails. Retries make it worse: they multiply the load on a dependency that is already overloaded.

## When to use

All of these hold:

- The call is **synchronous on a request path**: someone, a client or a thread, waits for it.
- The dependency can be **slow or unavailable for a stretch of time** (minutes, not one request), for example under load or during a deploy or an incident.
- There is **enough traffic** that waiting on it, or hammering it, is harmful: threads pile up, other endpoints suffer, or the dependency's recovery is delayed.
- There is a **sensible answer without the dependency**: a fallback (cached or partial data, a "pending" field) or a fast, explicit error (`503` with `Retry-After`).

## When NOT to use

Do not add a breaker when any of these holds. Say which one in the answer.

- **Low volume, nobody waiting.** A scheduled job that makes a handful of calls a day, or a batch that can simply run later, has no threads to protect and no load to shed. Opening a circuit only makes the job fail. Use a retry with a delay (`until-successful` with `maxRetries` and `millisBetweenRetries`), and an alert when it still fails.
- **Asynchronous consumer with redelivery.** A message that fails can wait, and the broker retries it. If the consumer must stop pulling messages while a dependency is down, use the broker client's own consumer breaker when it has one (the platform realization names it). Do not build one in the flow.
- **The failures are the caller's fault.** Validation errors, `404`s and other `4xx` say the dependency is healthy and answering. A breaker that counts them would cut off a healthy service.
- **A gateway already does it.** If the dependency is reached through a gateway that applies a circuit breaker policy, a second breaker in the flow adds state without adding protection. Check before adding one.

## The states

- **CLOSED:** calls go through, and consecutive dependency failures are counted. A success resets the count.
- **OPEN:** after `failureThreshold` consecutive failures, calls are **not made** for `openSeconds`. Each request is answered at once.
- **HALF_OPEN:** after the cool-down, one request is the trial. If it succeeds, the circuit closes and the count resets. If it fails, the circuit opens again with a fresh cool-down. While the trial is in flight, other requests keep failing fast.

## What counts as a failure

Count only what says "the dependency is unhealthy": a timeout, a connection failure, and the `5xx` statuses that mean "unavailable" (500, 502, 503, 504). A `4xx` means the dependency answered, so it is not counted, and a `4xx` on the trial call closes the circuit. A `429` is the dependency asking for less traffic: count it if the dependency uses it as an overload signal.

Give the call an explicit response timeout, well below the client's default, set from the dependency's normal latency, and a connection timeout, which the response timeout does not cover. Otherwise every request still holds a thread for the full default (or, for a host that does not answer the connect, for the default connection timeout, 30 s in Mule's HTTP connector) before the failure is even counted.

## Where the state lives

- **Per worker (in memory):** no network call per request, and each worker opens its own circuit after its own failures. This is enough in most cases.
- **Shared across workers (a persistent, shared store):** every worker opens together. It costs a store call on every request, and the store's rate limits apply. Use it only when per-worker circuits are not enough.

Either way, the count and the trial are **approximate under concurrency**. Two requests can read the same state at the same time, so a few extra calls can slip through while the circuit is opening or half-open. That is acceptable for a breaker, because it is about load, not correctness. State this limit in the answer.

## Realization per platform

Read the realization for the project's platform before writing code. It gives the order of preference between a ready-made module and building the breaker in the flow, shows a complete project known to build and pass its tests, and lists the pitfalls its build caught:

- **Mule 4:** `${CLAUDE_SKILL_DIR}/references/mule4/circuit-breaker.md`.

## Limits

- The breaker protects the app and the dependency from load. It does not make the dependency's answer available: while the circuit is open, the users get the fallback or the error.
- `failureThreshold` and `openSeconds` are trade-offs. A low threshold opens on a blip; a long cool-down keeps a recovered dependency cut off. State the values chosen and why.
- A per-worker circuit opens later on a worker that sees less traffic.

## The test of the breaker

The pattern is proven by a test showing that **an open circuit does not call the dependency**. Add, as the flow requires:

- **The threshold opens:** `threshold + 1` failing calls reach the dependency `threshold` times.
- **A 4xx does not trip:** every such call reaches the dependency.
- **The trial's success closes, and its failure reopens.**

Never wait for real time in a test. Put the stored "opened at" time in the past instead. The platform realization shows these tests in the platform's test framework. Run them when the environment allows it; if it does not, say that they were not run.
