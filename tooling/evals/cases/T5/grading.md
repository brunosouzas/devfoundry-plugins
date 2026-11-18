# T5 — grading (H2, implicit Circuit Breaker)

The request never names a pattern. The problem: a synchronous call to a dependency that, under load, hangs for 30–60 s and then answers `503`, and that recovers more slowly while callers keep hitting it. Waiting on every call ties up the app's threads (so even `GET /products` stops), and the traffic delays the dependency's recovery. More retries make both worse. The fix is to stop calling for a while after repeated failures, and to answer without the score (the doc allows a pending score).

Graded on the code and the final answer. One point per item; PASS = all five.

| # | Item | PASS when |
| --- | --- | --- |
| B1 | Open: fail fast | Failures of the score call are counted in state shared across requests (Object Store or equivalent). After a threshold, the call is **not made** for a cool-down period, and the flow answers at once (the application with the score pending, or a defined error such as 503). A timeout alone, or a retry, does not count. |
| B2 | Recovery: half-open | After the cool-down, a trial call is let through. Success closes the circuit (the count resets); failure opens it again. |
| B3 | What counts as a failure | Only failures that mean "the dependency is unhealthy" trip it (timeout, connectivity, 5xx), not `404` or other 4xx. **And** the score call gets an explicit response timeout well below the default, so a slow call cannot hold a thread for 30–60 s. |
| B4 | Limits stated (flexible) | The answer or a code comment states a limit of the breaker: whether its state is per worker or shared across workers, or that under concurrency the count and the half-open trial are approximate. |
| N1 | No wrong pattern | No Idempotent Receiver: no dedup store or validator keyed on the request (the call is a read). |

Record also, ungraded: whether `GET /products` is mentioned; whether a retry (`until-successful`) was added, and where.
